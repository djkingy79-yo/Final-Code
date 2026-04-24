# ===========================================================================
# AI Report Generation Engine
# Extracted from server.py — analyze_case_with_ai and supporting functions
# ===========================================================================

import os
import re
import asyncio
from datetime import datetime, timezone

from fastapi import HTTPException

from config import db, logger
from services.llm_service import call_llm_for_json, call_llm_structured
from services.offence_helpers import (
    get_offence_context, get_offence_system_prompt,
)
from services.document_helpers import build_document_context
from services.report_quality import (
    _build_anchor_terms, _split_report_sections, _dedupe_report_content, _strip_report_placeholders,
    _sanitise_suspect_authorities,
    _clean_sentence_candidate, _is_valid_sentence_candidate,
)
from services.pipeline_orchestrator import (
    _enforce_pipeline_freshness,
    _load_issue_arguments,
    _load_submission_draft,
)
from offence_framework import OFFENCE_CATEGORIES, AUSTRALIAN_STATES
from models import ReportMetadata


# ---------------------------------------------------------------------------
# FORENSIC LANGUAGE ROTATION (locked 2026-02-21 at owner's request)
# The LLM previously over-used "It is arguable that..." opening almost every
# sentence. Forensic appellate advocacy varies register constantly. This
# single constant is referenced by every system prompt below so a single
# update propagates everywhere, and the LLM is instructed to ROTATE across
# at least eight forms, never repeating the same stem within three
# consecutive sentences.
# ---------------------------------------------------------------------------
FORENSIC_LANGUAGE_RULE = (
    "Use forensic appellate language and VARY your phrasing — never repeat "
    "the same opening stem within three consecutive sentences. Rotate across "
    "these approved forms (use all, in rotation): \"it is arguable that\", "
    "\"it is contended that\", \"it is submitted that\", \"it is open to "
    "argument that\", \"there is a tenable argument that\", \"there is a "
    "reasonably arguable case that\", \"a question arises as to whether\", "
    "\"it warrants consideration whether\", \"the material gives rise to an "
    "arguable basis that\", \"the proper course, it is submitted, would have "
    "been\", \"with respect, the [direction/finding/approach] is open to "
    "question\", \"it may be contended that\". NEVER use bare declarations "
    "like \"The judge erred\", \"This proves\", \"This clearly shows\", "
    "\"The sentence is manifestly excessive\". NEVER use weak hedging "
    "like \"may have\" or \"could potentially\". NEVER impute dishonesty, "
    "bias, or incompetence to any judicial officer, party, or representative. "
    "NEVER use inflammatory adjectives (outrageous, shocking, disgraceful, "
    "grossly, absurd)."
)


# Human-readable titles shown in the UI progress ticker for each pass.
# Keys match the first element of each pass tuple (e.g. "PASS 3/8").
PASS_TITLES = {
    # Full Detailed Legal Analysis — 8 passes, 15 sections
    "PASS 1/8": "Executive Brief + Forensic Chronology",
    "PASS 2/8": "Document Digest & Evidence Inventory",
    "PASS 3/8": "Grounds of Merit — Part 1",
    "PASS 4/8": "Grounds of Merit — Part 2 + Legal Framework",
    "PASS 5/8": "Sentencing Review & Comparative Analysis",
    "PASS 6/8": "Procedural History & Trial Conduct",
    "PASS 7/8": "Appellate Strategy & Authorities",
    "PASS 8/8": "Plain English Guide & Action Plan",
    # Extensive Log & Analysis — 10 passes, 24 sections
    "PASS 1/10": "Executive Brief + Forensic Chronology + Document Digest",
    "PASS 2/10": "Grounds of Merit — Full Analysis",
    "PASS 3/10": "Legal Framework & Statutory Interpretation",
    "PASS 4/10": "Sentencing Analysis & Comparative Jurisprudence",
    "PASS 5/10": "Expanded Grounds — Deep Argumentation",
    "PASS 6/10": "Case Authorities & Precedent Mapping",
    "PASS 7/10": "Appellate Court Considerations",
    "PASS 8/10": "Risk Register & Counter-Arguments",
    "PASS 9/10": "Strategic Operations & Submission Drafting",
    "PASS 10/10": "Client Brief & Plain English Guide",
}


async def _update_report_pass_progress(report_id: str, pass_index: int, total_passes: int, label: str):
    """Persist the current-pass progress to the report doc so the frontend can surface it."""
    if not report_id:
        return
    try:
        pass_title = PASS_TITLES.get(label, label)
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {
                "generation_progress": {
                    "current_pass": pass_index,
                    "total_passes": total_passes,
                    "pass_label": label,
                    "pass_title": pass_title,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            }}
        )
    except Exception as e:
        logger.debug(f"pass-progress update failed for {report_id}: {e}")


