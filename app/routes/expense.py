"""
Expense management routes.
"""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.ml_models.categorization import predict_category
from app.ml_models.risk_prediction import predict_risk
from app.models.expense import Expense
from app.services.auth import current_user_id, login_required


expense_bp = Blueprint("expense", __name__)

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Housing",
    "Utilities",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


@expense_bp.route("/expenses", methods=["GET"])
@login_required
def list_expenses():
    """Show all expenses of the logged-in user."""
    user_id = current_user_id()
    expenses = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .all()
    )

    risk_by_expense = {}
    for expense in expenses:
        risk_by_expense[expense.id] = predict_risk(
            user_id=user_id,
            amount=float(expense.amount),
            category=expense.category,
        )

    return render_template("expenses.html", expenses=expenses, risk_by_expense=risk_by_expense)


@expense_bp.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():
    """Create a new expense for the logged-in user."""
    if request.method == "POST":
        amount_raw = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        date_raw = request.form.get("date", "").strip()

        if not amount_raw or not date_raw:
            flash("Amount and date are required.", "danger")
            return render_template("add_expense.html", categories=EXPENSE_CATEGORIES)

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return render_template("add_expense.html", categories=EXPENSE_CATEGORIES)

        # If category is not selected, use ML prediction from description.
        if not category:
            if not description:
                flash("Add a description when category is left blank for auto-categorization.", "danger")
                return render_template("add_expense.html", categories=EXPENSE_CATEGORIES)
            category = predict_category(description)

            # Safety fallback in case model predicts an unexpected label.
            if category not in EXPENSE_CATEGORIES:
                category = "Other"

        if category not in EXPENSE_CATEGORIES:
            flash("Please choose a valid category.", "danger")
            return render_template("add_expense.html", categories=EXPENSE_CATEGORIES)

        try:
            expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Please enter a valid date.", "danger")
            return render_template("add_expense.html", categories=EXPENSE_CATEGORIES)

        expense = Expense(
            user_id=current_user_id(),
            amount=amount,
            description=description or None,
            category=category,
            date=expense_date,
        )
        risk_level = predict_risk(user_id=current_user_id(), amount=amount, category=category)
        db.session.add(expense)
        db.session.commit()

        flash(f"Expense added successfully. Risk level: {risk_level}", "success")
        return redirect(url_for("expense.list_expenses"))

    return render_template("add_expense.html", categories=EXPENSE_CATEGORIES)


@expense_bp.route("/edit_expense/<int:id>", methods=["GET", "POST"])
@login_required
def edit_expense(id: int):
    """Update an existing expense owned by the logged-in user."""
    expense = Expense.query.filter_by(id=id, user_id=current_user_id()).first()
    if not expense:
        flash("Expense not found.", "danger")
        return redirect(url_for("expense.list_expenses"))

    if request.method == "POST":
        amount_raw = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        date_raw = request.form.get("date", "").strip()

        if not amount_raw or not category or not date_raw:
            flash("Amount, category, and date are required.", "danger")
            return render_template(
                "edit_expense.html",
                expense=expense,
                categories=EXPENSE_CATEGORIES,
            )

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return render_template(
                "edit_expense.html",
                expense=expense,
                categories=EXPENSE_CATEGORIES,
            )

        if category not in EXPENSE_CATEGORIES:
            flash("Please choose a valid category.", "danger")
            return render_template(
                "edit_expense.html",
                expense=expense,
                categories=EXPENSE_CATEGORIES,
            )

        try:
            expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Please enter a valid date.", "danger")
            return render_template(
                "edit_expense.html",
                expense=expense,
                categories=EXPENSE_CATEGORIES,
            )

        expense.amount = amount
        expense.description = description or None
        expense.category = category
        expense.date = expense_date
        db.session.commit()

        flash("Expense updated successfully.", "success")
        return redirect(url_for("expense.list_expenses"))

    return render_template("edit_expense.html", expense=expense, categories=EXPENSE_CATEGORIES)


@expense_bp.route("/delete_expense/<int:id>", methods=["POST"])
@login_required
def delete_expense(id: int):
    """Delete an existing expense owned by the logged-in user."""
    expense = Expense.query.filter_by(id=id, user_id=current_user_id()).first()
    if not expense:
        flash("Expense not found.", "danger")
        return redirect(url_for("expense.list_expenses"))

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully.", "success")
    return redirect(url_for("expense.list_expenses"))
