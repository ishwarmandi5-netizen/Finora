"""
Spending risk prediction model.

Predicts whether a new expense is Safe, Risky, or High Risk for a user.
"""

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sqlalchemy import func

from app import db
from app.models.expense import Expense


def _rule_label(amount: float, average_spending: float) -> str:
    """Create a simple training label from amount vs average spending."""
    if average_spending <= 0:
        return "Safe"

    if amount < average_spending:
        return "Safe"
    if amount <= average_spending * 1.5:
        return "Risky"
    return "High Risk"


def predict_risk(user_id: int, amount: float, category: str) -> str:
    """
    Predict risk level for a candidate expense.

    Features:
    - amount
    - category (encoded by DictVectorizer)
    - user's average spending
    - frequency of spending in the selected category
    """
    user_expenses = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.date.asc(), Expense.id.asc())
        .all()
    )

    # Fast fallback when there is not enough data for model training.
    if len(user_expenses) < 3:
        if amount < 500:
            return "Safe"
        if amount <= 2000:
            return "Risky"
        return "High Risk"

    overall_average = sum(exp.amount for exp in user_expenses) / len(user_expenses)

    category_count_map = dict(
        db.session.query(Expense.category, func.count(Expense.id))
        .filter(Expense.user_id == user_id)
        .group_by(Expense.category)
        .all()
    )

    training_rows = []
    training_labels = []
    for exp in user_expenses:
        row = {
            "amount": float(exp.amount),
            "category": exp.category,
            "avg_spending": float(overall_average),
            "frequency": float(category_count_map.get(exp.category, 0)),
        }
        training_rows.append(row)
        training_labels.append(_rule_label(float(exp.amount), float(overall_average)))

    # If all labels collapse into one class, return deterministic rule label.
    unique_labels = set(training_labels)
    if len(unique_labels) < 2:
        return _rule_label(amount, overall_average)

    model = Pipeline(
        steps=[
            ("vectorizer", DictVectorizer(sparse=False)),
            ("classifier", LogisticRegression(max_iter=500, random_state=42)),
        ]
    )
    model.fit(training_rows, training_labels)

    prediction_row = {
        "amount": float(amount),
        "category": category,
        "avg_spending": float(overall_average),
        "frequency": float(category_count_map.get(category, 0)),
    }
    predicted_label = model.predict([prediction_row])[0]
    return str(predicted_label)