async def analyze_case_with_ai(case_id: str, user_id: str, report_type: str, aggressive_mode: bool = False, report_id: str = None) -> dict:
    """Use AI to analyse case and generate report — HARDENED with structured LLM calls"""
    
    # Get case data
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # ================= PIPELINE GUARD =================
    high_value_report = report_type in ["full_detailed", "extensive_log"]
    pipeline_status = None

    if high_value_report:
        try:
            pipeline_status = await _enforce_pipeline_freshness(
                case_id,
                user_id,
                auto_refresh=True,
            )
            logger.info(f"Pipeline guard for {case_id}/{report_type}: {pipeline_status.get('status')}")
        except Exception as pg_err:
            logger.warning(f"Pipeline guard failed (non-fatal) for {case_id}: {pg_err}")

    # ================= LOAD PIPELINE DATA =================
    structured_context = None
    if high_value_report:
        case_extract_data = await db.case_extracts.find_one(
            {"case_id": case_id, "user_id": user_id}, {"_id": 0}
        )
        issue_verifications_data = await db.issue_verifications.find(
            {"case_id": case_id, "user_id": user_id}, {"_id": 0}
        ).to_list(100)

        structured_context = {
            "facts": case_extract_data.get("merged_facts", []) if case_extract_data else [],
            "events": case_extract_data.get("merged_events", []) if case_extract_data else [],
            "findings": case_extract_data.get("merged_findings", []) if case_extract_data else [],
            "verified_issues": issue_verifications_data,
        }

    # Load issue arguments (if any exist)
    pipeline_arguments = await _load_issue_arguments(case_id, user_id) if high_value_report else []
    submission_draft = await _load_submission_draft(case_id, user_id) if high_value_report else None

    # Get documents with full content
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    # Get timeline
    timeline = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    # Get notes
    notes = await db.notes.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    # Get identified grounds
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)

    # ============================================================
    # FORENSIC PIPELINE — counsel feedback 23 Feb 2026.
    # ============================================================
    # Drive the brief from cleaned/scored/strategised grounds, NOT the raw
    # database list. The pipeline:
    #     ground_normaliser  →  appeal_strength  →  ground_cleanup  →
    #     proviso_engine     →  barrister_mode   →  outcome_predictor →
    #     attack_plan        →  evidence_builder
    # The outputs (strategy, predicted_outcome, attack_plan, evidence_builder)
    # are persisted on the case record and injected into the prompt context
    # so the LLM brief and the on-screen Counsel Briefing block stay aligned.
    # ============================================================
    forensic_strategy = None
    forensic_predicted_outcome = None
    forensic_attack_plan = None
    forensic_evidence_builder = None
    forensic_proviso_summary = None
    try:
        from services.ground_normaliser import (
            EvidenceFlags,
            ground_from_dict,
            ground_to_dict,
            normalise_generated_grounds,
        )
        from services.appeal_strength import (
            CaseEvidenceProfile,
            score_grounds_for_realism,
        )
        from services.ground_cleanup import apply_cleanup
        from services.proviso_engine import apply_proviso_engine, case_proviso_summary
        from services.barrister_mode import build_strategy_summary
        from services.outcome_predictor import predict_outcome
        from services.attack_plan import generate_attack_plan
        from services.evidence_builder import generate_evidence_builder

        case_jurisdiction = str(case.get("state") or case.get("jurisdiction") or "").upper().strip()
        if case_jurisdiction == "FEDERAL":
            case_jurisdiction = "CTH"

        if grounds:
            raw_grounds = [ground_from_dict(g) for g in grounds]

            def _doc_text_lower(d: dict) -> str:
                return ((d.get("filename") or "") + " " + (d.get("content_text") or "")).lower()

            doc_blob_lower = " ".join(_doc_text_lower(d) for d in documents)

            flags = EvidenceFlags(
                transcript_support=any("transcript" in (d.get("filename", "") or "").lower() for d in documents),
                sentencing_remarks=any("sentenc" in (d.get("filename", "") or "").lower() for d in documents),
                counsel_affidavit=("counsel" in doc_blob_lower and "affidavit" in doc_blob_lower),
                juror_affidavit=("juror" in doc_blob_lower and "affidavit" in doc_blob_lower),
                psychiatric_reports=("psychiatr" in doc_blob_lower),
                judge_alone_application_material=("judge alone" in doc_blob_lower or "judge-alone" in doc_blob_lower),
                pretrial_publicity_material=("publicity" in doc_blob_lower or "media" in doc_blob_lower),
            )

            normalised = normalise_generated_grounds(
                raw_grounds=raw_grounds,
                flags=flags,
                jurisdiction=case_jurisdiction,
            )

            profile = CaseEvidenceProfile(
                has_trial_transcript=flags.transcript_support,
                has_sentencing_remarks=flags.sentencing_remarks,
                has_psychiatric_reports=flags.psychiatric_reports,
                disputed_intent=any(
                    "intent" in (g.get("title", "") or "").lower()
                    or "mens rea" in (g.get("title", "") or "").lower()
                    for g in grounds
                ),
                competing_psychiatric_opinions=("dr martin" in doc_blob_lower and "dr allnutt" in doc_blob_lower),
            )

            scored = score_grounds_for_realism(normalised, profile)
            cleaned = apply_cleanup(scored, case_jurisdiction)
            with_proviso = apply_proviso_engine(cleaned)

            forensic_strategy = build_strategy_summary(with_proviso)
            forensic_predicted_outcome = predict_outcome(forensic_strategy)
            forensic_attack_plan = generate_attack_plan(forensic_strategy)
            forensic_evidence_builder = generate_evidence_builder(forensic_strategy)
            forensic_proviso_summary = case_proviso_summary(with_proviso)

            # Replace `grounds` with the cleaned/strategised list so every
            # downstream prompt builder uses the post-pipeline data.
            grounds = [ground_to_dict(g) for g in with_proviso]

            # Persist the strategy + outcome + plans onto the case record so
            # the existing CounselBriefingBlock UI picks them up automatically
            # without a second pipeline run.
            try:
                await db.cases.update_one(
                    {"case_id": case_id},
                    {"$set": {
                        "predicted_outcome": forensic_predicted_outcome,
                        "attack_plan": forensic_attack_plan,
                        "evidence_builder": forensic_evidence_builder,
                        "proviso_summary": forensic_proviso_summary,
                        "strategy_snapshot": {
                            "primary": ground_to_dict(forensic_strategy["primary"]) if forensic_strategy.get("primary") else None,
                            "secondary": ground_to_dict(forensic_strategy["secondary"]) if forensic_strategy.get("secondary") else None,
                            "tertiary": ground_to_dict(forensic_strategy["tertiary"]) if forensic_strategy.get("tertiary") else None,
                            "abandon": [ground_to_dict(g) for g in forensic_strategy.get("abandon", [])],
                        },
                    }},
                )
            except Exception as persist_err:
                logger.warning(f"Failed to persist forensic outputs for case {case_id}: {persist_err}")
    except Exception as pipeline_err:
        logger.warning(
            f"Forensic pipeline skipped for case {case_id} ({pipeline_err}); "
            f"falling back to raw grounds for the report."
        )
    
    # ── Auto-detect case metadata if still defaults (HARDENED via call_llm_for_json) ──
    # DO NOT UNDO — Also re-detect if sentence contains crime narrative (e.g. "for murdering")
    _current_sentence = (case.get('sentence') or "").strip()
    _sentence_has_narrative = bool(re.search(r'\bfor\s+(?:murder|kill|assault|robb|stab|rap|kidnap|abus|supplying|dealing)', _current_sentence, re.I)) if _current_sentence else False
    needs_detection = (
        not case.get('offence_category')
        or not case.get('offence_type')
        or not case.get('state')
        or (not _current_sentence or _sentence_has_narrative)
    )
    if needs_detection and documents:
        try:
            combined_text = ""
            for d in documents:
                ct = d.get("content_text") or ""
                if ct:
                    combined_text += f"\n--- {d.get('filename','')} ---\n{ct[:6000]}\n"
            if len(combined_text) > 200:
                detect_prompt = f"""Analyse the following case documents and extract metadata.
Return ONLY valid JSON (no markdown, no explanation):
{{
  "offence_category": "<one of: homicide, assault, sexual_offences, robbery_theft, drug_offences, fraud_dishonesty, firearms_weapons, domestic_violence, public_order, terrorism, driving_offences>",
  "offence_type": "<specific offence e.g. Murder, Assault Occasioning ABH, Armed Robbery>",
  "sentence": "<the HEAD SENTENCE and non-parole period ONLY. Format: '[X] years imprisonment with a non-parole period of [Y] years [and Z months]'. Do NOT include the crime description, victim details, or case narrative. If life sentence, state 'Life imprisonment with a non-parole period of [X] years'. If sentence not stated, null.>",
  "state": "<one of: nsw, vic, qld, sa, wa, tas, nt, act, cth — if determinable; map federal/Commonwealth → cth>",
  "court": "<court name if found>"
}}
Rules:
- offence_category MUST be from the listed values only. Read the ACTUAL documents — do NOT default to homicide.
- If the document is about assault, category is "assault". If robbery, "robbery_theft", etc.
- sentence must be ONLY the numerical sentence and non-parole period. Never include what the crime was or who the victim was.
- If a field cannot be determined, set to null. state must be lowercase.

DOCUMENTS:
{combined_text[:30000]}"""

                def _validate_metadata(parsed: dict) -> bool:
                    valid_cats = ["homicide","assault","sexual_offences","robbery_theft","drug_offences","fraud_dishonesty","firearms_weapons","domestic_violence","public_order","terrorism","driving_offences"]
                    cat = parsed.get("offence_category")
                    return cat in valid_cats if cat else True

                meta = await call_llm_for_json(
                    system_prompt="You are a legal document analyst. Extract factual metadata only. Return valid JSON.",
                    user_prompt=detect_prompt,
                    session_id=f"rpt_detect_{case_id}",
                    task_type="metadata_detection",
                    validation_fn=_validate_metadata,
                )

                valid_cats = ["homicide","assault","sexual_offences","robbery_theft","drug_offences","fraud_dishonesty","firearms_weapons","domestic_violence","public_order","terrorism","driving_offences"]
                # State allowlist — counsel feedback 23 Feb 2026: must include
                # Commonwealth/federal matters. Normalise "federal" → "cth".
                valid_sts = ["nsw","vic","qld","sa","wa","tas","nt","act","cth","federal"]
                update_fields = {}
                if meta.get("offence_category") in valid_cats:
                    update_fields["offence_category"] = meta["offence_category"]
                if meta.get("offence_type"):
                    update_fields["offence_type"] = meta["offence_type"]
                if meta.get("sentence"):
                    # DO NOT UNDO — Clean sentence to strip crime descriptions, victim info
                    cleaned_sentence = _clean_sentence_candidate(meta["sentence"])
                    if _is_valid_sentence_candidate(cleaned_sentence):
                        update_fields["sentence"] = cleaned_sentence
                    elif meta["sentence"].strip():
                        update_fields["sentence"] = meta["sentence"].strip()
                if meta.get("state") and str(meta["state"]).lower() in valid_sts:
                    state_val = str(meta["state"]).lower()
                    # Counsel feedback 23 Feb 2026: federal → cth normalisation.
                    if state_val == "federal":
                        state_val = "cth"
                    update_fields["state"] = state_val
                if meta.get("court"):
                    update_fields["court"] = meta["court"]
                if update_fields:
                    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
                    update_fields["classification_source"] = "ai_detected"
                    update_fields["requires_metadata_review"] = True
                    await db.cases.update_one({"case_id": case_id}, {"$set": update_fields})
                    # Re-read case with updated metadata
                    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
                    logger.info(f"Report gen auto-detected metadata for {case_id}: {update_fields}")
        except Exception as e:
            logger.warning(f"Report gen auto-detect failed for {case_id}: {e}")
    
    # Get offence-specific context — NO SILENT DEFAULTS
    offence_category = case.get('offence_category') or 'general'
    offence_context = get_offence_context(case)
    category_data = OFFENCE_CATEGORIES.get(offence_category) or {}
    category_name = category_data.get('name', offence_category.replace('_', ' ').title())
    state = case.get('state') or ''
    state_info = AUSTRALIAN_STATES.get(state, {})
    
    # Context limits — FULL DETAIL for quality reports
    context_limits = {
        "quick_summary": {
            "per_doc_chars": 700,
            "total_doc_chars": 6000,
            "timeline_limit": 40,
            "notes_limit": 20,
            "note_chars": 180,
            "grounds_limit": 30,
            "ground_desc_chars": 200,
            "ground_analysis_chars": 200,
            "ground_deep_chars": 0,
        },
        "full_detailed": {
            "per_doc_chars": 2400,
            "total_doc_chars": 24000,
            "timeline_limit": 150,
            "notes_limit": 80,
            "note_chars": 500,
            "grounds_limit": 80,
            "ground_desc_chars": 600,
            "ground_analysis_chars": 500,
            "ground_deep_chars": 0,
        },
        "extensive_log": {
            "per_doc_chars": 3200,
            "total_doc_chars": 32000,
            "timeline_limit": 200,
            "notes_limit": 100,
            "note_chars": 600,
            "grounds_limit": 100,
            "ground_desc_chars": 800,
            "ground_analysis_chars": 700,
            "ground_deep_chars": 700,
        },
    }
    limits = context_limits.get(report_type, context_limits["quick_summary"])

    # Prepare comprehensive context for AI with bounded document content
    case_context = f"""
=== CASE INFORMATION ===
Title: {case.get('title', 'N/A')}
Defendant: {case.get('defendant_name', 'N/A')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}
Judge: {case.get('judge', 'N/A')}
Sentence: {case.get('sentence', 'N/A')}
Summary: {case.get('summary', 'N/A')}

{offence_context}
"""

    doc_context = build_document_context(
        documents,
        per_doc_char_limit=limits["per_doc_chars"],
        total_char_budget=limits["total_doc_chars"],
        include_description=True,
        content_heading="CONTENT"
    )
    
    # Include bounded document content for cross-referencing
    if documents:
        case_context += f"=== CASE DOCUMENTS ({doc_context['included_docs']} included / {len(documents)} total files) ===\n"
        case_context += doc_context["text"] + "\n"
        if doc_context["omitted_docs"] > 0:
            case_context += f"[Note: {doc_context['omitted_docs']} document(s) omitted from prompt for speed optimisation.]\n"
    else:
        case_context += "=== NO DOCUMENTS UPLOADED ===\n"

    if timeline:
        timeline_slice = timeline[:limits["timeline_limit"]]
        case_context += f"\n=== TIMELINE OF EVENTS ({len(timeline_slice)} included / {len(timeline)} total events) ===\n"
        for event in timeline_slice:
            case_context += f"- {event.get('event_date', 'Unknown')}: [{event.get('event_type')}] {event.get('title')}\n"
            if event.get('description'):
                case_context += f"  Details: {event.get('description')}\n"
        if len(timeline) > limits["timeline_limit"]:
            case_context += f"[... {len(timeline) - limits['timeline_limit']} additional events omitted for speed ...]\n"

    if notes:
        notes_slice = notes[:limits["notes_limit"]]
        case_context += f"\n=== LEGAL NOTES ({len(notes_slice)} included / {len(notes)} total notes) ===\n"
        for note in notes_slice:
            case_context += f"- [{note.get('category')}] {note.get('title')}: {note.get('content', '')[:limits['note_chars']]}\n"
        if len(notes) > limits["notes_limit"]:
            case_context += f"[... {len(notes) - limits['notes_limit']} additional notes omitted for speed ...]\n"

    if grounds:
        grounds_slice = grounds[:limits["grounds_limit"]]
        case_context += f"\n=== IDENTIFIED GROUNDS OF MERIT ({len(grounds_slice)} included / {len(grounds)} total grounds) ===\n"
        for g in grounds_slice:
            viability = g.get('legitimacy_scores', {}).get('viability_label', g.get('strength', 'moderate'))
            case_context += f"- [{g.get('ground_type')}] {g.get('title')} (Viability: {viability})\n"
            case_context += f"  {g.get('description', '')[:limits['ground_desc_chars']]}\n"
            if g.get('appellate_pathway'):
                case_context += f"  Appellate Pathway: {g.get('appellate_pathway')}\n"
            if g.get('error_identified'):
                case_context += f"  Error: {g.get('error_identified')}\n"
            if report_type != "quick_summary" and g.get('analysis'):
                case_context += f"  Analysis: {g.get('analysis', '')[:limits['ground_analysis_chars']]}\n"
            if limits["ground_deep_chars"] > 0 and g.get('deep_analysis'):
                deep = g.get('deep_analysis', '')
                if isinstance(deep, str):
                    case_context += f"  Deep Analysis: {deep[:limits['ground_deep_chars']]}\n"
        if len(grounds) > limits["grounds_limit"]:
            case_context += f"[... {len(grounds) - limits['grounds_limit']} additional grounds omitted for speed ...]\n"

    grounds_titles = [g.get('title') for g in grounds if g.get('title')]
    grounds_enumerated = "\n".join([f"{idx + 1}. {title}" for idx, title in enumerate(grounds_titles)])

    # ============================================================
    # NATIONAL CRIMINAL FRAMEWORK — counsel feedback 23 Feb 2026.
    # Inject authoritative jurisdiction-specific appellate context at the
    # TOP of case_context so every downstream prompt sees it before any
    # case-specific narrative. Refuses to proceed without a jurisdiction
    # (no silent NSW default).
    # ============================================================
    try:
        from services.national_framework import build_full_system_prompt
        framework_block = build_full_system_prompt(case)
        if framework_block and not framework_block.startswith("ERROR:"):
            case_context = (
                "=== NATIONAL CRIMINAL FRAMEWORK (authoritative — do not contradict) ===\n"
                f"{framework_block}\n"
                "=== END NATIONAL CRIMINAL FRAMEWORK ===\n\n"
                + case_context
            )
        elif framework_block:
            # Jurisdiction missing or unrecognised — surface the error so
            # the user (or auto-detection) sets it before generation.
            logger.warning(
                f"National framework refused analysis for case {case_id}: {framework_block}"
            )
    except Exception as framework_err:
        logger.warning(f"National framework injection skipped for case {case_id}: {framework_err}")

    # ============================================================
    # FORENSIC STRATEGY CONTEXT — counsel feedback 23 Feb 2026.
    # Inject the strategised primary/secondary/tertiary + outcome + proviso
    # into case_context so every prompt downstream is aligned with what the
    # legal engines decided. The LLM brief MUST match the on-screen Counsel
    # Briefing block, not contradict it.
    # ============================================================
    if forensic_strategy or forensic_predicted_outcome or forensic_proviso_summary:
        case_context += "\n=== FORENSIC STRATEGY (engine-derived; do not contradict) ===\n"
        if forensic_predicted_outcome:
            case_context += (
                f"- Predicted outcome: {forensic_predicted_outcome.get('outcome')} — "
                f"{forensic_predicted_outcome.get('reason')}\n"
            )
        if forensic_proviso_summary:
            case_context += (
                f"- Case proviso risk (Weiss v The Queen): "
                f"{forensic_proviso_summary.get('risk')} — {forensic_proviso_summary.get('summary')}\n"
            )
        for role in ("primary", "secondary", "tertiary"):
            sg = (forensic_strategy or {}).get(role)
            if sg is not None:
                case_context += (
                    f"- {role.upper()} ground: \"{sg.title}\" "
                    f"[{sg.type}] viability={sg.viability} "
                    f"proviso_risk={getattr(sg, 'proviso_risk', 'n/a')} "
                    f"crown_strength={getattr(sg, 'crown_strength', 'n/a')}\n"
                )
        if forensic_strategy and forensic_strategy.get("abandon"):
            ab_titles = [g.title for g in forensic_strategy["abandon"]][:5]
            case_context += f"- ABANDON candidates (do not lead with these): {'; '.join(ab_titles)}\n"
        case_context += (
            "INSTRUCTION: lead the brief with the PRIMARY ground; SECONDARY then TERTIARY. "
            "Adopt the predicted outcome. Address the proviso risk explicitly for any conviction "
            "ground rated moderate/high. Do NOT introduce grounds outside this strategy.\n"
        )

    # ================= INJECT STRUCTURED PIPELINE DATA =================
    if high_value_report and structured_context:
        facts_text = "\n".join([f"- {f}" if isinstance(f, str) else f"- {f}" for f in structured_context["facts"]]) if structured_context["facts"] else "No extracted facts available."
        events_text = "\n".join([f"- {e}" if isinstance(e, str) else f"- {e}" for e in structured_context["events"]]) if structured_context["events"] else "No extracted events available."
        findings_text = "\n".join([f"- {f}" if isinstance(f, str) else f"- {f}" for f in structured_context["findings"]]) if structured_context["findings"] else "No extracted findings available."

        verified_text = ""
        for vi in structured_context["verified_issues"]:
            verified_text += f"\n--- Issue: {vi.get('title', 'Untitled')} (Type: {vi.get('ground_type', 'unknown')}) ---\n"
            verified_text += f"  Verification status: {vi.get('verification_status', 'unverified')}\n"
            if vi.get("supporting_items"):
                verified_text += f"  Supporting items: {len(vi['supporting_items'])}\n"
            if vi.get("undermining_items"):
                verified_text += f"  Undermining items: {len(vi['undermining_items'])}\n"
            if vi.get("legitimacy_scores"):
                verified_text += f"  Legitimacy: {vi['legitimacy_scores']}\n"

        case_context += f"""
=== STRUCTURED PIPELINE DATA (VERIFIED MATERIAL) ===

CASE FACTS:
{facts_text}

TIMELINE EVENTS:
{events_text}

KEY FINDINGS:
{findings_text}

VERIFIED APPEAL ISSUES:
{verified_text if verified_text else "No verified issues available."}
"""

    # Define prompts based on report type with offence-specific language
    base_system = get_offence_system_prompt(offence_category, state)
    report_guardrails = f"""
MANDATORY GUARDRAILS:
- Use a HYBRID tone: court-ready legal analysis + plain-English action notes for the client.
- Use Australian English only.
- Anchor findings to supplied case material; clearly mark uncertainty when evidence is incomplete.
- Include legislation as: section + Act + jurisdiction + year (e.g. s.18 Crimes Act 1900 (NSW) for NSW, s.3 Crimes Act 1958 (Vic) for VIC).
- Include sentencing comparisons and precedent outcomes where relevant.
- DO NOT include cost estimates, fee ranges, funding commentary, or budget analysis.
- DO NOT include witness contradiction sections or witness credibility scoring sections.

LANGUAGE RULES — ABSOLUTE AND NON-NEGOTIABLE:
- This report is an EDUCATIONAL TOOL. It is NOT written by a legal team speaking on behalf of the applicant.
- NEVER use the words "we", "us", "our", or "them" when referring to the legal team, analysis team, or report authors.
- NEVER use the words "you" or "your" when addressing the reader or the applicant. WRONG: "The appeal is your opportunity to challenge your conviction." RIGHT: "The appeal represents an opportunity for the applicant to challenge the conviction."
- Instead of "we are arguing" write "the applicant argues" or "this analysis identifies".
- Instead of "we will file" write "the legal professional will file" or "the applicant should file".
- Instead of "our submissions" write "the submissions" or "the applicant's submissions".
- Instead of "contact us" write "contact the legal professional" or "contact the assisting legal practitioner".
- Instead of "we are aiming to show" write "the appeal aims to demonstrate" or "the applicant seeks to establish".
- Instead of "our claims" write "the applicant's claims" or "the claims advanced".
- Instead of "your appeal" write "the appeal". Instead of "your conviction" write "the conviction". Instead of "your sentence" write "the sentence".
- Instead of "you should" write "the applicant should". Instead of "you may" write "the applicant may". Instead of "for you" write "for the applicant".
- The report must read as a neutral educational analysis document, NOT as a first-person legal team communication and NOT as a second-person advisory letter.
- Use third-person references throughout: "the applicant", "the defendant", "the legal professional", "this analysis", "the appeal".
- Violations of this rule make the report legally problematic and unprofessional.

NO PLACEHOLDER TEXT — ABSOLUTE RULE:
- NEVER write future-tense placeholder text like "The table will reference...", "Details will be provided...", "This section will include...", "Content will be added...", or "Analysis will cover...".
- Every sentence must contain ACTUAL analysis, ACTUAL data, or ACTUAL legal content. If a table cannot be populated with real data from the case material, populate it with the best available comparable cases from Australian jurisprudence.
- If information is unavailable, state that explicitly ("No sentencing comparisons could be identified from the supplied material") rather than promising future content.

FORENSIC APPELLATE LANGUAGE — ABSOLUTE AND NON-NEGOTIABLE:
Appellate work is about ARGUABILITY, not declarations. All conclusions must be framed forensically:
- BANNED PHRASES (NEVER use these): "The trial judge erred", "The judge clearly erred", "This clearly shows", "This proves", "This demonstrates conclusively", "The conviction is unsafe", "The sentence is excessive", "The error is established".
- REQUIRED FORENSIC FRAMING (use these instead):
  * "It is arguable that the trial judge erred in..."
  * "It is contended that..."
  * "There is a tenable argument that..."
  * "On one view of the evidence..."
  * "It may be submitted that..."
  * "A reasonable argument exists that..."
  * "The available material supports the contention that..."
  * "It is open to the appellant to argue that..."
- The distinction is critical: an appeal brief identifies ARGUABLE errors, it does not declare findings of fact. The Court of Criminal Appeal makes findings — the brief identifies where findings are open.
- Exception: When citing what a court HAS decided in a precedent case, declarative language is appropriate (e.g. "In R v Smith, the Court held that...").
- For AGGRESSIVE MODE only: stronger language is permitted (e.g. "The Crown's position is untenable", "The error is compelling") but still avoid absolute declarations about the current case.

CONTENT QUALITY — STRICTLY ENFORCED (violations make the report worthless):
- DO the analysis. Do NOT describe what analysis should be done. WRONG: "Delve into aggravating and mitigating factors." RIGHT: "Under the relevant sentencing legislation for {state_info.get('name', 'this jurisdiction')}, the aggravating factors include [cite specific factors from the case material]. However, it is arguable that the sentencing judge failed to give adequate weight to [specific mitigating factor with statutory reference]..."
- NEVER create filler sections with titles like "URGENCY PRIORITY", "RELEVANCE", "KEY TAKEAWAY", "SUMMARY", "OVERVIEW" as standalone sections. These are padding. Instead, weave relevance and urgency INTO the substantive analysis.
- NEVER write generic consultant-speak like "Leverage legal databases to draw parallels that authenticate excessive sentencing claims through empirical trends." Instead, NAME the specific cases, cite the specific sentencing outcomes, and EXPLAIN the specific parallels.
- Every paragraph MUST reference specific names, dates, section numbers, case citations, or document names from the supplied case material. If a paragraph could apply to ANY appeal case, it is too generic — rewrite it with THIS case's specific facts.
- Avoid repetition across sections. If a point is already covered, deepen it with NEW evidence, dates, or authority rather than restating it.
- Do NOT reuse boilerplate phrases. Every paragraph must read as drafted specifically for this case and this report tier.
- For legislation sections: Do NOT just name the Act and describe what it covers in general terms. APPLY each provision to THIS case's specific facts. WRONG: "The sentencing Act discusses parole periods." RIGHT: "Under the applicable sentencing legislation for {state_info.get('name', 'the relevant jurisdiction')}, the non-parole period must reflect the objective seriousness of the offence. In [defendant name]'s case, the [X]-year non-parole period imposed is arguable as disproportionate when compared with [specific comparator case with citation]..."
- For precedent/sentencing tables: Include the full case citation, the specific factual similarity to THIS case, the actual sentence imposed, and the specific relevance to the current appeal. NEVER use a one-line vague description.

LEGISLATION ACCURACY — CRITICAL ANTI-HALLUCINATION RULE:
- ALWAYS cite the FULL Act name with the year and jurisdiction (e.g. "Crimes Act 1900 (NSW)", "Crimes Act 1958 (Vic)", NOT "Crimes Act" or "the Act").
- Use ONLY the legislation for the case's jurisdiction ({state_info.get('name', 'UNSPECIFIED')}). Do NOT cite NSW legislation for non-NSW cases.
- Where RECENT LEGISLATION UPDATES are provided in the case context, you MUST reference these current amendments where they are relevant to the case. Do NOT cite repealed or superseded provisions when a current amended version exists.
- Do NOT fabricate section numbers. If the exact section is not known, reference the Act by name only and note that the specific section should be verified.
- Where the case involves a recently commenced offence (post-2022), check whether transitional provisions apply — the offence must have been committed AFTER the commencement date for the new provisions to apply.

JURISDICTION FIDELITY — ABSOLUTE AND NON-NEGOTIABLE:
- The case jurisdiction is specified in the CASE PROFILE above. You MUST use ONLY the legislation, sentencing acts, evidence acts, criminal codes, and appellate procedures from THAT jurisdiction.
- Do NOT default to NSW legislation when analysing a case from another jurisdiction. For example:
  * A VICTORIA case uses Crimes Act 1958 (Vic), Sentencing Act 1991 (Vic), Evidence Act 2008 (Vic), Criminal Procedure Act 2009 (Vic) — NOT the NSW equivalents.
  * A QUEENSLAND case uses Criminal Code Act 1899 (Qld), Penalties and Sentences Act 1992 (Qld), Evidence Act 1977 (Qld) — NOT the NSW equivalents.
  * A SOUTH AUSTRALIA case uses Criminal Law Consolidation Act 1935 (SA), Sentencing Act 2017 (SA), Evidence Act 1929 (SA) — NOT the NSW equivalents.
  * A WESTERN AUSTRALIA case uses Criminal Code Act Compilation Act 1913 (WA), Sentencing Act 1995 (WA), Evidence Act 1906 (WA) — NOT the NSW equivalents.
  * A TASMANIA case uses Criminal Code Act 1924 (Tas), Sentencing Act 1997 (Tas), Evidence Act 2001 (Tas) — NOT the NSW equivalents.
  * A NORTHERN TERRITORY case uses Criminal Code Act 1983 (NT), Sentencing Act 1995 (NT), Evidence (National Uniform Legislation) Act 2011 (NT) — NOT the NSW equivalents.
  * An ACT case uses Criminal Code 2002 (ACT) and Crimes Act 1900 (ACT), Crimes (Sentencing) Act 2005 (ACT), Evidence Act 2011 (ACT) — NOT the NSW equivalents.
- Commonwealth/Federal legislation (Criminal Code Act 1995 (Cth), Crimes Act 1914 (Cth), Judiciary Act 1903 (Cth)) applies across ALL jurisdictions and may be cited where relevant.
- If the jurisdiction is UNSPECIFIED, you MUST flag this explicitly and state: "The jurisdiction has not been confirmed. The following analysis references [State] legislation, which must be verified as correct for the actual jurisdiction of this case."

STRICT NO-HALLUCINATION CONTROLS:
- Do NOT invent, fabricate, or guess ANY of the following: case names, case citations, section numbers, Act names, judge names, dates, sentences, or penalty amounts.
- If you do not know the exact citation for a case, do NOT make one up. Instead write: "See [description of relevant authority — e.g. 'the leading NSW authority on provocation'] — citation should be verified by the legal practitioner."
- Do NOT cite cases that do not exist. If you reference a case by name, you MUST be confident it is a real decided case. If uncertain, flag it: "[Citation to be verified]".
- Do NOT invent section numbers. If a provision exists but the exact section number is uncertain, reference the Act and Part/Division only: "See Part 3 of the Crimes Act 1900 (NSW)" rather than fabricating a specific section.
- Do NOT assume facts not in the supplied case material. If the case material does not mention a particular fact (e.g. the defendant's age, prior criminal history, mental health), do NOT assume or infer it. State: "The supplied material does not address [X]."
- Do NOT hallucinate sentencing statistics or comparative data. If you provide sentencing ranges or median sentences, these must be from real, verifiable sources. If uncertain, state: "Sentencing statistics should be verified against Judicial Commission of [State] data."

FORMATTING RULES — STRICTLY ENFORCED:
- DO NOT begin your response with any preamble, greeting, or introduction.
- DO NOT use placeholder notes in brackets like "[Note: Continue...]", "[Insert details...]". Every section MUST contain COMPLETE, REAL content.
- Every section heading MUST be followed by substantive content (minimum 3-4 detailed paragraphs). If a section cannot be substantiated from the case material, omit it entirely.
- Include the year in ALL legislation references (e.g. Crimes Act 1900 (NSW), NOT just Crimes Act (NSW)).
- SECTION HEADINGS: Use ONLY ## for numbered section headings (e.g. ## 1. EXECUTIVE BRIEF). Do NOT create sub-sections with ### headings. Do NOT put bold text on its own line as a sub-heading. Instead, write flowing paragraphs and use bold text inline (e.g. "The **legal threshold** for this ground requires...").
- CRITICAL MARKDOWN SPACING: Every heading line (##, ###, ####) MUST appear on its OWN line with a BLANK LINE BEFORE IT and a BLANK LINE AFTER IT. NEVER place a heading at the end of a paragraph (e.g. "...appellant. ## 2. CHRONOLOGY"). NEVER place prose on the same line as a heading. Non-compliant output will be rejected.
- FOR GROUND ANALYSIS: Write each ground as a continuous series of detailed paragraphs (minimum 300 words in Quick Summary, 800+ words in Full Detailed, 1200+ words in Extensive). Do NOT use bullet points. Cover the legal threshold, case facts, viability, Crown response, defence rebuttal, and impact all within flowing prose.
"""
    
    if report_type == "quick_summary":
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating a FREE Quick Summary — an ISSUE IDENTIFICATION report. Its purpose is to identify and list the potential grounds of appeal, NOT to provide deep legal analysis. Deliver real legal value in a concise overview, then clearly explain what deeper paid reports add. IMPORTANT: Write at least 2000 words. Narrative sections (Case Snapshot, Sentencing Overview, Value Statement) must have 3-5 substantive paragraphs. Structured sections (Issues, Grounds, Legislation) use the specified format (numbered items, lists, or tables).

