"""
Group-related model definitions.
"""

from datetime import date, datetime

from app import db


class Group(db.Model):
    """Represents a shared expense group."""

    __tablename__ = "groups"

    # Primary key for the group record
    id = db.Column(db.Integer, primary_key=True)
    # Display name of the group
    name = db.Column(db.String(120), nullable=False)
    # User who created the group (references users.id)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # Timestamp for when the group was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Link to the user who created this group
    creator = db.relationship("User", back_populates="created_groups", foreign_keys=[created_by])

    # Association rows connecting this group to users
    memberships = db.relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # Many-to-many convenience relation: group <-> users
    members = db.relationship(
        "User",
        secondary="group_members",
        back_populates="groups",
        viewonly=True,
        lazy=True,
    )

    # Shared expenses inside this group
    group_expenses = db.relationship(
        "GroupExpense",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self) -> str:
        return f"<Group id={self.id} name={self.name}>"


class GroupMember(db.Model):
    """Association model for group membership (user <-> group)."""

    __tablename__ = "group_members"

    # Primary key for membership row
    id = db.Column(db.Integer, primary_key=True)
    # Group id for this membership (references groups.id)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False, index=True)
    # User id for this membership (references users.id)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Ensure one user cannot be added to the same group multiple times
    __table_args__ = (db.UniqueConstraint("group_id", "user_id", name="uq_group_member"),)

    # Link to the related group
    group = db.relationship("Group", back_populates="memberships")
    # Link to the related user
    user = db.relationship("User", back_populates="group_memberships")

    def __repr__(self) -> str:
        return f"<GroupMember group_id={self.group_id} user_id={self.user_id}>"


class GroupExpense(db.Model):
    """Expense entry recorded inside a group."""

    __tablename__ = "group_expenses"

    # Primary key for the group expense row
    id = db.Column(db.Integer, primary_key=True)
    # Group where this expense belongs (references groups.id)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False, index=True)
    # User who paid this expense (references users.id)
    paid_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # Total amount paid for this group expense
    amount = db.Column(db.Float, nullable=False)
    # Optional note describing the expense
    description = db.Column(db.String(255))
    # Date when the group expense occurred
    date = db.Column(db.Date, default=date.today, nullable=False)

    # Relationship to the parent group
    group = db.relationship("Group", back_populates="group_expenses")
    # Relationship to the user who paid
    payer = db.relationship("User", back_populates="group_expenses_paid", foreign_keys=[paid_by])

    def __repr__(self) -> str:
        return f"<GroupExpense id={self.id} group_id={self.group_id} amount={self.amount}>"
