"""
evidence_builder.py

Generates affidavit templates, document requests, and evidence plans
based on identified appellate grounds.

For each PRIMARY / SECONDARY ground, answers: "What do I need to prove
this ground in court?" — producing a deterministic plan the report
renderer can show counsel, along with ready-to-adapt affidavit skeletons.

Every output carries the mandatory warning that all material must be
reviewed and finalised by a qualified Australian legal practitioner.

Counsel feedback 23 Feb 2026 — exact logic supplied by counsel.
"""

from __future__ import annotations

from services.ground_normaliser import Ground


MANDATORY_WARNING = (
    "This evidence plan is a guide only. All affidavits and material must be "
    "prepared and reviewed by a qualified Australian legal practitioner before use."
)


def affidavit_template_psychiatric() -> str:
    return (
        "AFFIDAVIT OF EXPERT WITNESS\n\n"
        "I, [Name], of [Address], [Occupation], say on oath:\n\n"
        "1. I am a qualified [psychiatrist/psychologist] with experience in forensic assessment.\n"
        "2. I have reviewed the material provided including:\n"
        "   (a) Trial transcript\n"
        "   (b) Medical records\n"
        "   (c) Prior expert reports\n\n"
        "3. In my opinion, at the time of the alleged offence:\n"
        "   (a) The accused was suffering from [diagnosis]\n"
        "   (b) This condition affected their capacity to:\n"
        "       (i) understand events\n"
        "       (ii) control actions\n"
        "       (iii) know right from wrong\n\n"
        "4. It is my opinion that this condition is consistent with substantial impairment.\n\n"
        "SWORN:"
    )


def affidavit_template_juror() -> str:
    return (
        "AFFIDAVIT OF WITNESS (JUROR CONDUCT)\n\n"
        "I, [Name], say on oath:\n\n"
        "1. I observed the following conduct during the trial:\n"
        "2. [Describe interaction, behaviour, or communication]\n\n"
        "3. This occurred on [date/time] and involved [persons].\n\n"
        "4. The conduct appeared to indicate [bias/prejudice].\n\n"
        "SWORN:"
    )


def document_request_list(ground: Ground) -> list[str]:
    docs = ["Full trial transcript"]

    if ground.type == "conviction":
        docs.append("Judge's summing-up and directions")
        docs.append("Exhibit list and evidence schedule")

    if ground.type == "procedure":
        docs.append("Voir dire transcripts")
        docs.append("Pre-trial applications and rulings")

    if ground.type == "sentence":
        docs.append("Sentencing remarks")
        docs.append("Pre-sentence reports")

    if "mental" in (ground.error_identified or "").lower():
        docs.append("Psychiatric and medical records")

    return docs


def evidence_steps(ground: Ground) -> list[str]:
    steps: list[str] = []

    if ground.type == "conviction":
        steps.append("Obtain complete trial transcript")
        steps.append("Review jury directions for error")
        if "mental" in (ground.error_identified or "").lower():
            steps.append("Commission independent psychiatric assessment")

    if ground.type == "procedure":
        steps.append("Identify procedural irregularities in transcript")
        steps.append("Secure witness or juror affidavit evidence")

    if ground.type == "sentence":
        steps.append("Compare sentence with similar cases")
        steps.append("Analyse sentencing remarks for error")

    return steps


def build_evidence_plan(ground: Ground) -> dict:
    plan: dict = {
        "ground": ground.title,
        "documents_required": document_request_list(ground),
        "steps": evidence_steps(ground),
        "affidavits": [],
    }

    text = (ground.error_identified or "").lower()

    if "mental" in text:
        plan["affidavits"].append({
            "type": "psychiatric",
            "template": affidavit_template_psychiatric(),
        })

    if "jury" in text or "juror" in text:
        plan["affidavits"].append({
            "type": "juror_conduct",
            "template": affidavit_template_juror(),
        })

    return plan


