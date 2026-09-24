"""
Intent detection — determines the specific purpose of an email
within its category.

Why rule-based: Intent at the email level (e.g., "Interview Invitation"
vs "Job Offer" within Job/Career) is highly predictable from keyword
patterns. This is faster, more explainable, and more reliable than
training a separate ML model for a small dataset.
"""
import re
from typing import Optional


# Intent patterns: (pattern, intent_label, priority)
# Higher priority = checked first when multiple patterns match
INTENT_PATTERNS: list[tuple[str, str, int]] = [
    # Job / Career
    (r"interview.*scheduled|schedule.*interview|invite.*interview|interview.*invitation", "Interview Invitation", 100),
    (r"job offer|pleased to offer|offer of employment|formal offer", "Job Offer", 100),
    (r"we regret|unfortunately.*not|not been selected|unsuccessful", "Job Rejection", 90),
    (r"application.*received|thank you for applying|applied for", "Application Confirmation", 80),
    (r"reference check|background check", "Reference Check", 80),
    (r"salary|compensation|package|ctc|benefits", "Salary Discussion", 70),

    # Education
    (r"assignment.*due|submission.*deadline|deadline.*assignment|project.*due", "Assignment Deadline", 100),
    (r"exam.*schedule|examination.*date|test.*date", "Exam Notification", 100),
    (r"admission.*confirm|confirmed.*admission|seat.*confirm", "Admission Confirmation", 100),
    (r"grade|result.*publish|marks.*available|scorecard", "Result Notification", 90),
    (r"fee.*due|tuition.*payment|fee.*reminder", "Fee Payment Reminder", 90),
    (r"class.*cancel|lecture.*cancel|session.*postpone", "Class Cancellation", 85),
    (r"scholarship|financial aid", "Scholarship Information", 80),

    # E-commerce
    (r"order.*confirm|confirm.*order|order.*placed", "Order Confirmation", 100),
    (r"order.*ship|shipped|out for delivery|delivery.*schedule", "Shipping Update", 90),
    (r"order.*deliver|delivered.*successfully", "Delivery Confirmation", 90),
    (r"refund.*process|refund.*initiat|money.*back|return.*approv", "Refund Update", 90),
    (r"return.*request|request.*return|return.*initiat", "Return Request", 85),
    (r"order.*cancel|cancel.*order", "Order Cancellation", 85),
    (r"invoice|receipt|payment.*confirm", "Invoice/Receipt", 80),

    # Finance / Banking
    (r"suspicious.*activity|unauthorized.*access|fraud.*alert|security.*alert", "Security Alert", 100),
    (r"otp|one.time.*password|verification.*code", "OTP/Verification", 100),
    (r"account.*block|card.*block|suspend", "Account Blocked", 100),
    (r"transaction.*alert|debit.*alert|credit.*alert|amount.*debit|amount.*credit", "Transaction Alert", 90),
    (r"statement.*available|account.*statement", "Account Statement", 70),
    (r"loan.*approv|loan.*rejected", "Loan Update", 85),
    (r"payment.*due|emi.*due|bill.*due", "Payment Due", 90),

    # Travel
    (r"flight.*confirm|booking.*confirm|e.ticket|boarding.*pass", "Flight Confirmation", 100),
    (r"flight.*cancel|cancellation.*flight", "Flight Cancellation", 95),
    (r"flight.*delay|delayed.*flight", "Flight Delay", 90),
    (r"hotel.*confirm|reservation.*confirm", "Hotel Confirmation", 90),
    (r"check.in.*reminder|check.in.*available", "Check-in Reminder", 85),

    # Healthcare
    (r"appointment.*confirm|confirm.*appointment|appointment.*schedul", "Appointment Confirmation", 100),
    (r"appointment.*remind|reminder.*appointment", "Appointment Reminder", 95),
    (r"appointment.*cancel|cancel.*appointment", "Appointment Cancellation", 90),
    (r"test.*result|lab.*result|report.*available", "Test Results", 90),
    (r"prescription.*ready|medication.*ready", "Prescription Ready", 85),

    # Work / Professional
    (r"meeting.*schedul|schedule.*meeting|invite.*meeting|meeting.*invitation", "Meeting Invitation", 95),
    (r"meeting.*cancel|cancel.*meeting", "Meeting Cancellation", 90),
    (r"meeting.*reschedul|reschedule.*meeting", "Meeting Rescheduled", 90),
    (r"project.*update|status.*update|progress.*report", "Project Update", 75),
    (r"performance.*review|appraisal", "Performance Review", 85),
    (r"deadline.*project|project.*deadline", "Project Deadline", 90),

    # Customer Support
    (r"ticket.*open|case.*open|support.*request.*creat", "Support Ticket Created", 80),
    (r"ticket.*resolv|case.*resolv|issue.*resolv", "Issue Resolved", 75),
    (r"follow.*up|following up", "Follow-up", 70),
    (r"complaint.*receiv|complaint.*log", "Complaint Received", 80),

    # Events / Invitations
    (r"invite.*event|invitation.*event|event.*invite", "Event Invitation", 90),
    (r"webinar.*register|register.*webinar|webinar.*confirm", "Webinar Registration", 85),
    (r"conference.*register|seminar.*register", "Conference Registration", 85),

    # Government / Official
    (r"tax.*notice|income.*tax|it.*return", "Tax Notice", 95),
    (r"pan.*card|aadhaar|passport.*renew", "Document Update", 85),
    (r"legal.*notice|court.*notice", "Legal Notice", 100),

    # Promotions / Marketing
    (r"offer.*expires|sale.*end|last.*chance|limited.*time", "Expiring Offer", 75),
    (r"exclusive.*offer|special.*deal|coupon.*code|promo.*code", "Promotional Offer", 60),
    (r"newsletter|weekly.*digest|monthly.*digest", "Newsletter", 40),

    # Social / Personal
    (r"birthday|happy birthday", "Birthday Greeting", 50),
    (r"wedding.*invitation|invite.*wedding", "Wedding Invitation", 80),
    (r"catch.*up|let.*meet|coffee|lunch|dinner.*plan", "Social Meetup", 60),
]