""" + FORENSIC_LANGUAGE_RULE + """"""
        user_prompt = f"""Analyse this {category_name.lower()} appeal matter and produce a QUICK SUMMARY REPORT (Issue Identification).

{case_context}

Write MINIMUM 2000 words. This is an ISSUE IDENTIFICATION report — identify all potential grounds clearly but do not provide the deep appellate pathway analysis (that is for paid reports). Structure EXACTLY as follows:

## 1. CASE SNAPSHOT
3-4 paragraphs covering: defendant, offence, jurisdiction, sentence imposed, non-parole period, key procedural dates, presiding judge, and what material was reviewed. Be specific to the supplied facts.

MANDATORY: Start this section with: "This analysis is based on [X] documents and [Y] timeline events. [Z] grounds of appeal have been identified." Use EXACT counts from supplied data.

## 2. PRIMARY ISSUES IDENTIFIED
6-10 numbered items. Each must include:
- Issue title framed as an appellate ground (e.g. "Failure to Properly Evaluate Psychiatric Evidence")
- Which document/evidence it comes from
- Why it matters for the appeal

## 3. ALL GROUNDS IDENTIFIED (PREVIEW)
You MUST list EVERY ground identified. For each ground:
- Ground title + type (e.g., Procedural Error, Sentencing Error, Miscarriage of Justice)
- Appellate viability: Arguable — Strong / Arguable — Moderate / Requires Development
- 2-3 sentence legal rationale referencing the specific case facts
- One immediate action step

Do NOT use percentage success rates. Use appellate viability language only.

## 4. KEY LEGISLATION (PREVIEW)
List the most relevant statutory provisions from {state_info.get('name', 'the relevant jurisdiction')} and Commonwealth law. You MUST cite the CORRECT legislation for the case's jurisdiction — NOT NSW legislation for non-NSW cases. Include ACTUAL section numbers, years, and one-line relevance notes. Cite at minimum:
- The jurisdiction's primary Criminal Code/Act (with specific sections relevant to the offence)
- The jurisdiction's Sentencing Act (with relevant sentencing provisions — aggravating/mitigating factors, non-parole periods)
- The jurisdiction's Evidence Act (if evidentiary issues arise)
- The jurisdiction's Criminal Appeal Act (appeal grounds and powers)
- Any Commonwealth legislation that applies
If the exact section number is not known, do NOT include that entry.

## 5. SENTENCING OVERVIEW
2-3 paragraphs comparing the sentence imposed against typical appellate principles for this offence category. Include a mini comparison table:
| Comparator Case | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Key Insight |
Include at least 3 rows. Do NOT include cases with "[Surname]" or placeholder citations.

## 6. APPEAL OUTLOOK
Overall appellate viability assessment: Arguable — Strong / Arguable — Moderate / Requires Development.
2-3 paragraphs explaining the reasoning, strongest pathway to relief, and main risk factors. Do NOT use percentages.

## 7. PLAIN ENGLISH GUIDE
Explain the case and appeal in clear, plain English for a non-lawyer. CRITICAL: Use ONLY third-person language ("the applicant", "the legal professional"). ABSOLUTE BAN on "we", "us", "our", "you", "your".

IMPORTANT:
- No cost estimates or funding discussion.
- No witness contradiction section.
- Be specific to the supplied material — do not write generic legal advice.
- Do NOT use percentage success rates anywhere. Use appellate viability language.
- Do NOT include "Similar Cases (AI-Suggested)" with unverified citations. If citing cases, use REAL citations only.

GROUNDS TO COVER (MUST INCLUDE ALL):
{grounds_enumerated}

