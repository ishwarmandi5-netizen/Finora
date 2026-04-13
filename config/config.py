"""
Environment-based configuration settings.

Use environment variables for sensitive values in real deployments.
"""

import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace-this-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"


class DevelopmentConfig(BaseConfig):
    """Settings for local development."""

    DEBUG = True


class ProductionConfig(BaseConfig):
    """Settings for production deployment."""

    DEBUG = False
