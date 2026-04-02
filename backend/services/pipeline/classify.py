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
    system_prompt = """You are a specialist Australian appellate lawyer conducting a thorough issue-spot.
Your task is to identify ALL potential grounds of appeal that are supported by the case material.
Be thorough and exhaustive — identify every distinct legal issue, procedural error, evidential problem,
sentencing concern, and rights violation that could form a ground of appeal.
Do NOT merge different issues together. Each distinct legal argument deserves its own ground.
For example, a sentencing error based on double-counting is DIFFERENT from a sentencing error based
on manifest excess. A failure to call witnesses is DIFFERENT from a failure to object to evidence.
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

    user_prompt = f"""Based on the extracted record below, identify ALL potential grounds of appeal.
Be thorough — examine every aspect of the case for possible appealable issues.

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
- Identify as many distinct grounds as the evidence supports. Aim for 8-15 grounds if the case material warrants it.
- Do NOT merge different legal arguments into one ground. Each distinct issue gets its own entry.
  For example: "Sentencing Error — Manifest Excess" and "Sentencing Error — Double-Counting Aggravating Factors" are TWO separate grounds.
  "Failure to Call Key Witnesses" and "Failure to Object to Inadmissible Evidence" are TWO separate grounds.
  "Prejudicial Media Coverage" and "Jury Non-Sequestration" are TWO separate grounds even though both relate to jury.
- Each ground MUST identify a specific, distinct legal issue or error.
- Use conditional language (possible issue, potential ground, may warrant).
- Link each issue to specific extracted fact/event/finding IDs.
- ground_type MUST be from the listed values.
- classification_confidence should reflect genuine assessment:
  * "strong" = clear factual/legal basis in the record, likely arguable
  * "moderate" = some supporting evidence, warrants further investigation  
  * "weak" = only a marginal indicator, limited evidence in the record
- Only classify issues genuinely supported by the extracted record."""

    parsed = await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"classify_{case['case_id']}",
        task_type="issue_classification",
        validation_fn=_validate_issue_classification,
    )

    issues = []
    for raw in parsed.get("issues", [])[:15]:  # Allow up to 15 grounds for thorough analysis
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