MATERIAL COUNTS:
- Total documents analysed: {len(documents)}
- Total timeline events: {len(timeline)}
- Total grounds identified: {len(grounds)}"""

    elif report_type == "full_detailed":
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating a PAID Full Detailed Report ($150 AUD). This report is the PRIMARY product the client is paying for.

CRITICAL RULES FOR THIS REPORT:
1. The client ALREADY has a FREE Quick Summary. If ANY section in this report resembles the Quick Summary, the product is WORTHLESS.
2. Every section must be 3x MORE detailed than the equivalent free report section.
3. Every paragraph must cite SPECIFIC case facts: names (Joshua Homann, Kirralee Paepaerei, Justice McCallum), dates (21 September 2015, 25 May 2018), section numbers (s.23A Crimes Act 1900 (NSW)), and document names.
4. NEVER write generic legal explanations. WRONG: "The appeal process involves reviewing the original decision." RIGHT: "Homann's appeal to the NSWCCA challenges the 30-year sentence imposed by Justice McCallum on 25 May 2018 for the murder of Kirralee Paepaerei, arguing that the non-parole period of 22 years and 6 months is manifestly excessive when compared with..."
5. EVERY ground listed in GROUNDS TO COVER MUST be covered in FULL in Sections 4, 7, 11, and 15. If there are 5 grounds, write 5 full analyses. NO OMISSIONS.
6. Write in FLOWING PARAGRAPHS, not bullet points. Bullet points are ONLY acceptable inside tables or checklists.
7. Each section heading must be followed by AT LEAST 4-6 detailed paragraphs of substantive analysis.

Include forensic appellate strategy, professional courtroom framing, and plain-English action notes. Include hyperlinks to AustLII legislation, case databases, and court forms where the URL is known and verifiable. Do NOT fabricate URLs — if the exact AustLII path is not known, reference the legislation by name and section number only.
CRITICAL: NEVER use placeholder text in parentheses like '(Entries will develop...)'. Every section MUST have REAL, SUBSTANTIVE CONTENT with actual legal analysis."""
        user_prompt = f"""Create a FULL DETAILED LEGAL ANALYSIS REPORT for this {category_name.lower()} appeal case.

{case_context}

GROUNDS TO COVER — YOU MUST INCLUDE EVERY SINGLE ONE (if 5 grounds, write 5 full analyses):
{grounds_enumerated}

MATERIAL COUNTS (use these exact numbers in the report):
- Total documents analysed: {len(documents)}
- Total timeline events: {len(timeline)}
- Total grounds identified: {len(grounds)}

TARGET: 15,000-20,000 words minimum. This is a $150 AUD paid product. It must be AT LEAST 3x the depth of the free Quick Summary in EVERY section.

ANTI-LAZINESS RULES — VIOLATIONS MAKE THE REPORT WORTHLESS:
1. Section 1 (Executive Brief): MUST be 4-6 paragraphs with strategic assessment, NOT just a case snapshot rehash. Name the strongest ground, the weakest ground, the most likely outcome, and the recommended immediate action.
2. Section 2 (Forensic Chronology): MUST have 12+ dated events in FULL PARAGRAPH FORMAT (not bullet points). Each entry: date, what happened, source document, legal significance. Write 3-4 sentences per event minimum.
3. Section 3 (Document Evidence Digest): MUST analyse EVERY uploaded document individually with key extracts, reliability, and appellate relevance. One paragraph per document minimum.
4. Section 4 (Grounds Portfolio): MUST cover EVERY ground with 800+ words each. Include: legal threshold, case-specific facts, viability rating with reasoning, Crown response prediction (what will the prosecution argue?), defence rebuttal strategy, practical impact if ground succeeds. Write as flowing prose, NOT bullets.
5. Section 7 (Outcome Options): MUST write 300+ words for EACH outcome pathway (conviction quashed, retrial, downgrade, sentence reduction, appeal dismissed). Reference which specific grounds support each outcome.
6. Section 11 (How to Argue): MUST cover EVERY ground — if there are 5 grounds, write 5 complete argument strategies with lead proposition, supporting authority, prosecution answer, and rebuttal. 400+ words per ground.
7. Section 12 (Submissions Blueprint): Write ACTUAL draft submission paragraphs ready for court. Include specific argument sequences, authority placement, and time allocation. NOT bullet point summaries.
8. Section 15 (Client Brief): MUST cover EVERY ground and EVERY outcome in plain English. Explain what each ground means in simple terms and what happens if it succeeds. 1000+ words minimum for this section.

SECTION ORDERING: Analysis first, then Strategy, then Practical steps, then Client brief at the end.

Use this exact structure:

## 1. EXECUTIVE BRIEF
High-impact strategic summary: 4-6 paragraphs covering strongest grounds, jurisdiction posture, likely pathways to relief, urgency items, recommended strategy, and risk factors. Include case snapshot (defendant, offence, sentence, court, judge) and primary issues. This section must ADD strategic value beyond the free report.

MANDATORY: Start with: "This analysis is based on [X] documents and [Y] timeline events. [Z] grounds of appeal have been identified." Use EXACT counts.

## 2. FORENSIC CASE CHRONOLOGY
Full chronological reconstruction with 12+ dated entries. Each entry must be a FULL PARAGRAPH (3-4 sentences minimum) with: exact date, what occurred, which document/evidence supports it, and legal significance for the appeal. Write this as a narrative, NOT as bullet points.

## 3. DOCUMENT EVIDENCE DIGEST
For EACH document uploaded: title, key extracts (quote directly), reliability context, probative value, and specific appellate relevance. One detailed paragraph per document minimum.

## 4. GROUNDS OF MERIT — APPELLATE PATHWAY ANALYSIS
For EACH ground listed in GROUNDS TO COVER (ALL of them — no omissions):
Write as "Ground X: [Exact Title]" then 800+ words using the MANDATORY appellate structure:

**Appellate Pathway:** State the specific statutory provision engaged (e.g. "Miscarriage of justice under s 6(1) Criminal Appeal Act 1912 (NSW)")

**Ground:** Frame the arguable error forensically: "It is arguable that the trial judge erred in failing to..." or "It is contended that..." — NOT bare declarations.

**Error Identified:** What specifically is arguable as having gone wrong at trial. Reference case facts, dates, evidence. Use forensic language: "It is arguable that...", "It is contended that...".

**Materiality:** Why this error matters. How it affected the verdict or sentence.

**Consequence:** Legal consequence (verdict unsafe, miscarriage of justice, sentence set aside).

**Appellate Viability:**
- Outcome impact: Determinative / Influential / Minor
- Legal alignment: Direct authority / Analogous / Weak
- Evidence support: Strong / Partial / Limited

**Crown Response:** What the prosecution will argue.
**Defence Rebuttal:** Counter with specific authority.

Write as flowing prose. Minimum 800 words per ground.

## 5. COMPARATIVE SENTENCING TABLE (8+ CASES)
CRITICAL: Produce an ACTUAL populated markdown table with real case data — NEVER placeholder text like "The table will reference..." or "Details will be provided...".
Markdown table with 8+ comparable cases, then Detailed Outcome Analysis paragraph for each row.
| Case | Offence | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Reduction (Years + %) | Key Reason |
Include AustLII search URL.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Markdown table with 8+ rows:
| Common Ground | Frequency in Comparable Appeals | Typical Success Pattern | Best Supporting Evidence |

## 7. OUTCOME OPTIONS AVAILABLE
First, markdown table. Then 300+ words for EACH pathway referencing specific grounds from Section 4:
- **Conviction quashed** — which grounds support this, legal threshold, likelihood
- **Retrial ordered** — implications, timeframes, changes
- **Conviction substituted/downgraded** — legal basis, sentence impact
- **Sentence reduced as manifestly excessive** — before/after with specific numbers
- **Appeal dismissed** — consequences, further options (High Court)

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
Specific missing material with urgency priority (Critical/Important/Helpful) and exact remediation steps.

## 9. PRECEDENT OUTCOME MATRIX (10-12 CASES)
For each: citation, factual similarity, hearing outcome, extracted legal principle.

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP
APPLY each provision to THIS case — section number, Act name with year, specific relevance to Homann's appeal.

## 11. HOW TO ARGUE EACH TOP GROUND
For EACH ground (ALL of them — no omissions), write 400+ words covering:
- Lead proposition (core argument in 2 sentences)
- Supporting authority cluster (statute + 2-3 precedent anchors with citations)
- Expected prosecution answer (what will the Crown argue?)
- Rebuttal strategy with specific authority
- How establishing this ground leads to successful appeal outcome

## 12. SUBMISSIONS BLUEPRINT
Write ACTUAL draft submission text ready for court. Not bullet point summaries.
Written submission strategy: full argument sequence paragraphs, authority placement, framing of each ground.
Oral submission strategy: likely bench questions with response lines, time allocation per ground.

## 13. HOW TO START YOUR APPEAL + REQUIRED FORMS
Step-by-step guide specific to {state_info.get('name', 'the relevant jurisdiction')} with forms table.

## 14. PRIORITISED ACTION PLAN
72-hour / 7-day / 28-day actions. Each action: what to do, who to contact, objective.

## 15. CLIENT PLAIN-ENGLISH BRIEF
1000+ words explaining in plain English: what the appeal is about, what EACH ground means, the viability of each ground (arguable/moderate/strong or requires development), what happens next, realistic outcomes, and what the applicant should do now. Cover EVERY ground individually. CRITICAL: Use ONLY third-person language. ABSOLUTE BAN on "you", "your", "we", "us", "our". Use "the applicant", "the legal professional". Do NOT use percentage success rates — use appellate viability language instead (arguable, moderate, strong, requires development).

IMPORTANT:
- No cost discussion. No witness contradiction section.
- Every section must have substantive content — no placeholders.
- Keep ALL outcomes within SECTION 7. Keep ALL timeframes within SECTION 14.
- NEVER truncate. Write the ACTUAL full content."""

    else:  # extensive_log
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating the PREMIUM Extensive Report ($200 AUD) — the most detailed and case-specific legal analysis available.

The user has ALREADY received BOTH:
1. A FREE Quick Summary (case overview, top grounds preview, basic sentencing comparison)
2. A PAID Full Detailed Report (executive brief, forensic chronology, evidence digest, grounds portfolio with Crown/defence strategy, 8+ sentencing comparisons, outcome options matrix, evidence gaps checklist, 10-12 precedent cases, statutory framework, argument strategy, submissions blueprint, appeal steps guide, action plan, and plain-English brief)

THIS PREMIUM REPORT MUST BUILD ON — NOT REPEAT — THE FULL DETAILED REPORT. Do NOT re-state the same analysis. Instead:
- Where the Full Detailed analysed each ground with Crown response and rebuttal, THIS report must provide 1200+ word DEEP analysis per ground with fallback positions, additional authorities, and draft submission paragraphs.
- Where the Full Detailed provided 8+ sentencing comparisons, THIS report must provide 12+ with detailed paragraph analysis for EACH case.
- Where the Full Detailed had a precedent matrix of 10-12 cases, THIS report must have 15+ with specific factual comparisons.
- THIS report adds 5 ENTIRELY NEW sections not in the Full Detailed: Hearing Preparation Notes, Conference Preparation Pack, Court Pathway Operations Playbook, Similar Case Search Options, and Risk Assessment + Contingency Planning.
- Every shared section must go SIGNIFICANTLY deeper with fresh analysis, additional authorities, and more detailed strategy.

Every section must directly reference the supplied case material. Include hyperlinks to AustLII legislation, case databases, and court forms where the URL is known and verifiable. Do NOT fabricate URLs — if the exact AustLII path is not known, reference the legislation by name and section number only.
CRITICAL: NEVER use placeholder text. Every section MUST have REAL, SUBSTANTIVE, CASE-SPECIFIC CONTENT. Each ground analysis must be at least 1200 words. Reference specific documents, dates, and facts from the case throughout."""
        user_prompt = f"""Create a PREMIUM EXTENSIVE legal analysis report for this {category_name.lower()} appeal case. This must be the MOST COMPREHENSIVE report — significantly more detailed and case-specific than the Full Detailed tier.

{case_context}

GROUNDS TO COVER (MUST INCLUDE ALL — if 9 grounds, write 9 full analyses):
{grounds_enumerated}

MATERIAL COUNTS (use these exact numbers in the report):
- Total documents analysed: {len(documents)}
- Total timeline events: {len(timeline)}
- Total grounds identified: {len(grounds)}

Target range 25000-35000 words. Every section must reference specific facts, documents, and dates from this case.

CRITICAL — NO REPETITION FROM FULL DETAILED REPORT:
The user already has a Full Detailed Report covering grounds analysis, sentencing table (8 cases), outcome options, evidence gaps, precedent matrix (10-12 cases), statutory framework, argument strategy, submissions blueprint, appeal steps, and action plan. This Premium Extensive report must ADVANCE BEYOND all of that with deeper per-ground analysis (1200+ words each), expanded tables (12+ sentencing, 15+ precedents), and 5 ENTIRELY NEW sections: Hearing Preparation Notes, Conference Preparation Pack, Court Pathway Operations Playbook, Similar Case Search Options, and Risk Assessment + Contingency Planning. Do NOT copy or paraphrase content from the lower-tier reports.

SECTION ORDERING: Case-specific analysis first, then broader legal framework, then strategy, then practical steps, then client brief at the very end.

Use this exact structure:

## 1. EXECUTIVE BRIEF
Confident assessment of the appeal: strongest grounds with specific evidence anchors, jurisdiction posture, pathways to relief, urgency items, and a clear one-paragraph statement of the case. Include a case snapshot paragraph (defendant, offence, sentence, court, judge) and a short list of primary issues at the end.

MANDATORY: Start this section with a summary line: "This analysis is based on [X] documents and [Y] timeline events. [Z] grounds of appeal have been identified." Use the EXACT counts from the supplied case data.

## 2. FORENSIC CASE CHRONOLOGY
Comprehensive chronological reconstruction with at least 15 dated entries. For each entry:
- Date
- Event description (specific to the case facts)
- Source document/evidence
- Legal significance for the appeal
Include pre-trial, trial, sentencing, and post-sentencing events.

## 3. DOCUMENT EVIDENCE DIGEST
For EACH document/source in the case material:
- Key extracts (quote directly where possible)
- Reliability and credibility assessment
- Probative value for the appeal
- Which grounds this evidence supports
- Rating: Critical / Important / Supporting / Peripheral

## 4. GROUNDS OF MERIT — DEEP APPELLATE ANALYSIS
For EACH ground listed in GROUNDS TO COVER above (no omissions), provide a MINIMUM 1200-word analysis using the MANDATORY structure:

**Appellate Pathway:** The specific statutory provision engaged and the basis of the appeal.

**Trial Finding:** What the trial judge found or accepted on this issue.

**Error Identified:** Frame the arguable error using forensic language: "It is arguable that the trial judge erred in..." or "It is contended that...". Use forensic appellate language throughout — identify arguability, not bare declarations.

**Materiality:** Why this error matters to the outcome. How it affected the verdict or sentence.

**Consequence:** The legal consequence — verdict unsafe, miscarriage of justice, sentence must be set aside.

**Appellate Viability:**
- Outcome impact: Determinative / Influential / Minor
- Legal alignment: Direct authority / Analogous / Weak
- Evidence support: Strong / Partial / Limited

**Crown Response and Rebuttal:** Likely Crown prosecution response with detailed defence counter-strategy.

**Fallback Position:** Alternative argument if primary submission is rejected.

**Draft Submission Paragraph:** A paragraph ready to be adapted for written submissions.

Write each ground as a numbered entry starting with "Ground X: [Exact Title]" and then flowing paragraphs (no bullet-only answers). Minimum 1200 words per ground.

## 5. COMPARATIVE SENTENCING TABLE (12+ CASES)
CRITICAL: This section MUST contain an ACTUAL populated markdown table with real case data — NEVER placeholder text like "The table will reference..." or "Details will be provided...". If exact data cannot be found, use the best available comparable cases from Australian jurisprudence.

