"""
Train the TF-IDF + Linear SVC email classifier.

Usage: python -m scripts.train_classifier  (from backend/ directory)

Output: app/ml/models/email_classifier.pkl

The training data is loaded from data/training_data.json.
Reports accuracy, per-class precision/recall/F1, and confusion matrix.
"""
import json
import logging
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent / "data" / "training_data.json"
MODEL_PATH = Path(__file__).parent.parent / "app" / "ml" / "models" / "email_classifier.pkl"


def load_data():
    with open(DATA_PATH) as f:
        data = json.load(f)
    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]
    return texts, labels


def build_pipeline():
    """
    Pipeline: TfidfVectorizer → LinearSVC (wrapped in CalibratedClassifierCV
    to get probability estimates for confidence scores).

    TF-IDF config:
    - ngram_range=(1,2): unigrams + bigrams capture phrase patterns
    - max_features=15000: limits vocabulary for speed
    - sublinear_tf=True: reduces impact of very frequent terms
    - min_df=1: include all terms (small dataset)
    """
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        sublinear_tf=True,
        min_df=1,
        strip_accents="unicode",
        analyzer="word",
    )
    # CalibratedClassifierCV wraps LinearSVC to give probability output
    svc = CalibratedClassifierCV(LinearSVC(max_iter=2000, C=1.0))
    return Pipeline([("tfidf", tfidf), ("clf", svc)])


def train():
    logger.info("Loading training data from %s", DATA_PATH)
    texts, labels = load_data()
    logger.info("Loaded %d labeled samples across %d categories", len(texts), len(set(labels)))

    le = LabelEncoder()
    y = le.fit_transform(labels)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info("Training on %d samples, testing on %d samples", len(X_train), len(X_test))

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    # Evaluation
    y_pred = pipeline.predict(X_test)
    acc = (y_pred == y_test).mean()
    logger.info("Test accuracy: %.1f%%", acc * 100)

    target_names = list(le.classes_)
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=target_names))

    # Cross-validation
    logger.info("Running 5-fold cross-validation...")
    cv_scores = cross_val_score(build_pipeline(), texts, y, cv=5, scoring="accuracy")
    logger.info("CV Accuracy: %.1f%% ± %.1f%%", cv_scores.mean() * 100, cv_scores.std() * 100)

    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"pipeline": pipeline, "label_encoder": le}, f)
    logger.info("Model saved to %s", MODEL_PATH)

    return pipeline, le


if __name__ == "__main__":
    train()
