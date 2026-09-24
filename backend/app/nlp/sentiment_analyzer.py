"""
Sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner).

Why VADER: Designed specifically for social/professional text.
Works well without training data. Fast, rule-based, explainable.
Gives compound score from -1.0 (very negative) to +1.0 (very positive).
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            _analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            logger.warning("vaderSentiment not installed. Sentiment will be neutral.")
    return _analyzer


@dataclass
class SentimentResult:
    label: str   # positive / neutral / negative
    score: float  # compound: -1.0 to 1.0


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Analyze sentiment of email text.
    Returns a label and compound score.
    """
    if not text:
        return SentimentResult("neutral", 0.0)

    analyzer = _get_analyzer()
    if analyzer is None:
        return SentimentResult("neutral", 0.0)

    scores = analyzer.polarity_scores(text[:5000])  # Limit for performance
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return SentimentResult(label=label, score=round(compound, 4))