# Compiled for performance
_COMPILED_PATTERNS: Optional[list] = None


def _get_compiled():
    global _COMPILED_PATTERNS
    if _COMPILED_PATTERNS is None:
        _COMPILED_PATTERNS = [
            (re.compile(p, re.IGNORECASE), label, priority)
            for p, label, priority in INTENT_PATTERNS
        ]
    return _COMPILED_PATTERNS


def detect_intent(subject: str, body: str, category: str = "") -> str:
    """
    Detect the specific intent of an email.
    Returns the best-matching intent label or 'General Information'.
    """
    combined = f"{subject or ''} {body or ''}"
    compiled = _get_compiled()

    matches: list[tuple[str, int]] = []
    for pattern, label, priority in compiled:
        if pattern.search(combined):
            matches.append((label, priority))

    if not matches:
        return _fallback_intent(category)

    # Return the highest-priority match
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[0][0]


def _fallback_intent(category: str) -> str:
    """Generic intent when no specific pattern matches."""
    fallbacks = {
        "job_career": "Career Communication",
        "education": "Academic Notification",
        "ecommerce_shopping": "Order/Shopping Update",
        "finance_banking": "Financial Notification",
        "travel": "Travel Update",
        "healthcare": "Medical Communication",
        "work_professional": "Work Communication",
        "events_invitations": "Event Information",
        "government_official": "Official Communication",
        "promotions_marketing": "Promotional Content",
        "notifications": "System Notification",
        "customer_support": "Support Communication",
        "social_personal": "Personal Message",
    }
    return fallbacks.get(category.lower().replace(" / ", "_").replace(" ", "_"), "General Information")
