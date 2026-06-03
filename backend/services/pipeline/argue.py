#  — staged argument engine. Additive module.
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
    state = case.get('state', '') or ''
    jurisdiction_caveat = ""
    if not state:
        jurisdiction_caveat = "\nJURISDICTION NOT CONFIRMED — flag this explicitly. Do NOT default to NSW legislation.\n"
    else:
        jurisdiction_caveat = f"\nJurisdiction: {state.upper()}. Apply ONLY {state.upper()} legislation and appellate tests.\n"

    system_prompt = f"""You are a senior Australian criminal appeal barrister.
Draft structured appellate reasoning from verified issue material.
Do not overstate the issue. Do not say the appeal will succeed. Do not invent authority.
{jurisdiction_caveat}
ANTI-HALLUCINATION — ABSOLUTE:
- Do NOT invent case names, citations, section numbers, Act names, or facts not in the supplied materials.
- Only cite cases with REAL, complete Australian citations. If no verified citation is known, omit.
- If uncertain about a section number, reference the Act by name only — do NOT guess.

FORENSIC LANGUAGE — ABSOLUTE RULE:
- NEVER use declarative phrases: "The trial judge erred", "The judge clearly erred", "This proves", "The conviction is unsafe", "The sentence is excessive", "The error is established", "was denied", "was deprived".
- ALWAYS use forensic appellate framing: "It is arguable that...", "It is contended that...", "There is a tenable argument that...", "On one view of the evidence...", "It may be submitted that...", "The available material supports the contention that...".
- BANNED CHARACTERISATION LANGUAGE: NEVER write "The judge determined that [X]", "The court found that [X]", or "The judge concluded that [X]" when describing a trial-level characterisation of facts, conditions, or mental states. Use instead: "The judge treated [X] as..." / "The sentencing judge characterised [X] as..." / "The judge approached [X] on the basis that...".
- Appellate work identifies ARGUABLE errors — it does NOT declare findings. The Court makes findings.
- Use Australian English only (analyse, defence, offence, behaviour, favour).

GROUND TYPE RULES — ABSOLUTE:
- NEVER MERGE CONVICTION AND SENTENCING ISSUES in one ground. Conviction attacks the verdict; sentencing attacks the penalty. If both apply, flag them as TWO separate grounds.
- PARTIAL DEFENCES (s 23A Crimes Act 1900 (NSW) substantial impairment; diminished responsibility (QLD); mental impairment defence (VIC/SA/ACT); unsoundness of mind (WA/TAS)) operate on LIABILITY — they reduce murder to manslaughter. They are NEVER sentencing mitigation. Classify them as conviction grounds only.
- For mens rea / unsafe verdict grounds, EXPLICITLY apply the M v The Queen (1994) 181 CLR 487 formulation: "Could the jury, acting reasonably, have excluded a reasonable hypothesis consistent with lack of intent given the competing psychiatric evidence?"
- Post-verdict juror conduct (e.g. waving at victim's family AFTER verdict) has MINIMAL probative value. Do NOT elevate such conduct above "weak" unless there is a contemporaneous trial-record complaint and a juror affidavit.

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
- State: {case.get('state', '') or 'UNSPECIFIED'}
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

CRITICAL: Frame ALL conclusions using forensic appellate language. NEVER state "The trial judge erred" — instead state "It is arguable that the trial judge erred in...". The distinction is critical for professional appellate work.

Return ONLY valid JSON:
{{"issue": "short statement of the arguable issue", "legal_significance": "why this issue is arguably significant on appeal", "supporting_analysis": "how the supporting material advances the arguable error", "undermining_analysis": "what qualifies or weakens the argument", "evidentiary_gaps": ["gap 1", "gap 2"], "appellate_pathway": "unsafe verdict|misdirection|procedural unfairness|sentence error|other", "provisional_strength": "strong|moderate|weak", "caution_note": "brief caution about limits or review requirements"}}"""""

    return await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"argue_{issue.get('issue_id', 'issue')}",
        task_type="issue_argument",
        validation_fn=_validate_argument_payload,
    )
