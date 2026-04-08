"""
Criminal Appeal AI - Legitimacy Engine (Phase 4 — Three-Axis Viability Scoring)
DO NOT UNDO — Barrister-approved scoring model.

Three-Axis Model:
  1. Outcome Impact    — Determinative / Influential / Minor
  2. Legal Alignment   — Direct authority / Analogous / Weak
  3. Evidence Support   — Strong / Partial / Limited

Combined → Appellate Viability: Arguable — Strong / Arguable — Moderate / Requires Development

Hard safety rules:
  - No ground rated "Arguable — Strong" without evidence_support >= "partial"
  - Rating is calculated, never AI-guessed
  - Constitutional grounds (s 80) deprioritised unless direct authority exists
"""
from typing import List, Dict


# === Layer 1: Outcome Impact ===
# How much impact would this ground have on the appeal outcome?
OUTCOME_IMPACT_SCORES = {
    "miscarriage_of_justice": 3,  # Determinative
    "judicial_error": 3,
    "fresh_evidence": 3,
    "prosecution_misconduct": 3,
    "procedural_error": 2,        # Influential
    "jury_irregularity": 2,
    "ineffective_counsel": 2,
    "sentencing_error": 2,
    "constitutional_violation": 1, # Minor (deprioritised — rarely operative in state appeals)
    "other": 1,
}

# === Layer 2: Legal Alignment ===
# Ground types with direct appellate authority
DIRECT_AUTHORITY_GROUNDS = [
    "miscarriage_of_justice", "fresh_evidence", "judicial_error",
    "prosecution_misconduct", "sentencing_error",
]
ANALOGOUS_GROUNDS = [
    "procedural_error", "ineffective_counsel", "jury_irregularity",
]


def score_outcome_impact(ground_type: str) -> dict:
    """Score outcome impact. Returns label and numeric score (1-3)."""
    score = OUTCOME_IMPACT_SCORES.get(ground_type, 1)
    labels = {3: "Determinative", 2: "Influential", 1: "Minor"}
    return {"score": score, "label": labels.get(score, "Minor")}


def score_legal_alignment(ground_type: str) -> dict:
    """Score legal alignment based on whether direct authority supports this ground type."""
    if ground_type in DIRECT_AUTHORITY_GROUNDS:
        return {"score": 3, "label": "Direct authority"}
    elif ground_type in ANALOGOUS_GROUNDS:
        return {"score": 2, "label": "Analogous"}
    else:
        return {"score": 1, "label": "Weak"}


def score_evidence_support(evidence_list: List, undermining_list: List = None) -> dict:
    """
    Evidence scoring based on specificity and quantity:
      Strong  (3) = 3+ items with at least 2 substantive quotes (>80 chars)
      Partial (2) = 2+ items or 1 strong direct quote (>80 chars)
      Limited (1) = 1 item or short references only
      None    (0) = no evidence

    Undermining evidence reduces the score:
      - If undermining >= supporting, cap at 1
      - If undermining > 0, reduce by 1
    """
    if not evidence_list:
        return {"score": 0, "label": "None"}

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

    if strong_items >= 2 and any_items >= 3:
        base_score = 3
    elif strong_items >= 1 and any_items >= 2:
        base_score = 2
    elif any_items >= 1:
        base_score = 1
    else:
        base_score = 0

    undermining_count = len(undermining_list) if undermining_list else 0
    if undermining_count > 0:
        if undermining_count >= any_items:
            base_score = min(base_score, 1)
        else:
            base_score = max(0, base_score - 1)

    labels = {3: "Strong", 2: "Partial", 1: "Limited", 0: "None"}
    return {"score": base_score, "label": labels.get(base_score, "None")}


