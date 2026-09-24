"""
Text preprocessing for the NLP pipeline.

Why: Raw email text contains HTML, extra whitespace, signatures,
and boilerplate that degrade classifier accuracy if not cleaned.
"""
import re
import html


def clean_email_text(text: str) -> str:
    """
    Full cleaning pipeline for an email body:
    1. Unescape HTML entities
    2. Strip HTML tags
    3. Normalize whitespace
    4. Remove email signatures / boilerplate patterns
    5. Lowercase
    """
    if not text:
        return ""

    # 1. Unescape HTML entities (&amp; &lt; etc.)
    text = html.unescape(text)

    # 2. Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # 3. Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " URL ", text)

    # 4. Remove email signatures (lines starting with -- or ____)
    text = re.sub(r"\n[-_]{2,}.*", "", text, flags=re.DOTALL)

    # 5. Remove forwarded / replied-to headers
    text = re.sub(r"(On .+wrote:|From:.+\nSent:.+\nTo:.+)", "", text, flags=re.DOTALL)

    # 6. Collapse multiple spaces and newlines
    text = re.sub(r"\s+", " ", text).strip()

    # 7. Lowercase for feature extraction
    # (We keep original for entity extraction — done before this step)
    return text.lower()


def extract_clean_for_classification(subject: str, body: str) -> str:
    """
    Combine subject (weighted 2x) + body for TF-IDF input.
    Subject is repeated to give it more importance.
    """
    subject_clean = clean_email_text(subject or "")
    body_clean = clean_email_text(body or "")
    # Weight subject by repeating it
    return f"{subject_clean} {subject_clean} {body_clean}".strip()


def clean_for_entity_extraction(text: str) -> str:
    """
    Lighter cleaning for entity extraction — preserve case and structure
    since spaCy NER relies on capitalization and punctuation.
    """
    if not text:
        return ""
    # Unescape and strip HTML only
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
