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
