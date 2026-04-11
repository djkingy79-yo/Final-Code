# DO NOT UNDO — staged drafting pipeline. Additive module.
from services.llm_service import call_llm_for_report


async def draft_report_from_verified_material(case: dict, case_extract: dict, issues: list, verifications: list, report_type: str) -> dict:
    state = case.get('state', '') or 'UNSPECIFIED'
    jurisdiction_caveat = ""
    if not case.get('state'):
        jurisdiction_caveat = "\nJURISDICTION NOT CONFIRMED — flag this explicitly and note where analysis depends on jurisdiction-specific law. Do NOT default to NSW legislation.\n"
    else:
        jurisdiction_caveat = f"\nJurisdiction: {state.upper()}. Apply ONLY {state.upper()} legislation and appellate tests. Do NOT cite legislation from other states.\n"

    system_prompt = f"""Draft a professional criminal appeal report using only the supplied extracted and verified materials.
Do not introduce new grounds.
Do not invent authority.
Use cautious, professional, third-person language.
{jurisdiction_caveat}
ANTI-HALLUCINATION — ABSOLUTE:
- Do NOT invent case names, citations, statutory references, or facts not in the supplied materials.
- Do NOT state that an appeal will succeed or is likely to succeed.
- Use forensic appellate language: "It is arguable that...", "It is contended that...", NOT "The trial judge erred" or "This proves".
- Use Australian English spelling throughout (analyse, defence, offence, behaviour, honour, favour, centre).
- DISTINGUISH clearly between extracted fact, possible issue, legal inference, and missing material.
- Where evidence is incomplete, say so expressly."""

    user_prompt = f"""Draft a {report_type} criminal appeal report.

CASE SNAPSHOT:
{{
  "title": "{case.get('title', '')}",
  "defendant_name": "{case.get('defendant_name', '')}",
  "court": "{case.get('court', '')}",
  "state": "{case.get('state', '')}",
  "offence_category": "{case.get('offence_category', '')}",
  "offence_type": "{case.get('offence_type', '')}",
  "sentence": "{case.get('sentence', '')}"
}}

MERGED EXTRACT:
- Facts: {case_extract.get("merged_facts", [])[:120]}
- Events: {case_extract.get("merged_events", [])[:120]}
- Findings: {case_extract.get("merged_findings", [])[:120]}

CLASSIFIED ISSUES:
{issues[:50]}

VERIFICATIONS:
{verifications[:50]}

Required structure:
## 1. Case Overview
## 2. Procedural Chronology
## 3. Candidate Grounds
## 4. Evidentiary Support and Gaps
## 5. Legislative Framework
## 6. Recommended Next Steps

Do not state that an appeal will succeed.
Do not add new issues not present in the supplied materials."""

    return await call_llm_for_report(
        system_prompt,
        user_prompt,
        session_id=f"draft_{case['case_id']}_{report_type}",
        task_type="report_generation",
    )
