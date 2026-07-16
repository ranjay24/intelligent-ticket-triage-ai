"""
Lightweight PII redaction applied to ticket text BEFORE it is sent to the
LLM. The goal is that raw personal data (emails, phone numbers, card
numbers, etc.) never leaves for the model, while the original text is still
stored and shown to human agents who may need it.

This is heuristic (regex-based), not a full NER/ML detector — it is a
pragmatic privacy safeguard, not a guarantee. It is deliberately
conservative so it does not mask things the pipeline needs, such as order
identifiers like "ORD1001" (letters + digits never match these patterns).
"""

import re

# Order matters: more specific patterns run before looser ones.
_PATTERNS = [
    ("[EMAIL]", re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("[SSN]", re.compile(
        r"\b\d{3}-\d{2}-\d{4}\b")),
    ("[CARD]", re.compile(
        r"\b(?:\d[ -]?){13,18}\d\b")),          # 14-19 digit card-like runs
    ("[PHONE]", re.compile(
        r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")),
    ("[IP]", re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
]


def redact(text):
    """Return (redacted_text, count_of_redactions)."""
    if not text:
        return text, 0

    count = 0
    for tag, pattern in _PATTERNS:
        text, n = pattern.subn(tag, text)
        count += n

    return text, count