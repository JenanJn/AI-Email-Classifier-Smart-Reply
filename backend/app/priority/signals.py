"""
Priority signal detectors.

Each signal function returns a (score, reason) tuple where:
- score: 0 to the signal's max_weight
- reason: human-readable explanation string (empty string = no contribution)

Why separate signals: Makes the system explainable and independently testable.
Each signal can be tuned or replaced without affecting others.
"""
import re
from typing import Optional


# ── Signal 1: Urgency words (max 15) ─────────────────────────────────────────

URGENCY_WORDS = [
    "urgent", "urgently", "immediately", "asap", "as soon as possible",
    "right away", "without delay", "critical", "emergency", "time-sensitive",
    "time sensitive", "prompt", "promptly", "deadline", "expires",
]


def signal_urgency_words(text: str) -> tuple[int, str]:
    text_lower = text.lower()
    found = [w for w in URGENCY_WORDS if w in text_lower]
    if not found:
        return 0, ""
    score = min(len(found) * 5, 15)
    return score, f"Urgency language detected: '{found[0]}'"


# ── Signal 2: Deadline proximity (max 25) ────────────────────────────────────

TOMORROW_PATTERNS = [r"\btomorrow\b", r"\bwithin 24 hours\b", r"\bby tomorrow\b"]
WITHIN_48H_PATTERNS = [r"\bday after tomorrow\b", r"\bwithin 48 hours\b", r"\bin 2 days\b"]
THIS_WEEK_PATTERNS = [r"\bthis week\b", r"\bwithin a week\b", r"\bby (monday|tuesday|wednesday|thursday|friday)\b"]
TODAY_PATTERNS = [r"\btoday\b", r"\bby end of day\b", r"\bby eod\b", r"\bby close of business\b", r"\bbefore midnight\b"]


def signal_deadline_proximity(text: str) -> tuple[int, str]:
    text_lower = text.lower()

    for p in TODAY_PATTERNS:
        if re.search(p, text_lower):
            return 25, "Deadline is today — extremely time-sensitive"

    for p in TOMORROW_PATTERNS:
        if re.search(p, text_lower):
            return 22, "Deadline occurs within 24 hours"

    for p in WITHIN_48H_PATTERNS:
        if re.search(p, text_lower):
            return 15, "Deadline within 48 hours"

    for p in THIS_WEEK_PATTERNS:
        if re.search(p, text_lower):
            return 8, "Deadline within the current week"

    # Check for explicit dates (heuristic)
    if re.search(r"\bby\s+\w+\s+\d{1,2}", text_lower) or re.search(r"\bdue\s+(on|by|before)\b", text_lower):
        return 5, "Specific deadline date mentioned"

    return 0, ""


# ── Signal 3: Action required (max 15) ────────────────────────────────────────

ACTION_PATTERNS = [
    r"\bplease (confirm|reply|respond|call|contact|approve|submit|fill|complete|provide|send)\b",
    r"\brequires? (your|a) (response|reply|confirmation|approval|action|attention)\b",
    r"\baction required\b",
    r"\brespond by\b",
    r"\bplease (let us|let me) know\b",
    r"\byour (confirmation|response|reply|approval) is (required|needed|requested)\b",
    r"\bkindly (confirm|reply|respond|submit)\b",
    r"\bwaiting for your (response|reply|confirmation)\b",
    r"\bverify (your|the) (identity|account|details)\b",
    r"\bplease (verify|validate|confirm)\b",
    r"\bimmediately\b",
]


def signal_action_required(text: str) -> tuple[int, str, bool]:
    """Returns (score, reason, action_required_flag)."""
    text_lower = text.lower()
    for p in ACTION_PATTERNS:
        if re.search(p, text_lower):
            return 15, "Explicit action or confirmation requested", True
    return 0, "", False


# ── Signal 4: Category base score (max 10) ───────────────────────────────────

CATEGORY_BASE_SCORES = {
    "finance_banking": 10,
    "job_career": 9,
    "healthcare": 9,
    "government_official": 8,
    "work_professional": 7,
    "education": 7,
    "travel": 6,
    "customer_support": 6,
    "events_invitations": 5,
    "social_personal": 4,
    "ecommerce_shopping": 4,
    "notifications": 3,
    "promotions_marketing": 1,
    "other": 3,
}

