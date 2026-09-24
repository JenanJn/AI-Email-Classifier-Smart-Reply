"""
Named Entity Recognition using spaCy.

Why spaCy: Production-grade NER with support for PERSON, ORG, DATE,
TIME, MONEY, GPE (locations), and EVENT entities out of the box.
The en_core_web_sm model is fast and sufficient for email text.
"""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-load spaCy to avoid import-time errors if model isn't installed
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model en_core_web_sm loaded.")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            _nlp = None
        except Exception as exc:
            logger.warning(
                "spaCy could not be loaded (%s). Using regex entity extraction fallback.",
                exc,
            )
            _nlp = None
    return _nlp


@dataclass
class ExtractedEntity:
    entity_type: str
    entity_text: str
    confidence: float
    char_position: int


# Entity types we care about in emails
RELEVANT_TYPES = {"PERSON", "ORG", "DATE", "TIME", "MONEY", "GPE", "EVENT", "CARDINAL", "ORDINAL"}


def extract_entities(text: str) -> list[ExtractedEntity]:
    """
    Extract named entities from email text.
    Returns a deduplicated list of relevant entities.
    """
    if not text:
        return []

    nlp = _get_nlp()
    if nlp is None:
        # Fallback: use regex for basic date/time patterns
        return _regex_entity_fallback(text)

    doc = nlp(text[:10000])  # Limit to 10K chars for performance
    seen = set()
    entities = []

    for ent in doc.ents:
        if ent.label_ not in RELEVANT_TYPES:
            continue
        key = (ent.label_, ent.text.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        entities.append(
            ExtractedEntity(
                entity_type=ent.label_,
                entity_text=ent.text.strip(),
                confidence=0.85,  # spaCy doesn't expose per-entity confidence
                char_position=ent.start_char,
            )
        )

    return entities


def _regex_entity_fallback(text: str) -> list[ExtractedEntity]:
    """Basic regex-based entity extraction when spaCy is unavailable."""
    import re
    entities = []

    date_patterns = [
        r"\b(today|tomorrow|yesterday)\b",
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?,? \d{4}\b",
    ]
    time_patterns = [r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b", r"\b\d{1,2}\s*(?:am|pm)\b"]
    money_patterns = [r"\$[\d,]+(?:\.\d{2})?", r"₹[\d,]+(?:\.\d{2})?", r"£[\d,]+(?:\.\d{2})?"]

    for pattern in date_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            entities.append(ExtractedEntity("DATE", m.group(), 0.7, m.start()))

    for pattern in time_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            entities.append(ExtractedEntity("TIME", m.group(), 0.7, m.start()))

    for pattern in money_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            entities.append(ExtractedEntity("MONEY", m.group(), 0.8, m.start()))

    return entities


def get_deadline_text(entities: list[ExtractedEntity]) -> Optional[str]:
    """
    Extract the most likely deadline from detected entities.
    Prefer TIME entities co-located with DATE entities.
    """
    dates = [e for e in entities if e.entity_type == "DATE"]
    times = [e for e in entities if e.entity_type == "TIME"]

    if dates and times:
        return f"{dates[0].entity_text} at {times[0].entity_text}"
    if dates:
        return dates[0].entity_text
    if times:
        return times[0].entity_text
    return None
