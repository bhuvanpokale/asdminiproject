"""
PlacementPro - Student Placement Preparation and Job Tracking System
Built with Python, Flask, SQLite, Pytest, and Docker.
"""

import os
import sqlite3
from functools import wraps
from datetime import datetime, timezone
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    g,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "placementpro-local-dev-key-college-demo"
)
app.config["DATABASE"] = os.environ.get("DATABASE_FILE", "placementpro.db")


def get_db():
    """Get database connection for current request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Close the database connection when request context ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database tables."""
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            college TEXT,
            department TEXT,
            grad_year TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_name TEXT NOT NULL,
            role TEXT NOT NULL,
            job_type TEXT DEFAULT 'Full-time',
            salary TEXT,
            status TEXT DEFAULT 'Applied',
            application_date TEXT,
            deadline TEXT,
            job_url TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            application_id INTEGER,
            company_name TEXT NOT NULL,
            round_type TEXT NOT NULL,
            interview_date TEXT NOT NULL,
            interview_time TEXT NOT NULL,
            interview_mode TEXT DEFAULT 'Virtual',
            meeting_link TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS preparation_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Not Started',
            resource_url TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# -------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------


@app.route("/")
def index():
    """Home route redirects to dashboard if logged in, else login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()
        grad_year = request.form.get("grad_year", "").strip()

        if not username or not email or not password:
            flash("Username, email, and password are required.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
        ).fetchone()

        if existing:
            flash("Username or email already exists.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        db.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, department, grad_year)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, email, password_hash, full_name, department, grad_year),
        )
        db.commit()

        # Retrieve new user id and auto-seed default starter preparation topics
        new_user = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if new_user:
            seed_default_preparation(db, new_user["id"])
            db.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


def seed_default_preparation(db, user_id):
    """Seed initial placement preparation topics for new users."""
    default_topics = [
        ("Data Structures & Algorithms", "Arrays & Two Pointers", "Easy", "In Progress", "https://leetcode.com"),
        ("Data Structures & Algorithms", "Binary Trees & BST Traversals", "Medium", "Not Started", "https://leetcode.com"),
        ("Data Structures & Algorithms", "Dynamic Programming Basics", "Hard", "Not Started", "https://leetcode.com"),
        ("Core Computer Science", "Operating Systems: Process vs Thread & Scheduling", "Medium", "Completed", "https://geeksforgeeks.org"),
        ("Core Computer Science", "DBMS: Normalization & Indexing", "Medium", "Completed", "https://geeksforgeeks.org"),
        ("Core Computer Science", "Computer Networks: TCP/IP vs OSI model", "Easy", "Completed", "https://geeksforgeeks.org"),
        ("System Design", "Load Balancing & Horizontal Scaling", "Medium", "In Progress", "https://github.com"),
        ("Aptitude & Reasoning", "Quantitative Aptitude: Speed, Time & Work", "Easy", "Completed", "https://indiabix.com"),
        ("Behavioral & HR", "Tell Me About Yourself & STAR Method Prep", "Easy", "Completed", "https://themuse.com"),
    ]
    for cat, title, diff, stat, res in default_topics:
        db.execute(
            """
            INSERT INTO preparation_topics (user_id, category, title, difficulty, status, resource_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, cat, title, diff, stat, res),
        )


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, username),
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"] or user["username"]
            flash(f"Welcome back, {session['full_name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# -------------------------------------------------------------
# Dashboard & Main Features
# -------------------------------------------------------------


@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard displaying overview statistics and upcoming tasks."""
    user_id = session["user_id"]
    db = get_db()

    # Core statistics
    app_count = db.execute(
        "SELECT COUNT(*) AS total FROM applications WHERE user_id = ?",
        (user_id,),
    ).fetchone()["total"]

    interview_count = db.execute(
        "SELECT COUNT(*) AS total FROM interviews WHERE user_id = ?",
        (user_id,),
    ).fetchone()["total"]

    offer_count = db.execute(
        "SELECT COUNT(*) AS total FROM applications WHERE user_id = ? AND LOWER(status) = 'offered'",
        (user_id,),
    ).fetchone()["total"]

    # Preparation statistics
    total_prep = db.execute(
        "SELECT COUNT(*) AS total FROM preparation_topics WHERE user_id = ?",
        (user_id,),
    ).fetchone()["total"]

    completed_prep = db.execute(
        "SELECT COUNT(*) AS total FROM preparation_topics WHERE user_id = ? AND status = 'Completed'",
        (user_id,),
    ).fetchone()["total"]

    in_progress_prep = db.execute(
        "SELECT COUNT(*) AS total FROM preparation_topics WHERE user_id = ? AND status = 'In Progress'",
        (user_id,),
    ).fetchone()["total"]

    prep_percentage = (
        round((completed_prep / total_prep) * 100) if total_prep > 0 else 0
    )

    # Category breakdown for progress bars
    categories_raw = db.execute(
        """
        SELECT category,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
        FROM preparation_topics
        WHERE user_id = ?
        GROUP BY category
        """,
        (user_id,),
    ).fetchall()

    categories_progress = []
    for row in categories_raw:
        tot = row["total"]
        comp = row["completed"] or 0
        pct = round((comp / tot) * 100) if tot > 0 else 0
        categories_progress.append(
            {"category": row["category"], "total": tot, "completed": comp, "percent": pct}
        )

    # Upcoming interviews
    upcoming_interviews = db.execute(
        """
        SELECT * FROM interviews
        WHERE user_id = ? AND LOWER(status) NOT IN ('completed', 'cancelled')
        ORDER BY interview_date ASC, interview_time ASC
        LIMIT 5
        """,
        (user_id,),
    ).fetchall()

    # Recent applications
    recent_applications = db.execute(
        """
        SELECT * FROM applications
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,),
    ).fetchall()

    stats = {
        "applications": app_count,
        "interviews": interview_count,
        "offers": offer_count,
        "prep_percentage": prep_percentage,
        "total_prep": total_prep,
        "completed_prep": completed_prep,
        "in_progress_prep": in_progress_prep,
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        upcoming_interviews=upcoming_interviews,
        recent_applications=recent_applications,
        categories_progress=categories_progress,
    )


