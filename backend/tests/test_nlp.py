"""Tests for the NLP pipeline components."""
import pytest
from app.nlp.preprocessor import clean_email_text, extract_clean_for_classification
from app.nlp.intent_detector import detect_intent
from app.nlp.sentiment_analyzer import analyze_sentiment
from app.priority.engine import compute_priority


class TestPreprocessor:
    def test_removes_html_tags(self):
        text = "<p>Hello <b>World</b></p>"
        result = clean_email_text(text)
        assert "<" not in result
        assert "hello" in result
        assert "world" in result

    def test_lowercases_text(self):
        result = clean_email_text("URGENT MEETING TOMORROW")
        assert result == result.lower()

    def test_handles_empty_string(self):
        assert clean_email_text("") == ""

    def test_removes_html_entities(self):
        result = clean_email_text("Hello &amp; World &lt;test&gt;")
        assert "&amp;" not in result
        assert "hello" in result

    def test_subject_weighted_in_classification(self):
        result = extract_clean_for_classification("interview invitation", "please attend")
        # Subject appears twice
        assert result.count("interview") == 2


class TestIntentDetector:
    def test_interview_invitation(self):
        intent = detect_intent(
            "Interview Invitation",
            "We are pleased to invite you for an interview scheduled for tomorrow at 10 AM."
        )
        assert "Interview" in intent

    def test_order_confirmation(self):
        intent = detect_intent(
            "Your order has been confirmed",
            "Order #12345 confirmed. Estimated delivery in 3 days."
        )
        assert "Order" in intent or "Confirmation" in intent

    def test_security_alert(self):
        intent = detect_intent(
            "Suspicious activity detected",
            "We detected unauthorized access on your account."
        )
        assert "Security" in intent or "Alert" in intent

    def test_fallback_intent(self):
        intent = detect_intent("Hello", "Just checking in.", "other")
        assert isinstance(intent, str)
        assert len(intent) > 0

    def test_job_offer(self):
        intent = detect_intent(
            "Offer Letter",
            "We are pleased to offer you the position. Please review the job offer attached."
        )
        assert "Offer" in intent


class TestSentimentAnalyzer:
    def test_positive_sentiment(self):
        result = analyze_sentiment("Congratulations! We are delighted to offer you this wonderful opportunity.")
        assert result.label == "positive"
        assert result.score > 0

    def test_negative_sentiment(self):
        result = analyze_sentiment("We regret to inform you that your application has been rejected. We are sorry.")
        assert result.label in ("negative", "neutral")

    def test_neutral_sentiment(self):
        result = analyze_sentiment("Your meeting is scheduled for 3 PM on Tuesday.")
        assert result.label == "neutral"

    def test_empty_text(self):
        result = analyze_sentiment("")
        assert result.label == "neutral"
        assert result.score == 0.0


class TestPriorityEngine:
    def test_high_priority_interview(self):
        result = compute_priority(
            subject="Interview Invitation — Tomorrow 10 AM",
            body="Please confirm your availability for the interview scheduled for tomorrow at 10 AM.",
            category_slug="job_career",
            sender_email="hr@company.com",
        )
        # Score breakdown: deadline(22) + action(15) + category(9) + event(10) + sender(5) = 61
        assert result.score >= 55
        assert result.level in ("high", "medium")
        assert result.action_required is True

    def test_low_priority_promotion(self):
        result = compute_priority(
            subject="SALE: 70% off everything",
            body="Shop our amazing sale with great deals and discounts on all products.",
            category_slug="promotions_marketing",
        )
        assert result.level == "low"
        assert result.score < 40

    def test_security_alert_high(self):
        result = compute_priority(
            subject="Suspicious activity on your account",
            body="We detected unauthorized access. Please verify your account immediately.",
            category_slug="finance_banking",
        )
        # Breakdown: urgency(5) + action(15) + category(10) + security(10) = 40
        assert result.score >= 35
        assert result.level in ("high", "medium")

    def test_action_required_flag(self):
        result = compute_priority(
            subject="Please confirm",
            body="Please confirm your attendance by replying to this email.",
            category_slug="work_professional",
        )
        assert result.action_required is True

    def test_explanations_not_empty_for_high_priority(self):
        result = compute_priority(
            subject="URGENT: Deadline today",
            body="This is due by end of day. Please respond urgently.",
            category_slug="work_professional",
        )
        assert len(result.explanations) > 0

    def test_score_bounded(self):
        result = compute_priority(
            subject="URGENT URGENT today asap deadline immediately",
            body="urgent asap immediately today deadline action required confirm please",
            category_slug="finance_banking",
        )
        assert 0 <= result.score <= 100
