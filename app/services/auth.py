"""
Authentication helper utilities.
"""

from functools import wraps

import bcrypt
from flask import flash, redirect, session, url_for

from app.models.user import User


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Compare a plain password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def login_user(user: User) -> None:
    """Create a user session."""
    session["user_id"] = user.id


def logout_user() -> None:
    """Clear active user session."""
    session.pop("user_id", None)


def current_user_id() -> int | None:
    """Return currently logged-in user id, if available."""
    return session.get("user_id")


def login_required(view_func):
    """Protect routes that require authentication."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user_id():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped_view
