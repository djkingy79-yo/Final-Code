# DO NOT UNDO — grounds router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Grounds of Merit Router
ADDITIVE HARDENING PATCH
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import asyncio
import uuid
import json
import logging

from config import db, is_admin_user
from auth_utils import get_current_user
from services.offence_helpers import get_offence_context, enforce_forensic_language
from models import (
    GroundOfMerit,
    GroundOfMeritCreate,
    GroundOfMeritUpdate,
    FEATURE_PRICES,
    feature_type_variants,
    canonical_feature_type,
    EvidenceItem,
    LawSection,
    SimilarCase,
)
from services.llm_service import call_llm_with_fallback
from services.legitimacy_engine import calculate_ground_rating
from services.pipeline import (
    extract_document_artifacts,
    classify_case_issues,
    verify_issue,
)
from services.pipeline_models import CaseExtract


def _safe_isoformat(d, key):
    """Safely convert a datetime field to isoformat string. Handles missing keys and non-datetime values."""
    if key not in d:
        d[key] = datetime.now(timezone.utc).isoformat()
    elif hasattr(d[key], "isoformat"):
        d[key] = d[key].isoformat()
    # else: already a string or other type — leave as is

logger = logging.getLogger(__name__)


GROUND_TYPES = [
    "procedural_error", "fresh_evidence", "miscarriage_of_justice",
    "sentencing_error", "judicial_error", "ineffective_counsel",
    "prosecution_misconduct", "jury_irregularity", "constitutional_violation", "other"
]

router = APIRouter(prefix="/api", tags=["grounds"])


# ============================================================================
# ADDITIVE COMPATIBILITY HELPERS
# ============================================================================

def _normalise_ground_type(value: str) -> str:
    v = (value or "other").strip().lower()
    return v if v in GROUND_TYPES else "other"


def _wrap_evidence_items(raw_items):
    wrapped = []
    for item in raw_items or []:
        try:
            if isinstance(item, EvidenceItem):
                wrapped.append(item)
            elif isinstance(item, dict):
                wrapped.append(EvidenceItem(**item))
            else:
                wrapped.append(EvidenceItem(quote=str(item)))
        except Exception:
            wrapped.append(EvidenceItem(quote=str(item)))
    return wrapped


def _wrap_law_sections(raw_items):
    wrapped = []
    for item in raw_items or []:
        try:
            if isinstance(item, LawSection):
                wrapped.append(item)
            elif isinstance(item, dict):
                wrapped.append(LawSection(
                    act=item.get("act", ""),
                    section=item.get("section", ""),
                    jurisdiction=item.get("jurisdiction"),
                    title=item.get("title"),
                    verification_status=item.get("verification_status", "unverified"),
                ))
        except Exception:
            continue
    return wrapped


def _wrap_similar_cases(raw_items):
    wrapped = []
    for item in raw_items or []:
        try:
            if isinstance(item, SimilarCase):
                wrapped.append(item)
            elif isinstance(item, dict):
                wrapped.append(SimilarCase(
                    case_name=item.get("case_name", ""),
                    citation=item.get("citation"),
                    jurisdiction=item.get("jurisdiction"),
                    relevance_note=item.get("relevance_note"),
                    verification_status=item.get("verification_status", "unverified"),
                ))
        except Exception:
            continue
    return wrapped


def _legacy_evidence_dump(evidence_items):
    dumped = []
    for item in evidence_items or []:
        if isinstance(item, EvidenceItem):
            dumped.append(item.model_dump())
        elif isinstance(item, dict):
            dumped.append(item)
        else:
            dumped.append(EvidenceItem(quote=str(item)).model_dump())
    return dumped


def _law_sections_dump(items):
    return [item.model_dump() if isinstance(item, LawSection) else item for item in (items or [])]


def _similar_cases_dump(items):
    return [item.model_dump() if isinstance(item, SimilarCase) else item for item in (items or [])]


# ============================================================================
# PIPELINE DELEGATION HELPERS
# ============================================================================

async def _ensure_document_extracts(case: dict, documents: list):
    """Ensure every uploaded document has a staged extraction record. Additive only.
    Uses concurrent processing (max 3 at a time) to reduce wall-clock time for large cases.
    """
    # Filter to only documents needing extraction
    docs_to_process = []
    for document in documents:
        existing = await db.document_extracts.find_one(
            {"case_id": case["case_id"], "document_id": document["document_id"], "user_id": case["user_id"]},
            {"_id": 0}
        )
        if not existing:
            docs_to_process.append(document)

    if not docs_to_process:
        return 0

    semaphore = asyncio.Semaphore(3)
    created_count = 0
    errors = []

    async def process_one(document):
        nonlocal created_count
        async with semaphore:
            try:
                extract = await extract_document_artifacts(case, document)
                extract_dict = extract.model_dump()
                _safe_isoformat(extract_dict, "created_at")
                await db.document_extracts.update_one(
                    {"case_id": case["case_id"], "document_id": document["document_id"], "user_id": case["user_id"]},
                    {"$set": extract_dict},
                    upsert=True,
                )
                created_count += 1
            except Exception as e:
                logger.error(f"Document extract failed for {document.get('document_id')}: {e}")
                errors.append(str(e))

    await asyncio.gather(*[process_one(doc) for doc in docs_to_process])

    if errors and created_count == 0:
        raise Exception(f"All document extractions failed: {errors[0]}")

    return created_count


async def _refresh_case_extract_from_pipeline(case: dict) -> dict:
    """Merge all document extracts into a case-level extract."""
    extracts = await db.document_extracts.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
    ).to_list(500)
    merged_facts, merged_events, merged_findings, extract_ids = [], [], [], []
    for ext in extracts:
        extract_ids.append(ext.get("extract_id"))
        merged_facts.extend(ext.get("facts", []))
        merged_events.extend(ext.get("events", []))
        merged_findings.extend(ext.get("findings", []))
    case_extract = CaseExtract(
        case_id=case["case_id"],
        user_id=case["user_id"],
        metadata={
            "state": case.get("state"),
            "offence_category": case.get("offence_category"),
            "offence_type": case.get("offence_type"),
            "sentence": case.get("sentence"),
            "court": case.get("court"),
            "classification_source": case.get("classification_source", "existing"),
        },
        merged_facts=merged_facts,
        merged_events=merged_events,
        merged_findings=merged_findings,
        document_extract_ids=extract_ids,
    )
    case_extract_dict = case_extract.model_dump()
    _safe_isoformat(case_extract_dict, "created_at")
    await db.case_extracts.update_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"$set": case_extract_dict},
        upsert=True,
    )
    return case_extract_dict


