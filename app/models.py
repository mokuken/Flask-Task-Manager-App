"""Database models for Task Manager."""

from datetime import datetime
from app import db


class Task(db.Model):
    """Represents a single task in the system."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default="Normal")

    def __repr__(self):
        return f"<Task {self.id}: {self.title}>"
