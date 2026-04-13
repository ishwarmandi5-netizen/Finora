"""
User model definition.
"""

from datetime import datetime

from app import db


class User(db.Model):
    """Application user account."""

    __tablename__ = "users"

    # Primary key for the user record
    id = db.Column(db.Integer, primary_key=True)
    # Full name of the user
    name = db.Column(db.String(120), nullable=False)
    # Unique email used for login and identification
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    # Securely stored password hash (never plain-text password)
    password_hash = db.Column(db.String(255), nullable=False)
    # Timestamp for when the user account was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # One user can have many personal expenses
    expenses = db.relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # Association rows connecting this user to groups
    group_memberships = db.relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # Many-to-many convenience relation: user <-> groups
    groups = db.relationship(
        "Group",
        secondary="group_members",
        back_populates="members",
        viewonly=True,
        lazy=True,
    )

    # Groups created by this user
    created_groups = db.relationship(
        "Group",
        back_populates="creator",
        foreign_keys="Group.created_by",
        lazy=True,
    )

    # Group expenses paid by this user
    group_expenses_paid = db.relationship(
        "GroupExpense",
        back_populates="payer",
        foreign_keys="GroupExpense.paid_by",
        lazy=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