Markdown table with at least 12 comparable sentencing outcomes. IMPORTANT: Include only verified authorities already present in the supplied material or in the internal framework. If fewer than 12 verified comparators are available, include as many verified comparators as exist and STATE CLEARLY that verified comparators are insufficient — do not fabricate citations:
| Case | Offence | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Reduction (Years + %) | Key Reason |
Include AustLII search link: [Search {state_info.get('appeal_court', 'the Court of Criminal Appeal')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/')})
After the table, provide a DETAILED paragraph for EACH case explaining:
- What was the original sentence and sentencing judge's reasoning
- What the appeal court decided and why
- How the reduction was achieved and which grounds succeeded
- How this compares to the current case

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
| Common Ground | Frequency in Comparable Appeals | Typical Success Pattern | Best Supporting Evidence |
Then provide detailed analysis of how each common ground applies or does not apply to THIS specific case.

## 7. OUTCOME OPTIONS — DETAILED PATHWAY ANALYSIS
Markdown table:
| Option | Legal Threshold | Likelihood in This Matter | Core Evidence Trigger | Practical Result |
Then provide DETAILED analysis (minimum 150 words each) for EVERY pathway (keep ALL outcomes within THIS section — do NOT create separate ## headings for each outcome):
- **Conviction quashed** — what standard must be met, what evidence supports this, what the defendant's position would be, which grounds support this outcome
- **Retrial ordered** — when this happens instead of quashing, what the retrial process involves, timeframes
- **Conviction substituted/downgraded** (e.g., murder to manslaughter) — legal basis, resulting sentence range, how this has worked in comparable cases
- **Sentence reduced as manifestly excessive** — show explicit before/after: Original sentence/NPP → Revised sentence/NPP with reasoning for reduction
- **Appeal dismissed** — consequences, options for special leave to the High Court, time limits

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
For each gap:
- What is missing from the case file
- Why it matters for the appeal
- Exact steps to obtain it (who to contact, what to request, expected timeframe)
- Priority: Critical / Important / Helpful
- Impact on which grounds if not remediated

## 9. PRECEDENT OUTCOME MATRIX (15+ CASES)
For each of at least 15 cases (IMPORTANT: include only verified authorities already present in the supplied material or in the internal framework; if fewer than 15 verified comparators are available, include as many verified comparators as exist and STATE CLEARLY that verified comparators are insufficient — do not fabricate citations):
- Full citation
- Factual similarity to this matter (specific comparison)
- Hearing outcome
- Extracted legal principle
- How this principle applies to the current case
Include AustLII link: [Search {state_info.get('appeal_court', 'the Court of Criminal Appeal')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/')})

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP
15+ statutory provisions with:
- Section number, Act name with year, jurisdiction
- AustLII link: [AustLII Legislation](https://www.austlii.edu.au/cgi-bin/viewdb/au/legis/)
- How this provision specifically applies to the current case
- Any recent amendments that affect the appeal

## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
For each priority ground (minimum 200 words each):
- Lead proposition (the core argument stated in 1-2 powerful lines)
- Supporting authority cluster (specific statute section + 3-4 precedent cases with citations)
- Expected Crown prosecution response (specific to this case)
- Detailed rebuttal strategy for the hearing
- Fallback argument if the primary submission is rejected
- **How establishing this ground leads to a specific appeal outcome** (what order to seek)

## 12. SUBMISSIONS BLUEPRINT
Written submission strategy (write as flowing paragraphs, NOT bullet lists):
Discuss the recommended argument sequence and why this ordering maximises impact. Explain the authority placement strategy for each ground. Describe how each ground should be framed in written submissions with key passages to quote from case material.

Oral submission strategy (write as flowing paragraphs, NOT bullet lists):
Discuss the likely bench questions for each ground with prepared responses. Cover time allocation per ground, opening and closing lines, and how to handle judicial scepticism on weaker grounds.

## 13. HEARING PREPARATION NOTES
For each ground, write detailed flowing paragraphs (NOT bullet lists or dot points):
Cover the key arguments and talking points for each ground, the anticipated questions from the bench with suggested responses, which authority to cite first and why, and any visual aids or demonstratives to prepare.
- Concessions to make strategically vs points to contest

## 14. CONFERENCE PREPARATION PACK
For briefing a barrister:
- One-page case summary (lead theory)
- Authorities shortlist with key passages highlighted
- Orders sought (specific orders to request from the court)
- Case strengths (with evidence references)
- Case weaknesses and mitigation strategy
- Client instructions summary
- Key dates and deadlines

## 15. COURT PATHWAY OPERATIONS PLAYBOOK
For EACH relevant court level ({state_info.get('name', 'the relevant jurisdiction')} specific):
- Filing sequence and required documents
- Court registry details and contact information
- Deadlines for each filing step
- Extension-of-time route if deadlines have passed
- What happens at each stage of the process

## 16. HOW TO START YOUR APPEAL + REQUIRED FORMS
Step-by-step guide specific to {state_info.get('name', 'the relevant jurisdiction')}:
1. Obtain trial transcripts and exhibits
2. Identify and finalise grounds of appeal
3. Lodge Notice of Intention to Appeal
4. Prepare detailed written submissions
5. Serve documents on the Crown/DPP
6. Attend the appeal hearing
For each step: plain English explanation, required form, deadline, and link.
Forms table:
| Form/Document | Purpose | Where to Obtain | Filing Deadline |
Links: [Legal Aid {state_info.get('name', 'the relevant jurisdiction')}]({state_info.get('legal_aid_url', 'https://www.legalaid.nsw.gov.au/')}) | [AustLII](https://www.austlii.edu.au/) | [Court Forms]({state_info.get('court_forms_url', '#')})

## 17. SIMILAR CASE SEARCH OPTIONS
Tailored AustLII search guidance:
- 5+ query strings specifically designed for this case's offence and grounds profile
- Links: [Search {state_info.get('appeal_court', 'the Court of Criminal Appeal')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/')}) | [Search all states](https://www.austlii.edu.au/)
- Court-level filtering suggestions
- Keyword alternatives for each ground
- How to narrow results to the most relevant period and jurisdiction

## 18. PRIORITISED ACTION PLAN
72-hour actions (urgent — time-sensitive filings, evidence at risk of loss):
- Specific action, who to contact, deadline, objective

7-day actions (important — evidence gathering, legal research):
- Specific action, resources needed, dependencies

28-day actions (strategic — submission drafting, hearing preparation):
- Specific action, preparation steps, milestones

## 19. OPERATIONS ENGINE — CRITICAL MISSING EVIDENCE
Auto-generated checklist of evidence gaps identified from the case analysis:
For each gap:
- What is missing (e.g. "Psychiatric report addressing intoxication impact")
- Why it matters to the appeal
- How to obtain it
- Priority: Critical / Important / Desirable

## 20. EVIDENCE REQUEST LIST
Specific documents and materials that must be obtained:
| Item | Source | Purpose | Priority | Deadline |
Include: transcripts, expert reports, affidavits, medical records, CCTV, forensic reports.

## 21. SUGGESTED EXPERT REPORTS
For each identified evidentiary gap:
- Type of expert required (psychiatrist, forensic pathologist, etc.)
- What opinion is needed
- How the opinion would strengthen the appeal
- Suggested brief outline for instructing the expert

## 22. FILING PATHWAY
Step-by-step filing requirements for {state_info.get('name', 'the relevant jurisdiction')}:
- Notice of Intention to Appeal (if not filed) — deadline and form
- Detailed grounds of appeal — content requirements
- Written submissions — structure and page limits
- Application for leave (if required) — criteria
- Supporting affidavit requirements
- Service requirements on DPP/Crown

## 23. RISK ASSESSMENT + CONTINGENCY PLANNING
For each ground:
- Appellate viability assessment (arguable/moderate/strong or requires development)
- Main risk factor
- Contingency if this ground fails
- Impact on overall appeal if this ground is excluded

Overall appeal risk assessment:
- Best case scenario
- Most likely outcome
- Worst case scenario and mitigation

Do NOT use percentage success rates. Use appellate viability language only.

## 24. CLIENT PLAIN-ENGLISH BRIEF
THIS MUST BE THE FINAL SECTION. Write this as if explaining the case to the defendant in everyday language, BUT STRICTLY IN THIRD PERSON:
- What the appeal is about and why it matters
- What are the strongest arguments in the applicant's favour (reference specific facts)
- What are the realistic prospects for the appeal (use viability language: arguable, moderate, strong — NOT percentages)
- What the different possible outcomes mean for the applicant personally
- What the applicant needs to do right now, this week, and this month
- What to expect at the hearing
- Honest assessment of risks alongside the opportunities
CRITICAL: This section is an educational tool. Use ONLY third-person language ("the applicant", "the legal professional", "this analysis"). NEVER use "we", "us", "our", "you", "your", or "them" when referring to the legal team or the applicant. WRONG: "The appeal is your opportunity to challenge your conviction." RIGHT: "The appeal represents an opportunity for the applicant to challenge the conviction."

IMPORTANT:
- Use markdown headings and tables exactly where specified.
- Working hyperlinks to AustLII and court websites throughout.
- Every section MUST reference specific facts from the supplied case material — no generic legal advice.
- This report must be VISIBLY more comprehensive than the Full Detailed tier.
- Australian English throughout.
- No cost discussion. No witness contradiction section.
- Quote directly from supplied documents where relevant.
- Every conclusion must be tied to case material or clearly marked as an assumption.
- NEVER use continuation markers like "... (continue with further analysis)", "... (continue analysis of other cases)", or similar truncation. Write the ACTUAL content for every section.
- Do NOT insert meta-commentary about the document itself (e.g., "This truncated document provides..."). Only output the report content.
- Keep ALL outcome pathways (conviction quashed, retrial, etc.) within SECTION 7 — do NOT create separate ## headings for individual outcomes.
- Keep ALL action items (72-hour, 7-day, 28-day) within SECTION 18 — do NOT create separate ## headings for each timeframe."""

    if aggressive_mode:
        aggressive_directive = """

AGGRESSIVE ADVOCACY MODE (USER-REQUESTED) — THIS FUNDAMENTALLY CHANGES YOUR APPROACH:

TONE SHIFT — You are no longer a cautious analyst. You are a senior criminal appeal barrister preparing to ARGUE this case in court. Write as if you are personally invested in winning this appeal:
- In aggressive mode, stronger forensic language is permitted: "This ground is compelling", "The Crown's position is untenable", "It is forcefully contended that the sentencing judge erred"
- NEVER hedge with "may", "could potentially", "it is possible that". Instead: "The evidence establishes", "It is contended that this constitutes a clear error", "There is a compelling argument that the conviction cannot stand"
- Frame EVERY ground as an argument TO BE WON, not a possibility to be explored
- Attack prosecution weaknesses directly: "The Crown's reliance on [X] is fatally undermined by [Y]"
- Draft ACTUAL submission paragraphs that could be read to the bench word-for-word
- For each ground, write the opening line you would say to the Court of Appeal judges
- Assume a standard (non-aggressive) version already exists. This aggressive report must add materially NEW arguments, authorities, and case-specific detail — do NOT rephrase or recycle the standard report.
- If a point is already made earlier in this report, deepen it with NEW evidence, dates, or authority rather than repeating it.
- This aggressive report must be approximately DOUBLE the depth of the standard report. Do not compress or summarise.

EXPANDED SCOPE:
1. DOUBLE the word count target for the entire report.
2. For EVERY ground of appeal, provide:
   - The STRONGEST possible legal argument as if arguing before the bench
   - Minimum 3 specific case citations that directly support this ground
   - A draft submission paragraph ready to be read in court
   - The specific orders to seek if this ground succeeds
   - Fallback position with alternative argument if primary is challenged
3. COMPARATIVE SENTENCING TABLE: 15+ cases if verified comparators exist. IMPORTANT: Include only verified authorities already present in the supplied material or in the internal framework; if fewer than 15 verified comparators exist, include what exists and STATE CLEARLY that verified comparators are insufficient — do not fabricate citations. For each, explain HOW the reduction was achieved.
4. OUTCOME OPTIONS: 250+ words per pathway. Reference ALL identified grounds for each pathway.
5. SUBMISSIONS: Write FULL draft argument paragraphs, not outlines. Include opening, authority chains, and closing for each ground.
6. PRECEDENT MATRIX: 20+ cases if verified comparators exist. IMPORTANT: Include only verified authorities already present in the supplied material or in the internal framework; if fewer than 20 verified comparators exist, include what exists and STATE CLEARLY that verified comparators are insufficient — do not fabricate citations. Provide detailed factual comparison for each.
7. Every conclusion must state the SPECIFIC order sought from the court.
8. Write as if the appeal WILL succeed — identify the path to victory, not just the obstacles.
"""
        system_prompt = f"{system_prompt}\n{aggressive_directive}"
        user_prompt = f"""{user_prompt}

AGGRESSIVE ADVOCACY MODE IS ON. Write as a senior barrister who believes in this appeal.
- DOUBLE the word count target.
- Use confident, forensic advocacy language throughout — frame as arguable, contended, tenable — never bare declarations, and never hedging with "may have" or "could potentially".
- Draft actual submission paragraphs for each ground that could be read to the bench.
- Frame the analysis as building the STRONGEST possible case for the appellant.
- Every section must reference specific case facts and documents.
- Attack Crown weaknesses directly and confidently.
- Write the opening line you would use to address the Court of Appeal for each key argument."""

    # Call AI — HARDENED via call_llm_structured with enhanced report-generation timeouts
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="AI service not configured — OPENAI_API_KEY missing")

    _report_generation_metadata = {"models_used": [], "fallback_used": False}

    async def _subprocess_llm(prompt_text):
        """DO_NOT_UNDO — Run LLM call with pass-level retry for 502/service errors.
        
        The 4 model fallbacks inside call_llm_structured handle per-call retries.
        This outer retry handles cases where ALL 4 models fail on the same pass
        (e.g., upstream proxy 502 storm). Waits 30-60s between outer retries.
        """
        call_timeout = 420 if report_type in ("full_detailed", "extensive_log") else 300
        max_pass_retries = 3

        for retry in range(max_pass_retries):
            response = await call_llm_structured(
                system_prompt=system_prompt,
                user_prompt=prompt_text,
                session_id=f"rpt_gen_{case_id}",
                task_type="report_generation",
                max_tokens=16384,
                timeout_seconds=call_timeout,
                require_json=False,
                validation_fn=None,
            )

            if response["ok"]:
                if response.get("model"):
                    _report_generation_metadata["models_used"].append(response["model"])
                if response.get("fallback_used"):
                    _report_generation_metadata["fallback_used"] = True
                return response["content"]

            # All 4 models failed — wait and retry the entire pass
            if retry < max_pass_retries - 1:
                backoff = 10 + retry * 10  # 10s, 20s
                logger.warning(f"All models failed for pass (attempt {retry+1}/{max_pass_retries}). Waiting {backoff}s before retry. Error: {response['error']}")
                await asyncio.sleep(backoff)

        raise Exception(f"All LLM attempts failed after {max_pass_retries} pass retries. Last error: {response['error']}")

    response = None
    last_error = None
    try:
        # DO_NOT_UNDO — Condensed prompt for multi-pass generation.
        # Full document text is only needed for Pass 1-2 (Executive Brief, Chronology, Document Digest).
        # Later passes (Grounds analysis, Sentencing, Strategy, etc.) need grounds data, case metadata,
        # and pipeline data but NOT 100k+ of raw document text. This eliminates 502 proxy timeouts
        # on large prompts WITHOUT changing report depth or content.
        condensed_prompt = f"""
=== CASE INFORMATION ===
Title: {case.get('title', 'N/A')}
Defendant: {case.get('defendant_name', 'N/A')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}
Judge: {case.get('judge', 'N/A')}
Sentence: {case.get('sentence', 'N/A')}
Summary: {case.get('summary', 'N/A')}

{offence_context}

=== CASE DOCUMENTS ({len(documents)} files — full text was provided in earlier passes) ===
"""
        for d in documents:
            condensed_prompt += f"- {d.get('filename', 'Unknown')} ({d.get('document_type', 'unknown')})\n"
        condensed_prompt += "\n"

        if timeline:
            condensed_prompt += f"=== TIMELINE OF EVENTS ({len(timeline)} events) ===\n"
            for event in timeline[:20]:
                condensed_prompt += f"- {event.get('event_date', 'Unknown')}: [{event.get('event_type')}] {event.get('title')}\n"
            condensed_prompt += "\n"

        if grounds:
            condensed_prompt += f"=== IDENTIFIED GROUNDS OF MERIT ({len(grounds)} grounds) ===\n"
            for g in grounds:
                condensed_prompt += f"- [{g.get('ground_type')}] {g.get('title')} (Strength: {g.get('strength')})\n"
                desc = (g.get('description') or '')[:500]
                if desc:
                    condensed_prompt += f"  {desc}\n"
                analysis = (g.get('analysis') or '')[:500]
                if analysis:
                    condensed_prompt += f"  Analysis: {analysis}\n"
            condensed_prompt += "\n"

        if structured_context:
            facts = structured_context.get("facts", [])
            findings = structured_context.get("findings", [])
            verified = structured_context.get("verified_issues", [])
            condensed_prompt += "=== STRUCTURED PIPELINE DATA ===\n"
            if facts:
                condensed_prompt += "CASE FACTS:\n"
                for f in facts[:15]:
                    condensed_prompt += f"- {f}\n" if isinstance(f, str) else f"- {f}\n"
            if findings:
                condensed_prompt += "\nKEY FINDINGS:\n"
                for f in findings[:10]:
                    condensed_prompt += f"- {f}\n" if isinstance(f, str) else f"- {f}\n"
            if verified:
                condensed_prompt += "\nVERIFIED APPEAL ISSUES:\n"
                for vi in verified:
                    condensed_prompt += f"- {vi.get('title', 'Untitled')} ({vi.get('ground_type', 'unknown')})\n"
            condensed_prompt += "\n"

        logger.info(f"Report prompt sizes: full={len(user_prompt)} chars, condensed={len(condensed_prompt)} chars")

        if report_type == "full_detailed":
            # DO_NOT_UNDO — 8-pass generation is FINAL. Previous 5-pass produced only ~7,890 words.
            # Current 8-pass produces ~12,000+ words. NEVER reduce pass count.
            half_grounds = max(1, len(grounds) // 2)
            # DO_NOT_UNDO — grounds_enumerated is ONE line per ground (e.g. "1. Title").
            # Split by actual ground count, not by arbitrary line multiplier.
            all_ground_lines = grounds_enumerated.split('\n')
            first_grounds = all_ground_lines[:half_grounds]
            second_grounds = all_ground_lines[half_grounds:]
            first_grounds_text = '\n'.join(first_grounds) if first_grounds else grounds_enumerated
            second_grounds_text = '\n'.join(second_grounds) if second_grounds else ""
            
            passes = [
                ("PASS 1/8", f"""
NOW GENERATE ONLY SECTIONS 1-2. Write 3000+ WORDS for this pass. Every paragraph must reference specific case facts.

## 1. EXECUTIVE BRIEF (1200+ words)
Write 6 FULL paragraphs — each paragraph must be 150+ words. This is a COUNSEL BRIEFING, not a case summary rehash.
Think: "what does counsel need to know in 5 minutes?"

- Paragraph 1: "This analysis is based on {len(documents)} documents and {len(timeline)} timeline events. {len(grounds)} grounds of appeal have been identified." Then strategic overview of the appeal's overall appellate position. Do NOT use percentage success rates — use viability language (arguable, moderate, strong).
- Paragraph 2: Key appellate themes (e.g. psychiatric evidence conflict, intoxication + intent interaction, procedural fairness concerns). NOT a list of grounds — identify the 2-3 overarching legal themes.
- Paragraph 3: Priority grounds (strongest first) with specific evidence anchors and why they have the best appellate viability.
- Paragraph 4: Strategic risks — what the prosecution will exploit, evidence gaps, weak factual anchors.
- Paragraph 5: Recommended immediate actions with specific deadlines and who to contact.
- Paragraph 6: Overall appellate position summary — "There are arguable grounds capable of attracting appellate consideration, subject to refinement and evidentiary development" or equivalent honest assessment.

CRITICAL: Do NOT repeat content from the 3 underlying reports. This must be SYNTHESIS only.

""" + FORENSIC_LANGUAGE_RULE + """

## 2. FORENSIC CASE CHRONOLOGY (1500+ words)
Write 15+ dated events as FULL PARAGRAPHS (4-5 sentences each). NOT bullet points. Each event:
"On [DATE], [WHAT HAPPENED]. This is evidenced by [SOURCE DOCUMENT]. The legal significance is [WHY IT MATTERS FOR APPEAL]. This event [IMPACT]."
Cover ALL of: offence date and circumstances, arrest, charges, bail, committal, psychiatric assessments, trial dates, key evidence, verdict, sentencing, appeal filing.

STOP after section 2. Write every paragraph in full."""),

                ("PASS 2/8", f"""
NOW GENERATE ONLY SECTION 3. Write 2000+ WORDS for this pass. Analyse EVERY single uploaded document.

## 3. DOCUMENT EVIDENCE DIGEST (2000+ words)
For EACH of the {len(documents)} uploaded documents, write a FULL PARAGRAPH (150+ words each) covering:
- Document title and type
- Key extracts — quote directly from the content where possible
- Reliability and credibility assessment
- Probative value — what does this document prove or disprove?
- Which specific grounds of appeal does this document support?
- Rating: Critical / Important / Supporting / Peripheral

If there are {len(documents)} documents, write {len(documents)} detailed paragraphs minimum.

STOP after section 3."""),

                ("PASS 3/8", f"""
NOW GENERATE ONLY SECTION 4 (FIRST HALF OF GROUNDS). Write 4000+ WORDS for this pass.

## 4. GROUNDS OF MERIT — APPELLATE PATHWAY ANALYSIS (Part 1)
Write detailed appellate analyses for the FIRST {half_grounds} grounds. Each ground MUST follow this structure:

GROUNDS TO COVER IN THIS PASS:
{first_grounds_text}

For EACH ground, write as "Ground X: [Exact Title]" then 800+ words using the MANDATORY structure:
1. **Appellate Pathway:** The specific statutory provision engaged (e.g. "Miscarriage of justice under the Criminal Appeal Act")
2. **Ground:** Frame the arguable error — "It is arguable that the trial judge erred in failing to..." or "It is contended that..."
3. **Error Identified:** What is arguable as having gone wrong. Reference documents, dates, witnesses by name. Use forensic language: "It is arguable that...", "It is contended that...".
4. **Materiality:** Why this error matters. How it affected the verdict or sentence.
5. **Consequence:** Legal consequence (verdict unsafe, miscarriage of justice, sentence set aside).
6. **Appellate Viability:** Outcome impact (Determinative/Influential/Minor), Legal alignment (Direct/Analogous/Weak), Evidence support (Strong/Partial/Limited).
7. **Crown Response:** What the prosecution will argue (4-5 sentences). Reference authority ONLY if a real, verifiable citation is known — otherwise argue on principle without citing a specific case.
8. **Defence Rebuttal:** How to counter the Crown's likely position (4-5 sentences). Reference authority ONLY if a real, verifiable citation is known — otherwise frame the rebuttal on legal principle.

Write 800+ words per ground. Do NOT compress into bullet points. Use forensic appellate language throughout — frame as arguable, not declarations.

STOP after covering the first {half_grounds} grounds."""),

                ("PASS 4/8", f"""
NOW GENERATE ONLY SECTION 4 (SECOND HALF OF GROUNDS) AND SECTION 5. Write 4000+ WORDS for this pass.

## 4. GROUNDS OF MERIT — APPELLATE PATHWAY ANALYSIS (Part 2)
Continue with the REMAINING grounds. Each must follow the same mandatory structure as Part 1.

GROUNDS TO COVER IN THIS PASS:
{second_grounds_text if second_grounds_text.strip() else grounds_enumerated}

For EACH ground, use the same structure: Appellate Pathway → Ground → Error Identified → Materiality → Consequence → Appellate Viability → Crown Response → Defence Rebuttal.

## 5. COMPARATIVE SENTENCING TABLE (8+ CASES)
PRODUCE AN ACTUAL POPULATED MARKDOWN TABLE with case data. Then write a Detailed Outcome Analysis paragraph for EACH case in the table.
| Case | Offence | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Reduction | Key Reason |
CRITICAL: Only include cases with REAL, VERIFIABLE citations (e.g. "R v Smith [2015] NSWCCA 123"). If fewer than 8 verified cases are known for this offence type, include only those that ARE known — do NOT fabricate citations to reach the target count. It is better to have 4 verified cases than 8 fabricated ones.

STOP after section 5."""),

                ("PASS 5/8", """
NOW GENERATE ONLY SECTIONS 6-7. Write 3000+ WORDS for this pass.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Markdown table with 8+ rows:
| Common Ground | Frequency in Comparable Appeals | Typical Success Pattern | Best Supporting Evidence |
Then for each common ground, explain how it applies or does not apply to THIS specific case.

## 7. OUTCOME OPTIONS AVAILABLE
Summary table first, then write 400+ WORDS for EACH of these 5 pathways:
- **Conviction quashed** — which grounds support this, legal threshold, appellate viability assessment (300+ words)
- **Retrial ordered** — triggers, what changes, timeframes (200+ words)
- **Conviction substituted/downgraded** — legal basis, sentence impact (200+ words)
- **Sentence reduced as manifestly excessive** — show exact before/after numbers with reasoning. State the appellate threshold: "Intervention required where the sentence is manifestly excessive, OR relevant mitigating factors were not properly weighed." (300+ words)
- **Appeal dismissed** — consequences, High Court special leave options (200+ words)
Do NOT use percentage success rates. Use appellate viability language.

STOP after section 7."""),

                ("PASS 6/8", """
NOW GENERATE ONLY SECTIONS 8-10. Write 3000+ WORDS for this pass.

## 8. OPERATIONS ENGINE — EVIDENTIARY GAPS + REMEDIATION (800+ words)
List 8+ specific gaps with urgency ratings. For each:
- What's missing (e.g. "Psychiatric report addressing intoxication impact")
- Why it matters and which ground it affects
- How to obtain it (specific steps, who to contact)
- Priority: Critical / Important / Desirable
- Impact on appeal if not obtained

Include: evidence request list, missing affidavit prompts, suggested expert reports.

## 9. PRECEDENT OUTCOME MATRIX (10-12 CASES)
For each case write a FULL PARAGRAPH: citation, factual similarity, outcome, extracted principle, how it applies to THIS case.
Do NOT include cases with "[Surname]" or unverified citations.

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP (1000+ words)
For EACH relevant provision write a paragraph APPLYING it to THIS case — section + Act + year + jurisdiction + specific relevance. Not generic descriptions.
Law sections MUST have ACTUAL section numbers. If the section number is not known, do NOT include that entry.

STOP after section 10."""),

                ("PASS 7/8", f"""
NOW GENERATE ONLY SECTIONS 11-12. Write 3000+ WORDS for this pass.

## 11. COUNSEL BRIEFING NOTE — HOW TO ARGUE EACH GROUND
Think: "what does counsel need in a 5-minute briefing on each ground?"
You MUST cover EVERY ground — ALL {len(grounds)} of them. For EACH ground write 400+ words:
GROUNDS TO COVER:
{grounds_enumerated}

For each ground — NO repetition of content from underlying reports. SYNTHESIS ONLY:
- **Lead Proposition**: Core argument in 2 powerful forensically-framed sentences ("It is arguable that...", "It is contended that...")
- **Appellate Pathway**: Which statutory provision is engaged
- **Supporting Authority Cluster**: Statute + 3 precedent cases (REAL citations only)
- **Expected Prosecution Answer**: 4-5 sentences with specific authorities
- **Rebuttal Strategy**: 4-5 sentences with counter-authorities
- **Strategic Risk**: Main weakness or gap
- **If Established**: Specific court order to seek

## 12. SUBMISSIONS BLUEPRINT (1200+ words)
Write ACTUAL DRAFT SUBMISSION TEXT ready for court.
**Written Submissions**: Full argument sequence paragraphs with authority placement. Write the opening paragraph and closing paragraph.
**Oral Submissions**: Bench questions with prepared responses. Time allocation per ground. Opening and closing strategies.

STOP after section 12."""),

                ("PASS 8/8", f"""
NOW GENERATE ONLY SECTIONS 13-15. Write 4000+ WORDS for this pass. Section 15 is critical.

## 13. FILING PATHWAY + REQUIRED FORMS (800+ words)
Step-by-step filing requirements:
- Notice of Intention to Appeal — deadline and form
- Detailed grounds of appeal — content requirements
- Written submissions — structure and page limits
- Application for leave (if required) — criteria
- Supporting affidavit requirements
- Service requirements on DPP/Crown
Each step: plain English explanation, required form, deadline.

## 14. PRIORITISED ACTION PLAN (800+ words)
72-hour actions (at least 5): exact action, who to contact, deadline, objective.
7-day actions (at least 5): exact action, resources needed, dependencies.
28-day actions (at least 5): exact action, preparation steps, milestones.

## 15. PLAIN-ENGLISH BRIEF (2000+ words)
For EACH of the {len(grounds)} grounds individually:
- What this ground means in simple terms (3-4 sentences)
- Why it matters (2-3 sentences)
- Appellate viability (honest assessment — arguable/moderate/strong, NOT percentages)
- What happens if it succeeds (specific outcome)

Then cover:
- The overall appeal: what, why, timeline
- Overall position: "There are arguable grounds capable of attracting appellate consideration, subject to refinement and evidentiary development." (or equivalent honest assessment)
- Each possible outcome and what it means
- What the applicant should do right now, this week, this month
- ABSOLUTE BAN: NEVER use "we", "us", "our", "you", "your". Use "the applicant", "the legal professional".

Do NOT truncate. Write ALL content."""),
            ]
            
            parts = []
            resume_from = 0
            if report_id:
                existing_report = await db.reports.find_one(
                    {"report_id": report_id},
                    {"_id": 0, "content.partial_analysis": 1, "content.passes_completed": 1},
                )
                existing_content = (existing_report or {}).get("content") or {}
                existing_partial = existing_content.get("partial_analysis") or ""
                existing_passes_completed = int(existing_content.get("passes_completed") or 0)
                if existing_partial and existing_passes_completed > 0:
                    parts = [existing_partial]
                    resume_from = min(existing_passes_completed, len(passes))
                    logger.info(f"Resuming full_detailed report {report_id} from pass {resume_from + 1}")

            # DO_NOT_UNDO — Same condensed context optimisation for full_detailed.
            # Pass 1 (Exec Brief + Chronology) and Pass 2 (Document Digest) get full context.
            # Passes 3-8 (Grounds analysis, Sentencing, Strategy) get condensed context.
            for pass_index, (label, instruction) in enumerate(passes[resume_from:], start=resume_from + 1):
                await _update_report_pass_progress(report_id, pass_index, len(passes), label)
                base_prompt = user_prompt if pass_index <= 2 else condensed_prompt
                pass_prompt = base_prompt + instruction
                # DO_NOT_UNDO — TPM safety cap. OpenAI Tier 1 gives gpt-4o only
                # 30,000 tokens per minute. If system (~17k chars ≈ 4.3k tokens)
                # plus user exceed ~25,000 tokens of input, the request is
                # rejected with 429 before it even starts and we silently
                # fall back to gpt-4o-mini (quality loss on a $150 product).
                # 1 token ≈ 4 chars for English text, so 90,000 chars ≈ 22,500
                # tokens user input; plus ~4,300 token system ≈ 26,800 total
                # input; plus max_tokens output ≈ fits inside 30,000 TPM.
                # If a case is so large the prompt exceeds the cap, we truncate
                # from the MIDDLE (preserving instructions at the top and the
                # pass-specific instruction at the bottom).
                TPM_SAFE_CAP = 90000
                if len(pass_prompt) > TPM_SAFE_CAP:
                    head_keep = int(TPM_SAFE_CAP * 0.55)
                    tail_keep = TPM_SAFE_CAP - head_keep - 200
                    truncated = (
                        pass_prompt[:head_keep]
                        + "\n\n[... middle context truncated for API token limits; see remaining context below ...]\n\n"
                        + pass_prompt[-tail_keep:]
                    )
                    logger.warning(
                        f"Full detailed {label} prompt exceeded TPM-safe cap: "
                        f"{len(pass_prompt)} → {len(truncated)} chars"
                    )
                    pass_prompt = truncated
                logger.info(f"Full detailed {label} prompt size: system={len(system_prompt)}, user={len(pass_prompt)}")
                part = await _subprocess_llm(pass_prompt)
                parts.append(part)
                logger.info(f"Full detailed {label} response: {len(part)} chars")
                # Partial save after each pass to prevent data loss on server restart
                if report_id:
                    partial_content = "\n\n".join(parts)
                    await db.reports.update_one(
                        {"report_id": report_id},
                        {"$set": {"content.analysis": partial_content, "content.partial": True, "content.partial_analysis": partial_content, "content.passes_completed": pass_index}}
                    )
            
            response = "\n\n".join(parts)
            logger.info(f"Full detailed combined: {len(response)} chars")

        elif report_type == "extensive_log":
            # Ten-pass generation for extensive_log (24 sections)
            passes = [
                ("PASS 1/10", f"""

NOW GENERATE ONLY SECTIONS 1-3. Write 5000+ WORDS for this pass. This is a $200 PREMIUM report — every paragraph must be packed with case-specific facts, not generic legal education.

## 1. EXECUTIVE BRIEF (1200+ words)
Write 6-8 FULL paragraphs (NOT bullet points):
- Paragraph 1: Document/timeline/grounds counts from supplied data, then strategic overview of the appeal's overall appellate position (do NOT use percentage success rates — use viability language: arguable, moderate, strong)
- Paragraph 2: The 2-3 STRONGEST grounds with specific evidence anchors and legal tests that support them
- Paragraph 3: The weakest ground and why it's still worth pursuing (or should be abandoned)
- Paragraph 4: Jurisdiction-specific posture — what the {state_info.get('appeal_court', 'the Court of Criminal Appeal')} typically does with this type of appeal
- Paragraph 5: Most likely outcome pathway and realistic assessment of relief
- Paragraph 6: Key risks the prosecution will exploit and how to counter them
- Paragraph 7: Immediate actions required with specific deadlines
- Paragraph 8: Summary of 8+ primary issues identified with document references

CRITICAL: Do NOT use percentage probabilities or success rates anywhere in this report. Use appellate viability language only (arguable, moderate, strong, requires development).

""" + FORENSIC_LANGUAGE_RULE + """

## 2. FORENSIC CASE CHRONOLOGY (1500+ words)
Write 18+ dated events as FULL PARAGRAPHS (4-5 sentences each). NOT bullet points. Each event:
"On [EXACT DATE], [WHAT HAPPENED in detail]. This is established by [SOURCE DOCUMENT with specific reference]. The legal significance for the appeal is [SIGNIFICANCE]. The prosecution's likely treatment of this event is [PROSECUTION VIEW], while the defence can argue [DEFENCE POSITION]."
Cover: offence date and circumstances, arrest, charges laid, bail, committal, psychiatric/forensic reports, plea, trial dates, key witness testimony, jury directions, verdict, sentencing submissions, sentence, appeal filing.

## 3. DOCUMENT EVIDENCE DIGEST (1200+ words)
For EACH of the {len(documents)} uploaded documents, write 2-3 FULL PARAGRAPHS analysing:
- Document title and date
- Key extracts (QUOTE directly from the document content where possible)
- Reliability and credibility assessment
- Probative value — what it proves or disproves
- Which specific grounds this document supports
- Rating: Critical / Important / Supporting / Peripheral
If there are 10 documents, write 20-30 paragraphs.

STOP after section 3. Write ALL content — do NOT truncate."""),
                ("PASS 2/10", f"""

NOW GENERATE ONLY SECTIONS 4-5. Write 6000+ WORDS for this pass. Section 4 is the HEART of the $200 report — each ground must be a mini-essay.

## 4. GROUNDS OF MERIT — DEEP ANALYSIS
You MUST write about EVERY ground listed below. If there are 5 grounds, write 5 complete analyses. NO OMISSIONS.
GROUNDS TO COVER:
{grounds_enumerated}

For EACH ground, write 1200+ words as flowing paragraphs (NOT bullet points) covering:
1. "Ground X: [Exact Title from above]" as the heading
2. LEGAL THRESHOLD: The specific test for this ground — cite the statutory provision (section + Act + year) and the leading case that established the test. Explain what must be proved.
3. FACTUAL BASIS: How THIS case's specific facts satisfy the test. Reference documents, dates, witness statements. Quote from case material where possible.
4. VIABILITY RATING: Strong / Moderate / Weak — with 5-6 sentences explaining WHY, citing comparable cases where this type of ground succeeded or failed.
5. CROWN RESPONSE PREDICTION: Write 4-5 sentences predicting EXACTLY what the prosecution will argue. Be specific — name the authorities they'll rely on.
6. DEFENCE REBUTTAL STRATEGY: Write 4-5 sentences with the specific counter-argument. Name authorities that trump the Crown's position.
7. FALLBACK POSITION: If the primary argument fails, what's the fallback? (2-3 sentences)
8. APPEAL IMPACT: If this ground succeeds — conviction quashed? Sentence reduced? Retrial? What specific court order should be sought?
9. KEY AUTHORITY: Name the single most important case, provide the citation, and explain in 3-4 sentences exactly how it applies to this ground in this case.

## 5. COMPARATIVE SENTENCING TABLE (12+ CASES)
CRITICAL: Produce an ACTUAL populated markdown table with real case data — NEVER placeholder text like "The table will reference..." or "Details will be provided...".
Markdown table with 12+ rows IF verified comparators exist. IMPORTANT: Include only verified authorities already present in the supplied material or in the internal framework; if fewer than 12 verified comparators exist, produce as many rows as exist and STATE CLEARLY that verified comparators are insufficient — do not fabricate citations. After the table, write a DETAILED PARAGRAPH for EACH of the verified cases (200+ words each) explaining: original sentencing reasoning, appeal court's reasoning, how the reduction was achieved, which grounds succeeded, and how this specifically compares to the current case.

STOP after section 5."""),
                ("PASS 3/10", f"""

NOW GENERATE ONLY SECTIONS 6-8. Write 4000+ WORDS for this pass.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Markdown table with 10+ rows, then for EACH common ground write 100+ words explaining how it does or does not apply to THIS specific case. Reference the actual grounds identified in this case where they overlap.

## 7. OUTCOME OPTIONS — DETAILED PATHWAY ANALYSIS
First provide summary table, then write 400+ WORDS for EACH of these 5 pathways (ALL within this one section):
- **Conviction quashed entirely**: Which of the {len(grounds)} grounds support this? What's the legal standard (e.g., miscarriage of justice)? What evidence is strongest? What is the appellate viability of this pathway?
- **Retrial ordered**: What triggers a retrial? What changes? Timeframes? Risks? What happens if the same evidence is presented?
- **Conviction substituted/downgraded**: Could the charge be reduced? Under what legal basis? What would the new sentence range be? Which grounds support this?
- **Sentence reduced as manifestly excessive**: Show EXACT before/after — Original sentence/NPP → realistic revised sentence/NPP with reasoning. Which sentencing comparisons from Section 5 support this?
- **Appeal dismissed**: What happens? Consequences for the applicant? Special leave to High Court — threshold, timeframe, realistic prospects?

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST (800+ words)
List 10+ specific gaps. For each: what's missing, why it matters, exact steps to obtain it (who to contact, what to request, expected timeframe), priority (Critical/Important/Helpful), impact on which grounds if not remediated.

STOP after section 8."""),
                ("PASS 4/10", """

NOW GENERATE ONLY SECTIONS 9-10. Write 3200+ WORDS for this pass.

## 9. PRECEDENT OUTCOME MATRIX (12+ CASES)
For each of at least 12 verified cases (IMPORTANT: include only verified authorities already present in the supplied material or in the internal framework; if fewer than 12 verified comparators exist, write the paragraphs for as many verified comparators as exist and STATE CLEARLY that verified comparators are insufficient — do not fabricate citations), write a FULL PARAGRAPH (not just a table row):
- Full citation
- Factual similarity to THIS matter (be specific — offence type, relationship, circumstances)
- Hearing outcome
- Extracted legal principle
- How this principle applies to the current case (3-4 sentences)

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP (1000+ words)
12+ statutory provisions. For EACH provision, write a FULL PARAGRAPH:
- Section number, Act name with year, jurisdiction
- What the provision covers (1 sentence)
- How it SPECIFICALLY APPLIES to THIS case (3-4 sentences) — name the defendant, the offence, the ground it relates to
- Any recent amendments or judicial interpretation that affects the appeal

STOP after section 10."""),
                ("PASS 5/10", f"""

NOW GENERATE ONLY SECTION 11. Write 2800+ WORDS for this pass. This pass exists so EVERY ground can be fully argued without truncation.

## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
MUST cover ALL {len(grounds)} grounds. For EACH ground write 500+ words:
GROUNDS TO COVER:
{grounds_enumerated}

For each ground:
- **Lead Proposition**: The core argument in 2 powerful sentences
- **Supporting Authority Cluster**: Specific statute + 3-4 precedent cases with full citations and 2-3 sentences explaining each
- **Expected Crown Response**: 4-5 sentences predicting what the prosecution will argue
- **Rebuttal Strategy**: 4-5 sentences with specific counter-authorities
- **Fallback Position**: If the primary argument is rejected, what's the alternative? (3-4 sentences)
- **If Established**: What specific court order should be sought?

STOP after section 11."""),
                ("PASS 6/10", f"""

NOW GENERATE ONLY SECTIONS 12-14. Write 5000+ WORDS for this pass. These are the sections that make this $200 report UNIQUE. Sections 13 and 14 DO NOT exist in the $150 report.

## 12. SUBMISSIONS BLUEPRINT (1500+ words)
**Written Submission Strategy**: Write ACTUAL DRAFT PARAGRAPHS that could be filed with the court. For each major ground, write 2-3 paragraphs of draft submission text. Include argument sequence, authority placement, and framing. Write the opening paragraph and closing paragraph of the written submissions.

**Oral Submission Strategy** (write as flowing paragraphs, NOT bullet lists): For each ground, discuss the opening line to say to the bench, the likely bench questions with prepared response lines, time allocation recommendations, and how to handle judicial scepticism on weaker grounds. Write this as continuous prose.

## 13. HEARING PREPARATION NOTES (1200+ words — NEW SECTION NOT IN $150 REPORT)
For EACH of the {len(grounds)} grounds, write detailed flowing paragraphs (NOT bullet lists or dot points):
Cover the key arguments and talking points for each ground, the top 3 anticipated bench questions with suggested answers woven into the prose, which authority to cite first and why, concessions to make strategically vs points to contest, and any visual aids or demonstratives to prepare. Write as continuous analytical prose.

## 14. CONFERENCE PREPARATION PACK (1200+ words — NEW SECTION NOT IN $150 REPORT)
For briefing a barrister — write as an actual document:
- One-page case summary (write the ACTUAL summary — 300+ words covering lead theory, key facts, strongest grounds)
- Authorities shortlist (10+ cases with key passages identified)
- Orders sought (list specific court orders to request)
- Case strengths with evidence references (6+ points)
- Case weaknesses and mitigation strategy (4+ points with specific counter-arguments)
- Client instructions summary

STOP after section 14."""),
                ("PASS 7/10", f"""

NOW GENERATE ONLY SECTIONS 15-17. Write 4000+ WORDS for this pass. These sections are UNIQUE to the $200 report.

## 15. COURT PATHWAY OPERATIONS PLAYBOOK (1200+ words — NEW SECTION NOT IN $150 REPORT)
For EACH relevant court level in {state_info.get('name', 'the relevant jurisdiction')}:
- Court name and jurisdiction
- Filing sequence with specific documents required at each stage
- Court registry details (address, phone, email where available)
- Deadlines for each filing step
- Extension-of-time route if deadlines have passed — specific provisions and what needs to be demonstrated
- What happens at each stage (directions hearing, callover, full hearing)
- Estimated timeframes from filing to hearing
- Costs considerations

## 16. HOW TO START YOUR APPEAL + REQUIRED FORMS (800+ words)
Step-by-step guide specific to {state_info.get('name', 'the relevant jurisdiction')} with FULL DETAIL per step:
1. Obtain trial transcripts and exhibits — from which court registry, expected cost and timeframe
2. Identify and finalise grounds of appeal — how to narrow from identified grounds to filed grounds
3. Lodge Notice of Intention to Appeal — form name, deadline, where to lodge
4. Prepare detailed written submissions — structure, length, authorities
5. Serve documents on the Crown/DPP — who, where, method
6. Attend the appeal hearing — what to expect, who attends
Forms table: | Form/Document | Purpose | Where to Obtain | Filing Deadline |

## 17. SIMILAR CASE SEARCH OPTIONS (800+ words — NEW SECTION NOT IN $150 REPORT)
5+ tailored AustLII search queries specifically designed for this case:
For each query:
- The exact search string
- What it's designed to find
- Expected number of results and how to filter them
- Key cases to look for in results
- How to use the results to strengthen the appeal
Court-level filtering suggestions and keyword alternatives for each ground.

STOP after section 17."""),
                ("PASS 8/10", """

NOW GENERATE ONLY SECTIONS 18-19. Write 3000+ WORDS for this pass.

## 18. PRIORITISED ACTION PLAN (1000+ words)
72-hour actions (urgent — at least 6 specific actions):
For each: exact action, who to contact (name the office/registry), deadline, objective, what happens if missed.

7-day actions (important — at least 6 specific actions):
For each: exact action, resources needed, dependencies, expected outcome.

28-day actions (strategic — at least 6 specific actions):
For each: exact action, preparation steps, milestones, how this contributes to the appeal.

## 19. OPERATIONS ENGINE — CRITICAL MISSING EVIDENCE (1200+ words — NEW SECTION NOT IN $150 REPORT)
Auto-generated checklist of evidence gaps identified from the case analysis. For EACH gap, write 100+ words covering:
- What is missing (name the specific document, report, or testimony)
- Why it matters to the appeal — which specific ground(s) does it affect?
- Exact steps to obtain it (who to contact, what to request, expected timeframe)
- Priority: Critical / Important / Desirable
- Impact on appeal viability if NOT obtained

Identify at least 8 evidence gaps. This section is what differentiates the $200 report from the $150 report — it must be operationally specific, not generic.

STOP after section 19."""),
                ("PASS 9/10", f"""

NOW GENERATE ONLY SECTIONS 20-22. Write 3500+ WORDS for this pass. These sections are the OPERATIONS ENGINE that makes the $200 report unique.

## 20. EVIDENCE REQUEST LIST (800+ words — NEW SECTION NOT IN $150 REPORT)
Specific documents and materials that must be obtained. Produce an ACTUAL populated markdown table:
| Item | Source | Purpose | Priority | Deadline |
Include at least 10 rows. After the table, write a paragraph for each Critical-priority item explaining why it is essential.
Include: transcripts, expert reports, affidavits, medical records, CCTV, forensic reports, psychiatric assessments, sentencing submissions.

## 21. SUGGESTED EXPERT REPORTS (800+ words — NEW SECTION NOT IN $150 REPORT)
For each identified evidentiary gap that requires expert opinion, write 150+ words covering:
- Type of expert required (psychiatrist, forensic pathologist, toxicologist, etc.)
- What specific opinion is needed and what question should be put to the expert
- How the opinion would strengthen the appeal — which ground(s) does it support?
- Suggested brief outline for instructing the expert (3-4 key points to include in the brief)
Identify at least 4 expert reports needed.

## 22. FILING PATHWAY (800+ words — NEW SECTION NOT IN $150 REPORT)
Step-by-step filing requirements specific to {state_info.get('name', 'the relevant jurisdiction')}:
- Notice of Intention to Appeal (if not filed) — deadline, form name, where to lodge
- Detailed grounds of appeal — content requirements, format, page limits
- Written submissions — structure, length, authorities format
- Application for leave (if required) — criteria, threshold, what must be demonstrated
- Supporting affidavit requirements — who swears, what content
- Service requirements on DPP/Crown — method, timing, proof of service
- Extension of time (if applicable) — what must be shown, typical outcomes
Produce a timeline table: | Step | Document | Deadline | Filed With | Served On |

STOP after section 22."""),
                ("PASS 10/10", f"""

NOW GENERATE ONLY SECTIONS 23-24. Write 5000+ WORDS for this pass. Section 24 is the CLIENT BRIEF — it must be thorough and cover EVERY ground.

## 23. RISK ASSESSMENT + CONTINGENCY PLANNING (1200+ words — NEW SECTION NOT IN $150 REPORT)
For EACH of the {len(grounds)} grounds, write 150+ words covering:
- Appellate viability assessment (arguable/moderate/strong — NOT percentages)
- Main risk factor (what could go wrong?)
- Contingency if this ground fails (what's the backup?)
- Impact on overall appeal if this ground is excluded

Overall appeal risk assessment (500+ words):
- Best case scenario, likelihood, and path to get there
- Most likely outcome with realistic assessment
- Worst case scenario and mitigation strategy
- How grounds interact — if Ground 1 fails, does Ground 3 become stronger?
- Whether grounds should be argued independently or as a package

## 24. CLIENT PLAIN-ENGLISH BRIEF (2000+ words)
THIS IS THE FINAL SECTION. Write in plain, everyday English that explains the case in THIRD PERSON.

For EACH of the {len(grounds)} grounds individually:
- What this ground means in simple terms (2-3 sentences)
- Why it matters for the appeal (2-3 sentences)
- What the chances are (honest assessment)
- What happens if it succeeds (specific outcome)

Then cover:
- The overall appeal: what it is, why it's happening, and the realistic timeline
- Each possible outcome and what it means personally for the applicant
- Exactly what the applicant should do right now, this week, and this month
- What to expect at the hearing — how long, who's there, what happens
- Honest assessment of risks alongside the opportunities
- ABSOLUTE BAN: NEVER use "we", "us", "our", "you", "your". Use "the applicant", "the legal professional", "this analysis". WRONG: "The appeal is your opportunity." RIGHT: "The appeal represents an opportunity for the applicant."

Do NOT truncate. Write ALL content for both sections."""),
            ]
            
            parts = []
            resume_from = 0
            if report_id:
                existing_report = await db.reports.find_one(
                    {"report_id": report_id},
                    {"_id": 0, "content.partial_analysis": 1, "content.passes_completed": 1},
                )
                existing_content = (existing_report or {}).get("content") or {}
                existing_partial = existing_content.get("partial_analysis") or ""
                existing_passes_completed = int(existing_content.get("passes_completed") or 0)
                if existing_partial and existing_passes_completed > 0:
                    parts = [existing_partial]
                    resume_from = min(existing_passes_completed, len(passes))
                    logger.info(f"Resuming extensive_log report {report_id} from pass {resume_from + 1}")

            for pass_index, (label, instruction) in enumerate(passes[resume_from:], start=resume_from + 1):
                await _update_report_pass_progress(report_id, pass_index, len(passes), label)
                # Pass 1 gets full document context; passes 2-8 get condensed context
                base_prompt = user_prompt if pass_index == 1 else condensed_prompt
                pass_prompt = base_prompt + instruction
                # TPM safety cap — see full_detailed loop above for rationale.
                TPM_SAFE_CAP = 90000
                if len(pass_prompt) > TPM_SAFE_CAP:
                    head_keep = int(TPM_SAFE_CAP * 0.55)
                    tail_keep = TPM_SAFE_CAP - head_keep - 200
                    pass_prompt = (
                        pass_prompt[:head_keep]
                        + "\n\n[... middle context truncated for API token limits; see remaining context below ...]\n\n"
                        + pass_prompt[-tail_keep:]
                    )
                    logger.warning(f"Extensive log {label} prompt truncated to {len(pass_prompt)} chars for TPM-safe cap")
                logger.info(f"Extensive log {label} prompt size: system={len(system_prompt)}, user={len(pass_prompt)}")
                part = await _subprocess_llm(pass_prompt)
                parts.append(part)
                logger.info(f"Extensive log {label} response: {len(part)} chars")
                # Save partial progress after each pass so server restarts don't lose work
                partial_response = "\n\n".join(parts)
                await db.reports.update_one(
                    {"report_id": report_id},
                    {"$set": {"content.partial_analysis": partial_response, "content.passes_completed": pass_index}}
                )
            
            response = "\n\n".join(parts)
            logger.info(f"Extensive log combined: {len(response)} chars")

        else:
            logger.info(f"Report prompt size: system={len(system_prompt)}, user={len(user_prompt)}, total={len(system_prompt)+len(user_prompt)}")
            response = await _subprocess_llm(user_prompt)
    except Exception as e:
        last_error = e
        logger.error(f"Report generation failed: {e}")
    
    if response is None:
        logger.error(f"All report generation attempts failed: {last_error}")
        raise HTTPException(status_code=503, detail=f"AI report generation failed after retries: {str(last_error)}")

    anchor_terms = _build_anchor_terms(case, documents, timeline, grounds)
    response = _dedupe_report_content(response, report_type, anchor_terms)

    # DO_NOT_UNDO — Missing section repair. The resume logic can produce reports with
    # missing sections if a pass's LLM output truncated. This step detects missing
    # sections and generates them in-place BEFORE the expansion step runs.
    if report_type in ("quick_summary", "full_detailed", "extensive_log"):
        # Define expected main sections for each report type
        expected_sections_map = {
            "quick_summary": {
                "## 1.": "CASE SNAPSHOT",
                "## 2.": "PRIMARY ISSUES IDENTIFIED",
                "## 3.": "ALL GROUNDS IDENTIFIED (PREVIEW)",
                "## 4.": "KEY LEGISLATION (PREVIEW)",
                "## 5.": "SENTENCING OVERVIEW",
                "## 6.": "APPEAL OUTLOOK",
                "## 7.": "PLAIN ENGLISH GUIDE",
            },
            "full_detailed": {
                "## 1.": "EXECUTIVE BRIEF",
                "## 2.": "FORENSIC CASE CHRONOLOGY",
                "## 3.": "DOCUMENT EVIDENCE DIGEST",
                "## 4.": "GROUNDS OF MERIT",
                "## 5.": "COMPARATIVE SENTENCING TABLE",
                "## 7.": "OUTCOME OPTIONS",
            },
            "extensive_log": {
                "## 1.": "EXECUTIVE BRIEF",
                "## 2.": "FORENSIC CASE CHRONOLOGY",
                "## 3.": "DOCUMENT EVIDENCE DIGEST",
                "## 4.": "GROUNDS OF MERIT",
                "## 5.": "COMPARATIVE SENTENCING TABLE",
                "## 9.": "PRECEDENT OUTCOME MATRIX",
                "## 11.": "HOW TO ARGUE EACH TOP GROUND",
                "## 18.": "PRIORITISED ACTION PLAN",
                "## 19.": "OPERATIONS ENGINE — CRITICAL MISSING EVIDENCE",
                "## 20.": "EVIDENCE REQUEST LIST",
                "## 21.": "SUGGESTED EXPERT REPORTS",
                "## 22.": "FILING PATHWAY",
                "## 23.": "RISK ASSESSMENT + CONTINGENCY PLANNING",
                "## 24.": "CLIENT PLAIN-ENGLISH BRIEF",
            },
        }
        expected = expected_sections_map.get(report_type, {})
        sections_in_report = _split_report_sections(response)

        for prefix, name in expected.items():
            # Check if this section exists in the report (match "## N." prefix)
            if not any(h.startswith(prefix.rstrip()) for h, _ in sections_in_report if h):
                logger.warning(f"Missing section detected: {prefix} {name}. Generating repair.")
                try:
                    doc_list = "\n".join([f"- {d.get('original_filename', d.get('filename', 'Unknown'))}" for d in documents[:20]])
                    # Size targets scale to report depth — quick_summary sections are
                    # concise (issue identification only); paid reports need heavy prose.
                    if report_type == "quick_summary":
                        target_chars = "1500-3000 characters"
                        min_repaired = 300
                    else:
                        target_chars = "4000-6000 characters"
                        min_repaired = 500
                    repair_prompt = f"""Generate the MISSING section for a legal appeal report.

CASE: {case.get('title', 'Unknown')} ({case.get('state') or 'Unspecified'})
SENTENCE: {case.get('sentence', 'Not specified')}
DOCUMENTS ({len(documents)}):
{doc_list}

GROUNDS:
{grounds_enumerated}

WRITE THIS SECTION:
{prefix} {name}

INSTRUCTIONS:
- Write {target_chars} of substantive, case-specific content
- Reference specific case facts, dates, documents, and legal authorities
- Use flowing paragraphs, NOT bullet points
- Australian English, strict third-person only (NEVER "you", "your", "we", "us")
- Start the section with exactly: {prefix} {name}
- Do NOT include any other section headings
"""
                    repaired = await _subprocess_llm(repair_prompt)
                    if repaired and len(repaired.strip()) > min_repaired:
                        # Find the insertion point — insert before the NEXT numbered section
                        section_num = int(prefix.replace("##", "").replace(".", "").strip())
                        insert_point = len(response)
                        for h, _ in sections_in_report:
                            if h:
                                try:
                                    h_num = int(re.search(r"(\d+)", h).group(1))
                                    if h_num > section_num:
                                        insert_point = response.find(h)
                                        break
                                except (ValueError, AttributeError):
                                    continue
                        # Clean up the repair output
                        cleaned_repair = repaired.strip()
                        if not cleaned_repair.startswith("##"):
                            cleaned_repair = f"{prefix} {name}\n\n{cleaned_repair}"
                        response = response[:insert_point] + "\n\n" + cleaned_repair + "\n\n" + response[insert_point:]
                        logger.info(f"Repaired missing section: {prefix} {name} ({len(cleaned_repair)} chars)")
                        # Re-split after insertion
                        sections_in_report = _split_report_sections(response)
                except Exception as exc:
                    logger.warning(f"Section repair failed for {prefix} {name}: {exc}")

    # DO_NOT_UNDO — Minimum character targets. NEVER lower these values.
    min_lengths = {
        "quick_summary": 14000,
        "full_detailed": 80000,
        "extensive_log": 150000
    }
    target_length = min_lengths.get(report_type, 12000)
    if aggressive_mode:
        target_length = int(target_length * 2.0)

    # Expand ANY report that falls below target — multi-pass reports can still be short
    if len(response) < target_length:
        logger.info(f"Report below target ({len(response)} < {target_length}), running expansion pass(es)")
        
        if report_type in ("full_detailed", "extensive_log"):
            # For multi-pass reports, expand the THINNEST sections individually to avoid 502 errors
            sections = _split_report_sections(response)
            # Sort sections by content length (shortest first) and expand the thin ones
            thin_sections = [(heading, content) for heading, content in sections if heading and len(content) < 3000]
            thin_sections.sort(key=lambda x: len(x[1]))
            
            for heading, content in thin_sections[:6]:  # Expand up to 6 thin sections
                try:
                    section_expand_prompt = f"""You are expanding one section of a legal report for a criminal appeal case.

CASE CONTEXT:
{case_context[:15000]}

SECTION TO EXPAND: {heading}
Current content ({len(content)} chars — this is TOO SHORT, must be 4000+ chars):

{content}

INSTRUCTIONS:
- Rewrite this ENTIRE section with MUCH MORE detail. Target 4000-6000 characters minimum.
- Reference specific case facts: names, dates, section numbers, case citations.
- Write in flowing paragraphs, NOT bullet points.
- Use Australian English and strict third-person language.
- Include statutory references with full citations (section + Act + year + jurisdiction).
- The section heading must remain exactly: {heading}
- Do NOT include any other section headings. Write ONLY this one section.
- Make the content case-specific — avoid generic legal advice.

GROUNDS COVERED IN THIS CASE:
{grounds_enumerated}
"""
                    expanded_section = await _subprocess_llm(section_expand_prompt)
                    if expanded_section and len(expanded_section) > len(content) * 1.3:
                        # Replace the thin section with the expanded version
                        # Find the section in the response and replace it
                        escaped_heading = re.escape(heading)
                        section_pattern = rf"({escaped_heading})\n([\s\S]*?)(?=\n## \d+\.|$)"
                        match = re.search(section_pattern, response)
                        if match:
                            # Extract just the new content (strip the heading if the LLM repeated it)
                            new_content = expanded_section
                            if new_content.strip().startswith(heading):
                                new_content = new_content.strip()[len(heading):].strip()
                            response = response[:match.start(2)] + new_content + response[match.end(2):]
                            logger.info(f"Section expanded: {heading} ({len(content)} → {len(new_content)} chars)")
                except Exception as exc:
                    logger.warning(f"Section expansion failed for {heading}: {exc}")
                    continue
        else:
            # For single-pass reports (quick_summary), try a full expansion
            expansion_attempts = 0
            while len(response) < target_length and expansion_attempts < 2:
                expansion_attempts += 1
                try:
                    expansion_prompt = f"""{case_context}

The report below is {len(response)} characters but must be at least {target_length} characters. EXPAND IT SUBSTANTIALLY. 

RULES:
- Keep ALL existing ## section headings exactly as-is. Do NOT rename or reorder sections.
- Do NOT remove or rewrite any existing text — only ADD new paragraphs.
- Add case-specific details: names, dates, section numbers, case citations, document references.
- Every added paragraph must reference specific facts from THIS case.
- Avoid repetition — add NEW analysis, additional authorities, deeper reasoning.
- Write in FLOWING PARAGRAPHS, not bullet points.
- Maintain Australian English and third-person language throughout.

REPORT TO EXPAND:
{response}
"""
                    expanded = await _subprocess_llm(expansion_prompt)
                    if expanded and len(expanded) > len(response) * 1.05:
                        response = expanded
                        logger.info(f"Expansion attempt {expansion_attempts}: {len(response)} chars")
                    else:
                        logger.warning(f"Expansion attempt {expansion_attempts} did not add enough content")
                        break
                except Exception as exc:
                    logger.warning(f"Report expansion attempt {expansion_attempts} failed: {exc}")
                    break

    response = _strip_report_placeholders(response)
    response = _sanitise_suspect_authorities(response)
    # DO_NOT_UNDO — Normalise markdown BEFORE persisting so bad LLM formatting
    # (inline `## Heading`, `- **Bullet**` glued to prose, missing blank lines
    # around tables) can never hit the DB. Applies to all report types.
    from services.md_normaliser import normalise_markdown
    response = normalise_markdown(response)
    response = response.strip()

    # Preserve the actual grounds linked to the case so reports reflect the real ground count.
    grounds_of_merit = [
        {
            "ground_id": ground.get("ground_id"),
            "title": ground.get("title", "Untitled ground"),
            "description": ground.get("description", ""),
            "strength": ground.get("strength", "moderate"),
            "ground_type": ground.get("ground_type", "other"),
        }
        for ground in grounds
    ]
    
    if aggressive_mode:
        response += """

---

**IMPORTANT DISCLAIMER:** This report is for educational and research purposes only. It does not constitute legal advice. Always consult a qualified legal practitioner before taking any action.
"""

    # Build provenance metadata
    report_metadata = ReportMetadata(
        generated_by_model=_report_generation_metadata["models_used"][-1] if _report_generation_metadata["models_used"] else None,
        fallback_used=_report_generation_metadata["fallback_used"],
        documents_analyzed=len(documents),
        timeline_events_analyzed=len(timeline),
        grounds_considered=len(grounds),
        verification_status="draft",
        confidence_note="AI-generated output requiring legal review",
    )

    return {
        "analysis": response,
        "grounds_of_merit": grounds_of_merit,
        "case_data": case,
        "document_count": len(documents),
        "event_count": len(timeline),
        "metadata": report_metadata.model_dump(),
        "pipeline_metadata": {
            "status": pipeline_status.get("status") if pipeline_status else "not_checked",
            "staleness": pipeline_status.get("staleness") if pipeline_status else None,
            "auto_refreshed": pipeline_status.get("status") == "refreshed" if pipeline_status else False,
            "pipeline_argument_count": len(pipeline_arguments),
            "submission_draft_present": bool(submission_draft),
        },
    }


