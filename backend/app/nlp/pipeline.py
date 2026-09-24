"""
Main NLP pipeline orchestrator.

Coordinates all NLP components in the correct order:
1. Clean text (with case preserved for entity extraction)
2. Extract entities (spaCy / regex fallback)
3. Analyze sentiment (VADER)
4. Classify category (ML model)
5. Detect intent (rule-based patterns)

Returns a structured NLPResult dataclass.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

from app.nlp.entity_extractor import ExtractedEntity, extract_entities, get_deadline_text
from app.nlp.intent_detector import detect_intent
from app.nlp.preprocessor import clean_for_entity_extraction, extract_clean_for_classification
from app.nlp.sentiment_analyzer import SentimentResult, analyze_sentiment

logger = logging.getLogger(__name__)


@dataclass
class NLPResult:
    # Classification
    category: str = "Other"
    category_slug: str = "other"
    category_confidence: float = 0.0

    # Intent
    intent: str = "General Information"

    # Sentiment
    sentiment: str = "neutral"
    sentiment_score: float = 0.0

    # Entities
    entities: list[ExtractedEntity] = field(default_factory=list)
    deadline_text: Optional[str] = None

    # Cleaned text (for downstream use)
    clean_text: str = ""


class NLPPipeline:
    """
    Orchestrates the full NLP processing pipeline.
    Components are loosely coupled — each can be replaced independently.
    """

    def __init__(self):
        self._classifier = None

    def _get_classifier(self):
        """Lazy-load the ML classifier to avoid startup cost."""
        if self._classifier is None:
            from app.ml.classifier import EmailClassifier
            self._classifier = EmailClassifier()
        return self._classifier

    def process(self, subject: str, body: str) -> NLPResult:
        """
        Run the full pipeline synchronously.
        (FastAPI runs this in a thread pool via asyncio.to_thread)
        """
        result = NLPResult()

        # ── Step 1: Prepare text variants ────────────────────────────────
        # Keep original case for entity extraction
        entity_text = clean_for_entity_extraction(f"{subject or ''}\n\n{body or ''}")
        # Lowercase + cleaned for classification
        classification_text = extract_clean_for_classification(subject or "", body or "")
        result.clean_text = classification_text

        # ── Step 2: Entity extraction ─────────────────────────────────────
        # Uses original-case text so spaCy NER works correctly
        result.entities = extract_entities(entity_text)
        result.deadline_text = get_deadline_text(result.entities)

        # ── Step 3: Sentiment analysis ────────────────────────────────────
        sentiment: SentimentResult = analyze_sentiment(body or "")
        result.sentiment = sentiment.label
        result.sentiment_score = sentiment.score

        # ── Step 4: ML Classification ─────────────────────────────────────
        classifier = self._get_classifier()
        cat_result = classifier.predict(classification_text)
        result.category = cat_result["category"]
        result.category_slug = cat_result["slug"]
        result.category_confidence = cat_result["confidence"]

        # ── Step 5: Intent detection ──────────────────────────────────────
        result.intent = detect_intent(subject or "", body or "", result.category_slug)

        logger.debug(
            "NLP pipeline complete: category=%s (%.0f%%), intent=%s, sentiment=%s",
            result.category,
            result.category_confidence * 100,
            result.intent,
            result.sentiment,
        )
        return result


# Singleton pipeline instance
_pipeline: Optional[NLPPipeline] = None


def get_pipeline() -> NLPPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = NLPPipeline()
    return _pipeline
