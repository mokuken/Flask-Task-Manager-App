"""Initialize Flask application and database."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    """Application factory pattern for Flask app."""
    app = Flask(__name__)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init DB
    db.init_app(app)

    # Import models
    from app import models  # noqa: F401

    # Register routes
    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
