"""
attack_plan.py

Generates counsel-style attack plan for each strategic ground.

For each selected ground (PRIMARY + SECONDARY), produces:
  - Attack Strategy     (how to run the ground)
  - Evidence Gaps       (what is missing)
  - Required Material   (what must be obtained)
  - Crown Response      (what will be said against you)
  - Counter Strategy    (how to defeat Crown)
  - Next Steps          (practical actions)

This is exactly what happens in a barrister conference — turned into a
deterministic, reproducible data structure that the report renderer can
show counsel in the exported PDF/Print bundle.

Counsel feedback 23 Feb 2026 — exact logic supplied by counsel.
"""

from __future__ import annotations

from services.ground_normaliser import Ground


def build_attack_strategy(ground: Ground) -> str:
    text = (ground.error_identified or "").lower()

    if ground.type == "conviction":
        if "mens rea" in text or "mental" in text:
            return (
                "Focus the argument on the failure to properly determine the mental element. "
                "Emphasise competing psychiatric evidence and argue that the jury could not "
                "have excluded a reasonable hypothesis inconsistent with intent."
            )
        return (
            "Attack the safety of the verdict by demonstrating that the evidence does not "
            "support the conclusion beyond reasonable doubt."
        )

    if ground.type == "procedure":
        return (
            "Frame the argument as a denial of procedural fairness affecting the integrity "
            "of the trial. Emphasise that justice must be seen to be done."
        )

    if ground.type == "sentence":
        return (
            "Demonstrate that the sentencing discretion miscarried by reference to established "
            "principles and comparable authorities."
        )

    return "Ground requires tailored strategy."


def identify_evidence_gaps(ground: Ground) -> list[str]:
    gaps: list[str] = []

    if ground.record_support == "limited":
        gaps.append("Limited transcript or documentary support.")

    if ground.type == "conviction" and "mental" in (ground.error_identified or "").lower():
        gaps.append("Absence of comprehensive psychiatric reports.")

    if ground.type == "procedure" and ground.crown_strength == "strong":
        gaps.append("Lack of direct evidence of prejudice or bias.")

    return gaps


def required_materials(ground: Ground) -> list[str]:
    materials: list[str] = []

    if ground.type == "conviction":
        materials.append("Full trial transcript")
        if "mental" in (ground.error_identified or "").lower():
            materials.append("Expert psychiatric reports")
            materials.append("Affidavit from defence expert")

    if ground.type == "procedure":
        materials.append("Trial transcript (directions and rulings)")
        materials.append("Affidavit evidence of juror conduct (if applicable)")

    if ground.type == "sentence":
        materials.append("Sentencing remarks")
        materials.append("Comparable sentencing authorities")

    return materials


def anticipate_crown_response(ground: Ground) -> str:
    if ground.crown_strength == "strong":
        return (
            "The Crown will argue that the evidence against the accused was overwhelming "
            "and that any error did not affect the outcome."
        )

    if ground.crown_strength == "moderate":
        return (
            "The Crown will argue that the jury was entitled to prefer its evidence "
            "and that no miscarriage of justice occurred."
        )

    return (
        "The Crown response is likely to focus on reinforcing the trial findings."
    )


def counter_strategy(ground: Ground) -> str:
    if getattr(ground, "proviso_risk", "") == "high":
        return (
            "Counter the proviso by demonstrating that the error went to a central issue "
            "and that the verdict was not inevitable."
        )

    return (
        "Emphasise that the identified error affected a critical aspect of the case and "
        "undermines confidence in the verdict."
    )


def next_steps(ground: Ground) -> list[str]:
    steps: list[str] = []

    steps.append("Obtain full case record")

    if ground.type == "conviction":
        steps.append("Review jury directions on intent")
        steps.append("Compare competing expert evidence")

    if ground.type == "procedure":
        steps.append("Identify any objections raised at trial")
        steps.append("Locate supporting affidavits")

    if ground.type == "sentence":
        steps.append("Analyse sentencing remarks against comparable cases")

    return steps


def build_attack_plan_for_ground(ground: Ground) -> dict:
    return {
        "title": ground.title,
        "strategy": build_attack_strategy(ground),
        "evidence_gaps": identify_evidence_gaps(ground),
        "required_material": required_materials(ground),
        "crown_response": anticipate_crown_response(ground),
        "counter_strategy": counter_strategy(ground),
        "next_steps": next_steps(ground),
    }


def generate_attack_plan(strategy: dict) -> dict:
    plan: dict = {}

    if strategy.get("primary"):
        plan["primary"] = build_attack_plan_for_ground(strategy["primary"])

    if strategy.get("secondary"):
        plan["secondary"] = build_attack_plan_for_ground(strategy["secondary"])

    return plan


# ---------------------------------------------------------------------------
# LLM refinement layer — counsel feedback 23 Feb 2026.
# ---------------------------------------------------------------------------
# The deterministic plan above gives the correct STRUCTURE. The LLM pass
# refines WORDING so it reads like counsel's own brief: case-specific
# facts, defendant name, specific authorities, jurisdictional framing.
# The LLM is explicitly bounded — it may not invent new grounds, add new
# sub-particulars, re-rate viability, or change the ground type.
# ---------------------------------------------------------------------------

