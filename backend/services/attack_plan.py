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
