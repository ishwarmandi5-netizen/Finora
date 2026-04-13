"""
Simple budgeting recommendation model using Decision Tree Regression.
"""

from sklearn.tree import DecisionTreeRegressor
from sqlalchemy import func

from app import db
from app.models.expense import Expense


def suggest_budget(user_id: int) -> dict:
    """
    Suggest per-category budgets from a user's past spending behavior.

    Features per category:
    - total_spent
    - number_of_transactions

    Output:
    - suggested budget (slightly above historical spending)
    """
    category_rows = (
        db.session.query(
            Expense.category,
            func.sum(Expense.amount).label("total_spent"),
            func.count(Expense.id).label("transaction_count"),
        )
        .filter(Expense.user_id == user_id)
        .group_by(Expense.category)
        .order_by(Expense.category.asc())
        .all()
    )

    if not category_rows:
        return {}

    feature_rows = []
    target_values = []
    categories = []

    for row in category_rows:
        total_spent = float(row.total_spent or 0.0)
        transaction_count = int(row.transaction_count or 0)

        feature_rows.append([total_spent, transaction_count])
        # Target is slightly higher than historical spending.
        target_values.append(total_spent * 1.10)
        categories.append(row.category)

    # With very little data, a direct heuristic is more stable than ML fitting.
    if len(feature_rows) < 2:
        return {categories[i]: round(target_values[i], 2) for i in range(len(categories))}

    model = DecisionTreeRegressor(max_depth=3, random_state=42)
    model.fit(feature_rows, target_values)
    predictions = model.predict(feature_rows)

    suggested = {}
    for index, category in enumerate(categories):
        suggested[category] = round(max(0.0, float(predictions[index])), 2)

    return suggested
