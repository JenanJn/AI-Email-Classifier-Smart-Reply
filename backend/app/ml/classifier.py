"""
Email Category Classifier — TF-IDF + Linear SVC.

Why Linear SVC:
- Consistently best accuracy for multi-class text classification with TF-IDF
- Fast at inference (microseconds per email)
- More accurate than Naive Bayes on short-to-medium texts
- Interpretable: feature coefficients show which words drive each class
- Easy to retrain as new labeled data arrives

Architecture:
  sklearn Pipeline: TfidfVectorizer → LinearSVC
  - TF-IDF with bigrams (1,2), max 15k features, sublinear_tf=True
  - Subject weighted 2x by repeating it in the input text (done in preprocessor)

The model is trained by scripts/train_classifier.py and saved as a .pkl file.
On first run without a saved model, falls back to keyword-based rules.
"""
import json
import logging
import os
import pickle
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent / "models" / "email_classifier.pkl"

# ── Category metadata ─────────────────────────────────────────────────────────

CATEGORIES = [
    {"name": "Job / Career",          "slug": "job_career",          "icon": "Briefcase",     "color": "#6366F1"},
    {"name": "Work / Professional",   "slug": "work_professional",   "icon": "Building2",     "color": "#8B5CF6"},
    {"name": "Education",             "slug": "education",           "icon": "GraduationCap", "color": "#3B82F6"},
    {"name": "E-commerce / Shopping", "slug": "ecommerce_shopping",  "icon": "ShoppingBag",   "color": "#F59E0B"},
    {"name": "Finance / Banking",     "slug": "finance_banking",     "icon": "CreditCard",    "color": "#EF4444"},
    {"name": "Travel",                "slug": "travel",              "icon": "Plane",         "color": "#06B6D4"},
    {"name": "Healthcare",            "slug": "healthcare",          "icon": "HeartPulse",    "color": "#EC4899"},
    {"name": "Social / Personal",     "slug": "social_personal",     "icon": "Users",         "color": "#10B981"},
    {"name": "Events / Invitations",  "slug": "events_invitations",  "icon": "CalendarDays",  "color": "#F97316"},
    {"name": "Government / Official", "slug": "government_official", "icon": "Landmark",      "color": "#64748B"},
    {"name": "Promotions / Marketing","slug": "promotions_marketing","icon": "Tag",           "color": "#A855F7"},
    {"name": "Notifications",         "slug": "notifications",       "icon": "Bell",          "color": "#0EA5E9"},
    {"name": "Customer Support",      "slug": "customer_support",    "icon": "Headphones",    "color": "#14B8A6"},
    {"name": "Other",                 "slug": "other",               "icon": "Mail",          "color": "#94A3B8"},
]

SLUG_TO_META = {c["slug"]: c for c in CATEGORIES}
NAME_TO_META = {c["name"]: c for c in CATEGORIES}

# ── Keyword rules fallback (when no trained model exists) ─────────────────────

KEYWORD_RULES: list[tuple[list[str], str]] = [
    (["interview", "job offer", "hiring", "vacancy", "resume", "cv", "application", "career", "recruitment", "position", "candidate"], "Job / Career"),
    (["meeting", "project", "deadline", "team", "colleague", "office", "manager", "sprint", "deliverable", "client", "proposal"], "Work / Professional"),
    (["assignment", "exam", "course", "semester", "professor", "university", "college", "grade", "lecture", "homework", "syllabus"], "Education"),
    (["order", "shipment", "delivery", "product", "amazon", "flipkart", "cart", "purchase", "tracking", "dispatch", "refund"], "E-commerce / Shopping"),
    (["bank", "account", "transaction", "payment", "credit card", "debit", "loan", "emi", "upi", "neft", "suspicious", "fraud"], "Finance / Banking"),
    (["flight", "hotel", "booking", "travel", "itinerary", "boarding", "reservation", "trip", "airline", "check-in"], "Travel"),
    (["appointment", "doctor", "hospital", "prescription", "clinic", "medical", "health", "diagnosis", "test result"], "Healthcare"),
    (["invitation", "wedding", "birthday", "party", "celebrate", "friend", "family", "dinner", "catch up"], "Social / Personal"),
    (["event", "conference", "webinar", "seminar", "workshop", "register", "attend", "venue", "speaker"], "Events / Invitations"),
    (["government", "tax", "official", "authority", "notice", "legal", "compliance", "regulatory", "aadhaar", "pan"], "Government / Official"),
    (["offer", "discount", "sale", "promo", "coupon", "deal", "% off", "limited time", "exclusive", "subscribe"], "Promotions / Marketing"),
    (["notification", "alert", "reminder", "update", "system", "automated", "do not reply"], "Notifications"),
    (["support", "ticket", "complaint", "issue", "help", "resolve", "customer service", "query", "request"], "Customer Support"),
]


class EmailClassifier:
    """
    Email category classifier.
    Loads the trained sklearn Pipeline if available,
    otherwise uses keyword-based fallback rules.
    """

    def __init__(self):
        self._model = None
        self._label_encoder = None
        self._use_ml = False
        self._load_model()

    def _load_model(self) -> None:
        if not MODEL_PATH.exists():
            logger.info(
                "No trained model found at %s. Using keyword-rule fallback. "
                "Run scripts/train_classifier.py to train the ML model.",
                MODEL_PATH,
            )
            return
        try:
            with open(MODEL_PATH, "rb") as f:
                saved = pickle.load(f)
            self._model = saved["pipeline"]
            self._label_encoder = saved["label_encoder"]
            self._use_ml = True
            logger.info("ML classifier loaded from %s", MODEL_PATH)
        except Exception as e:
            logger.error("Failed to load classifier model: %s", e)

    def predict(self, text: str) -> dict:
        """
        Classify the email text.
        Returns: {category, slug, confidence}
        """
        if self._use_ml and self._model is not None:
            return self._predict_ml(text)
        return self._predict_rules(text)

    def _predict_ml(self, text: str) -> dict:
        """Sklearn pipeline prediction with probability scores.
        Uses predict_proba (available because we wrap LinearSVC in CalibratedClassifierCV).
        """
        try:
            probs = self._model.predict_proba([text])[0]
            pred_idx = int(probs.argmax())
            confidence = float(probs[pred_idx])
            predicted_label = self._label_encoder.inverse_transform([pred_idx])[0]
            meta = NAME_TO_META.get(predicted_label, CATEGORIES[-1])
            return {
                "category": meta["name"],
                "slug": meta["slug"],
                "confidence": round(min(confidence * 1.4, 0.99), 2),
            }
        except Exception as e:
            logger.error("ML prediction failed: %s. Falling back to rules.", e)
            return self._predict_rules(text)

    def _predict_rules(self, text: str) -> dict:
        """Keyword frequency-based fallback classifier."""
        text_lower = text.lower()
        scores: dict[str, int] = {}

        for keywords, category in KEYWORD_RULES:
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = scores.get(category, 0) + score

        if not scores:
            meta = NAME_TO_META["Other"]
            return {"category": "Other", "slug": meta["slug"], "confidence": 0.4}

        best_category = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = min(scores[best_category] / max(total_score, 1), 0.95)
        # Normalize confidence to be more realistic
        confidence = 0.5 + (confidence * 0.45)

        meta = NAME_TO_META.get(best_category, CATEGORIES[-1])
        return {
            "category": meta["name"],
            "slug": meta["slug"],
            "confidence": round(confidence, 2),
        }

    @property
    def is_using_ml(self) -> bool:
        return self._use_ml
