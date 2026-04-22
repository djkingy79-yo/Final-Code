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
# LLM often emits numbered bold-label paragraphs INLINE as a single block:
#   "1. **Appellate Pathway:** text. 2. **Ground:** text. 3. **Error Identified:** ..."
# which renders as one giant run-on paragraph. Split each "N. **Label:**"
# onto its own paragraph so every sub-heading becomes a real <h4>-style block.
_NUMBERED_BOLD_LABEL_INLINE = re.compile(
    r"(^|[.!?])\s*(?:\d+\.)\s+\*\*([A-Z][A-Za-z][^*\n]{1,60}?:)\*\*\s+",
    re.MULTILINE,
)
# Same for un-numbered inline bold labels mid-paragraph:
#   "...established. **Materiality:** This error... **Consequence:** ..."
_BOLD_LABEL_INLINE = re.compile(
    r"([.!?])\s+\*\*([A-Z][A-Za-z][^*\n]{1,60}?:)\*\*\s+"
)
# A paragraph of raw prose with no \n\n internal breaks and > 800 chars is a
# wall-of-text LLM slip. Insert a paragraph break after sentences that end
# with a date or legal citation, or after every 3rd sentence (>= 200 chars
# elapsed since last break). Preserves sentence boundaries.
_LONG_PARA_SENTENCE_SPLIT_MIN_CHARS = 800


def normalise_markdown(raw: str | None) -> str:
    """Normalise raw LLM markdown so every heading/list/table has the blank
    lines a standards-compliant markdown parser needs.

    Idempotent: safe to run multiple times on the same text.
    """
    if not raw:
        return ""
    text = str(raw).replace("\r\n", "\n")
    text = _DOUBLE_SPACE_NL.sub("\n", text)

    # Headings — use lambda replacements so any backslash-digit sequences
    # inside captured content (e.g. "see \3 authority") aren't re-interpreted
    # as regex backreferences during substitution.
    text = _ATX_NO_BLANK_BEFORE.sub(lambda m: f"{m.group(1)}\n\n{m.group(2)} ", text)
    text = _ATX_INLINE_AFTER_PUNCT.sub(lambda m: f"{m.group(1)}\n\n{m.group(2)} {m.group(3)}\n\n", text)
    text = _ATX_INLINE_AFTER_WORD.sub(lambda m: f"{m.group(1)}\n\n{m.group(2)} {m.group(3)}\n\n", text)
    text = _ATX_HEADING_BODY_SPLIT.sub(lambda m: f"{m.group(1)} {m.group(2)}\n\n", text)

    # Lists + tables (same lambda-safe substitutions)
    text = _BULLETS_NO_BLANK_BEFORE.sub(lambda m: f"{m.group(1)}\n\n{m.group(2)}", text)
    text = _NUMLIST_NO_BLANK_BEFORE.sub(lambda m: f"{m.group(1)}\n\n{m.group(2)}", text)
    text = _TABLE_NO_BLANK_BEFORE.sub(lambda m: f"{m.group(1)}\n\n{m.group(2)}", text)

    # Collapse triple+ newlines (no captures — safe to use raw replacement)
    text = _TRIPLE_NEWLINES.sub("\n\n", text)

    # Tighten consecutive bullets that were over-separated by earlier passes
    text = _BULLET_TIGHTEN.sub(lambda m: f"{m.group(1)}\n", text)
    text = _NUMLIST_TIGHTEN.sub(lambda m: f"{m.group(1)}\n", text)

    # Split "1. **Label:** ..." mid-paragraph sequences onto their own lines.
    # Run twice in case two numbered labels appeared back-to-back.
    for _ in range(2):
        text = _NUMBERED_BOLD_LABEL_INLINE.sub(lambda m: f"{m.group(1)}\n\n**{m.group(2)}** ", text)

    # Split un-numbered bold-label paragraphs inline after a sentence-ending
    # period. Common in Deep Investigation Analysis output.
    for _ in range(2):
        text = _BOLD_LABEL_INLINE.sub(lambda m: f"{m.group(1)}\n\n**{m.group(2)}** ", text)

    # Inline bullets glued to prose by punctuation
    text = _INLINE_BULLET_AFTER_PUNCT.sub(lambda m: f"{m.group(1)}\n- **", text)
    text = _INLINE_BULLET_AFTER_WORD.sub(lambda m: f"{m.group(1)}\n- **", text)

    # Wall-of-text repair: any paragraph > 800 chars with no internal \n\n
    # and at least 6 sentence boundaries gets split after every 3rd sentence.
    # Preserves semantics; only acts on LLM paragraphs that are unambiguously
    # too long to read. Uses literal replacement (no regex substitution) so
    # backslash-digit sequences inside content can never be mis-interpreted
    # as backreferences (e.g. "see \3" citations blew up before).
    paragraphs = text.split("\n\n")
    repaired_paras = []
    for p in paragraphs:
        if (
            len(p) >= _LONG_PARA_SENTENCE_SPLIT_MIN_CHARS
            and "\n" not in p
            and p.count(". ") >= 6
        ):
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", p)
            chunks = []
            current = []
            for s in sentences:
                current.append(s)
                joined_len = sum(len(x) for x in current) + len(current) - 1
                if len(current) >= 3 and joined_len >= 300:
                    chunks.append(" ".join(current))
                    current = []
            if current:
                chunks.append(" ".join(current))
            repaired_paras.append("\n\n".join(chunks))
        else:
            repaired_paras.append(p)
    text = "\n\n".join(repaired_paras)

    return text.strip()
