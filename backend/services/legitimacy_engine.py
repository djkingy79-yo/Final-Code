"""
Criminal Appeal AI - Legitimacy Engine
3-layer forensic validation for grounds of merit scoring.

Layers:
  1. Legal Basis     — Does this ground map to a recognised appellate pathway?
  2. Evidence Score   — Is there direct evidentiary support from case documents?
  3. Appellate Viability — Would the Court of Criminal Appeal realistically intervene?

Hard safety rules:
  - No ground can be rated STRONG without evidence score >= 2
  - Rating is calculated, never AI-guessed
"""
from typing import List, Dict


# Layer 1 — Recognised appellate pathway scores
LEGAL_BASIS_SCORES = {
    "miscarriage_of_justice": 3,
    "procedural_error": 3,
    "judicial_error": 3,
    "fresh_evidence": 3,
    "prosecution_misconduct": 3,
    "constitutional_violation": 3,
    "sentencing_error": 2,
    "jury_irregularity": 2,
    "ineffective_counsel": 2,
    "other": 1,
}

# Ground types with high appellate intervention likelihood
HIGH_VALUE_GROUNDS = [
    "miscarriage_of_justice", "fresh_evidence", "judicial_error",
    "prosecution_misconduct", "constitutional_violation",
]
MEDIUM_VALUE_GROUNDS = [
    "procedural_error", "ineffective_counsel", "sentencing_error",
]


def score_legal_basis(ground_type: str) -> int:
    """Map ground type to recognised appellate pathway. Returns 1-3."""
    return LEGAL_BASIS_SCORES.get(ground_type, 1)


def score_evidence(evidence_list: List, undermining_list: List = None) -> int:
    """
    Evidence scoring based on specificity and quantity:
      3 = multiple strong evidence items (3+ items, at least one direct quote >50 chars)
      2 = some evidence (2+ items or 1 strong direct quote >80 chars)
      1 = minimal evidence (1 item or short references)
      0 = no evidence provided
    
    Undermining evidence reduces the score:
      - If undermining >= supporting, cap at 1
      - If undermining > 0, reduce by 1
    """
    if not evidence_list:
        return 0

    # Count substantive items
    strong_items = 0
    any_items = 0
    for item in evidence_list:
        text = ""
        if isinstance(item, dict):
            text = str(item.get("quote") or item.get("text") or "").strip()
        elif isinstance(item, str):
            text = item.strip()
        elif isinstance(item, list):
            text = " ".join(str(x) for x in item).strip()
        else:
            text = str(item).strip()

        if text:
            any_items += 1
            if len(text) > 80:
                strong_items += 1

    # Base score from quantity and quality
    if strong_items >= 2 and any_items >= 3:
        base_score = 3
    elif strong_items >= 1 and any_items >= 2:
        base_score = 2
    elif any_items >= 1:
        base_score = 1
    else:
        base_score = 0

    # Apply undermining penalty
    undermining_count = len(undermining_list) if undermining_list else 0
    if undermining_count > 0:
        if undermining_count >= any_items:
            base_score = min(base_score, 1)
        else:
            base_score = max(0, base_score - 1)

    return base_score


def score_appellate_viability(ground_type: str, evidence_score: int) -> int:
    """
    Conservative viability model aligned with NSWCCA / general appellate reality.
    Returns 0-3.
    """
    if evidence_score == 0:
        return 0

    if ground_type in HIGH_VALUE_GROUNDS and evidence_score >= 2:
        return 3
    elif ground_type in MEDIUM_VALUE_GROUNDS and evidence_score >= 2:
        return 2
    elif ground_type in HIGH_VALUE_GROUNDS:
        return 2
    elif ground_type in MEDIUM_VALUE_GROUNDS:
        return 1
    else:
        return 1


def _generate_confidence_note(ground_type: str, evidence_score: int) -> str:
    """Generate a calibrated confidence note for this ground."""
    if evidence_score == 0:
        return "No direct evidentiary support identified — requires documentary verification before any reliance"
    if evidence_score == 1:
        return "Limited evidentiary basis — requires further documentary substantiation"
    if ground_type == "fresh_evidence":
        return "Viability depends on whether evidence satisfies the fresh evidence test (could not have been obtained with reasonable diligence; would likely have produced a different verdict)"
    if ground_type == "jury_irregularity":
        return "Requires proof of actual irregularity affecting the verdict, not speculation"
    if ground_type == "ineffective_counsel":
        return "Requires demonstration that representation fell below objective standard of competence and affected the outcome"
    if ground_type == "sentencing_error":
        return "Appellate courts afford considerable deference to sentencing judges — manifest excess or specific error required"
    return "Assessment subject to full transcript, evidentiary, and legal review by qualified counsel"


def calculate_ground_rating(ground: Dict) -> Dict:
    """
    Calculate a defensible legitimacy rating for a ground of merit.

    Returns dict with:
      - legal_score (0-3)
      - evidence_score (0-3)
      - viability_score (0-3)
      - total_score (0-9)
      - rating: strong | moderate | weak
      - confidence_note: calibrated note
    """
    ground_type = ground.get("ground_type", "other")
    evidence_list = ground.get("supporting_evidence") or ground.get("key_evidence") or []
    undermining_list = ground.get("undermining_items") or ground.get("undermining_evidence") or []

    legal_score = score_legal_basis(ground_type)
    evidence_score = score_evidence(evidence_list, undermining_list)
    viability_score = score_appellate_viability(ground_type, evidence_score)

    total = legal_score + evidence_score + viability_score

    if total >= 8:
        rating = "strong"
    elif total >= 4:
        rating = "moderate"
    else:
        rating = "weak"

    # HARD SAFETY RULE: No STRONG without evidence score >= 2
    if evidence_score < 2 and rating == "strong":
        rating = "moderate"

    return {
        "legal_score": legal_score,
        "evidence_score": evidence_score,
        "viability_score": viability_score,
        "total_score": total,
        "rating": rating,
        "confidence_note": _generate_confidence_note(ground_type, evidence_score),
    }


def validate_ground_type(ground_type) -> str:
    """Normalise and validate ground type. Returns valid type or 'other'."""
    if isinstance(ground_type, list):
        ground_type = ground_type[0] if ground_type else "other"
    normalised = str(ground_type or "").strip().lower().replace(" ", "_")
    if normalised in LEGAL_BASIS_SCORES:
        return normalised
    return "other"