# -------------------------------------------------------------
# Applications Module
# -------------------------------------------------------------


@app.route("/applications")
@login_required
def applications():
    """List job applications with filtering and search."""
    user_id = session["user_id"]
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip()

    db = get_db()
    query = "SELECT * FROM applications WHERE user_id = ?"
    params = [user_id]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND (company_name LIKE ? OR role LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    query += " ORDER BY created_at DESC"
    applications_list = db.execute(query, params).fetchall()

    return render_template(
        "applications.html",
        applications=applications_list,
        status_filter=status_filter,
        search_query=search_query,
    )


@app.route("/applications/add", methods=["POST"])
@login_required
def add_application():
    """Add a new job application."""
    user_id = session["user_id"]
    company_name = request.form.get("company_name", "").strip()
    role = request.form.get("role", "").strip()
    job_type = request.form.get("job_type", "Full-time")
    salary = request.form.get("salary", "").strip()
    status = request.form.get("status", "Applied")
    application_date = request.form.get(
        "application_date", datetime.now().strftime("%Y-%m-%d")
    )
    deadline = request.form.get("deadline", "")
    job_url = request.form.get("job_url", "")
    notes = request.form.get("notes", "")

    if not company_name or not role:
        flash("Company name and role are required.", "danger")
        return redirect(url_for("applications"))

    db = get_db()
    db.execute(
        """
        INSERT INTO applications (user_id, company_name, role, job_type, salary, status, application_date, deadline, job_url, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            company_name,
            role,
            job_type,
            salary,
            status,
            application_date,
            deadline,
            job_url,
            notes,
        ),
    )
    db.commit()
    flash(f"Application for {company_name} added successfully!", "success")
    return redirect(url_for("applications"))


@app.route("/applications/edit/<int:app_id>", methods=["POST"])
@login_required
def edit_application(app_id):
    """Edit an existing job application."""
    user_id = session["user_id"]
    db = get_db()

    app_record = db.execute(
        "SELECT * FROM applications WHERE id = ? AND user_id = ?",
        (app_id, user_id),
    ).fetchone()

    if not app_record:
        flash("Application record not found.", "danger")
        return redirect(url_for("applications"))

    company_name = request.form.get("company_name", "").strip()
    role = request.form.get("role", "").strip()
    job_type = request.form.get("job_type", "Full-time")
    salary = request.form.get("salary", "").strip()
    status = request.form.get("status", "Applied")
    application_date = request.form.get("application_date", "")
    deadline = request.form.get("deadline", "")
    job_url = request.form.get("job_url", "")
    notes = request.form.get("notes", "")

    if not company_name or not role:
        flash("Company name and role cannot be empty.", "danger")
        return redirect(url_for("applications"))

    db.execute(
        """
        UPDATE applications
        SET company_name = ?, role = ?, job_type = ?, salary = ?, status = ?,
            application_date = ?, deadline = ?, job_url = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            company_name,
            role,
            job_type,
            salary,
            status,
            application_date,
            deadline,
            job_url,
            notes,
            app_id,
            user_id,
        ),
    )
    db.commit()
    flash(f"Application for {company_name} updated successfully!", "success")
    return redirect(url_for("applications"))