CATEGORY_REASONS = {
    "finance_banking": "Financial/banking communication typically requires attention",
    "job_career": "Career-related email carries inherent importance",
    "healthcare": "Medical communication is high-priority by nature",
    "government_official": "Official government communication requires attention",
    "work_professional": "Professional work communication",
    "education": "Academic communication",
    "travel": "Travel-related communication",
    "customer_support": "Customer support communication",
}


def signal_category_base(category_slug: str) -> tuple[int, str]:
    score = CATEGORY_BASE_SCORES.get(category_slug, 3)
    reason = CATEGORY_REASONS.get(category_slug, "")
    return score, reason


# ── Signal 5: Event / scheduled item (max 10) ────────────────────────────────

EVENT_PATTERNS = [
    r"\b(interview|meeting|appointment|exam|test|presentation|review)\s+(is\s+)?(scheduled|set|confirmed|arranged)\b",
    r"\bscheduled\s+(interview|meeting|appointment)\b",
    r"\b(at|on)\s+\d{1,2}(:\d{2})?\s*(am|pm)\b",
    # Also fire if the subject or body simply mentions an interview/meeting with a time
    r"\b(interview|meeting|appointment)\b.{0,60}\b(tomorrow|today|am|pm|\d{1,2}:\d{2})\b",
    r"\b(tomorrow|today)\b.{0,60}\b(interview|meeting|appointment)\b",
]


def signal_event_scheduled(text: str) -> tuple[int, str]:
    text_lower = text.lower()
    for p in EVENT_PATTERNS:
        if re.search(p, text_lower):
            return 10, "Scheduled event (interview/meeting/appointment) detected"
    return 0, ""


# ── Signal 6: Financial / security alert (max 10) ────────────────────────────

SECURITY_PATTERNS = [
    r"\b(unauthorized|suspicious|fraud|unusual)\s+(activity|access|transaction|login)\b",
    r"\baccount\s+(blocked|suspended|locked|compromised)\b",
    r"\bsecurity\s+alert\b",
    r"\bverif(y|ication)\s+(your\s+)?(identity|account)\b",
    r"\bunauthorized\s+access\b",
    r"\bsuspicious\s+(login|activity)\b",
]


def signal_financial_security(text: str) -> tuple[int, str]:
    text_lower = text.lower()
    for p in SECURITY_PATTERNS:
        if re.search(p, text_lower):
            return 10, "Security or fraud alert detected"
    return 0, ""


# ── Signal 7: Time-sensitive language (max 10) ───────────────────────────────

TIME_SENSITIVE_PATTERNS = [
    r"\bexpires?\s+(in|on|by|tonight|today|tomorrow)\b",
    r"\bonly\s+\d+\s+(hours?|days?)\s+left\b",
    r"\blast\s+chance\b",
    r"\blimited\s+time\b",
    r"\bdon[''t]t\s+miss\b",
    r"\bfinal\s+(reminder|notice|warning)\b",
    r"\boverdue\b",
]


def signal_time_sensitive_language(text: str) -> tuple[int, str]:
    text_lower = text.lower()
    for p in TIME_SENSITIVE_PATTERNS:
        if re.search(p, text_lower):
            return 10, "Time-sensitive language detected"
    return 0, ""


# ── Signal 8: Sender importance (max 5) ──────────────────────────────────────

ORG_DOMAIN_PATTERNS = [
    r"@(?!gmail|yahoo|hotmail|outlook|proton|icloud)[a-z]+\.(com|org|edu|gov|net|in)\b",
]

NO_REPLY_PATTERNS = [r"\bno.?reply@\b", r"\bnoreply@\b"]


def signal_sender_importance(sender_email: Optional[str]) -> tuple[int, str]:
    if not sender_email:
        return 0, ""
    if any(re.search(p, sender_email, re.IGNORECASE) for p in ORG_DOMAIN_PATTERNS):
        return 5, "Email from an organizational domain"
    return 0, ""
