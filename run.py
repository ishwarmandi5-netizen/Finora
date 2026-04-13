"""
Application entry point for local development.

Usage:
    python run.py
"""

import os

from app import create_app


# Allows switching config classes via environment variable if needed.
# Example:
#   set FINORA_CONFIG=config.config.ProductionConfig
config_path = os.getenv("FINORA_CONFIG", "config.config.DevelopmentConfig")
app = create_app(config_path)


if __name__ == "__main__":
    app.run()
