# DO NOT UNDO — Barrister Tools router (Crown Response Simulator + Fresh
# Evidence Gallagher Wizard). Both endpoints are LLM-backed AI-assist tools
# that assume the caller is self-represented and produce EDUCATIONAL output.
# All output must pass the non-legal-advice disclaimer rendered on the client.
"""
Criminal Appeal AI — Barrister Tools Router
Added 2026-02-21 by owner. These endpoints bridge the gap between
"AI-generated grounds" and "submission-ready appellate argument":

  1. POST /api/cases/{case_id}/grounds/{ground_id}/crown-response
     Stress-tests a ground by generating the DPP's likely rebuttal with
     authorities + a weakness score (1-10) so the appellant can address
     the weakness BEFORE filing.

  2. POST /api/cases/{case_id}/fresh-evidence/evaluate
     Takes the user's Gallagher-factor inputs and returns a structured
     evaluation + auto-drafted submission paragraph applying:
       R v Gallagher (1986) 160 CLR 392
       Mickelberg v The Queen (1989) 167 CLR 259
       R v Lawless [1974] VR 398
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

from config import db
from auth_utils import get_current_user
from services.llm_service import call_llm_for_json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["barrister-tools"])


# ============================================================================
# CROWN RESPONSE SIMULATOR
# ============================================================================

_CROWN_SYSTEM_PROMPT = """You are a senior Crown Prosecutor with 25 years of
experience in Australian criminal appellate advocacy. You draft the Crown's
WRITTEN SUBMISSIONS IN REPLY for the Director of Public Prosecutions in
response to a criminal appeal ground advanced by the appellant.

Your output is the STRONGEST version of the Crown's argument — a genuine
stress-test to expose weakness BEFORE the appellant files. You do NOT coach
the appellant. You argue for dismissal.

STRICT LANGUAGE RULES (these are NON-NEGOTIABLE):
• Write in third person only — never use "we", "us", "our", "you", "your",
  "I", "my". Refer to parties as "the Crown", "the appellant", "the trial
  judge", "the Court".
• Use Australian forensic appellate English (analyse, judgement, offence).
• Cite authorities using AGLC4 (Australian Guide to Legal Citation) form:
  • Cases: R v Smith (2019) 97 NSWLR 812; R v Tran [2021] NSWCCA 156.
  • Statutes: Criminal Appeal Act 1912 (NSW) s 6.
• Every submission paragraph must end with a pinpoint reference or "[citation
  required]" — never leave an unsupported assertion.
• Do NOT hallucinate authorities. If uncertain, use "[citation required]".

