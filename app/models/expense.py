"""
Expense model definition.
"""

from datetime import date, datetime

from app import db


class Expense(db.Model):
    """Personal expense entry for a user."""

    __tablename__ = "expenses"

    # Primary key for the expense record
    id = db.Column(db.Integer, primary_key=True)
    # Owner of this expense (references users.id)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # Money spent in this transaction
    amount = db.Column(db.Float, nullable=False)
    # Expense category, e.g. Food, Rent, Transport
    category = db.Column(db.String(100), nullable=False)
    # Optional free-text note for context
    description = db.Column(db.String(255))
    # Date when the expense happened
    date = db.Column(db.Date, default=date.today, nullable=False)
    # Timestamp for when this record was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Each expense belongs to one user
    user = db.relationship("User", back_populates="expenses")

    def __repr__(self) -> str:
        return f"<Expense id={self.id} user_id={self.user_id} amount={self.amount}>"