def generate_evidence_builder(strategy: dict) -> dict:
    output: dict = {"warning": MANDATORY_WARNING}

    if strategy.get("primary"):
        output["primary"] = build_evidence_plan(strategy["primary"])

    if strategy.get("secondary"):
        output["secondary"] = build_evidence_plan(strategy["secondary"])

    return output


# ---------------------------------------------------------------------------
# LLM refinement layer — counsel feedback 23 Feb 2026.
# ---------------------------------------------------------------------------
# The deterministic builder above gives the correct STRUCTURE + mandatory
# warning. The LLM pass customises the affidavit template wording for the
# specific ground and case (defendant name, offence, jurisdictional
# statutory partial defence, procedural specifics) while preserving:
#   - the mandatory warning text (exactly)
#   - the set of affidavits (no adds / no removes)
#   - the affidavit 'type' field (unchanged)
#   - the structured skeleton: heading + numbered paragraphs + SWORN:
# ---------------------------------------------------------------------------

import logging  # noqa: E402 — grouped with LLM helpers

_log = logging.getLogger(__name__)

_REFINEMENT_SYSTEM_PROMPT = (
    "You are a senior junior counsel preparing evidence-gathering material "
    "for an Australian criminal appeal. Third-person forensic register only. "
    "Australian spelling (analyse, organise, judgement, offence).\n\n"
    "STYLE RULES:\n"
    "- NEVER use 'we', 'us', 'our', 'you', 'your'.\n"
    "- Refer to the accused by surname where passed in the user prompt.\n"
    "- Cite statutory framing by section and Act (e.g. 's 23A Crimes Act 1900 "
    "(NSW)') where naturally relevant.\n"
    "- Document-request items stay crisp noun phrases (e.g. 'Full trial "
    "transcript'); do NOT turn them into sentences.\n"
    "- Affidavit templates KEEP their existing skeleton — heading in capitals, "
    "numbered paragraphs (1., 2., 3., ...), nested sub-paragraphs ((a), (b), "
    "(i), (ii)), and the closing 'SWORN:' block. Fill placeholders with the "
    "case-specific facts provided; leave placeholders unfilled where facts are "
    "not supplied (do not invent).\n\n"
    "HARD BOUNDS:\n"
    "- Do NOT invent additional documents, steps, or affidavits.\n"
    "- Do NOT add or remove entries from any list.\n"
    "- Do NOT change affidavit 'type' values.\n"
    "- Do NOT change the 'ground' title.\n"
    "- Return STRICT JSON matching the shape of the input ground plan."
)


def _build_refinement_user_prompt(
    plan_for_ground: dict,
    ground: object,
    case_context: dict,
) -> str:
    return (
        f"CASE CONTEXT\n"
        f"- Defendant surname: {case_context.get('defendant_surname') or '[not provided]'}\n"
        f"- Jurisdiction: {case_context.get('jurisdiction') or '[not provided]'}\n"
        f"- Offence type: {case_context.get('offence_type') or '[not provided]'}\n"
        f"- Case summary: {(case_context.get('case_summary') or '')[:800]}\n"
        f"\nGROUND\n"
        f"- Title: {getattr(ground, 'title', '')}\n"
        f"- Type: {getattr(ground, 'type', '')}\n"
        f"- Authorities: {', '.join(getattr(ground, 'authorities', []) or []) or '[none]'}\n"
        f"- Law sections: {', '.join(getattr(ground, 'relevant_law_sections', []) or []) or '[none]'}\n"
        f"- Error identified: {(getattr(ground, 'error_identified', None) or '')[:400]}\n"
        f"- Trial finding: {(getattr(ground, 'trial_finding', None) or '')[:400]}\n"
        f"\nDETERMINISTIC EVIDENCE PLAN TO REFINE (JSON)\n"
        f"```json\n{_json_dump_compact(plan_for_ground)}\n```\n"
        f"\nTASK\n"
        f"Rewrite each string value so it references the defendant's surname, "
        f"the specific offence, and relevant statutory framing where natural. "
        f"Preserve list lengths and affidavit skeletons. Return the FULL JSON "
        f"with the same keys, same list counts, and same affidavit 'type' values."
    )


