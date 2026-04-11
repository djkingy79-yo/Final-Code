"""
Criminal Appeal AI - Case Metadata Validation & Citation Post-Processing

Provides:
  1. Soft pre-generation metadata validation (warnings, not blocks)
  2. Citation hallucination detection and stripping
"""
import re
import logging

logger = logging.getLogger(__name__)


# ── Metadata Validation (soft gate) ──────────────────────────────────────

def validate_case_metadata(case: dict) -> dict:
    """
    Validate case metadata completeness before AI generation.
    Returns a dict with 'complete' bool and 'warnings' list.
    This is a SOFT gate — generation proceeds regardless, but warnings
    are logged and can be surfaced to the user.
    """
    warnings = []
    state = case.get("state") or ""
    offence_cat = case.get("offence_category") or ""
    offence_type = case.get("offence_type") or ""

    if not state:
        warnings.append(
            "State/jurisdiction is not set. The analysis may lack state-specific "
            "legislation, sentencing frameworks, and appellate pathways."
        )
    if not offence_cat:
        warnings.append(
            "Offence category is not set. The analysis will lack offence-specific "
            "legislation references, elements to prove, and available defences."
        )
    if not offence_type:
        warnings.append(
            "Specific offence type is not set. The AI will infer from documents, "
            "which may reduce accuracy of legislation citations."
        )

    return {
        "complete": len(warnings) == 0,
        "warnings": warnings,
        "state": state,
        "offence_category": offence_cat,
        "offence_type": offence_type,
    }


def log_metadata_warnings(case_id: str, validation: dict, feature: str):
    """Log metadata warnings for audit trail."""
    if not validation["complete"]:
        for w in validation["warnings"]:
            logger.warning(f"[{feature}] case={case_id}: {w}")


# ── Citation Hallucination Detection ─────────────────────────────────────

# Valid Australian citation patterns:
# - "R v Smith [2023] NSWCCA 123"
# - "Smith v The Queen (2020) 271 CLR 456"
# - "DPP v Jones [2019] VSCA 78"
# Court abbreviation whitelist (real Australian courts)
_VALID_COURT_ABBREVS = {
    # High Court
    "HCA", "CLR", "ALR", "ALJR",
    # Federal
    "FCA", "FCAFC", "FCR",
    # NSW
    "NSWCCA", "NSWSC", "NSWCA", "NSWDC", "NSWLC",
    # VIC
    "VSCA", "VSC", "VCC", "VMC",
    # QLD
    "QCA", "QSC", "QDC",
    # SA
    "SASCFC", "SASC", "SADC", "SACA",
    # WA
    "WASCA", "WASC", "WADC",
    # TAS
    "TASCCA", "TASSC", "TASMC",
    # NT
    "NTCCA", "NTSC", "NTMC",
    # ACT
    "ACTCA", "ACTSC",
    # Other
    "UKPC", "UKHL", "UKSC",
}

# Pattern: [Year] COURT Number  e.g. [2023] NSWCCA 123
_MEDIUM_NEUTRAL_PATTERN = re.compile(
    r'\[(\d{4})\]\s+([A-Z]{2,8})\s+(\d+)'
)

# Pattern: (Year) Volume Reporter Page  e.g. (2020) 271 CLR 456
_LAW_REPORT_PATTERN = re.compile(
    r'\((\d{4})\)\s+(\d+)\s+([A-Z]{2,5})\s+(\d+)'
)

# Placeholder patterns that indicate hallucination
_PLACEHOLDER_PATTERNS = [
    re.compile(r'\[Surname\]', re.IGNORECASE),
    re.compile(r'\[Year\]', re.IGNORECASE),
    re.compile(r'\[Full Citation\]', re.IGNORECASE),
    re.compile(r'\[Citation\]', re.IGNORECASE),
    re.compile(r'\[Court\]', re.IGNORECASE),
    re.compile(r'v\s+\[?\w+\]?\s+\[\d{4}\]\s+[A-Z]+\s+\d+.*(?:hypothetical|fictional|illustrative)', re.IGNORECASE),
]

# Suspicious patterns: overly generic or templated citations
_SUSPICIOUS_PATTERNS = [
    re.compile(r'R v [A-Z][a-z]+ \[\d{4}\] [A-Z]+ \d+ at \[not available\]', re.IGNORECASE),
    re.compile(r'citation not available', re.IGNORECASE),
    re.compile(r'citation pending', re.IGNORECASE),
    re.compile(r'no citation available', re.IGNORECASE),
    re.compile(r'section not provided', re.IGNORECASE),
    re.compile(r'section unknown', re.IGNORECASE),
]


