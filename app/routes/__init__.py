"""
Routing package for application endpoints.
"""

from app.routes.auth import auth_bp
from app.routes.expense import expense_bp

__all__ = ["auth_bp", "expense_bp"]