def _json_dump_compact(obj) -> str:
    import json
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def _validate_refined_shape(original: dict, refined: dict) -> bool:
    """
    Shape-preservation validator for a single ground's evidence plan.
    Ensures the LLM didn't add/remove keys, change types, change list
    lengths, or change affidavit types.
    """
    if not isinstance(refined, dict):
        return False
    if set(refined.keys()) != set(original.keys()):
        return False
    # ground title must stay a string
    if "ground" in original and not isinstance(refined.get("ground"), str):
        return False
    for list_key in ("documents_required", "steps"):
        if list_key in original:
            orig_list = original[list_key]
            ref_list = refined.get(list_key)
            if not isinstance(ref_list, list):
                return False
            if len(ref_list) != len(orig_list):
                return False
            if not all(isinstance(x, str) for x in ref_list):
                return False
    if "affidavits" in original:
        orig_affs = original["affidavits"] or []
        ref_affs = refined.get("affidavits") or []
        if not isinstance(ref_affs, list) or len(ref_affs) != len(orig_affs):
            return False
        for orig_a, ref_a in zip(orig_affs, ref_affs):
            if not isinstance(ref_a, dict):
                return False
            if set(ref_a.keys()) != set(orig_a.keys()):
                return False
            # 'type' must be unchanged
            if ref_a.get("type") != orig_a.get("type"):
                return False
            if not isinstance(ref_a.get("template"), str):
                return False
            # template must still contain the structural skeleton markers
            t = ref_a["template"]
            if "SWORN" not in t.upper():
                return False
    return True


async def _refine_single_plan(
    plan_for_ground: dict,
    ground: object,
    case_context: dict,
    session_id: str,
) -> dict:
    from services.llm_service import call_llm_for_json

    def _valid(parsed: dict) -> bool:
        return _validate_refined_shape(plan_for_ground, parsed)

    refined = await call_llm_for_json(
        system_prompt=_REFINEMENT_SYSTEM_PROMPT,
        user_prompt=_build_refinement_user_prompt(plan_for_ground, ground, case_context),
        session_id=session_id,
        task_type="general",
        validation_fn=_valid,
        max_tokens=1600,
        timeout_seconds=60,
    )
    # Overlay onto deterministic plan so any missing key stays as fallback.
    merged = dict(plan_for_ground)
    merged.update({k: v for k, v in refined.items() if k in plan_for_ground})
    return merged


async def refine_evidence_builder_with_llm(
    builder: dict,
    strategy: dict,
    case_context: dict,
    session_id: str = "evidence-builder-refine",
) -> dict:
    """
    Take a deterministic evidence builder produced by generate_evidence_builder()
    and refine each ground's wording (documents, steps, affidavit templates)
    using the LLM. The mandatory warning is preserved verbatim. Per-ground
    fallback to deterministic text on any LLM failure.
    """
    if not builder:
        return builder

    refined: dict = {}
    # Preserve warning verbatim — never LLM-touched.
    if "warning" in builder:
        refined["warning"] = builder["warning"]

    for role in ("primary", "secondary"):
        plan_for_ground = builder.get(role)
        ground = (strategy or {}).get(role)
        if not plan_for_ground or ground is None:
            if plan_for_ground is not None:
                refined[role] = plan_for_ground
            continue
        try:
            refined[role] = await _refine_single_plan(
                plan_for_ground, ground, case_context, session_id=f"{session_id}-{role}"
            )
        except Exception as refine_err:
            _log.warning(f"LLM evidence-builder refine skipped for {role}: {refine_err}")
            refined[role] = plan_for_ground
    return refined
