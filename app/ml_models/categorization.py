"""
Simple text classification model for expense category prediction.

Model:
- TF-IDF vectorizer for converting text into numeric features
- Logistic Regression classifier for category prediction
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Small in-code training dataset (intentionally simple for explainability)
TRAINING_SAMPLES = [
    # Food
    ("pizza from dominos", "Food"),
    ("burger and fries", "Food"),
    ("restaurant dinner", "Food"),
    ("coffee and snacks", "Food"),
    ("lunch meal", "Food"),
    # Transport
    ("uber ride", "Transport"),
    ("bus ticket", "Transport"),
    ("train pass", "Transport"),
    ("fuel refill", "Transport"),
    ("taxi fare", "Transport"),
    # Bills
    ("electricity bill", "Bills"),
    ("monthly rent payment", "Bills"),
    ("internet recharge", "Bills"),
    ("water bill", "Bills"),
    ("phone bill", "Bills"),
    # Shopping
    ("bought clothes", "Shopping"),
    ("new shoes purchase", "Shopping"),
    ("amazon order", "Shopping"),
    ("grocery shopping", "Shopping"),
    ("shopping mall purchase", "Shopping"),
    # Entertainment
    ("movie tickets", "Entertainment"),
    ("netflix subscription", "Entertainment"),
    ("video games", "Entertainment"),
    ("concert ticket", "Entertainment"),
    ("theme park entry", "Entertainment"),
]


def _train_model() -> Pipeline:
    """Train and return a simple TF-IDF + Logistic Regression pipeline."""
    texts = [row[0] for row in TRAINING_SAMPLES]
    labels = [row[1] for row in TRAINING_SAMPLES]

    model_pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    model_pipeline.fit(texts, labels)
    return model_pipeline


# Train once at import time for quick inference in routes
_CATEGORIZATION_MODEL = _train_model()


def predict_category(description: str) -> str:
    """
    Predict category from expense description.

    Args:
        description: Raw text description entered by user.
    Returns:
        Predicted category label.
    """
    cleaned_description = (description or "").strip()
    if not cleaned_description:
        return "Other"

    prediction = _CATEGORIZATION_MODEL.predict([cleaned_description])[0]
    return str(prediction)