import logging  # noqa: E402 — grouped with LLM helpers

_log = logging.getLogger(__name__)

_REFINEMENT_SYSTEM_PROMPT = (
    "You are a senior junior counsel drafting a strictly forensic, third-person "
    "appellate brief under Australian practice. Australian spelling only "
    "(analyse, organise, judgement, offence). "
    "\n\nIMPORTANT STYLE RULES:\n"
    "- Third-person only. NEVER use 'we', 'us', 'our', 'you', 'your'.\n"
    "- Forensic appellate register. No marketing language. No hedging adjectives.\n"
    "- Reference authorities by full citation (e.g. 'House v The King (1936) 55 CLR "
    "499') when naturally relevant; do NOT invent authorities.\n"
    "- Reference the defendant by surname where used (passed in user prompt).\n"
    "- Keep each refined field to the SAME TYPE AND APPROXIMATE LENGTH as the "
    "deterministic input. One-paragraph fields stay one paragraph; lists stay "
    "lists of the same count or fewer.\n"
    "\nHARD BOUNDS:\n"
    "- Do NOT invent new grounds, new sub-particulars, or new legal issues.\n"
    "- Do NOT change the ground type or viability rating.\n"
    "- Do NOT add fields not present in the input plan.\n"
    "- Refine WORDING only; every refined value must remain a direct rewording "
    "of the deterministic input.\n"
    "\nReturn STRICT JSON matching the shape of the input plan."
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
        f"- Viability: {getattr(ground, 'viability', '')}\n"
        f"- Proviso risk: {getattr(ground, 'proviso_risk', '')}\n"
        f"- Authorities: {', '.join(getattr(ground, 'authorities', []) or []) or '[none]'}\n"
        f"- Law sections: {', '.join(getattr(ground, 'relevant_law_sections', []) or []) or '[none]'}\n"
        f"- Trial finding: {(getattr(ground, 'trial_finding', None) or '')[:400]}\n"
        f"- Error identified: {(getattr(ground, 'error_identified', None) or '')[:400]}\n"
        f"- Materiality: {(getattr(ground, 'materiality', None) or '')[:400]}\n"
        f"\nDETERMINISTIC ATTACK PLAN TO REFINE (JSON)\n"
        f"```json\n{_json_dump_compact(plan_for_ground)}\n```\n"
        f"\nTASK\n"
        f"Rewrite each string value in the plan so it reads like a real counsel "
        f"brief. Inject jurisdictional framing, authorities, and defendant surname "
        f"where natural. Keep list lengths the same or fewer. Return the FULL JSON "
        f"with the same keys and list/string shapes."
    )


def _json_dump_compact(obj) -> str:
    import json
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


_REQUIRED_STRING_KEYS = {"title", "strategy", "crown_response", "counter_strategy"}
_REQUIRED_LIST_KEYS = {"evidence_gaps", "required_material", "next_steps"}


def _validate_refined_shape(original: dict, refined: dict) -> bool:
    """Ensure the LLM didn't add keys, drop required ones, or change types."""
    if not isinstance(refined, dict):
        return False
    # Allowed keys = whatever was in the original. No adds.
    if not set(refined.keys()).issubset(set(original.keys())):
        return False
    for k in _REQUIRED_STRING_KEYS:
        if k in original and not isinstance(refined.get(k, ""), str):
            return False
    for k in _REQUIRED_LIST_KEYS:
        if k in original:
            if not isinstance(refined.get(k, []), list):
                return False
            if not all(isinstance(x, str) for x in refined[k]):
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
        # call_llm_for_json expects validation at the top-level dict.
        return _validate_refined_shape(plan_for_ground, parsed)

    refined = await call_llm_for_json(
        system_prompt=_REFINEMENT_SYSTEM_PROMPT,
        user_prompt=_build_refinement_user_prompt(plan_for_ground, ground, case_context),
        session_id=session_id,
        task_type="general",
        validation_fn=_valid,
        max_tokens=1200,
        timeout_seconds=45,
    )
    # Belt-and-braces: overlay refined onto original so any missing key stays
    # as the deterministic fallback rather than silently disappearing.
    merged = dict(plan_for_ground)
    merged.update({k: v for k, v in refined.items() if k in plan_for_ground})
    return merged


async def refine_attack_plan_with_llm(
    plan: dict,
    strategy: dict,
    case_context: dict,
    session_id: str = "attack-plan-refine",
) -> dict:
    """
    Take a deterministic attack plan produced by generate_attack_plan() and
    refine its wording using the LLM, one ground at a time.
    On any per-ground failure, fall back to the deterministic text for that
    ground so the feature is fully non-blocking.
    """
    if not plan:
        return plan

    refined: dict = {}
    for role in ("primary", "secondary"):
        plan_for_ground = plan.get(role)
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
            _log.warning(f"LLM refine skipped for {role} ground: {refine_err}")
            refined[role] = plan_for_ground
    return refined
