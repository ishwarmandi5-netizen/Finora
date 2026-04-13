"""
Authentication routes.
"""

from datetime import date, timedelta

from sqlalchemy import func
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.ml_models.budgeting import suggest_budget
from app.ml_models.forecasting import predict_future_expense
from app.models.expense import Expense
from app.models.user import User
from app.services.auth import current_user_id, hash_password, login_required, login_user, logout_user, verify_password


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if current_user_id():
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log in an existing user."""
    if current_user_id():
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password_hash):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        login_user(user)
        flash("Welcome back!", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Protected dashboard with monthly insights."""
    user_id = current_user_id()
    user = db.session.get(User, user_id)

    # Build month date range: [first_day_of_month, first_day_of_next_month)
    today = date.today()
    month_start = today.replace(day=1)
    next_month_start = (month_start + timedelta(days=32)).replace(day=1)

    # Total expense for current month
    total_monthly_expense = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= month_start,
            Expense.date < next_month_start,
        )
        .scalar()
    )

    # Category-wise totals for current month (for pie chart)
    category_rows = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= month_start,
            Expense.date < next_month_start,
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    pie_labels = [row[0] for row in category_rows]
    pie_values = [float(row[1]) for row in category_rows]

    # Daily spending trend for current month (for line chart)
    trend_rows = (
        db.session.query(Expense.date, func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= month_start,
            Expense.date < next_month_start,
        )
        .group_by(Expense.date)
        .order_by(Expense.date.asc())
        .all()
    )
    trend_map = {row[0]: float(row[1]) for row in trend_rows}

    trend_labels = []
    trend_values = []
    cursor = month_start
    while cursor <= today:
        trend_labels.append(cursor.strftime("%d %b"))
        trend_values.append(trend_map.get(cursor, 0.0))
        cursor += timedelta(days=1)

    predicted_next_expense = predict_future_expense(user_id)
    budget_suggestions = suggest_budget(user_id)

    return render_template(
        "dashboard.html",
        user=user,
        total_monthly_expense=float(total_monthly_expense or 0.0),
        predicted_next_expense=float(predicted_next_expense),
        budget_suggestions=budget_suggestions,
        current_month_name=today.strftime("%B %Y"),
        pie_labels=pie_labels,
        pie_values=pie_values,
        trend_labels=trend_labels,
        trend_values=trend_values,
    )
