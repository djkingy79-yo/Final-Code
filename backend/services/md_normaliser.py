"""
Markdown normaliser — runs BEFORE persisting LLM output.

The LLM frequently produces markdown without proper blank-line spacing around
headings, bullet lists, and tables. Without normalisation the frontend sees
literal "## Heading" or "- **Foo**:" text inside paragraphs.

This utility must mirror `/app/frontend/src/utils/mdRender.js :: normaliseMarkdown`
so the rendering pipeline is identical on both tiers. Apply it at save-time
and (one-off) during backfill.
"""

from __future__ import annotations
import re


_DOUBLE_SPACE_NL = re.compile(r"[ \t]{2,}\n")
_ATX_INLINE_AFTER_PUNCT = re.compile(
    r"([.!?:;])\s+(#{2,6})\s+([A-Z0-9][^\n#]{2,100})(?=\s|$)"
)
_ATX_INLINE_AFTER_WORD = re.compile(
    r'([a-zA-Z0-9)"])\s{1,4}(#{2,6})\s+([A-Z0-9][^\n#]{2,100})(?=\s|$)'
)
_ATX_NO_BLANK_BEFORE = re.compile(r"([^\n])\n(#{1,6})\s")
_ATX_HEADING_BODY_SPLIT = re.compile(
    r"(#{3,6})\s+"
    r"((?:[A-Z][A-Za-z0-9'\-]+(?:\s+(?:and|of|in|to|on|for|the|a|an|vs\.?|v\.?))?\s?){1,5})"
    r"(?=[A-Z][a-z]+\s+(?:is|was|has|have|had|will|would|may|can|might|shall|should|must|appears|indicates))"
)
_BULLETS_NO_BLANK_BEFORE = re.compile(r"([^\n\-\*\d])\n([\-\*]\s+)")
_NUMLIST_NO_BLANK_BEFORE = re.compile(r"([^\n\-\*\d])\n(\d+\.\s+)")
_TABLE_NO_BLANK_BEFORE = re.compile(r"([^\n|])\n(\|)")
_TRIPLE_NEWLINES = re.compile(r"\n{3,}")
_BULLET_TIGHTEN = re.compile(r"([\-\*][^\n]+)\n\n(?=[\-\*]\s)")
_NUMLIST_TIGHTEN = re.compile(r"(\d+\.[^\n]+)\n\n(?=\d+\.\s)")
_INLINE_BULLET_AFTER_PUNCT = re.compile(r"([:.!?])\s*-\s\*\*")
_INLINE_BULLET_AFTER_WORD = re.compile(r"([a-z.]\.)\s+-\s\*\*")


def normalise_markdown(raw: str | None) -> str:
    """Normalise raw LLM markdown so every heading/list/table has the blank
    lines a standards-compliant markdown parser needs.

    Idempotent: safe to run multiple times on the same text.
    """
    if not raw:
        return ""
    text = str(raw).replace("\r\n", "\n")
    text = _DOUBLE_SPACE_NL.sub("\n", text)

    # Headings
    text = _ATX_NO_BLANK_BEFORE.sub(r"\1\n\n\2 ", text)
    text = _ATX_INLINE_AFTER_PUNCT.sub(r"\1\n\n\2 \3\n\n", text)
    text = _ATX_INLINE_AFTER_WORD.sub(r"\1\n\n\2 \3\n\n", text)
    text = _ATX_HEADING_BODY_SPLIT.sub(r"\1 \2\n\n", text)

    # Lists + tables
    text = _BULLETS_NO_BLANK_BEFORE.sub(r"\1\n\n\2", text)
    text = _NUMLIST_NO_BLANK_BEFORE.sub(r"\1\n\n\2", text)
    text = _TABLE_NO_BLANK_BEFORE.sub(r"\1\n\n\2", text)

    # Collapse triple+ newlines
    text = _TRIPLE_NEWLINES.sub("\n\n", text)

    # Tighten consecutive bullets that were over-separated by earlier passes
    text = _BULLET_TIGHTEN.sub(r"\1\n", text)
    text = _NUMLIST_TIGHTEN.sub(r"\1\n", text)

    # Inline bullets glued to prose by punctuation
    text = _INLINE_BULLET_AFTER_PUNCT.sub(r"\1\n- **", text)
    text = _INLINE_BULLET_AFTER_WORD.sub(r"\1\n- **", text)

    return text.strip()