async def _classify_pipeline_issues(case: dict, case_extract: dict) -> list[dict]:
    """Run staged issue classification and persist results.

    DO_NOT_UNDO — 3 Apr 2026: If issues already exist, DO NOT re-classify.
    Re-classification generates new LLM titles that slip past dedup and multiply grounds.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    existing_issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)

    if len(existing_issues) >= 8:
        logger.info(f"Skipping re-classification for case {case['case_id']}: {len(existing_issues)} issues already exist (>= 8)")
        return existing_issues

    logger.info(f"Re-classifying case {case['case_id']}: only {len(existing_issues)} issues exist (< 8), looking for more")
    issues = await classify_case_issues(case, case_extract)

    persisted = []
    for issue in issues:
        issue_dict = issue.model_dump()
        _safe_isoformat(issue_dict, "created_at")
        issue_title = normalise_au_spelling((issue.title or "").strip())
        issue_dict["title"] = issue_title

        matched = None
        for ei in persisted:
            ei_title = (ei.get("title") or "").strip()
            if is_ground_duplicate(issue_title, ei_title):
                matched = ei
                break

        if matched:
            await db.issue_classifications.update_one(
                {"issue_id": matched["issue_id"]},
                {"$set": issue_dict},
            )
            saved = await db.issue_classifications.find_one(
                {"issue_id": matched["issue_id"]}, {"_id": 0}
            )
        else:
            await db.issue_classifications.update_one(
                {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue_title, "ground_type": issue.ground_type},
                {"$set": issue_dict},
                upsert=True,
            )
            saved = await db.issue_classifications.find_one(
                {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue_title, "ground_type": issue.ground_type},
                {"_id": 0}
            )

        if saved:
            persisted.append(saved)
    return persisted


async def _sync_pipeline_issues_to_grounds(case_id: str, user_id: str) -> int:
    """Project pipeline issues + verifications into existing grounds_of_merit collection.

    DO_NOT_UNDO — MUST use fuzzy dedup via is_ground_duplicate(). NEVER revert to exact-title
    upsert. Exact-title upsert was the ROOT CAUSE of grounds multiplying from 4 to 27+.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    ).to_list(500)

    # DO_NOT_UNDO — Jurisdiction-aware ground normalisation.
    # Lawyer feedback: app was misclassifying conviction grounds as sentencing
    # and defaulting to NSW pathway regardless of case jurisdiction. The
    # normaliser below:
    #   - splits mixed grounds (e.g. a parent ground with conviction + sentence
    #     sub-particulars becomes two distinct grounds)
    #   - re-classifies each ground from its content using the case's actual
    #     jurisdiction (NSW / VIC / QLD / SA / WA / TAS / NT / ACT / CTH)
    #   - computes the correct appellate pathway for that jurisdiction
    #   - de-duplicates grounds that reduce to the same canonical issue
    #   - caps viability when corroborating evidence is missing
    # See /app/backend/services/ground_normaliser.py and jurisdiction_rules.py.
    case_doc = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    case_jurisdiction = str(
        (case_doc or {}).get("jurisdiction") or (case_doc or {}).get("state") or "NSW"
    ).upper().strip()
    if case_jurisdiction == "FEDERAL":
        case_jurisdiction = "CTH"

    # Outcome prediction — computed after normalisation/cleanup runs. Default
    # to None so the persist block still works even if normalisation fails.
    predicted_outcome = None
    attack_plan = None
    evidence_builder = None

    try:
        from services.ground_normaliser import (
            EvidenceFlags,
            Ground,
            normalise_generated_grounds,
        )

        raw_grounds: list[Ground] = []
        for issue in issues:
            gtype = (issue.get("ground_type") or "").lower().strip()
            if gtype not in ("conviction", "sentence", "procedure", "evidence", "ineffective_counsel"):
                gtype = None  # normaliser will classify from content
            raw_grounds.append(
                Ground(
                    title=issue.get("title", ""),
                    type=gtype,
                    pathway=issue.get("appellate_pathway", ""),
                    viability="requires_development",
                    supporting_evidence=[],
                    relevant_law_sections=[],
                    authorities=[],
                    trial_finding=issue.get("trial_finding"),
                    error_identified=issue.get("error_identified"),
                    materiality=issue.get("materiality"),
                    consequence=issue.get("consequence"),
                )
            )

        flags = EvidenceFlags()  # corroborating evidence flags default False; detailed case flags evaluated downstream during verification

        normalised_grounds = normalise_generated_grounds(
            raw_grounds=raw_grounds,
            flags=flags,
            jurisdiction=case_jurisdiction,
        )

        # Realism scoring — post-normalisation. Attaches record_support,
        # verdict_robustness, crown_strength, and failure_risk to each ground,
        # and caps viability where the record or prosecution case is strong.
        try:
            from services.appeal_strength import (
                CaseEvidenceProfile,
                score_grounds_for_realism,
            )
            # Evidence profile — pull from case_doc if the main agent has
            # populated it on the case record; otherwise safe defaults (all False)
            # which gives conservative realism assessments.
            cx = case_doc or {}
            profile = CaseEvidenceProfile(
                has_trial_transcript=bool(cx.get("has_trial_transcript")),
                has_sentencing_remarks=bool(cx.get("has_sentencing_remarks")),
                has_psychiatric_reports=bool(cx.get("has_psychiatric_reports")),
                has_counsel_affidavit=bool(cx.get("has_counsel_affidavit")),
                has_juror_affidavit=bool(cx.get("has_juror_affidavit")),
                has_expert_reports=bool(cx.get("has_expert_reports")),
                has_judge_alone_material=bool(cx.get("has_judge_alone_material")),
                has_pretrial_publicity_material=bool(cx.get("has_pretrial_publicity_material")),
                has_forensic_evidence=bool(cx.get("has_forensic_evidence")),
                has_direct_evidence=bool(cx.get("has_direct_evidence")),
                has_strong_circumstantial_evidence=bool(cx.get("has_strong_circumstantial_evidence")),
                multiple_consistent_witnesses=bool(cx.get("multiple_consistent_witnesses")),
                confession_or_admission=bool(cx.get("confession_or_admission")),
                cctv_or_audio=bool(cx.get("cctv_or_audio")),
                post_offence_conduct_supports_guilt=bool(cx.get("post_offence_conduct_supports_guilt")),
                disputed_identity=bool(cx.get("disputed_identity")),
                disputed_intent=bool(cx.get("disputed_intent")),
                competing_psychiatric_opinions=bool(cx.get("competing_psychiatric_opinions")),
                no_eyewitnesses=bool(cx.get("no_eyewitnesses")),
            )
            normalised_grounds = score_grounds_for_realism(normalised_grounds, profile)

            # Final cleanup — counsel feedback 23 Feb 2026. Runs AFTER realism
            # scoring so it can use record_support / verdict_robustness /
            # crown_strength to uplift grounds that were over-downgraded, and
            # scrub misclassified sub-particulars that survived the splitter.
            from services.ground_cleanup import apply_cleanup
            normalised_grounds = apply_cleanup(normalised_grounds, case_jurisdiction)
        except Exception as realism_err:
            logger.warning(f"Realism scoring skipped for case {case_id}: {realism_err}")

        # Rebuild `issues` list preserving per-issue metadata (issue_id,
        # description, timestamps) but replacing type + pathway with the
        # normaliser's verdict, and splitting any issue that produced > 1
        # normalised ground.
        normalised_by_title = {}
        for ng in normalised_grounds:
            normalised_by_title.setdefault(ng.title, ng)

        rewritten_issues: list[dict] = []
        for issue in issues:
            original_title = issue.get("title", "")
            # Find all normalised grounds whose title matches OR whose content
            # derives from this issue (the normaliser may rename the title).
            match = normalised_by_title.get(original_title)
            if match is None:
                # Titles were rewritten during splitting — re-classify this issue
                # using the normaliser and take its first output.
                from services.ground_normaliser import classify_text
                gt = classify_text(
                    " ".join([
                        original_title,
                        issue.get("description", ""),
                        issue.get("error_identified", ""),
                    ]),
                    case_jurisdiction,
                )
                from services.jurisdiction_rules import infer_pathway
                new_issue = dict(issue)
                new_issue["ground_type"] = gt
                new_issue["appellate_pathway"] = infer_pathway(case_jurisdiction, gt)
                rewritten_issues.append(new_issue)
            else:
                new_issue = dict(issue)
                new_issue["ground_type"] = match.type or issue.get("ground_type", "other")
                new_issue["appellate_pathway"] = match.pathway or issue.get("appellate_pathway", "")
                new_issue["title"] = match.title or original_title
                new_issue["record_support"] = match.record_support
                new_issue["verdict_robustness"] = match.verdict_robustness
                new_issue["crown_strength"] = match.crown_strength
                new_issue["failure_risk"] = match.failure_risk
                new_issue["proviso_risk"] = getattr(match, "proviso_risk", None)
                new_issue["reasoning_trail"] = match.reasoning_trail or []
                rewritten_issues.append(new_issue)
        issues = rewritten_issues

        # Counsel feedback 23 Feb 2026 — Issue 7 improvement. Predict the
        # likely appellate outcome based on the primary/secondary ground
        # selection + proviso risk, and surface it on the case payload so
        # the Barrister Brief and cover page show aligned projections.
        try:
            from services.outcome_predictor import select_strategy, predict_outcome
            from services.attack_plan import generate_attack_plan
            from services.evidence_builder import generate_evidence_builder
            strategy = select_strategy(normalised_grounds)
            predicted_outcome = predict_outcome(strategy)
            # Counsel feedback 23 Feb 2026 — attack plan + evidence builder.
            # Produce deterministic counsel-conference output so the exported
            # report can show strategy / evidence gaps / required material /
            # Crown response / counter strategy / next steps for primary +
            # secondary grounds, plus affidavit templates.
            attack_plan = generate_attack_plan(strategy)
            evidence_builder = generate_evidence_builder(strategy)

            # LLM refinement pass — counsel feedback 23 Feb 2026. Rewrites
            # the deterministic attack-plan wording to sound like counsel's
            # own brief (case facts, defendant surname, authorities,
            # jurisdictional framing). Bounded — cannot invent grounds, add
            # keys, or change viability. Falls back to the deterministic
            # plan per-ground on any LLM failure so this is fully optional.
            try:
                from services.attack_plan import refine_attack_plan_with_llm
                defendant = ((case_doc or {}).get("defendant_name") or "").strip()
                defendant_surname = defendant.split()[-1] if defendant else ""
                case_context = {
                    "defendant_surname": defendant_surname,
                    "jurisdiction": case_jurisdiction,
                    "offence_type": (case_doc or {}).get("offence_type") or (case_doc or {}).get("charge") or "",
                    "case_summary": (case_doc or {}).get("summary") or "",
                }
                attack_plan = await refine_attack_plan_with_llm(
                    plan=attack_plan,
                    strategy=strategy,
                    case_context=case_context,
                    session_id=f"attack-plan-{case_id}",
                )
            except Exception as refine_err:
                logger.warning(f"LLM attack-plan refinement skipped for case {case_id}: {refine_err}")

            # Same LLM refinement pattern for the evidence builder — customises
            # affidavit templates, document requests, and steps to the case.
            # Hard guardrails preserve list lengths, affidavit types, and the
            # SWORN: skeleton. Per-ground fallback on any failure.
            try:
                from services.evidence_builder import refine_evidence_builder_with_llm
                evidence_builder = await refine_evidence_builder_with_llm(
                    builder=evidence_builder,
                    strategy=strategy,
                    case_context=case_context,
                    session_id=f"evidence-builder-{case_id}",
                )
            except Exception as refine_err:
                logger.warning(f"LLM evidence-builder refinement skipped for case {case_id}: {refine_err}")
        except Exception as outcome_err:
            logger.warning(f"Outcome prediction skipped for case {case_id}: {outcome_err}")
            predicted_outcome = None
            attack_plan = None
            evidence_builder = None
    except Exception as norm_err:
        logger.warning(f"Ground normalisation skipped for case {case_id}: {norm_err}")

    # Pre-load existing grounds for fuzzy matching
    all_existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "ground_id": 1, "title": 1},
    ).to_list(200)

    count = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user_id}, {"_id": 0}
        )

        issue_title = normalise_au_spelling((issue.get("title") or "").strip())

        # Fuzzy match against all existing grounds
        existing_ground = None
        for eg in all_existing_grounds:
            eg_title = (eg.get("title") or "").strip()
            if is_ground_duplicate(issue_title, eg_title):
                existing_ground = eg
                break

        ground_doc = {
            "case_id": case_id,
            "user_id": user_id,
            "title": existing_ground["title"] if existing_ground else issue_title,
            "ground_type": issue.get("ground_type", "other"),
            "description": issue.get("description", ""),
            "appellate_pathway": issue.get("appellate_pathway", ""),
            "error_identified": issue.get("error_identified", ""),
            "materiality": issue.get("materiality", ""),
            "strength": (verification or {}).get("legitimacy_scores", {}).get("rating", "moderate"),
            "status": "investigated" if verification else "identified",
            "supporting_evidence": (verification or {}).get("supporting_items", []),
            "law_sections": (verification or {}).get("law_sections", []),
            "similar_cases": (verification or {}).get("similar_cases", []),
            "legitimacy_scores": (verification or {}).get("legitimacy_scores", {}),
            "source_mode": "derived",
            "requires_human_review": (verification or {}).get("requires_human_review", True),
            "verification_status": (verification or {}).get("verification_status", "unverified"),
            # Realism scoring — set by services/appeal_strength.py
            "record_support": issue.get("record_support"),
            "verdict_robustness": issue.get("verdict_robustness"),
            "crown_strength": issue.get("crown_strength"),
            "failure_risk": issue.get("failure_risk"),
            "proviso_risk": issue.get("proviso_risk"),
            "reasoning_trail": issue.get("reasoning_trail") or [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if existing_ground:
            await db.grounds_of_merit.update_one(
                {"ground_id": existing_ground["ground_id"]},
                {"$set": ground_doc},
            )
        else:
            ground_doc["ground_id"] = f"gnd_{uuid.uuid4().hex[:12]}"
            ground_doc["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.grounds_of_merit.insert_one(ground_doc)
            all_existing_grounds.append({"ground_id": ground_doc["ground_id"], "title": issue_title})

        count += 1
    # Persist the predicted outcome + counsel conference outputs at the
    # case level so the Barrister Brief and cover page can show aligned
    # projections. None means the prediction didn't run (rare — only on
    # normalisation error).
    try:
        persist_doc: dict = {}
        if predicted_outcome is not None:
            persist_doc["predicted_outcome"] = predicted_outcome
        if attack_plan is not None:
            persist_doc["attack_plan"] = attack_plan
        if evidence_builder is not None:
            persist_doc["evidence_builder"] = evidence_builder
        if persist_doc:
            await db.cases.update_one(
                {"case_id": case_id, "user_id": user_id},
                {"$set": persist_doc},
            )
    except Exception as persist_err:
        logger.warning(f"Failed to persist outcome/attack_plan/evidence_builder for case {case_id}: {persist_err}")
    return count


async def _ensure_pipeline_identification(case: dict, documents: list) -> dict:
    """Full staged path: extract → refresh → classify → sync to grounds.
    DO_NOT_UNDO — Final safety net: runs cleanup_duplicate_grounds AFTER sync.
    """
    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues
    extracted_count = await _ensure_document_extracts(case, documents)
    case_extract = await _refresh_case_extract_from_pipeline(case)
    issues = await _classify_pipeline_issues(case, case_extract)
    synced_count = await _sync_pipeline_issues_to_grounds(case["case_id"], case["user_id"])
    # Safety net: clean up any duplicates that may have slipped through
    await cleanup_duplicate_grounds(db, case["case_id"], case["user_id"])
    await cleanup_duplicate_issues(db, case["case_id"], case["user_id"])
    return {"extracted_count": extracted_count, "classified_count": len(issues), "synced_count": synced_count}


async def _verify_issue_and_sync(case: dict, issue: dict, ground_id: str | None = None) -> dict:
    """Verify one classified issue, then sync the projection back into grounds_of_merit."""
    case_extract = await db.case_extracts.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
    )
    if not case_extract:
        case_extract = await _refresh_case_extract_from_pipeline(case)
    supporting_context = {
        "facts": case_extract.get("merged_facts", []),
        "events": case_extract.get("merged_events", []),
        "findings": case_extract.get("merged_findings", []),
    }
    verification = await verify_issue(case, issue, supporting_context)
    verification_dict = verification.model_dump()
    _safe_isoformat(verification_dict, "created_at")
    if not verification_dict.get("verification_id"):
        verification_dict["verification_id"] = f"ver_{uuid.uuid4().hex[:12]}"
    await db.issue_verifications.update_one(
        {"case_id": case["case_id"], "issue_id": issue["issue_id"], "user_id": case["user_id"]},
        {"$set": verification_dict},
        upsert=True,
    )
    await _sync_pipeline_issues_to_grounds(case["case_id"], case["user_id"])
    # DO_NOT_UNDO — 3 Apr 2026: cleanup after EVERY sync, no exceptions
    from services.ground_dedup import cleanup_duplicate_grounds
    await cleanup_duplicate_grounds(db, case["case_id"], case["user_id"])
    if ground_id:
        projected = await db.grounds_of_merit.find_one(
            {"ground_id": ground_id, "case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
        )
        if projected:
            return projected
    projected = await db.grounds_of_merit.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue.get("title"), "ground_type": issue.get("ground_type")}, {"_id": 0}
    )
    return projected or verification_dict


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.get("/cases/{case_id}/grounds", response_model=dict)
async def get_grounds_of_merit(case_id: str, request: Request):
    """Get all grounds of merit for a case - requires payment to see details"""
    user = await get_current_user(request)
    
    # Admin can view any case's grounds
    if is_admin_user(user.email):
        case = await db.cases.find_one({"case_id": case_id})
    else:
        case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    STRENGTH_ORDER = {"strong": 0, "moderate": 1, "weak": 2, "unknown": 3}

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort([("created_at", -1)]).to_list(200)

    # Sort: priority_order first (if set by user reorder), then strength, then title
    grounds.sort(key=lambda g: (
        g.get("priority_order", 999),
        STRENGTH_ORDER.get(g.get("strength", "unknown"), 3),
        g.get("title", "")
    ))

    # For payment lookup, use the case owner's user_id (not admin's)
    case_owner_id = case.get("user_id", user.user_id)
    
    payment = await db.payments.find_one({
        "case_id": case_id,
        "user_id": case_owner_id,
        "feature_type": {"$in": feature_type_variants("grounds_of_merit")},
        "status": "completed"
    })

    is_unlocked = (
        payment is not None 
        or any(canonical_feature_type(f) == "grounds_of_merit" for f in (case.get("unlocked_features") or []))
        or is_admin_user(user.email)
    )

    if is_unlocked:
        # Retroactively score any grounds missing legitimacy_scores
        for g in grounds:
            if not g.get("ground_id"):
                g["ground_id"] = f"gnd_{uuid.uuid4().hex[:12]}"
                await db.grounds_of_merit.update_one(
                    {"case_id": case_id, "title": g.get("title"), "ground_type": g.get("ground_type")},
                    {"$set": {"ground_id": g["ground_id"]}}
                )
            if "source_mode" not in g:
                g["source_mode"] = "legacy"
            if "verification_status" not in g:
                g["verification_status"] = "unverified"
            # Only calculate legitimacy scores for grounds that have been investigated
            # and have actual evidence. Newly identified grounds stay at their assigned strength.
            if not g.get("legitimacy_scores") and g.get("status") == "investigated" and g.get("supporting_evidence"):
                scored = calculate_ground_rating({
                    "ground_type": g.get("ground_type", "other"),
                    "supporting_evidence": [{"quote": e.get("quote", "") if isinstance(e, dict) else str(e)} for e in (g.get("supporting_evidence") or [])],
                    "undermining_items": g.get("undermining_items") or [],
                })
                g["legitimacy_scores"] = scored
                g["strength"] = scored["rating"]
                await db.grounds_of_merit.update_one(
                    {"ground_id": g["ground_id"]},
                    {"$set": {"legitimacy_scores": scored, "strength": scored["rating"]}}
                )
        return {
            "grounds": grounds,
            "count": len(grounds),
            "is_unlocked": True,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
        }
    else:
        return {
            "grounds": [],
            "count": len(grounds),
            "is_unlocked": False,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"],
            "message": f"Found {len(grounds)} potential grounds of merit. Pay ${FEATURE_PRICES['grounds_of_merit']['price']:.2f} to unlock full details."
        }


@router.post("/cases/{case_id}/grounds", response_model=dict)
async def create_ground_of_merit(case_id: str, ground_data: GroundOfMeritCreate, request: Request):
    """Create a new ground of merit"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence_items = _wrap_evidence_items(ground_data.supporting_evidence)

    scored = calculate_ground_rating({
        "ground_type": _normalise_ground_type(ground_data.ground_type),
        "supporting_evidence": [{"quote": e.quote} for e in evidence_items]
    })

    ground = GroundOfMerit(
        case_id=case_id,
        user_id=user.user_id,
        title=ground_data.title,
        ground_type=_normalise_ground_type(ground_data.ground_type),
        description=ground_data.description,
        strength=scored["rating"],
        supporting_evidence=evidence_items,
        legitimacy_scores=scored,
        source_mode="manual",
        requires_human_review=True,
        verification_status="unverified",
    )

    ground_dict = ground.model_dump()
    _safe_isoformat(ground_dict, "created_at")
    _safe_isoformat(ground_dict, "updated_at")

    await db.grounds_of_merit.insert_one(ground_dict)
    await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
    return created_ground



# DO NOT UNDO — Ground priority reorder endpoint. MUST be defined BEFORE {ground_id} routes.
@router.put("/cases/{case_id}/grounds/reorder")
async def reorder_grounds(case_id: str, request: Request):
    """Reorder grounds by priority. Accepts a list of ground_ids in the desired order."""
    user = await get_current_user(request)
    if is_admin_user(user.email):
        case = await db.cases.find_one({"case_id": case_id})
    else:
        case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    body = await request.json()
    ground_ids = body.get("ground_ids", [])
    if not ground_ids:
        raise HTTPException(status_code=400, detail="ground_ids list required")

    # Validate uniqueness
    if len(ground_ids) != len(set(ground_ids)):
        raise HTTPException(status_code=400, detail="Duplicate ground_ids in payload")

    # Validate ALL ground_ids exist before applying any updates (atomic check)
    existing = await db.grounds_of_merit.find(
        {"case_id": case_id, "ground_id": {"$in": ground_ids}},
        {"_id": 0, "ground_id": 1}
    ).to_list(len(ground_ids))
    existing_ids = {g["ground_id"] for g in existing}
    missing = [gid for gid in ground_ids if gid not in existing_ids]
    if missing:
        raise HTTPException(status_code=404, detail=f"Ground not found: {missing[0]}")

    # All validated — apply updates
    for idx, ground_id in enumerate(ground_ids):
        await db.grounds_of_merit.update_one(
            {"ground_id": ground_id, "case_id": case_id},
            {"$set": {"priority_order": idx}}
        )

    return {"message": f"Reordered {len(ground_ids)} grounds successfully."}


@router.get("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def get_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Get a specific ground of merit"""
    user = await get_current_user(request)
    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    if "source_mode" not in ground:
        ground["source_mode"] = "legacy"
    if "verification_status" not in ground:
        ground["verification_status"] = "unverified"
    return ground


@router.put("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def update_ground_of_merit(case_id: str, ground_id: str, ground_data: GroundOfMeritUpdate, request: Request):
    """Update a ground of merit"""
    user = await get_current_user(request)

    update_fields = {k: v for k, v in ground_data.model_dump().items() if v is not None}

    if "ground_type" in update_fields:
        update_fields["ground_type"] = _normalise_ground_type(update_fields["ground_type"])

    if "supporting_evidence" in update_fields:
        evidence_items = _wrap_evidence_items(update_fields["supporting_evidence"])
        update_fields["supporting_evidence"] = _legacy_evidence_dump(evidence_items)

        scored = calculate_ground_rating({
            "ground_type": update_fields.get("ground_type", "other"),
            "supporting_evidence": [{"quote": e.get("quote", "")} for e in update_fields["supporting_evidence"]]
        })
        update_fields["legitimacy_scores"] = scored
        update_fields["strength"] = scored["rating"]

    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.grounds_of_merit.update_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")

    return await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.delete("/cases/{case_id}/grounds/{ground_id}")
async def delete_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Delete a ground of merit"""
    user = await get_current_user(request)
    result = await db.grounds_of_merit.delete_one({
        "ground_id": ground_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    return {"message": "Ground of merit deleted"}


# ============================================================================
# INVESTIGATE SINGLE GROUND — Background task pattern to avoid CF 524 timeout
# ============================================================================

# In-memory task tracker for investigation jobs
_investigate_tasks = {}


async def _run_investigation(task_id: str, case_id: str, ground_id: str, user_id: str):
    """Background task that performs the full investigation pipeline."""
    try:
        _investigate_tasks[task_id] = {"status": "running", "progress": "Fetching ground data..."}

        ground = await db.grounds_of_merit.find_one(
            {"ground_id": ground_id, "case_id": case_id, "user_id": user_id}, {"_id": 0}
        )
        if not ground:
            _investigate_tasks[task_id] = {"status": "failed", "error": "Ground not found"}
            return

        case = await db.cases.find_one(
            {"case_id": case_id, "user_id": user_id}, {"_id": 0}
        )
        if not case:
            _investigate_tasks[task_id] = {"status": "failed", "error": "Case not found"}
            return

        _investigate_tasks[task_id]["progress"] = "Looking up issue classification..."

        issue = await db.issue_classifications.find_one(
            {"case_id": case_id, "user_id": user_id, "title": ground.get("title"), "ground_type": ground.get("ground_type")},
            {"_id": 0}
        )
        if not issue:
            issue = {
                "issue_id": f"compat_{ground_id}",
                "case_id": case_id, "user_id": user_id,
                "title": ground.get("title", "Untitled ground"),
                "ground_type": ground.get("ground_type", "other"),
                "description": ground.get("description", ""),
            }

        case_extract = await db.case_extracts.find_one(
            {"case_id": case_id, "user_id": user_id}, {"_id": 0}
        )
        if not case_extract:
            case_extract = {"merged_facts": [], "merged_events": [], "merged_findings": []}

        supporting_context = {
            "facts": case_extract.get("merged_facts", []),
            "events": case_extract.get("merged_events", []),
            "findings": case_extract.get("merged_findings", []),
        }

        _investigate_tasks[task_id]["progress"] = "Verifying ground against evidence..."
        verification = await verify_issue(case, issue, supporting_context)
        verification_dict = verification.model_dump()
        _safe_isoformat(verification_dict, "created_at")
        # Ensure verification_id is set to avoid DuplicateKeyError on stale unique indexes
        if not verification_dict.get("verification_id"):
            verification_dict["verification_id"] = f"ver_{uuid.uuid4().hex[:12]}"

        await db.issue_verifications.update_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user_id},
            {"$set": verification_dict}, upsert=True,
        )

        _investigate_tasks[task_id]["progress"] = "Generating deep analysis..."

        deep_analysis_text = ""
        try:
            offence_context = get_offence_context(case)
            state_upper = (case.get('state') or 'unknown').upper()
            analysis_prompt = f"""Analyse the following ground of appeal in the criminal case of {case.get('defendant_name', 'the appellant')} ({state_upper}).

JURISDICTION: {state_upper}
{offence_context}

Ground: {ground.get('title', '')}
Type: {ground.get('ground_type', '')}
Description: {ground.get('description', '')}
Appellate Pathway: {ground.get('appellate_pathway') or 'Miscarriage of justice'}

Supporting evidence found:
{json.dumps(verification_dict.get('supporting_items', []), indent=2, default=str)[:2000]}

Undermining factors:
{json.dumps(verification_dict.get('undermining_items', []), indent=2, default=str)[:1000]}

Relevant legislation:
{json.dumps(verification_dict.get('law_sections', []), indent=2, default=str)[:1000]}

Similar cases:
{json.dumps(verification_dict.get('similar_cases', []), indent=2, default=str)[:1000]}

Legitimacy assessment: {json.dumps(verification_dict.get('legitimacy_scores', {}), default=str)}

LEGISLATION ACCURACY:
- Do NOT invent or fabricate any legislation, Act, section, or case authority.
- Only cite Acts that are current and in force for {state_upper}.
- Distinguish between the appellate pathway legislation and the substantive criminal legislation.
- If uncertain about a specific section number, omit it rather than guess.
- Do NOT default to NSW legislation for non-NSW cases. Use ONLY the correct legislation for {state_upper}.

Write a detailed appellate analysis of this ground (600-900 words) using the following MANDATORY structure:

## Trial Finding
What did the trial judge find or accept on this issue?

## Error Identified
What specific error is arguable? Use FORENSIC appellate language: "It is arguable that the trial judge erred in...", "It is contended that...", "There is a tenable argument that...". Do NOT use bare declarations like "The trial judge erred" (too definitive at appellate preparation stage). Do NOT use hedging like "may have" or "could potentially" (too weak).

## Materiality
Why does this error matter to the outcome of the case? How did it affect the verdict or sentence?

## Consequence
What is the legal consequence? (e.g. it is arguable that the verdict is unsafe, that a miscarriage of justice occurred, that the sentence must be set aside)

## Appellate Viability
Assess the strength of this ground using:
- Outcome impact: Determinative / Influential / Minor
- Legal alignment: Direct authority / Analogous / Weak
- Evidence support: Strong / Partial / Limited
State what further material could strengthen or weaken this ground.

GROUND FRAMING RULES:
- **NEVER MERGE CONVICTION AND SENTENCING ISSUES in one ground.** Conviction attacks the verdict (s 6(1) miscarriage of justice / unsafe verdict). Sentencing attacks the penalty (House v The King error / manifest excess). If both apply, the case has TWO grounds.
- **Partial defences — s 23A Crimes Act 1900 (NSW), substantial impairment, abnormality of mind, diminished responsibility (QLD), mental impairment defence (VIC/SA/ACT), unsoundness of mind (WA/TAS) — operate on LIABILITY (reducing murder to manslaughter). They are NEVER sentencing mitigation. Frame them as mens-rea displacement mechanisms, not as mental-health mitigation.**
- If this ground involves psychiatric/mental state evidence → frame as a CONVICTION SAFETY attack on mens rea determination. **EXPLICITLY articulate the M v The Queen (1994) 181 CLR 487 formulation**: "Could the jury, acting reasonably, have excluded a reasonable hypothesis consistent with lack of intent given the competing psychiatric evidence?" Omitting this formulation makes the ground structurally defective.
- If this ground involves jury-integrity conduct → distinguish clearly between (a) deliberative bias during trial (probative) and (b) post-verdict conduct (minimal probative value). Do NOT inflate post-verdict conduct to moderate or strong; require contemporaneous trial-record complaint and juror affidavit before elevating above "weak".
- If this ground involves ineffective counsel → note clearly that this ground is "Contingent — requires evidentiary support (affidavit from accused, transcript confirmation)" and that the threshold is extremely high.
- If this ground involves sentencing → tie to proportionality and moral culpability. The question is whether "the sentence reflects true culpability" not merely "the judge got it wrong."

RULES:
- Write in third person only. Use paragraphs, NOT bullet points in body text.
- Use forensic appellate language throughout. Frame all conclusions as arguable, not declarative.
- Every paragraph must tie back to the specific trial error, not generic legal textbook explanations.
- Australian English spelling only (analyse, defence, offence, behaviour, favour).
- Do NOT use first or second person."""

            deep_analysis_text = await call_llm_with_fallback(
                system_prompt=f"You are a senior Australian criminal appellate researcher conducting forensic issue analysis for counsel preparation in {state_upper}. Write in formal third person. Use the mandatory structure provided. Australian English only. Use forensic appellate language throughout — frame conclusions as arguable and contended, not as declarations of fact. The Court makes findings; the brief identifies where findings are open.",
                user_prompt=analysis_prompt,
                session_id=f"deep_analysis_{ground_id}",
                task_type="ground_deep_analysis",
            )
            if deep_analysis_text:
                deep_analysis_text = enforce_forensic_language(deep_analysis_text)
        except Exception as e:
            logger.warning(f"Deep analysis generation failed for ground {ground_id}: {e}")

        _investigate_tasks[task_id]["progress"] = "Saving results..."

        update_fields = {
            "status": "investigated",
            "verification_status": "verified",
        }
        if verification_dict.get("legitimacy_scores"):
            scores = verification_dict["legitimacy_scores"]
            update_fields["legitimacy_scores"] = scores
            update_fields["strength"] = scores.get("rating", ground.get("strength", "moderate"))
        if verification_dict.get("law_sections"):
            update_fields["law_sections"] = verification_dict["law_sections"]
        if verification_dict.get("similar_cases"):
            update_fields["similar_cases"] = verification_dict["similar_cases"]
        if verification_dict.get("supporting_items"):
            update_fields["supporting_evidence"] = verification_dict["supporting_items"]
        if deep_analysis_text:
            # Normalise markdown BEFORE storing — prevents inline `##` headings
            # and glued bullet lists from hitting the DB. See
            # /app/backend/services/md_normaliser.py for patterns handled.
            from services.md_normaliser import normalise_markdown
            deep_analysis_text = normalise_markdown(deep_analysis_text)
            update_fields["deep_analysis"] = {
                "full_analysis": deep_analysis_text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            update_fields["analysis"] = deep_analysis_text

        # Generate appellate_pathway if missing
        if not ground.get("appellate_pathway"):
            try:
                from services.offence_helpers import _build_state_framework_context
                state = (case.get("state") or "").lower().strip()
                leg_context = _build_state_framework_context(state) if state else ""
                ap_prompt = f"""Based on the following ground of appeal in a {state.upper()} criminal case, provide the single most appropriate appellate pathway.

Ground Title: {ground.get('title', '')}
Ground Type: {ground.get('ground_type', 'other')}
Description: {ground.get('description', '')}

{leg_context}

Return ONLY a concise appellate pathway string. Do NOT return JSON."""
                from services.llm_service import call_llm_structured
                ap_result = await call_llm_structured(
                    system_prompt="You are an Australian appellate law expert. Provide the correct appellate pathway provision for the specified jurisdiction. Do NOT default to NSW. Do NOT invent section numbers. Use Australian English only.",
                    user_prompt=ap_prompt,
                    session_id=f"appellate_pathway_{ground_id}",
                    task_type="general",
                    require_json=False,
                )
                ap_text = ap_result.get("content", "") if isinstance(ap_result, dict) else str(ap_result)
                ap_text = ap_text.strip().strip('"').strip("'").strip()
                if ap_text and len(ap_text) > 5 and (not isinstance(ap_result, dict) or ap_result.get("ok")):
                    update_fields["appellate_pathway"] = ap_text
            except Exception as ap_err:
                logger.warning(f"Failed to generate appellate pathway: {ap_err}")

        await db.grounds_of_merit.update_one(
            {"ground_id": ground_id, "case_id": case_id},
            {"$set": update_fields}
        )

        updated = await db.grounds_of_merit.find_one(
            {"ground_id": ground_id, "case_id": case_id}, {"_id": 0}
        )
        _investigate_tasks[task_id] = {"status": "completed", "result": updated}

    except Exception as e:
        logger.error(f"Background investigation failed for {ground_id}: {e}")
        _investigate_tasks[task_id] = {"status": "failed", "error": str(e)}


@router.post("/cases/{case_id}/grounds/{ground_id}/investigate", response_model=dict)
async def investigate_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Start background investigation of a ground. Returns task_id for polling."""
    user = await get_current_user(request)

    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground not found")

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Mark ground as investigating
    await db.grounds_of_merit.update_one(
        {"ground_id": ground_id, "case_id": case_id},
        {"$set": {"status": "investigating"}}
    )

    task_id = f"inv_{ground_id}_{uuid.uuid4().hex[:8]}"
    _investigate_tasks[task_id] = {"status": "started", "progress": "Starting investigation..."}

    import asyncio
    asyncio.create_task(_run_investigation(task_id, case_id, ground_id, user.user_id))

    return {"status": "started", "task_id": task_id, "ground_id": ground_id}


@router.get("/cases/{case_id}/grounds/{ground_id}/investigate/status", response_model=dict)
async def investigate_ground_status(case_id: str, ground_id: str, task_id: str, request: Request):
    """Poll investigation status."""
    await get_current_user(request)

    task = _investigate_tasks.get(task_id)
    if not task:
        # Task not found in memory — check if the ground is already investigated
        ground = await db.grounds_of_merit.find_one(
            {"ground_id": ground_id, "case_id": case_id}, {"_id": 0}
        )
        if ground and ground.get("status") == "investigated":
            return {"status": "completed", "result": ground}
        return {"status": "not_found"}

    if task["status"] == "completed":
        # Clean up the task from memory
        result = task.get("result", {})
        _investigate_tasks.pop(task_id, None)
        return {"status": "completed", "result": result}

    if task["status"] == "failed":
        error = task.get("error", "Unknown error")
        _investigate_tasks.pop(task_id, None)
        return {"status": "failed", "error": error}

    return {"status": "running", "progress": task.get("progress", "Processing...")}


# ============================================================================
# AUTO IDENTIFY GROUNDS — Background Task Pattern
# ============================================================================

async def _run_auto_identify_background(task_id: str, case_id: str, user_id: str, case: dict, documents: list, existing_grounds: list):
    """Background worker for auto-identify. Updates task status in DB as it progresses."""
    try:
        await db.pipeline_tasks.update_one(
            {"task_id": task_id},
            {"$set": {"status": "extracting", "progress": "Extracting document artifacts...", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        pipeline_result = await _ensure_pipeline_identification(case, documents)

        await db.pipeline_tasks.update_one(
            {"task_id": task_id},
            {"$set": {"status": "finalising", "progress": "Deduplicating and finalising grounds...", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )

        updated_grounds = await db.grounds_of_merit.find(
            {"case_id": case_id, "user_id": user_id}, {"_id": 0}
        ).to_list(200)

        existing_titles = {(g.get("title"), g.get("ground_type")) for g in existing_grounds}

        from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

        def is_duplicate(new_ground):
            if (new_ground.get("title"), new_ground.get("ground_type")) in existing_titles:
                return True
            new_title = normalise_au_spelling((new_ground.get("title") or "").strip())
            if not new_title:
                return False
            for eg in existing_grounds:
                eg_title = (eg.get("title") or "").strip()
                if is_ground_duplicate(new_title, eg_title):
                    return True
            return False

        new_grounds = [g for g in updated_grounds if not is_duplicate(g)]
        skipped_duplicates = max(0, pipeline_result["classified_count"] - len(new_grounds))

        await db.cases.update_one(
            {"case_id": case_id, "user_id": user_id},
            {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )

        result = {
            "identified_count": len(new_grounds),
            "skipped_duplicates": skipped_duplicates,
            "existing_grounds": len(existing_grounds),
            "message": (
                f"Found {len(new_grounds)} new grounds. "
                f"Pipeline extracted {pipeline_result['extracted_count']} new document extract(s), "
                f"classified {pipeline_result['classified_count']} issue(s), "
                f"and synced {pipeline_result['synced_count']} projected ground(s)."
            ),
            "unlock_required": True,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
        }

        await db.pipeline_tasks.update_one(
            {"task_id": task_id},
            {"$set": {"status": "completed", "result": result, "progress": "Complete", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    except Exception as e:
        logger.error(f"Background auto-identify failed for task {task_id}: {e}")
        await db.pipeline_tasks.update_one(
            {"task_id": task_id},
            {"$set": {"status": "failed", "error": str(e), "progress": "Failed", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )


@router.post("/cases/{case_id}/grounds/auto-identify", response_model=dict)
async def auto_identify_grounds(case_id: str, request: Request):
    """AI automatically identifies potential grounds of merit from case materials.
    Returns immediately with a task_id. Frontend polls /auto-identify/status for progress.
    """
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # ── Soft metadata validation (logs warnings, does not block) ──
    from services.case_validation import validate_case_metadata, log_metadata_warnings
    metadata_val = validate_case_metadata(case)
    log_metadata_warnings(case_id, metadata_val, "auto_identify_grounds")

    # Check if there's already a running task for this case
    active_task = await db.pipeline_tasks.find_one(
        {"case_id": case_id, "user_id": user.user_id, "task_type": "auto_identify", "status": {"$in": ["pending", "extracting", "finalising"]}},
        {"_id": 0}
    )
    if active_task:
        return {"task_id": active_task["task_id"], "status": "already_running", "message": "Analysis is already in progress."}

    existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).to_list(100)

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "file_data": 0}
    ).to_list(500)

    if not documents and not case.get("summary"):
        raise HTTPException(status_code=400, detail="No documents or case summary available for analysis")

    task_id = f"task_{uuid.uuid4().hex[:16]}"
    await db.pipeline_tasks.insert_one({
        "task_id": task_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "task_type": "auto_identify",
        "status": "pending",
        "progress": "Starting analysis...",
        "document_count": len(documents),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    # Fire and forget — runs in background
    asyncio.create_task(_run_auto_identify_background(task_id, case_id, user.user_id, case, documents, existing_grounds))

    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Analysing {len(documents)} document(s) in the background. This may take a few minutes for large cases.",
        "metadata_warnings": metadata_val.get("warnings", []),
    }


@router.get("/cases/{case_id}/grounds/auto-identify/status", response_model=dict)
async def auto_identify_status(case_id: str, request: Request):
    """Poll the status of a running auto-identify background task."""
    user = await get_current_user(request)

    task = await db.pipeline_tasks.find_one(
        {"case_id": case_id, "user_id": user.user_id, "task_type": "auto_identify"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )

    if not task:
        return {"status": "none", "message": "No analysis task found for this case."}

    response = {
        "task_id": task["task_id"],
        "status": task["status"],
        "progress": task.get("progress", ""),
        "document_count": task.get("document_count", 0),
    }

    if task["status"] == "completed":
        response["result"] = task.get("result", {})
    elif task["status"] == "failed":
        response["error"] = task.get("error", "Unknown error")

    return response



# ============================================================================
# DEDUP CLEANUP ENDPOINT
# ============================================================================

@router.post("/cases/{case_id}/grounds/cleanup-duplicates", response_model=dict)
async def cleanup_ground_duplicates(case_id: str, request: Request):
    """DO_NOT_UNDO — Remove duplicate grounds using fuzzy deduplication.
    Merges data from duplicates into the kept ground (first by created_at).
    """
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues

    grounds_result = await cleanup_duplicate_grounds(db, case_id, user.user_id)
    issues_result = await cleanup_duplicate_issues(db, case_id, user.user_id)

    return {
        "grounds": grounds_result,
        "issues": issues_result,
        "message": f"Cleaned up {grounds_result['removed']} duplicate grounds and {issues_result['removed']} duplicate issues.",
    }


# ============================================================================
# REFRESH LEGAL REFERENCES — Re-verify all grounds to get substantive law sections
# ============================================================================

@router.post("/cases/{case_id}/grounds/refresh-legal-refs", response_model=dict)
async def refresh_legal_references(case_id: str, request: Request):
    """Re-verify all grounds to update law_sections with substantive legislation
    (Crimes Act, Evidence Act, etc.) instead of generic appellate act references."""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(50)

    if not grounds:
        return {"updated": 0, "message": "No grounds to refresh."}

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case_extract:
        raise HTTPException(status_code=400, detail="No case extract available. Upload documents first.")

    supporting_context = {
        "facts": case_extract.get("merged_facts", []),
        "events": case_extract.get("merged_events", []),
        "findings": case_extract.get("merged_findings", []),
    }

    updated = 0
    for ground in grounds:
        try:
            issue_dict = {
                "issue_id": ground.get("ground_id", ""),
                "title": ground.get("title", ""),
                "ground_type": ground.get("ground_type", "other"),
                "description": ground.get("description", ""),
                "appellate_pathway": ground.get("appellate_pathway", ""),
            }
            verification = await verify_issue(case, issue_dict, supporting_context)
            v_dict = verification.model_dump()

            update_fields = {}
            # Always update law_sections — even if empty — to clear old stale entries
            update_fields["law_sections"] = v_dict.get("law_sections", [])
            if v_dict.get("similar_cases"):
                update_fields["similar_cases"] = v_dict["similar_cases"]
            if v_dict.get("legitimacy_scores"):
                update_fields["legitimacy_scores"] = v_dict["legitimacy_scores"]
                update_fields["strength"] = v_dict["legitimacy_scores"].get("rating", ground.get("strength", "moderate"))

            # Generate appellate_pathway if missing
            if not ground.get("appellate_pathway"):
                try:
                    from services.offence_helpers import _build_state_framework_context
                    state = (case.get("state") or "").lower().strip()
                    leg_context = _build_state_framework_context(state) if state else ""
                    ap_prompt = f"""Based on the following ground of appeal in a {state.upper()} criminal case, provide the single most appropriate appellate pathway (the statutory provision giving the right to appeal).

Ground Title: {ground.get('title', '')}
Ground Type: {ground.get('ground_type', 'other')}
Description: {ground.get('description', '')}

{leg_context}

Return ONLY a concise appellate pathway string, e.g.:
- "Miscarriage of justice under s 411 Criminal Code Act 1983 (NT)"
- "Error of law under s 5(1) Criminal Appeal Act 1912 (NSW)"
- "Sentencing error under s 5(1) Criminal Appeal Act 1912 (NSW)"
Do NOT return JSON. Return only the plain text appellate pathway."""
                    from services.llm_service import call_llm_structured
                    ap_result = await call_llm_structured(
                        system_prompt="You are an Australian appellate law expert. Provide the correct appellate pathway provision for the specified jurisdiction. Do NOT default to NSW. Do NOT invent section numbers. Use Australian English only.",
                        user_prompt=ap_prompt,
                        session_id=f"appellate_pathway_{ground.get('ground_id', '')}",
                        task_type="general",
                        require_json=False,
                    )
                    ap_text = ap_result.get("content", "") if isinstance(ap_result, dict) else str(ap_result)
                    ap_text = ap_text.strip().strip('"').strip("'").strip()
                    if ap_text and len(ap_text) > 5 and ap_result.get("ok"):
                        update_fields["appellate_pathway"] = ap_text
                except Exception as ap_err:
                    logger.warning(f"Failed to generate appellate pathway for {ground.get('ground_id')}: {ap_err}")

            if update_fields:
                update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
                await db.grounds_of_merit.update_one(
                    {"ground_id": ground["ground_id"], "case_id": case_id},
                    {"$set": update_fields}
                )
                updated += 1
        except Exception as e:
            logger.warning(f"Failed to refresh legal refs for ground {ground.get('ground_id')}: {e}")

    return {
        "updated": updated,
        "total": len(grounds),
        "message": f"Refreshed legal references for {updated}/{len(grounds)} grounds.",
    }




@router.post("/cases/{case_id}/grounds/backfill-pathways", response_model=dict)
async def backfill_appellate_pathways(case_id: str, request: Request):
    """Backfill appellate_pathway for all grounds in a case that are missing it."""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)

    updated = 0
    state = (case.get("state") or "").lower().strip()

    for ground in grounds:
        if ground.get("appellate_pathway"):
            continue
        try:
            from services.offence_helpers import _build_state_framework_context
            leg_context = _build_state_framework_context(state) if state else ""
            ap_prompt = f"""Based on the following ground of appeal in a {state.upper()} criminal case, provide the single most appropriate appellate pathway (the statutory provision giving the right to appeal).

Ground Title: {ground.get('title', '')}
Ground Type: {ground.get('ground_type', 'other')}
Description: {ground.get('description', '')}

{leg_context}

Return ONLY a concise appellate pathway string, e.g.:
- "Miscarriage of justice under s 6(1) Criminal Appeal Act 1912 (NSW)"
- "Error of law under s 5(1) Criminal Appeal Act 1912 (NSW)"
- "Sentencing error under s 5(1) Criminal Appeal Act 1912 (NSW)"
Do NOT return JSON. Return only the plain text appellate pathway."""
            from services.llm_service import call_llm_structured
            ap_result = await call_llm_structured(
                system_prompt="You are an Australian appellate law expert. Provide the correct appellate pathway provision for the specified jurisdiction. Do NOT default to NSW. Do NOT invent section numbers. Use Australian English only.",
                user_prompt=ap_prompt,
                session_id=f"backfill_pathway_{ground.get('ground_id', '')}",
                task_type="general",
                require_json=False,
            )
            ap_text = ap_result.get("content", "") if isinstance(ap_result, dict) else str(ap_result)
            ap_text = ap_text.strip().strip('"').strip("'").strip()
            if ap_text and len(ap_text) > 5 and (not isinstance(ap_result, dict) or ap_result.get("ok")):
                await db.grounds_of_merit.update_one(
                    {"ground_id": ground["ground_id"], "case_id": case_id},
                    {"$set": {"appellate_pathway": ap_text}}
                )
                updated += 1
                logger.info(f"Backfilled appellate_pathway for {ground['ground_id']}: {ap_text}")
        except Exception as e:
            logger.warning(f"Backfill appellate_pathway failed for {ground.get('ground_id')}: {e}")

    return {"updated": updated, "total": len(grounds), "message": f"Backfilled appellate pathways for {updated}/{len(grounds)} grounds."}