def _generate_confidence_note(ground_type: str, evidence_score: int) -> str:
    """Generate a calibrated confidence note for this ground with forensic framing."""
    if evidence_score == 0:
        return "No direct evidentiary support identified — requires documentary verification before any reliance."
    if evidence_score == 1:
        return "Limited evidentiary basis — requires further documentary substantiation."
    if ground_type == "fresh_evidence":
        return "Viability depends on whether evidence satisfies the fresh evidence test (could not have been obtained with reasonable diligence; would likely have produced a different verdict)."
    if ground_type == "jury_irregularity":
        return "Requires proof of actual irregularity affecting the verdict, not speculation. Related jury issues (judge-alone refusal, jury reduction, juror conduct) should be presented as sub-particulars under a single procedural unfairness ground."
    if ground_type == "ineffective_counsel":
        return "CONTINGENT — requires evidentiary support before advancement. The threshold is extremely high: an affidavit from the accused, evidence of advice given, and transcript confirmation are typically required. Without this evidentiary foundation, advancing this ground risks weakening overall appellate credibility."
    if ground_type == "miscarriage_of_justice":
        return "Where psychiatric or mental state evidence is involved, this ground should be framed as a conviction safety attack on mens rea determination — whether the requisite mental state (intent to kill, intent to cause GBH, or reckless indifference) was properly established given competing evidence."
    if ground_type == "sentencing_error":
        return "This ground should be framed around proportionality and moral culpability — whether the sentence reflects true culpability given all relevant circumstances, including any mental impairment. Appellate courts afford considerable deference to sentencing judges — manifest excess or specific error required."
    if ground_type == "constitutional_violation":
        return "Constitutional grounds are rarely the operative pathway in state criminal appeals. Consider reframing under miscarriage of justice or procedural unfairness."
    return "Assessment subject to full transcript, evidentiary, and legal review by qualified counsel."


def calculate_ground_rating(ground: Dict) -> Dict:
    """
    Calculate a defensible three-axis legitimacy rating for a ground of merit.

    Returns dict with:
      - outcome_impact: {score, label}
      - legal_alignment: {score, label}
      - evidence_support: {score, label}
      - total_score (0-9)
      - rating: strong | moderate | weak
      - viability_label: "Arguable — Strong" / "Arguable — Moderate" / "Requires Development"
      - confidence_note: calibrated note
    """
    ground_type = ground.get("ground_type", "other")
    evidence_list = ground.get("supporting_evidence") or ground.get("key_evidence") or []
    undermining_list = ground.get("undermining_items") or ground.get("undermining_evidence") or []

    outcome = score_outcome_impact(ground_type)
    legal = score_legal_alignment(ground_type)
    evidence = score_evidence_support(evidence_list, undermining_list)

    total = outcome["score"] + legal["score"] + evidence["score"]

    if total >= 7:
        rating = "strong"
        viability_label = "Arguable \u2014 Strong"
    elif total >= 4:
        rating = "moderate"
        viability_label = "Arguable \u2014 Moderate"
    else:
        rating = "weak"
        viability_label = "Requires Development"

    # HARD SAFETY RULE: No "strong" without evidence score >= 2
    if evidence["score"] < 2 and rating == "strong":
        rating = "moderate"
        viability_label = "Arguable \u2014 Moderate"

    # HARD SAFETY RULE: Constitutional grounds deprioritised
    if ground_type == "constitutional_violation" and rating == "strong":
        rating = "moderate"
        viability_label = "Arguable \u2014 Moderate"

    # HARD SAFETY RULE: Ineffective counsel capped unless strong evidence
    # This ground has an extremely high threshold — requires affidavit, transcript, etc.
    if ground_type == "ineffective_counsel" and rating == "strong" and evidence["score"] < 3:
        rating = "moderate"
        viability_label = "Arguable \u2014 Moderate"

    # Flag for contingent grounds
    is_contingent = ground_type == "ineffective_counsel"

    return {
        "outcome_impact": outcome,
        "legal_alignment": legal,
        "evidence_support": evidence,
        "total_score": total,
        "rating": rating,
        "viability_label": viability_label,
        "confidence_note": _generate_confidence_note(ground_type, evidence["score"]),
        "is_contingent": is_contingent,
        # Legacy compatibility fields — documented mapping:
        # - legal_score → legal_alignment.score (unchanged)
        # - evidence_score → evidence_support.score (unchanged)
        # - outcome_impact_score → outcome_impact.score (was viability_score in earlier versions)
        "legal_score": legal["score"],
        "evidence_score": evidence["score"],
        "outcome_impact_score": outcome["score"],
        "viability_score": outcome["score"],  # Deprecated alias — use outcome_impact_score
    }


def validate_ground_type(ground_type) -> str:
    """Normalise and validate ground type. Returns valid type or 'other'."""
    if isinstance(ground_type, list):
        ground_type = ground_type[0] if ground_type else "other"
    normalised = str(ground_type or "").strip().lower().replace(" ", "_")
    if normalised in OUTCOME_IMPACT_SCORES:
        return normalised
    return "other"
