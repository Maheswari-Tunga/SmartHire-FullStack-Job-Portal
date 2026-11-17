# SmartHire – Full-Stack Job Portal

A fresher-friendly full-stack project demonstrating Python, Flask, REST APIs, SQLite, JavaScript, HTML and CSS.

## Features
- User registration and login with password hashing
- Session-based authentication
- Browse and search jobs
- View job details
- Apply for jobs (duplicate applications prevented)
- View and track submitted applications
- Dashboard with application statistics
- Seeded sample job listings
- Responsive interface

## Technology stack
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Python 3, Flask
- Database: SQLite
- API: JSON REST endpoints

## Project structure
```text
SmartHire_FullStack/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── index.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:

   **Windows**
   ```bash
   py -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the application:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000

The SQLite database and sample jobs are created automatically on first run.

## Demo workflow
- Register a new account.
- Sign in.
- Search and filter the seeded job listings.
- Apply to a job.
- Open Dashboard to see the application and its status.

## API overview
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/register` | Create account |
| POST | `/api/login` | Sign in |
| POST | `/api/logout` | Sign out |
| GET | `/api/me` | Current user |
| GET | `/api/jobs` | List/search jobs |
| GET | `/api/jobs/<id>` | Job details |
| POST | `/api/jobs/<id>/apply` | Apply for a job |
| GET | `/api/applications` | Current user's applications |
| PATCH | `/api/applications/<id>` | Update own application note |

## Security and scope
- Passwords are stored as Werkzeug password hashes, not plain text.
- User-specific endpoints require a logged-in session.
- SQLite queries use parameterized statements.
- This is an educational portfolio project. Before production deployment, configure a strong `SECRET_KEY`, HTTPS, CSRF protection, rate limiting, database migrations, logging, and production-grade hosting.
- Job data is seeded sample data. No external job-board API is connected.
- No external generative-AI service is connected; do not describe this version as an AI-powered application.

## Resume-ready project description
**SmartHire – Full-Stack Job Portal**  
*Python, Flask, REST APIs, SQLite, JavaScript, HTML5, CSS3*
- Developed a full-stack job portal with user authentication, job search, job details and application tracking.
- Built Flask REST APIs for registration, login, job retrieval and job applications.
- Designed a relational SQLite database and implemented parameterized queries to manage users, jobs and applications.
- Created a responsive JavaScript frontend with search, filtering and a personalized application dashboard.

Only include features on your resume after running and testing them yourself.
