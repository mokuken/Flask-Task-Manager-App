"""Routes and views for Task Manager."""

from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from app import db
from app.models import Task

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Homepage: display all tasks."""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("index.html",
                           tasks=tasks,
                           now=datetime.utcnow(),
                           search_query=None)


@main.route("/add", methods=["POST"])
def add():
    """Add a new task."""
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
        )
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for("main.index"))


@main.route("/toggle/<int:task_id>")
def toggle(task_id):
    """Toggle a task's completion status."""
    task = Task.query.get_or_404(task_id)
    task.complete = not task.complete
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route("/delete/<int:task_id>")
def delete(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route("/search")
def search():
    """Search tasks by title or description."""
    query = request.args.get("q", "")
    if query:
        tasks = Task.query.filter(
            (Task.title.contains(query)) | (Task.description.contains(query))
        ).order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.order_by(Task.created_at.desc()).all()

    return render_template("index.html",
                           tasks=tasks,
                           now=datetime.utcnow(),
                           search_query=query)


@main.route("/filter/<string:status>")
def filter_tasks(status):
    """Filter tasks by status (done/pending/all)."""
    if status == "done":
        tasks = Task.query.filter_by(complete=True).all()
    elif status == "pending":
        tasks = Task.query.filter_by(complete=False).all()
    else:
        tasks = Task.query.all()

    return render_template("index.html",
                           tasks=tasks,
                           now=datetime.utcnow(),
                           search_query=None)