@app.route("/applications/delete/<int:app_id>", methods=["POST"])
@login_required
def delete_application(app_id):
    """Delete a job application."""
    user_id = session["user_id"]
    db = get_db()
    db.execute(
        "DELETE FROM applications WHERE id = ? AND user_id = ?",
        (app_id, user_id),
    )
    db.commit()
    flash("Application deleted successfully.", "info")
    return redirect(url_for("applications"))


# -------------------------------------------------------------
# Interviews Module
# -------------------------------------------------------------


@app.route("/interviews")
@login_required
def interviews():
    """List interview schedules."""
    user_id = session["user_id"]
    db = get_db()

    interviews_list = db.execute(
        """
        SELECT i.*, a.role
        FROM interviews i
        LEFT JOIN applications a ON i.application_id = a.id
        WHERE i.user_id = ?
        ORDER BY i.interview_date ASC, i.interview_time ASC
        """,
        (user_id,),
    ).fetchall()

    user_applications = db.execute(
        "SELECT id, company_name, role FROM applications WHERE user_id = ? ORDER BY company_name ASC",
        (user_id,),
    ).fetchall()

    return render_template(
        "interviews.html",
        interviews=interviews_list,
        applications=user_applications,
    )


@app.route("/interviews/add", methods=["POST"])
@login_required
def add_interview():
    """Add an interview schedule."""
    user_id = session["user_id"]
    company_name = request.form.get("company_name", "").strip()
    round_type = request.form.get("round_type", "Technical Round").strip()
    interview_date = request.form.get("interview_date", "").strip()
    interview_time = request.form.get("interview_time", "").strip()
    interview_mode = request.form.get("interview_mode", "Virtual")
    meeting_link = request.form.get("meeting_link", "").strip()
    status = request.form.get("status", "Scheduled")
    notes = request.form.get("notes", "").strip()
    application_id = request.form.get("application_id")

    if not company_name or not round_type or not interview_date:
        flash("Company name, round type, and date are required.", "danger")
        return redirect(url_for("interviews"))

    app_id_val = int(application_id) if application_id and application_id.isdigit() else None

    db = get_db()
    db.execute(
        """
        INSERT INTO interviews (user_id, application_id, company_name, round_type, interview_date, interview_time, interview_mode, meeting_link, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            app_id_val,
            company_name,
            round_type,
            interview_date,
            interview_time,
            interview_mode,
            meeting_link,
            status,
            notes,
        ),
    )
    db.commit()
    flash(f"Interview with {company_name} scheduled successfully!", "success")
    return redirect(url_for("interviews"))


@app.route("/interviews/edit/<int:interview_id>", methods=["POST"])
@login_required
def edit_interview(interview_id):
    """Edit interview details and status."""
    user_id = session["user_id"]
    db = get_db()

    interview_record = db.execute(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, user_id),
    ).fetchone()

    if not interview_record:
        flash("Interview record not found.", "danger")
        return redirect(url_for("interviews"))

    company_name = request.form.get("company_name", "").strip()
    round_type = request.form.get("round_type", "").strip()
    interview_date = request.form.get("interview_date", "").strip()
    interview_time = request.form.get("interview_time", "").strip()
    interview_mode = request.form.get("interview_mode", "Virtual")
    meeting_link = request.form.get("meeting_link", "").strip()
    status = request.form.get("status", "Scheduled")
    notes = request.form.get("notes", "").strip()

    if not company_name or not round_type or not interview_date:
        flash("Company name, round type, and date are required.", "danger")
        return redirect(url_for("interviews"))

    db.execute(
        """
        UPDATE interviews
        SET company_name = ?, round_type = ?, interview_date = ?, interview_time = ?,
            interview_mode = ?, meeting_link = ?, status = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            company_name,
            round_type,
            interview_date,
            interview_time,
            interview_mode,
            meeting_link,
            status,
            notes,
            interview_id,
            user_id,
        ),
    )
    db.commit()
    flash(f"Interview with {company_name} updated successfully!", "success")
    return redirect(url_for("interviews"))


@app.route("/interviews/delete/<int:interview_id>", methods=["POST"])
@login_required
def delete_interview(interview_id):
    """Delete an interview entry."""
    user_id = session["user_id"]
    db = get_db()
    db.execute(
        "DELETE FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, user_id),
    )
    db.commit()
    flash("Interview removed successfully.", "info")
    return redirect(url_for("interviews"))


# -------------------------------------------------------------
# Placement Preparation Module
# -------------------------------------------------------------