You return ONE JSON object only (no markdown, no preamble)."""


class CrownResponseResult(BaseModel):
    model_config = {"extra": "ignore"}
    ground_id: str
    crown_rebuttal: str = Field(..., description="The Crown's written submission in reply — forensic English, third person, AGLC4 citations.")
    key_counter_authorities: List[str] = Field(default_factory=list, description="AGLC4-formatted authorities the Crown relies on.")
    weakness_score: int = Field(..., ge=1, le=10, description="1 = ground is very strong (Crown has little); 10 = ground is very weak (Crown will succeed).")
    weakness_reasons: List[str] = Field(default_factory=list, description="Specific weaknesses in the appellant's ground that the Crown will exploit.")
    strategic_response: str = Field(..., description="How the appellant should pre-emptively address these weaknesses in their own written submissions.")
    generated_at: str
    generated_by: str = "crown_response_simulator_v1"


def _validate_crown_json(obj: dict) -> bool:
    required = {"crown_rebuttal", "key_counter_authorities", "weakness_score",
                "weakness_reasons", "strategic_response"}
    if not required.issubset(obj.keys()):
        return False
    if not isinstance(obj["crown_rebuttal"], str) or len(obj["crown_rebuttal"].strip()) < 120:
        return False
    if not isinstance(obj["key_counter_authorities"], list):
        return False
    try:
        score = int(obj["weakness_score"])
    except (TypeError, ValueError):
        return False
    if score < 1 or score > 10:
        return False
    if not isinstance(obj["weakness_reasons"], list) or not obj["weakness_reasons"]:
        return False
    if not isinstance(obj["strategic_response"], str) or len(obj["strategic_response"].strip()) < 80:
        return False
    # Reject first-person slip-ups — the #1 way the forensic voice breaks.
    joined = (obj["crown_rebuttal"] + " " + obj["strategic_response"]).lower()
    for banned in (" we ", " us ", " our ", " you ", " your ", " i ", " my "):
        if banned in f" {joined} ":
            return False
    return True


@router.post("/cases/{case_id}/grounds/{ground_id}/crown-response", response_model=dict)
async def generate_crown_response(case_id: str, ground_id: str, request: Request):
    """Generate the DPP's likely reply to a specific ground of merit."""
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground not found")

    jur = (case.get("state") or "NSW").upper()
    offence = case.get("offence_type") or "criminal offence"
    court = case.get("court") or "the trial court"

    user_prompt = (
        f"Jurisdiction: {jur}\n"
        f"Court below: {court}\n"
        f"Offence: {offence}\n"
        f"Appellant ground of appeal:\n"
        f"  Title: {ground.get('title', '')}\n"
        f"  Type: {ground.get('ground_type', '')}\n"
        f"  Strength (self-assessed): {ground.get('strength', 'moderate')}\n"
        f"  Description: {ground.get('description', '')}\n"
        f"  Supporting points: {ground.get('supporting_evidence', '')}\n"
        f"  Legal basis: {ground.get('legal_basis', '')}\n\n"
        f"TASK — produce the Crown's written submissions in reply to this\n"
        f"single ground. Return JSON with these keys ONLY:\n"
        f"  crown_rebuttal: string (3-6 paragraphs, forensic third-person,\n"
        f"    ends each paragraph with AGLC4 pinpoint or [citation required])\n"
        f"  key_counter_authorities: list of AGLC4 citations (5-8 items)\n"
        f"  weakness_score: integer 1-10\n"
        f"  weakness_reasons: list of 3-5 short strings\n"
        f"  strategic_response: 1-2 paragraphs suggesting how the appellant\n"
        f"    should pre-emptively address these weaknesses in their own\n"
        f"    submissions (still third person — refer to 'the appellant')"
    )

    session_id = f"crown_response:{case_id}:{ground_id}"
    try:
        parsed = await call_llm_for_json(
            system_prompt=_CROWN_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            session_id=session_id,
            task_type="forensic_analysis",
            validation_fn=_validate_crown_json,
            max_tokens=2800,
            timeout_seconds=120,
        )
    except Exception as exc:
        logger.warning("Crown response generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="AI stress-test failed. The response did not meet forensic quality standards; try again in a moment.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    result = {
        "crown_response_id": f"crr_{uuid.uuid4().hex[:12]}",
        "case_id": case_id,
        "ground_id": ground_id,
        "user_id": user.user_id,
        "crown_rebuttal": parsed["crown_rebuttal"].strip(),
        "key_counter_authorities": [str(c).strip() for c in parsed["key_counter_authorities"] if str(c).strip()],
        "weakness_score": int(parsed["weakness_score"]),
        "weakness_reasons": [str(r).strip() for r in parsed["weakness_reasons"] if str(r).strip()],
        "strategic_response": parsed["strategic_response"].strip(),
        "generated_at": now_iso,
        "generated_by": "crown_response_simulator_v1",
    }
    # Persist; allow re-generation by replacing the previous run for this ground.
    await db.crown_responses.delete_many(
        {"case_id": case_id, "ground_id": ground_id, "user_id": user.user_id}
    )
    await db.crown_responses.insert_one(result.copy())
    result.pop("_id", None)
    return result


@router.get("/cases/{case_id}/grounds/{ground_id}/crown-response", response_model=Optional[dict])
async def get_crown_response(case_id: str, ground_id: str, request: Request):
    """Retrieve the previously-generated Crown response for this ground, if any."""
    user = await get_current_user(request)
    result = await db.crown_responses.find_one(
        {"case_id": case_id, "ground_id": ground_id, "user_id": user.user_id},
        {"_id": 0},
    )
    return result  # None is a valid response → UI shows "not generated yet"


# ============================================================================
# FRESH EVIDENCE (GALLAGHER) WIZARD
# ============================================================================

class FreshEvidenceInput(BaseModel):
    model_config = {"extra": "ignore"}
    evidence_description: str = Field(..., min_length=30, description="Nature of the fresh evidence and what it proves.")
    reason_for_delay: str = Field(..., min_length=30, description="Why this evidence was not before the trial court (due diligence analysis).")
    materiality: str = Field(..., min_length=30, description="How the evidence would have affected the verdict or sentence.")
    credibility_basis: str = Field("", description="Why the evidence is credible / reliable (source, corroboration).")
    source_type: str = Field("affidavit", description="affidavit | document | forensic_report | witness_statement | expert_report | other")


_FRESH_EV_SYSTEM_PROMPT = """You are a senior criminal appellate barrister
specialising in fresh-evidence applications under the proviso and inherent
powers of Australian appellate courts. You apply the following authorities
strictly:

  • R v Gallagher (1986) 160 CLR 392 — the four-factor test
  • Mickelberg v The Queen (1989) 167 CLR 259 — materiality
  • R v Lawless [1974] VR 398 — credibility threshold
  • Ratten v The Queen (1974) 131 CLR 510 — "miscarriage of justice"

Your task is to EVALUATE the appellant's proposed fresh evidence against the
Gallagher factors and DRAFT the submission paragraph for inclusion in written
submissions.

STRICT LANGUAGE RULES:
• Third person only — NEVER "we", "us", "our", "you", "your", "I", "my".
  Refer to parties as "the appellant", "the Crown", "this Honourable Court".
• Australian forensic appellate English.
• AGLC4 citations throughout.
• Do NOT hallucinate authorities. If unsure, say "[authority required]".

Return ONE JSON object only (no markdown)."""


def _validate_fresh_evidence_json(obj: dict) -> bool:
    required = {"gallagher_assessment", "admissibility_likelihood",
                "submission_paragraph", "recommended_authorities",
                "practical_next_steps"}
    if not required.issubset(obj.keys()):
        return False
    if not isinstance(obj["gallagher_assessment"], dict):
        return False
    factors = {"new", "reasonable_diligence", "credible", "material"}
    if not factors.issubset(obj["gallagher_assessment"].keys()):
        return False
    for factor_key in factors:
        entry = obj["gallagher_assessment"][factor_key]
        if not isinstance(entry, dict):
            return False
        if not isinstance(entry.get("status"), str) or entry["status"] not in (
            "satisfied", "not_satisfied", "uncertain"
        ):
            return False
        if not isinstance(entry.get("reasoning"), str) or len(entry["reasoning"].strip()) < 40:
            return False
    if obj["admissibility_likelihood"] not in ("low", "moderate", "high"):
        return False
    if not isinstance(obj["submission_paragraph"], str) or len(obj["submission_paragraph"].strip()) < 200:
        return False
    if not isinstance(obj["recommended_authorities"], list) or len(obj["recommended_authorities"]) < 3:
        return False
    if not isinstance(obj["practical_next_steps"], list) or not obj["practical_next_steps"]:
        return False
    text = (obj["submission_paragraph"]).lower()
    for banned in (" we ", " us ", " our ", " you ", " your ", " i ", " my "):
        if banned in f" {text} ":
            return False
    return True


@router.post("/cases/{case_id}/fresh-evidence/evaluate", response_model=dict)
async def evaluate_fresh_evidence(case_id: str, payload: FreshEvidenceInput, request: Request):
    """Apply Gallagher factors to the proposed fresh evidence and draft the
    submission paragraph. Persists to fresh_evidence_applications collection."""
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    jur = (case.get("state") or "NSW").upper()
    court = case.get("court") or "the trial court"

    user_prompt = (
        f"Jurisdiction: {jur}\n"
        f"Court below: {court}\n"
        f"Offence: {case.get('offence_type') or 'unspecified'}\n"
        f"Appellant: {case.get('defendant_name') or 'the appellant'}\n\n"
        f"PROPOSED FRESH EVIDENCE\n"
        f"Source type: {payload.source_type}\n"
        f"Description: {payload.evidence_description}\n\n"
        f"Reason evidence was not before the trial court (due diligence):\n"
        f"{payload.reason_for_delay}\n\n"
        f"Materiality (how it would have affected verdict/sentence):\n"
        f"{payload.materiality}\n\n"
        f"Credibility basis: {payload.credibility_basis or '(not supplied)'}\n\n"
        f"TASK — return JSON with keys ONLY:\n"
        f"  gallagher_assessment: object with four keys 'new',\n"
        f"    'reasonable_diligence', 'credible', 'material'. Each value is\n"
        f"    an object with 'status' (satisfied | not_satisfied | uncertain)\n"
        f"    and 'reasoning' (3-4 sentences referencing the facts).\n"
        f"  admissibility_likelihood: 'low' | 'moderate' | 'high'\n"
        f"  submission_paragraph: one continuous submission paragraph of\n"
        f"    250-450 words, ready for insertion into written submissions,\n"
        f"    citing R v Gallagher (1986) 160 CLR 392 and any other relevant\n"
        f"    authority with AGLC4 pinpoints. Third person throughout.\n"
        f"  recommended_authorities: list of 4-6 AGLC4 citations\n"
        f"  practical_next_steps: list of 4-6 concise action items\n"
        f"    (e.g. 'obtain signed affidavit from witness X', 'lodge\n"
        f"    application under s 12 Criminal Appeal Act 1912 (NSW)')."
    )

    session_id = f"fresh_evidence:{case_id}"
    try:
        parsed = await call_llm_for_json(
            system_prompt=_FRESH_EV_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            session_id=session_id,
            task_type="forensic_analysis",
            validation_fn=_validate_fresh_evidence_json,
            max_tokens=3200,
            timeout_seconds=120,
        )
    except Exception as exc:
        logger.warning("Fresh-evidence evaluation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="AI evaluation failed quality checks. Please refine the inputs (each field needs 30+ characters) and try again.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    record = {
        "application_id": f"fea_{uuid.uuid4().hex[:12]}",
        "case_id": case_id,
        "user_id": user.user_id,
        "inputs": payload.model_dump(),
        "gallagher_assessment": parsed["gallagher_assessment"],
        "admissibility_likelihood": parsed["admissibility_likelihood"],
        "submission_paragraph": parsed["submission_paragraph"].strip(),
        "recommended_authorities": [str(a).strip() for a in parsed["recommended_authorities"] if str(a).strip()],
        "practical_next_steps": [str(s).strip() for s in parsed["practical_next_steps"] if str(s).strip()],
        "generated_at": now_iso,
        "generated_by": "fresh_evidence_gallagher_v1",
    }
    await db.fresh_evidence_applications.insert_one(record.copy())
    record.pop("_id", None)
    return record


@router.get("/cases/{case_id}/fresh-evidence", response_model=List[dict])
async def list_fresh_evidence(case_id: str, request: Request):
    """List all fresh-evidence applications the user has generated for this case."""
    user = await get_current_user(request)
    items = await db.fresh_evidence_applications.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).sort("generated_at", -1).to_list(50)
    return items
