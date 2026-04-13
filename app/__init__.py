"""
Application factory and shared extension instances.

This module wires up Flask, SQLAlchemy, and Flask-Migrate in a clean,
scalable way for production-style projects.
"""

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# Shared extension objects (initialized later inside create_app)
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object: str = "config.config.DevelopmentConfig") -> Flask:
    """
    Flask application factory.

    Args:
        config_object: Python path to the config class.
    """
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect schema changes.
    from app import models  # noqa: F401

    # Import and register blueprints here to avoid circular imports.
    from app.routes import auth_bp, expense_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expense_bp)

    return app
