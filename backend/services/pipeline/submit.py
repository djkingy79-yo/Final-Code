# DO NOT UNDO — staged submissions drafting engine. Additive module.
import json
from services.llm_service import call_llm_for_json


def _validate_submission_payload(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required_keys = [
        "draft_title",
        "proposed_grounds",
        "overview",
        "procedural_background",
        "ground_submissions",
        "relief_sought",
        "authority_list",
        "evidence_reference_list",
        "drafting_note",
    ]
    return all(key in payload for key in required_keys)


async def build_submissions_draft(
    case: dict,
    case_extract: dict,
    issues: list,
    verifications: list,
    arguments: list,
) -> dict:
    system_prompt = """You are a senior Australian criminal appeal barrister.
Draft structured appellate submission material from the supplied staged case artifacts.
Do not overstate the appeal.
Do not invent authority.
Do not assert that relief will be granted.
Return JSON only."""

    facts_text = json.dumps(case_extract.get("merged_facts", [])[:150], default=str)
    events_text = json.dumps(case_extract.get("merged_events", [])[:150], default=str)
    findings_text = json.dumps(case_extract.get("merged_findings", [])[:150], default=str)
    issues_text = json.dumps([{"title": i.get("title"), "ground_type": i.get("ground_type"), "confidence": i.get("classification_confidence")} for i in issues[:50]], default=str)
    verifications_text = json.dumps([{"title": v.get("title"), "verification_status": v.get("verification_status"), "rating": v.get("legitimacy_scores", {}).get("rating")} for v in verifications[:50]], default=str)
    arguments_text = json.dumps([{"issue": a.get("issue"), "appellate_pathway": a.get("appellate_pathway"), "provisional_strength": a.get("provisional_strength")} for a in arguments[:50]], default=str)

    user_prompt = f"""Build a structured criminal appeal submissions draft.

CASE:
- Title: {case.get('title', 'Unknown')}
- Defendant: {case.get('defendant_name', 'Unknown')}
- State: {case.get('state', 'nsw')}
- Offence Category: {case.get('offence_category', 'unknown')}
- Offence Type: {case.get('offence_type', 'N/A')}
- Court: {case.get('court', 'N/A')}
- Sentence: {case.get('sentence', 'N/A')}

CASE EXTRACT:
- Facts: {facts_text}
- Events: {events_text}
- Findings: {findings_text}

ISSUES:
{issues_text}

VERIFICATIONS:
{verifications_text}

ARGUMENTS:
{arguments_text}

Return ONLY valid JSON:
{{"draft_title": "short draft title", "proposed_grounds": [{{"ground_number": 1, "ground_text": "concise proposed ground", "ground_type": "judicial_error|procedural_error|miscarriage_of_justice|fresh_evidence|sentencing_error|other"}}], "overview": "short overview of the proposed appeal submissions", "procedural_background": "short procedural background", "ground_submissions": [{{"ground_number": 1, "heading": "short heading", "submission_text": "structured concise written submission text", "appellate_pathway": "unsafe verdict|misdirection|procedural unfairness|sentence error|other", "provisional_strength": "strong|moderate|weak"}}], "relief_sought": ["order sought 1", "order sought 2"], "authority_list": [{{"citation": "case or statute citation", "type": "case|statute|other", "relevance": "short relevance note"}}], "evidence_reference_list": [{{"source": "document or extract source", "reference": "page or item reference", "relevance": "short relevance note"}}], "drafting_note": "short caution that this is a draft for legal review"}}"""

    return await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"submit_{case.get('case_id', 'case')}",
        task_type="submissions_draft",
        validation_fn=_validate_submission_payload,
    )
