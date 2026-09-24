"""
Category-aware prompt builder for smart reply generation.

Design principle: The prompt is constructed from multiple context blocks
so the LLM understands the full situation and produces a relevant reply.
Different categories get different system personas and instructions.
"""
from typing import Optional

# ── Category-specific system instructions ────────────────────────────────────

CATEGORY_SYSTEM_PROMPTS = {
    "job_career": (
        "You are a professional job seeker or employee writing a career-related email reply. "
        "Maintain a formal, confident, and enthusiastic tone. Be concise and direct."
    ),
    "work_professional": (
        "You are a professional writing a workplace email reply. "
        "Use a clear, professional, and collaborative tone. Get to the point efficiently."
    ),
    "education": (
        "You are a student writing a reply to an academic email. "
        "Use a respectful, polite tone appropriate for communication with professors or institutions."
    ),
    "ecommerce_shopping": (
        "You are a customer writing a reply about an order, delivery, or return. "
        "Be clear about your order details and politely state your concern or confirmation."
    ),
    "finance_banking": (
        "You are a bank customer replying to a financial or banking email. "
        "Use a formal, cautious tone. Include relevant account/reference information placeholders. "
        "Never include real financial credentials in the reply."
    ),
    "travel": (
        "You are a traveler replying to a travel-related email. "
        "Be clear, friendly, and include relevant booking details."
    ),
    "healthcare": (
        "You are a patient or caregiver replying to a healthcare email. "
        "Use a respectful, clear tone and confirm or politely ask for clarification."
    ),
    "social_personal": (
        "You are writing a warm, friendly personal reply. "
        "Match the social context — invitation, greeting, or casual message."
    ),
    "events_invitations": (
        "You are replying to an event invitation or registration. "
        "Be enthusiastic but professional. Confirm or decline clearly."
    ),
    "government_official": (
        "You are writing a formal reply to an official government or legal communication. "
        "Use very formal language. Include reference numbers where appropriate."
    ),
    "promotions_marketing": (
        "You are replying to a promotional or marketing email. "
        "Be brief and direct — either acknowledging receipt or requesting more information."
    ),
    "customer_support": (
        "You are a customer writing to support. "
        "Clearly describe your issue and provide relevant reference numbers."
    ),
    "notifications": (
        "You are acknowledging a notification or automated message. "
        "Keep the reply brief and confirm receipt if needed."
    ),
    "other": (
        "You are writing a professional email reply. "
        "Match the tone of the original email."
    ),
}

# ── Tone modifiers ────────────────────────────────────────────────────────────

TONE_INSTRUCTIONS = {
    "formal": "Write in a formal, professional tone. Use complete sentences and avoid contractions.",
    "friendly": "Write in a warm, friendly, approachable tone while remaining professional.",
    "concise": "Write a very concise reply — 2–3 sentences maximum. Get to the point immediately.",
    "longer": "Write a comprehensive, detailed reply addressing all points in the original email.",
}

# ── Style modification instructions ──────────────────────────────────────────

STYLE_INSTRUCTIONS = {
    "shorter": "Rewrite the following reply to be significantly shorter (2–3 sentences). Keep only the essential message.",
    "formal": "Rewrite the following reply in a more formal, professional tone. Use formal language and avoid casual expressions.",
    "friendly": "Rewrite the following reply in a warmer, friendlier tone while keeping it professional.",
    "longer": "Expand the following reply to be more detailed and comprehensive. Address the original email more thoroughly.",
}


def build_generation_prompt(
    subject: str,
    body: str,
    sender_name: Optional[str],
    category: str,
    category_slug: str,
    intent: str,
    action_required: bool,
    deadline_text: Optional[str],
    entities: list[dict],
    tone: str = "formal",
) -> str:
    """
    Build the full prompt for initial reply generation.
    """
    system = CATEGORY_SYSTEM_PROMPTS.get(category_slug, CATEGORY_SYSTEM_PROMPTS["other"])
    tone_instr = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["formal"])

    # Build entity context
    entity_summary = ""
    if entities:
        key_entities = [e["entity_text"] for e in entities[:8]]
        entity_summary = f"\nKey information detected: {', '.join(key_entities)}"

    # Build deadline context
    deadline_instr = ""
    if deadline_text:
        deadline_instr = f"\nIMPORTANT: The email mentions a deadline or scheduled time: {deadline_text}. Acknowledge this in the reply."

    # Build action context
    action_instr = ""
    if action_required:
        action_instr = "\nThe original email requires a specific action or confirmation. Address this clearly in the reply."

    prompt = f"""{system}

{tone_instr}

ORIGINAL EMAIL:
From: {sender_name or 'Unknown Sender'}
Subject: {subject or '(No Subject)'}
---
{body[:2000]}
---

Email Category: {category}
Email Intent: {intent}{entity_summary}{deadline_instr}{action_instr}

INSTRUCTIONS:
1. Write ONLY the reply content — no subject line, no "Subject:" prefix
2. Start with an appropriate greeting
3. Address the main purpose of the email clearly
4. Be {tone} in tone
5. End with a professional sign-off
6. Use [Your Name] as a placeholder for the sender's name
7. Do not include any meta-commentary or explanations — just the reply

Write the email reply now:"""

    return prompt


def build_modification_prompt(
    current_reply: str,
    style: str,
    category_slug: str,
) -> str:
    """
    Build the prompt for modifying an existing reply.
    """
    instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["formal"])
    return f"""{instruction}

CURRENT REPLY:
---
{current_reply}
---

Write ONLY the modified reply. No explanations or meta-commentary."""