@app.route("/preparation")
@login_required
def preparation():
    """Manage preparation topics and track progress."""
    user_id = session["user_id"]
    category_filter = request.args.get("category", "").strip()

    db = get_db()
    query = "SELECT * FROM preparation_topics WHERE user_id = ?"
    params = [user_id]

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    query += " ORDER BY category ASC, id ASC"
    topics = db.execute(query, params).fetchall()

    # Get distinct categories
    categories = [
        row["category"]
        for row in db.execute(
            "SELECT DISTINCT category FROM preparation_topics WHERE user_id = ? ORDER BY category",
            (user_id,),
        ).fetchall()
    ]

    # Pre-calculate counts
    total = len(topics)
    completed = sum(1 for t in topics if t["status"] == "Completed")
    in_progress = sum(1 for t in topics if t["status"] == "In Progress")

    return render_template(
        "preparation.html",
        topics=topics,
        categories=categories,
        current_category=category_filter,
        total=total,
        completed=completed,
        in_progress=in_progress,
    )


@app.route("/preparation/add", methods=["POST"])
@login_required
def add_preparation_topic():
    """Add a new placement preparation topic."""
    user_id = session["user_id"]
    category = request.form.get("category", "Data Structures & Algorithms").strip()
    title = request.form.get("title", "").strip()
    difficulty = request.form.get("difficulty", "Medium")
    status = request.form.get("status", "Not Started")
    resource_url = request.form.get("resource_url", "").strip()
    notes = request.form.get("notes", "").strip()

    if not title:
        flash("Topic title is required.", "danger")
        return redirect(url_for("preparation"))

    db = get_db()
    db.execute(
        """
        INSERT INTO preparation_topics (user_id, category, title, difficulty, status, resource_url, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, category, title, difficulty, status, resource_url, notes),
    )
    db.commit()
    flash(f"Topic '{title}' added to preparation roadmap!", "success")
    return redirect(url_for("preparation"))


@app.route("/preparation/toggle/<int:topic_id>", methods=["POST"])
@login_required
def toggle_preparation_status(topic_id):
    """Quickly toggle topic status between Completed and Not Started."""
    user_id = session["user_id"]
    db = get_db()
    topic = db.execute(
        "SELECT * FROM preparation_topics WHERE id = ? AND user_id = ?",
        (topic_id, user_id),
    ).fetchone()

    if topic:
        new_status = "Not Started" if topic["status"] == "Completed" else "Completed"
        db.execute(
            "UPDATE preparation_topics SET status = ? WHERE id = ? AND user_id = ?",
            (new_status, topic_id, user_id),
        )
        db.commit()
        flash(f"Updated status of '{topic['title']}' to {new_status}.", "success")

    return redirect(url_for("preparation"))


@app.route("/preparation/delete/<int:topic_id>", methods=["POST"])
@login_required
def delete_preparation_topic(topic_id):
    """Delete a preparation topic."""
    user_id = session["user_id"]
    db = get_db()
    db.execute(
        "DELETE FROM preparation_topics WHERE id = ? AND user_id = ?",
        (topic_id, user_id),
    )
    db.commit()
    flash("Preparation topic removed.", "info")
    return redirect(url_for("preparation"))


# -------------------------------------------------------------
# REST API & Health Check (for DevOps verification / monitoring)
# -------------------------------------------------------------


@app.route("/health")
def health():
    """Health check endpoint for Docker, Jenkins, and AWS load balancers."""
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
        return (
            jsonify(
                {
                    "status": "healthy",
                    "app": "PlacementPro",
                    "version": "1.0.0",
                    "database": "connected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/api/stats")
@login_required
def api_stats():
    """API endpoint to get real-time placement statistics."""
    user_id = session["user_id"]
    db = get_db()

    app_count = db.execute(
        "SELECT COUNT(*) as c FROM applications WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    interview_count = db.execute(
        "SELECT COUNT(*) as c FROM interviews WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    offer_count = db.execute(
        "SELECT COUNT(*) as c FROM applications WHERE user_id = ? AND LOWER(status) = 'offered'",
        (user_id,),
    ).fetchone()["c"]

    total_prep = db.execute(
        "SELECT COUNT(*) as c FROM preparation_topics WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    completed_prep = db.execute(
        "SELECT COUNT(*) as c FROM preparation_topics WHERE user_id = ? AND status = 'Completed'",
        (user_id,),
    ).fetchone()["c"]

    return jsonify(
        {
            "applications": app_count,
            "interviews": interview_count,
            "offers": offer_count,
            "total_prep": total_prep,
            "completed_prep": completed_prep,
            "prep_percentage": round((completed_prep / total_prep) * 100)
            if total_prep > 0
            else 0,
        }
    )


# Ensure DB tables are initialized on start
with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
