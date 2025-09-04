"""Routes and views for Task Manager."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from app import db
from app.models import Task, User

main = Blueprint("main", __name__)

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


@main.route("/")
def index():
    """Homepage: display user's tasks."""
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()
    return render_template("index.html",
                           tasks=tasks,
                           now=datetime.utcnow(),
                           search_query=None,
                           user=user)


@main.route("/add", methods=["POST"])
def add():
    """Add a new task."""
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    title = request.form.get("title")
    description = request.form.get("description")
    deadline = request.form.get("deadline")
    priority = request.form.get("priority")

    if title:
        new_task = Task(
            title=title,
            description=description,
            deadline=datetime.strptime(deadline, "%Y-%m-%dT%H:%M") if deadline else None,
            priority=priority,
            user_id=user.id
        )
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for("main.index"))


@main.route("/toggle/<int:task_id>")
def toggle(task_id):
    """Toggle a task's completion status."""
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.index"))
    task.complete = not task.complete
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route("/delete/<int:task_id>")
def delete(task_id):
    """Delete a task."""
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.index"))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route("/search")
def search():
    """Search tasks by title or description."""
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    query = request.args.get("q", "")
    if query:
        tasks = Task.query.filter(
            ((Task.title.contains(query)) | (Task.description.contains(query))) & (Task.user_id == user.id)
        ).order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()

    return render_template("index.html",
                           tasks=tasks,
                           now=datetime.utcnow(),
                           search_query=query,
                           user=user)


@main.route("/filter/<string:status>")
def filter_tasks(status):
    """Filter tasks by status (done/pending/all)."""
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    if status == "done":
        tasks = Task.query.filter_by(complete=True, user_id=user.id).all()
    elif status == "pending":
        tasks = Task.query.filter_by(complete=False, user_id=user.id).all()
    else:
        tasks = Task.query.filter_by(user_id=user.id).all()

    return render_template("index.html",
                           tasks=tasks,
                           now=datetime.utcnow(),
                           search_query=None,
                           user=user)

# User registration
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("main.register"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("main.register"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "info")
        return redirect(url_for("main.login"))
    return render_template("register.html")

# User login
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['theme'] = user.theme or 'light'
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("main.login"))
    return render_template("login.html")

@main.route("/toggle_theme", methods=["POST"])
def toggle_theme():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    # Toggle theme
    user.theme = "dark" if user.theme == "light" else "light"
    db.session.commit()
    session['theme'] = user.theme
    return redirect(request.referrer or url_for("main.index"))

# User logout
@main.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logged out.", "info")
    return redirect(url_for("main.login"))
