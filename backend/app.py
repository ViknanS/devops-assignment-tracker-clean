from datetime import datetime, date
from pathlib import Path
import sqlite3
from flask import Flask, g, redirect, render_template, request, flash, url_for


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
app = Flask(
    __name__,
    template_folder=str(PROJECT_DIR / "frontend" / "templates"),
    static_folder=str(PROJECT_DIR / "frontend" / "static"),
)
app.config["DATABASE"] = str(BASE_DIR / "assignments.db")
app.config["SECRET_KEY"] = "dev-secret-key-change-me"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('High', 'Medium', 'Low')),
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'completed')),
            created_at TEXT NOT NULL
        )
        """
    )
    db.commit()


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def setup():
    init_db()


def assignment_view_model(row):
    today = date.today()
    deadline_dt = datetime.strptime(row["deadline"], "%Y-%m-%d").date()
    days_left = (deadline_dt - today).days
    is_completed = row["status"] == "completed"
    is_overdue = not is_completed and days_left < 0
    return {
        "id": row["id"],
        "title": row["title"],
        "subject": row["subject"],
        "deadline": row["deadline"],
        "priority": row["priority"],
        "status": row["status"],
        "days_left": days_left,
        "is_completed": is_completed,
        "is_overdue": is_overdue,
    }


@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "deadline_asc")

    order_clause = "deadline ASC"
    if sort_by == "deadline_desc":
        order_clause = "deadline DESC"

    db = get_db()
    params = []
    base_query = "SELECT * FROM assignments"
    if search_query:
        base_query += " WHERE title LIKE ? OR subject LIKE ?"
        like_query = f"%{search_query}%"
        params.extend([like_query, like_query])
    base_query += f" ORDER BY {order_clause}, id DESC"

    rows = db.execute(base_query, params).fetchall()
    assignments = [assignment_view_model(row) for row in rows]
    return render_template(
        "index.html",
        assignments=assignments,
        search_query=search_query,
        sort_by=sort_by,
    )


@app.route("/add", methods=["POST"])
def add_assignment():
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()
    priority = request.form.get("priority", "Medium").strip()

    if not title or not subject or not deadline:
        flash("Please fill in title, subject, and deadline.", "error")
        return redirect(url_for("index"))

    if priority not in {"High", "Medium", "Low"}:
        flash("Invalid priority selected.", "error")
        return redirect(url_for("index"))

    try:
        datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        flash("Invalid deadline format.", "error")
        return redirect(url_for("index"))

    db = get_db()
    db.execute(
        """
        INSERT INTO assignments (title, subject, deadline, priority, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
        """,
        (title, subject, deadline, priority, datetime.utcnow().isoformat()),
    )
    db.commit()
    flash("Assignment added successfully!", "success")
    return redirect(url_for("index"))


@app.route("/toggle/<int:assignment_id>", methods=["POST"])
def toggle_status(assignment_id):
    db = get_db()
    assignment = db.execute(
        "SELECT status FROM assignments WHERE id = ?", (assignment_id,)
    ).fetchone()
    if assignment is None:
        flash("Assignment not found.", "error")
        return redirect(url_for("index"))

    new_status = "completed" if assignment["status"] == "pending" else "pending"
    db.execute(
        "UPDATE assignments SET status = ? WHERE id = ?", (new_status, assignment_id)
    )
    db.commit()
    flash("Assignment status updated.", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:assignment_id>", methods=["POST"])
def delete_assignment(assignment_id):
    db = get_db()
    db.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    db.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
