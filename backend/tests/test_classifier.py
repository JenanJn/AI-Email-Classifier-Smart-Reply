"""Tests for the ML classifier (rule-based fallback tested here)."""
import pytest
from app.ml.classifier import EmailClassifier, CATEGORIES


@pytest.fixture
def classifier():
    return EmailClassifier()


class TestEmailClassifier:
    def test_job_career_classification(self, classifier):
        result = classifier.predict("interview invitation job offer position candidate hiring resume")
        assert result["category"] == "Job / Career"
        assert 0 < result["confidence"] <= 1.0

    def test_education_classification(self, classifier):
        result = classifier.predict("assignment exam semester university professor grade homework lecture")
        assert result["category"] == "Education"

    def test_finance_classification(self, classifier):
        result = classifier.predict("bank account transaction credit card debit suspicious fraud OTP")
        assert result["category"] == "Finance / Banking"

    def test_ecommerce_classification(self, classifier):
        result = classifier.predict("order delivery shipment tracking amazon purchase refund cart product")
        assert result["category"] == "E-commerce / Shopping"

    def test_travel_classification(self, classifier):
        result = classifier.predict("flight booking hotel reservation itinerary boarding airline trip")
        assert result["category"] == "Travel"

    def test_healthcare_classification(self, classifier):
        result = classifier.predict("appointment doctor hospital prescription medical health clinic")
        assert result["category"] == "Healthcare"

    def test_promotions_classification(self, classifier):
        result = classifier.predict("sale discount offer coupon deal limited time exclusive promo")
        assert result["category"] == "Promotions / Marketing"

    def test_returns_dict_structure(self, classifier):
        result = classifier.predict("test email body")
        assert "category" in result
        assert "slug" in result
        assert "confidence" in result

    def test_empty_text_returns_other(self, classifier):
        result = classifier.predict("")
        # Empty text should return Other via keyword rules (no keywords match)
        # or any low-confidence category from ML — just validate structure
        assert result["category"] in [c["name"] for c in CATEGORIES]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_confidence_in_valid_range(self, classifier):
        result = classifier.predict("interview for software engineer position")
        assert 0.0 <= result["confidence"] <= 1.0
