"""
Simple expense forecasting model using Linear Regression.
"""

from sklearn.linear_model import LinearRegression

from app import db
from app.models.expense import Expense


def predict_future_expense(user_id: int) -> float:
    """
    Predict a user's next expense amount using historical expense data.

    Approach:
    - Aggregate expense amounts by date
    - Convert date to numeric day index
    - Train Linear Regression and predict next day value

    Fallbacks:
    - No data: return 0.0
    - One data point: return that amount
    """
    daily_rows = (
        db.session.query(Expense.date, db.func.sum(Expense.amount))
        .filter(Expense.user_id == user_id)
        .group_by(Expense.date)
        .order_by(Expense.date.asc())
        .all()
    )

    if not daily_rows:
        return 0.0

    if len(daily_rows) == 1:
        return float(daily_rows[0][1])

    first_date = daily_rows[0][0]
    x_train = [[(row[0] - first_date).days] for row in daily_rows]
    y_train = [float(row[1]) for row in daily_rows]

    model = LinearRegression()
    model.fit(x_train, y_train)

    next_day_index = x_train[-1][0] + 1
    prediction = model.predict([[next_day_index]])[0]

    # Spending cannot be negative in this context.
    return float(max(0.0, prediction))