def validate_citation(citation_text: str) -> dict:
    """
    Validate a single citation string.
    Returns dict with 'valid', 'confidence', 'reason'.
    """
    if not citation_text or not citation_text.strip():
        return {"valid": False, "confidence": 0, "reason": "empty citation"}

    text = citation_text.strip()

    # Check for placeholder patterns (definite hallucination)
    for pat in _PLACEHOLDER_PATTERNS:
        if pat.search(text):
            return {"valid": False, "confidence": 0, "reason": "placeholder detected"}

    # Check for suspicious patterns
    for pat in _SUSPICIOUS_PATTERNS:
        if pat.search(text):
            return {"valid": False, "confidence": 0, "reason": "suspicious pattern"}

    # Check for medium neutral citation [Year] COURT Number
    mn_match = _MEDIUM_NEUTRAL_PATTERN.search(text)
    if mn_match:
        year = int(mn_match.group(1))
        court = mn_match.group(2)
        if court in _VALID_COURT_ABBREVS and 1900 <= year <= 2026:
            return {"valid": True, "confidence": 0.8, "reason": "medium neutral citation with known court"}
        elif 1900 <= year <= 2026:
            return {"valid": True, "confidence": 0.5, "reason": "medium neutral citation with unknown court abbreviation"}
        else:
            return {"valid": False, "confidence": 0.1, "reason": "implausible year"}

    # Check for law report citation (Year) Vol Reporter Page
    lr_match = _LAW_REPORT_PATTERN.search(text)
    if lr_match:
        year = int(lr_match.group(1))
        reporter = lr_match.group(3)
        if reporter in _VALID_COURT_ABBREVS and 1900 <= year <= 2026:
            return {"valid": True, "confidence": 0.8, "reason": "law report citation with known reporter"}
        elif 1900 <= year <= 2026:
            return {"valid": True, "confidence": 0.5, "reason": "law report citation with unknown reporter"}

    # No recognisable citation pattern found — could be a case name without citation
    # (e.g. "House v The King") — these are OK but lower confidence
    if re.search(r'v\s+(?:The\s+)?(?:Queen|King|State|Crown|DPP|R\b)', text, re.IGNORECASE):
        return {"valid": True, "confidence": 0.4, "reason": "case name without formal citation"}

    return {"valid": True, "confidence": 0.3, "reason": "unverified format"}


def strip_hallucinated_citations(text: str) -> str:
    """
    Post-process generated text to remove likely hallucinated citations.
    Strips lines/sentences containing placeholder or suspicious citation patterns.
    Preserves all other content.
    """
    if not text:
        return text

    lines = text.split('\n')
    cleaned = []
    stripped_count = 0

    for line in lines:
        should_strip = False

        # Check for placeholder patterns
        for pat in _PLACEHOLDER_PATTERNS:
            if pat.search(line):
                should_strip = True
                break

        # Check for suspicious patterns
        if not should_strip:
            for pat in _SUSPICIOUS_PATTERNS:
                if pat.search(line):
                    should_strip = True
                    break

        if should_strip:
            stripped_count += 1
            logger.info(f"Stripped hallucinated citation line: {line[:100]}...")
        else:
            cleaned.append(line)

    if stripped_count > 0:
        logger.info(f"Citation post-processing: stripped {stripped_count} suspicious lines")

    return '\n'.join(cleaned)


def validate_similar_cases(similar_cases: list) -> list:
    """
    Validate a list of similar case dicts from AI output.
    Removes cases with placeholder citations or no valid citation.
    Adds verification_status to remaining cases.
    """
    if not similar_cases:
        return []

    validated = []
    for case in similar_cases:
        citation = case.get("citation", "") or case.get("case_citation", "") or ""
        case_name = case.get("case_name", "") or case.get("name", "") or ""
        full_ref = f"{case_name} {citation}".strip()

        result = validate_citation(full_ref)

        if not result["valid"]:
            logger.info(f"Removed hallucinated similar case: {full_ref[:80]} ({result['reason']})")
            continue

        # Mark verification status based on confidence
        if result["confidence"] >= 0.7:
            case["verification_status"] = "unverified — check on AustLII"
        else:
            case["verification_status"] = "unverified — citation format uncertain, verify on AustLII"

        validated.append(case)

    removed = len(similar_cases) - len(validated)
    if removed > 0:
        logger.info(f"Similar case validation: removed {removed}/{len(similar_cases)} suspected hallucinations")

    return validated


def validate_law_sections(law_sections: list) -> list:
    """
    Validate law section references from AI output.
    Removes entries with placeholder section numbers.
    """
    if not law_sections:
        return []

    validated = []
    for section in law_sections:
        sec_ref = section.get("section", "") or section.get("section_number", "") or ""
        act_name = section.get("act", "") or section.get("act_name", "") or ""

        # Skip placeholder sections
        if any(p in sec_ref.lower() for p in ["not provided", "unknown", "n/a", "tbd", "placeholder"]):
            logger.info(f"Removed placeholder law section: {sec_ref} {act_name}")
            continue
        if any(p in act_name.lower() for p in ["not provided", "unknown", "n/a", "placeholder"]):
            logger.info(f"Removed placeholder law section act: {act_name}")
            continue
        if not sec_ref and not act_name:
            continue

        section["verification_status"] = "unverified — verify section number on AustLII"
        validated.append(section)

    removed = len(law_sections) - len(validated)
    if removed > 0:
        logger.info(f"Law section validation: removed {removed}/{len(law_sections)} placeholder sections")

    return validated
