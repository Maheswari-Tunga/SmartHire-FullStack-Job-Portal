const $ = (selector) => document.querySelector(selector);
const toast = (message) => {
  const el = $("#toast");
  if (!el) return;
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2800);
};
async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[c]));
}
let currentUser = null;
async function refreshUser() {
  try {
    const data = await api("/api/me");
    currentUser = data.user;
  } catch { currentUser = null; }
  const welcome = $("#welcomeText");
  if (welcome) welcome.textContent = currentUser ? `Hi, ${currentUser.name}` : "";
  const authButton = $("#authButton");
  if (authButton) authButton.hidden = !!currentUser;
  const logoutButton = $("#logoutButton");
  if (logoutButton) logoutButton.hidden = !currentUser;
  const dashboardLink = $("#dashboardLink");
  if (dashboardLink) dashboardLink.hidden = !currentUser;
}
async function loadJobs() {
  const list = $("#jobList");
  if (!list) return;
  const q = $("#searchInput")?.value.trim() || "";
  const location = $("#locationInput")?.value.trim() || "";
  list.innerHTML = '<div class="empty">Finding matching jobs…</div>';
  try {
    const params = new URLSearchParams({q, location});
    const data = await api(`/api/jobs?${params}`);
    $("#jobCount").textContent = `${data.jobs.length} opportunities`;
    if (!data.jobs.length) {
      list.innerHTML = '<div class="empty">No jobs match your search. Try a different keyword or location.</div>';
      return;
    }
    list.innerHTML = data.jobs.map(job => `
      <article class="job-card">
        <div class="company-mark">${escapeHtml(job.company.slice(0,1).toUpperCase())}</div>
        <div class="job-card-content">
          <div class="job-meta"><span>${escapeHtml(job.job_type)}</span><span>${escapeHtml(job.location)}</span></div>
          <h3>${escapeHtml(job.title)}</h3><p class="company-name">${escapeHtml(job.company)}</p>
          <p class="job-description">${escapeHtml(job.description)}</p>
          <p class="skills">${escapeHtml(job.skills)}</p>
          <div class="job-card-bottom"><strong>${escapeHtml(job.salary)}</strong>
            <button class="btn btn-primary apply-button" data-job-id="${job.id}">Apply now</button></div>
        </div>
      </article>`).join("");
    list.querySelectorAll(".apply-button").forEach(button => {
      button.addEventListener("click", () => applyForJob(button.dataset.jobId));
    });
  } catch (error) { list.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`; }
}
async function applyForJob(id) {
  if (!currentUser) {
    openAuthModal();
    $("#authMessage").textContent = "Please sign in or create an account before applying.";
    return;
  }
  try {
    const data = await api(`/api/jobs/${id}/apply`, {method:"POST", body:"{}"});
    toast(data.message);
  } catch (error) { toast(error.message); }
}
let authMode = "login";
function setAuthMode(mode) {
  authMode = mode;
  const registering = mode === "register";
  $("#modalTitle").textContent = registering ? "Create your account" : "Sign in";
  $("#authSubmit").textContent = registering ? "Create account" : "Sign in";
  $("#nameLabel").hidden = !registering;
  $("#nameField").required = registering;
  $("#passwordField").autocomplete = registering ? "new-password" : "current-password";
  $("#loginTab").classList.toggle("active", !registering);
  $("#registerTab").classList.toggle("active", registering);
  $("#authMessage").textContent = "";
}
function openAuthModal() {
  $("#authModal").hidden = false;
  setAuthMode("login");
}
function closeAuthModal() { if ($("#authModal")) $("#authModal").hidden = true; }

async function loadDashboard() {
  const list = $("#applicationList");
  if (!list) return;
  try {
    const data = await api("/api/dashboard");
    $("#totalApplications").textContent = data.total_applications;
    if (!data.recent.length) {
      list.innerHTML = '<div class="empty">You have not applied for any jobs yet. <a class="text-link" href="/">Explore open roles</a>.</div>';
      return;
    }
    list.innerHTML = data.recent.map(item => `
      <article class="application-card">
        <div><h3>${escapeHtml(item.title)}</h3><p class="company-name">${escapeHtml(item.company)}</p>
        <span class="muted small">Applied ${new Date(item.applied_at + " UTC").toLocaleDateString()}</span></div>
        <span class="status-pill">${escapeHtml(item.status)}</span>
      </article>`).join("");
  } catch (error) {
    list.innerHTML = `<div class="empty">${escapeHtml(error.message)} <a href="/">Return to jobs</a></div>`;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await refreshUser();
  if ($("#jobList")) {
    loadJobs();
    $("#searchButton").addEventListener("click", loadJobs);
    $("#searchInput").addEventListener("keydown", e => { if (e.key === "Enter") loadJobs(); });
    $("#locationInput").addEventListener("keydown", e => { if (e.key === "Enter") loadJobs(); });
  }
  if ($("#applicationList")) {
    if (!currentUser) {
      $("#applicationList").innerHTML = '<div class="empty">Please <a class="text-link" href="/">sign in</a> to view your applications.</div>';
      $("#totalApplications").textContent = "0";
    } else loadDashboard();
  }
  $("#authButton")?.addEventListener("click", openAuthModal);
  $("#closeModal")?.addEventListener("click", closeAuthModal);
  $("#authModal")?.addEventListener("click", e => { if (e.target.id === "authModal") closeAuthModal(); });
  $("#loginTab")?.addEventListener("click", () => setAuthMode("login"));
  $("#registerTab")?.addEventListener("click", () => setAuthMode("register"));
  $("#authForm")?.addEventListener("submit", async e => {
    e.preventDefault();
    const payload = {email: $("#emailField").value, password: $("#passwordField").value};
    if (authMode === "register") payload.name = $("#nameField").value;
    try {
      await api(authMode === "register" ? "/api/register" : "/api/login",
        {method:"POST", body:JSON.stringify(payload)});
      closeAuthModal();
      await refreshUser();
      toast(authMode === "register" ? "Account created. Welcome!" : "Welcome back!");
      if ($("#applicationList")) loadDashboard();
    } catch (error) { $("#authMessage").textContent = error.message; }
  });
  $("#logoutButton")?.addEventListener("click", async () => {
    try { await api("/api/logout", {method:"POST", body:"{}"}); }
    catch {}
    currentUser = null;
    window.location.href = "/";
  });
});
