# DO NOT UNDO — staged argument engine. Additive module.
import json
from services.llm_service import call_llm_for_json


def _validate_argument_payload(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required_keys = [
        "issue",
        "legal_significance",
        "supporting_analysis",
        "undermining_analysis",
        "evidentiary_gaps",
        "appellate_pathway",
        "provisional_strength",
        "caution_note",
    ]
    return all(key in payload for key in required_keys)


async def build_issue_argument(case: dict, issue: dict, verification: dict) -> dict:
    system_prompt = """You are a senior Australian criminal appeal barrister.
Draft structured appellate reasoning from verified issue material.
Do not overstate the issue.
Do not say the appeal will succeed.
Do not invent authority.
Return JSON only."""

    supporting_items = json.dumps(verification.get("supporting_items", []), default=str)
    undermining_items = json.dumps(verification.get("undermining_items", []), default=str)
    missing_items = json.dumps(verification.get("missing_items", []), default=str)
    law_sections = json.dumps(verification.get("law_sections", []), default=str)
    similar_cases = json.dumps(verification.get("similar_cases", []), default=str)
    legitimacy_scores = json.dumps(verification.get("legitimacy_scores", {}), default=str)

    user_prompt = f"""Build a structured legal argument for this verified issue.

CASE:
- Title: {case.get('title', 'Unknown')}
- State: {case.get('state', 'nsw')}
- Offence Category: {case.get('offence_category', 'unknown')}
- Offence Type: {case.get('offence_type', 'N/A')}
- Court: {case.get('court', 'N/A')}
- Sentence: {case.get('sentence', 'N/A')}

ISSUE:
- Title: {issue.get('title')}
- Ground Type: {issue.get('ground_type')}
- Description: {issue.get('description')}
- Classification Confidence: {issue.get('classification_confidence', 'moderate')}

VERIFICATION:
- Supporting Items: {supporting_items}
- Undermining Items: {undermining_items}
- Missing Items: {missing_items}
- Law Sections: {law_sections}
- Similar Cases: {similar_cases}
- Legitimacy Scores: {legitimacy_scores}
- Verification Status: {verification.get('verification_status', 'reviewed')}

Return ONLY valid JSON:
{{"issue": "short statement of the issue", "legal_significance": "why this issue may matter on appeal", "supporting_analysis": "how the supporting material advances the issue", "undermining_analysis": "what weakens or qualifies the issue", "evidentiary_gaps": ["gap 1", "gap 2"], "appellate_pathway": "unsafe verdict|misdirection|procedural unfairness|sentence error|other", "provisional_strength": "strong|moderate|weak", "caution_note": "brief caution about limits or review requirements"}}"""

    return await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"argue_{issue.get('issue_id', 'issue')}",
        task_type="issue_argument",
        validation_fn=_validate_argument_payload,
    )
