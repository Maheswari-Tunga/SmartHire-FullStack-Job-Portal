import os
import sqlite3
from functools import wraps
from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Please sign in to continue."}), 401
        return fn(*args, **kwargs)
    return wrapper

def row_to_dict(row):
    return dict(row) if row else None

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not name or not email or len(password) < 8:
        return jsonify({"error": "Enter your name, a valid email and a password of at least 8 characters."}), 400
    try:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            session["user_id"] = cur.lastrowid
            session["user_name"] = name
        return jsonify({"message": "Account created successfully.", "user": {"name": name, "email": email}}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with this email already exists."}), 409

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect email or password."}), 401
    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify({"message": "Signed in successfully.", "user": {"name": user["name"], "email": user["email"]}})

@app.post("/api/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Signed out successfully."})

@app.get("/api/me")
def me():
    if not session.get("user_id"):
        return jsonify({"user": None})
    with get_connection() as conn:
        user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    return jsonify({"user": row_to_dict(user)})

@app.get("/api/jobs")
def jobs():
    search = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if search:
        term = f"%{search}%"
        sql += " AND (title LIKE ? OR company LIKE ? OR skills LIKE ?)"
        params.extend([term, term, term])
    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")
    sql += " ORDER BY id DESC"
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return jsonify({"jobs": [row_to_dict(r) for r in rows]})

@app.get("/api/jobs/<int:job_id>")
def job_detail(job_id):
    with get_connection() as conn:
        job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        return jsonify({"error": "Job not found."}), 404
    return jsonify({"job": row_to_dict(job)})

@app.post("/api/jobs/<int:job_id>/apply")
@login_required
def apply(job_id):
    with get_connection() as conn:
        job = conn.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if not job:
            return jsonify({"error": "Job not found."}), 404
        try:
            conn.execute("INSERT INTO applications (user_id, job_id) VALUES (?, ?)",
                         (session["user_id"], job_id))
        except sqlite3.IntegrityError:
            return jsonify({"error": "You have already applied for this job."}), 409
    return jsonify({"message": "Application submitted successfully."}), 201

@app.get("/api/applications")
@login_required
def applications():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT a.id, a.status, a.note, a.applied_at,
                   j.title, j.company, j.location, j.job_type
            FROM applications a
            JOIN jobs j ON j.id = a.job_id
            WHERE a.user_id = ?
            ORDER BY a.applied_at DESC
        """, (session["user_id"],)).fetchall()
    items = [row_to_dict(r) for r in rows]
    return jsonify({"applications": items, "total": len(items)})

@app.patch("/api/applications/<int:application_id>")
@login_required
def update_application_note(application_id):
    data = request.get_json(silent=True) or {}
    note = str(data.get("note", "")).strip()[:500]
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE applications SET note = ? WHERE id = ? AND user_id = ?",
            (note, application_id, session["user_id"])
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Application not found."}), 404
    return jsonify({"message": "Note updated.", "note": note})

@app.get("/api/dashboard")
@login_required
def dashboard_data():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
        recent = conn.execute("""
            SELECT a.id, a.status, a.applied_at, j.title, j.company
            FROM applications a JOIN jobs j ON j.id = a.job_id
            WHERE a.user_id = ? ORDER BY a.applied_at DESC LIMIT 5
        """, (session["user_id"],)).fetchall()
    return jsonify({"total_applications": total, "recent": [row_to_dict(r) for r in recent]})

@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found."}), 404
    return "Page not found", 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
