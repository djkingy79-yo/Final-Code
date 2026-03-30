# DO NOT UNDO — staged classification pipeline. Additive module.
from services.llm_service import call_llm_for_json
from services.pipeline_models import IssueClassification

GROUND_TYPES = {
    "procedural_error",
    "fresh_evidence",
    "miscarriage_of_justice",
    "sentencing_error",
    "judicial_error",
    "ineffective_counsel",
    "prosecution_misconduct",
    "jury_irregularity",
    "constitutional_violation",
    "other",
}


def _validate_issue_classification(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False
    issues = payload.get("issues")
    if not isinstance(issues, list):
        return False
    for issue in issues:
        if not isinstance(issue, dict):
            return False
        if not issue.get("title"):
            return False
    return True


def _norm_ground_type(value: str) -> str:
    v = str(value or "other").strip().lower()
    return v if v in GROUND_TYPES else "other"


async def classify_case_issues(case: dict, case_extract: dict) -> list[IssueClassification]:
    system_prompt = """You are a specialist Australian appellate lawyer conducting a preliminary issue-spot.
Your task is to identify ONLY the most significant and distinct potential grounds of appeal.
Quality over quantity — a real appeal typically has 3 to 8 grounds at most.
Do NOT list every conceivable complaint. Merge related sub-issues into a single ground.
Use conditional language. Do not verify the issues. Do not state that any appeal will succeed."""

    facts_text = "\n".join([
        f"[{f.get('fact_id', '')}] ({f.get('type', 'general')}) {f.get('text', '')}"
        for f in case_extract.get("merged_facts", [])
    ])
    events_text = "\n".join([
        f"[{e.get('extracted_event_id', e.get('event_id', ''))}] {e.get('title', '')} ({e.get('event_date', 'unknown')})"
        for e in case_extract.get("merged_events", [])
    ])
    findings_text = "\n".join([
        f"[{f.get('finding_id', '')}] ({f.get('type', 'general')}) {f.get('text', '')}"
        for f in case_extract.get("merged_findings", [])
    ])

    state = case.get("state", "nsw")
    offence_cat = case.get("offence_category", "unknown")

    user_prompt = f"""Based on the extracted record below, identify the MOST SIGNIFICANT potential grounds of appeal.

Jurisdiction: {state.upper()}
Offence category: {offence_cat}
Offence type: {case.get('offence_type', 'Not specified')}

EXTRACTED FACTS:
{facts_text[:15000]}

EXTRACTED EVENTS:
{events_text[:5000]}

EXTRACTED FINDINGS:
{findings_text[:10000]}

Return ONLY valid JSON:
{{
  "issues": [
    {{
      "title": "<concise issue title>",
      "ground_type": "<procedural_error|fresh_evidence|miscarriage_of_justice|sentencing_error|judicial_error|ineffective_counsel|prosecution_misconduct|jury_irregularity|constitutional_violation|other>",
      "description": "<2-3 sentence description of the possible issue>",
      "linked_fact_ids": ["fact_xxx"],
      "linked_event_ids": ["xevt_xxx"],
      "linked_finding_ids": ["find_xxx"],
      "classification_confidence": "<strong|moderate|weak>"
    }}
  ]
}}

STRICT RULES:
- Return a MAXIMUM of 10 grounds. Focus only on the strongest, most distinct issues.
- MERGE related sub-issues into a single ground (e.g., all sentencing complaints become one "Sentencing Error" ground, all psychiatric evidence issues become one ground).
- Do NOT split the same underlying complaint into multiple grounds.
- Each ground MUST be materially distinct from every other ground.
- Use conditional language (possible issue, potential ground, may warrant).
- Link each issue to specific extracted fact/event/finding IDs.
- ground_type MUST be from the listed values.
- classification_confidence should reflect genuine assessment:
  * "strong" = clear factual/legal basis in the record, likely arguable
  * "moderate" = some supporting evidence, warrants further investigation  
  * "weak" = only a marginal indicator, limited evidence in the record
  If an issue is significant enough to list, it should be at least "moderate" unless the evidence is genuinely thin.
- Only classify issues genuinely supported by the extracted record."""

    parsed = await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"classify_{case['case_id']}",
        task_type="issue_classification",
        validation_fn=_validate_issue_classification,
    )

    issues = []
    for raw in parsed.get("issues", [])[:10]:  # Hard cap at 10 — a real appeal has 3-8 grounds
        issues.append(IssueClassification(
            case_id=case["case_id"],
            user_id=case["user_id"],
            title=raw.get("title", "Untitled issue"),
            ground_type=_norm_ground_type(raw.get("ground_type")),
            description=raw.get("description", ""),
            linked_fact_ids=raw.get("linked_fact_ids", []),
            linked_event_ids=raw.get("linked_event_ids", []),
            linked_finding_ids=raw.get("linked_finding_ids", []),
            classification_confidence=raw.get("classification_confidence", "moderate"),
            jurisdiction=state,
        ))

    return issues
