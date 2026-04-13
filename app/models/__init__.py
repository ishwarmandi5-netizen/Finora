"""
Database models package.

All models are imported here so SQLAlchemy metadata is fully loaded when
Flask-Migrate runs migration commands.
"""

from app.models.expense import Expense
from app.models.group import Group, GroupExpense, GroupMember
from app.models.user import User

__all__ = ["User", "Expense", "Group", "GroupMember", "GroupExpense"]
