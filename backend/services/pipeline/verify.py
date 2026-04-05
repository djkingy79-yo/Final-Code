# DO NOT UNDO — staged verification pipeline. Additive module.
from services.llm_service import call_llm_for_json
from services.legitimacy_engine import calculate_ground_rating
from services.pipeline_models import IssueVerification


def _validate_issue_verification(payload: dict) -> bool:
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("supporting_items"), list)
        and isinstance(payload.get("undermining_items"), list)
        and isinstance(payload.get("missing_items"), list)
    )


async def verify_issue(case: dict, issue: dict, supporting_context: dict) -> IssueVerification:
    system_prompt = """Assess the identified issue against the extracted record.
Return supporting, undermining, and missing material.
Do not overstate the issue.
Do not state that the issue is made out unless clearly supported.
Use AUSTRALIAN ENGLISH ONLY (analyse, organise, defence, offence, behaviour, favour, honour, centre, specialise, recognise, authorise, emphasise, summarise, counselling). Do NOT use American spellings.
Return JSON only."""

    user_prompt = f"""Verify this candidate appellate issue.

CASE:
- Title: {case.get('title', 'Unknown')}
- State: {case.get('state', 'nsw')}
- Offence Category: {case.get('offence_category', 'unknown')}

ISSUE:
- Title: {issue.get('title')}
- Ground Type: {issue.get('ground_type')}
- Description: {issue.get('description')}

SUPPORTING CONTEXT:
{supporting_context}

Return ONLY valid JSON:
{{
  "supporting_items": [
    {{
      "document_id": "optional",
      "filename": "optional",
      "quote": "supporting quote",
      "page_reference": "optional",
      "role": "supports",
      "confidence": "strong|moderate|weak"
    }}
  ],
  "undermining_items": [
    {{
      "document_id": "optional",
      "filename": "optional",
      "quote": "undermining quote",
      "page_reference": "optional",
      "role": "undermines",
      "confidence": "strong|moderate|weak"
    }}
  ],
  "missing_items": ["missing transcript or proof item"],
  "law_sections": [
    {{
      "act": "Act name",
      "section": "section",
      "jurisdiction": "{case.get('state', 'nsw')}",
      "title": "optional",
      "verification_status": "unverified"
    }}
  ],
  "similar_cases": [
    {{
      "case_name": "R v [Surname] [Year]",
      "citation": null,
      "jurisdiction": "{case.get('state', 'nsw')}",
      "relevance_note": "brief note on how this case is relevant",
      "verification_status": "unverified"
    }}
  ],
  "verification_status": "reviewed",
  "requires_human_review": true
}}"""

    parsed = await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"verify_{issue.get('issue_id', 'issue')}",
        task_type="issue_verification",
        validation_fn=_validate_issue_verification,
    )

    scores = calculate_ground_rating({
        "ground_type": issue.get("ground_type", "other"),
        "supporting_evidence": parsed.get("supporting_items", []),
        "undermining_items": parsed.get("undermining_items", []),
    })

    return IssueVerification(
        issue_id=issue["issue_id"],
        case_id=case["case_id"],
        user_id=case["user_id"],
        supporting_items=parsed.get("supporting_items", []),
        undermining_items=parsed.get("undermining_items", []),
        missing_items=parsed.get("missing_items", []),
        law_sections=parsed.get("law_sections", []),
        similar_cases=parsed.get("similar_cases", []),
        legitimacy_scores=scores,
        verification_status=parsed.get("verification_status", "reviewed"),
        requires_human_review=bool(parsed.get("requires_human_review", True)),
    )
