import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent / "smarthire.db"

SAMPLE_JOBS = [
    ("Python Developer Trainee", "TechNova Solutions", "Hyderabad", "Entry Level", "₹3.5–5 LPA",
     "Build and maintain Python applications, write clean code, work with SQL databases and collaborate with developers.",
     "Python, Flask, SQL, REST APIs"),
    ("Junior Software Engineer", "BrightPath Systems", "Bengaluru", "Fresher", "₹4–6 LPA",
     "Contribute to application development, debugging, code reviews and software testing.",
     "Python or Java, OOP, Git, SQL, problem solving"),
    ("Frontend Developer Intern", "PixelCraft Labs", "Remote", "Internship", "₹15,000/month",
     "Develop responsive web interfaces and integrate frontend components with REST APIs.",
     "HTML, CSS, JavaScript, React, Git"),
    ("QA Automation Trainee", "QualityWorks", "Chennai", "Entry Level", "₹3–4.5 LPA",
     "Prepare test cases, report defects and support functional and automation testing.",
     "Manual Testing, Python or Java, Selenium basics, SQL"),
    ("Graduate Engineer Trainee", "NextGen Digital", "Hyderabad", "Graduate", "₹4–5.5 LPA",
     "Work across software development tasks, database operations, debugging and technical documentation.",
     "Programming fundamentals, OOP, DBMS, SQL, communication"),
    ("Data Analyst Trainee", "InsightBridge", "Remote", "Entry Level", "₹3–4 LPA",
     "Clean datasets, write SQL queries and prepare reports for business stakeholders.",
     "SQL, Python, Pandas, Excel, Power BI"),
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            salary TEXT NOT NULL,
            description TEXT NOT NULL,
            skills TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            note TEXT DEFAULT '',
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, job_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if count == 0:
            conn.executemany("""
                INSERT INTO jobs (title, company, location, job_type, salary, description, skills)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, SAMPLE_JOBS)
