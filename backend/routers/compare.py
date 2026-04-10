# DO NOT UNDO — compare router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Compare Cases Router
Allows users to compare their own cases and see anonymized patterns from all users

ADDITIVE HARDENING PATCH
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel

from config import db
from auth_utils import get_current_user

router = APIRouter(prefix="/api/compare", tags=["compare"])


class CaseComparisonRequest(BaseModel):
    case_ids: List[str]


class PatternFilter(BaseModel):
    offence_category: Optional[str] = None
    state: Optional[str] = None
    ground_type: Optional[str] = None


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

MIN_PATTERN_SAMPLE = 10
MIN_FACTOR_SAMPLE = 10


def _safe_avg(total: int, count: int) -> float:
    if count <= 0:
        return 0.0
    return round(total / count, 1)


def _count_strengths(grounds: list) -> dict:
    return {
        "strong": len([g for g in grounds if g.get("strength") == "strong"]),
        "moderate": len([g for g in grounds if g.get("strength") == "moderate"]),
        "weak": len([g for g in grounds if g.get("strength") == "weak"]),
    }


def _top_items(dist: dict, limit: int = 5) -> list:
    return sorted(dist.items(), key=lambda x: x[1], reverse=True)[:limit]


# ============================================================================
# COMPARE MY CASES
# ============================================================================

@router.post("/my-cases")
async def compare_my_cases(request: Request):
    """
    Compare multiple cases from the user's own account.
    Supports both Pydantic body and raw JSON body for backward compatibility.
    """
    user = await get_current_user(request)

    body = await request.json()
    case_ids = body.get("case_ids", [])

    if len(case_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 cases to compare")

    if len(case_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 cases can be compared at once")

    cases = []
    for case_id in case_ids:
        case = await db.cases.find_one(
            {"case_id": case_id, "user_id": user.user_id},
            {"_id": 0}
        )
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        cases.append(case)

    case_grounds = {}
    for case in cases:
        grounds = await db.grounds_of_merit.find(
            {"case_id": case["case_id"], "user_id": user.user_id},
            {"_id": 0}
        ).to_list(100)
        case_grounds[case["case_id"]] = grounds

    case_timelines = {}
    for case in cases:
        events = await db.timeline_events.find(
            {"case_id": case["case_id"], "user_id": user.user_id},
            {"_id": 0}
        ).sort("event_date", 1).to_list(500)
        case_timelines[case["case_id"]] = events

    case_docs = {}
    for case in cases:
        docs = await db.documents.find(
            {"case_id": case["case_id"], "user_id": user.user_id},
            {"_id": 0, "file_data": 0}
        ).to_list(500)
        case_docs[case["case_id"]] = docs

    comparison_result = {
        "cases": [],
        "ground_comparison": {
            "common_ground_types": [],
            "unique_ground_types": {},
            "ground_type_distribution": {}
        },
        "timeline_comparison": {
            "avg_events_per_case": 0,
            "common_event_types": [],
            "timeline_gaps": {}
        },
        "document_comparison": {
            "avg_documents_per_case": 0,
            "category_distribution": {}
        },
        "common_ground_types": [],
        "jurisdiction_summary": "",
        "insights": [],
        "disclaimer": (
            "This comparison is descriptive. It highlights similarities in your case records and "
            "identified issues, but does not determine legal merit or likely appeal outcome."
        ),
        "assessment_note": (
            "This comparison is descriptive. It highlights similarities in your case records and "
            "identified issues, but does not determine legal merit or likely appeal outcome."
        )
    }

    for case in cases:
        case_id = case["case_id"]
        grounds = case_grounds.get(case_id, [])
        events = case_timelines.get(case_id, [])
        docs = case_docs.get(case_id, [])

        comparison_result["cases"].append({
            "case_id": case_id,
            "title": case.get("title"),
            "defendant_name": case.get("defendant_name"),
            "offence_category": case.get("offence_category"),
            "offence_type": case.get("offence_type"),
            "state": case.get("state"),
            "grounds_count": len(grounds),
            "events_count": len(events),
            "documents_count": len(docs),
            "ground_types": list(set(g.get("ground_type") for g in grounds if g.get("ground_type"))),
            "ground_strengths": _count_strengths(grounds),
            "strength_distribution": _count_strengths(grounds),
            "timeline_events": len(events),
            "documents": len(docs),
            "created_at": case.get("created_at", ""),
        })

    all_ground_types = []
    unique_ground_types = {}

    for case_id, grounds in case_grounds.items():
        per_case_types = list(set(g.get("ground_type") for g in grounds if g.get("ground_type")))
        unique_ground_types[case_id] = per_case_types
        all_ground_types.extend(per_case_types)

    ground_type_counts = {}
    for gt in all_ground_types:
        ground_type_counts[gt] = ground_type_counts.get(gt, 0) + 1

    common_types = [gt for gt, count in ground_type_counts.items() if count >= 2]

    comparison_result["ground_comparison"]["ground_type_distribution"] = ground_type_counts
    comparison_result["ground_comparison"]["common_ground_types"] = common_types
    comparison_result["ground_comparison"]["unique_ground_types"] = unique_ground_types
    comparison_result["common_ground_types"] = common_types

    event_type_counts = {}
    for events in case_timelines.values():
        for event in events:
            et = event.get("event_type", "event")
            event_type_counts[et] = event_type_counts.get(et, 0) + 1
    comparison_result["timeline_comparison"]["common_event_types"] = [k for k, _ in _top_items(event_type_counts)]

    category_dist = {}
    for docs in case_docs.values():
        for doc in docs:
            cat = doc.get("category", "other")
            category_dist[cat] = category_dist.get(cat, 0) + 1
    comparison_result["document_comparison"]["category_distribution"] = category_dist

    total_events = sum(len(events) for events in case_timelines.values())
    total_docs = sum(len(docs) for docs in case_docs.values())
    num_cases = len(cases)

    comparison_result["timeline_comparison"]["avg_events_per_case"] = _safe_avg(total_events, num_cases)
    comparison_result["document_comparison"]["avg_documents_per_case"] = _safe_avg(total_docs, num_cases)

    insights = []

    if common_types:
        insights.append(f"Recurring ground types across selected cases: {', '.join(common_types)}")

    total_strong = sum(cs["ground_strengths"]["strong"] for cs in comparison_result["cases"])
    if total_strong > 0:
        insights.append(f"Total grounds currently labelled strong across selected cases: {total_strong}")

    offence_categories = [c.get("offence_category") for c in cases if c.get("offence_category")]
    if offence_categories and len(set(offence_categories)) == 1:
        insights.append(f"All selected cases fall within the same offence category: {offence_categories[0]}")

    states = [c.get("state") for c in cases if c.get("state")]
    if states and len(set(states)) == 1:
        comparison_result["jurisdiction_summary"] = f"All cases are in {states[0].upper()} — same jurisdiction applies"
        insights.append(f"All selected cases are recorded in {states[0].upper()} — jurisdictional framework is consistent across the comparison")
    elif states:
        comparison_result["jurisdiction_summary"] = f"Cases span {len(set(states))} jurisdictions: {', '.join(sorted(set(s.upper() for s in states)))}"
        insights.append(f"Selected cases span multiple jurisdictions ({', '.join(sorted(set(s.upper() for s in states)))}) — legal frameworks differ across those matters")

    comparison_result["insights"] = insights

    return comparison_result


# ============================================================================
# ANONYMIZED PLATFORM PATTERNS
# ============================================================================

@router.get("/patterns")
async def get_anonymized_patterns(
    request: Request,
    offence_category: Optional[str] = None,
    state: Optional[str] = None,
    ground_type: Optional[str] = None
):
    """
    Get anonymized aggregate patterns from platform data.
    These are platform-record patterns only and are NOT court outcome statistics.
    """
    await get_current_user(request)

    case_filter = {}
    if offence_category:
        case_filter["offence_category"] = offence_category
    if state:
        case_filter["state"] = state

    matching_cases = await db.cases.find(
        case_filter,
        {"case_id": 1, "state": 1, "offence_category": 1, "_id": 0}
    ).to_list(10000)

    total_cases = len(matching_cases)

    if total_cases == 0:
        return {
            "total_cases_analyzed": 0,
            "total_cases": 0,
            "message": "No cases found matching the specified criteria",
            "patterns": {},
            "ground_type_distribution": {},
            "strength_distribution": {},
            "status_distribution": {},
            "insights": [],
            "recommendations": [],
            "assessment_note": "No platform data matched the selected filters.",
            "disclaimer": "These patterns reflect internal platform usage data, not court outcomes or legal success metrics."
        }

    if total_cases < MIN_PATTERN_SAMPLE:
        return {
            "total_cases_analyzed": total_cases,
            "total_cases": total_cases,
            "suppressed": True,
            "message": f"Insufficient data for reliable aggregate pattern analysis. At least {MIN_PATTERN_SAMPLE} cases required.",
            "patterns": {},
            "ground_type_distribution": {},
            "strength_distribution": {},
            "status_distribution": {},
            "insights": [],
            "recommendations": [],
            "filters_applied": {
                "offence_category": offence_category,
                "state": state,
                "ground_type": ground_type
            },
            "assessment_note": (
                f"At least {MIN_PATTERN_SAMPLE} matching cases are required before detailed aggregate "
                "pattern outputs are shown."
            ),
            "disclaimer": "These patterns reflect internal platform usage data, not court outcomes or legal success metrics."
        }

    case_ids = [c["case_id"] for c in matching_cases]

    ground_filter = {"case_id": {"$in": case_ids}}
    if ground_type:
        ground_filter["ground_type"] = ground_type

    grounds = await db.grounds_of_merit.find(ground_filter, {"_id": 0}).to_list(10000)

    ground_type_dist = {}
    strength_dist = {"strong": 0, "moderate": 0, "weak": 0}
    status_dist = {}

    for ground in grounds:
        gt = ground.get("ground_type", "other")
        ground_type_dist[gt] = ground_type_dist.get(gt, 0) + 1

        strength = ground.get("strength", "moderate")
        if strength in strength_dist:
            strength_dist[strength] += 1

        status = ground.get("status", "identified")
        status_dist[status] = status_dist.get(status, 0) + 1

    sorted_ground_types = sorted(ground_type_dist.items(), key=lambda x: x[1], reverse=True)

    total_grounds = len(grounds)
    confirmed_grounds = status_dist.get("confirmed", 0)
    confirmed_grounds_platform_rate = round((confirmed_grounds / total_grounds) * 100, 1) if total_grounds > 0 else 0

    state_dist = {}
    offence_dist = {}
    for case in matching_cases:
        s = case.get("state", "") or "unspecified"
        oc = case.get("offence_category", "other")
        state_dist[s] = state_dist.get(s, 0) + 1
        offence_dist[oc] = offence_dist.get(oc, 0) + 1

    insights = []

    if sorted_ground_types:
        top_ground = sorted_ground_types[0]
        insights.append(f"Most frequently identified ground type in this filtered platform dataset: {top_ground[0]} ({top_ground[1]} records)")

    if strength_dist["strong"] > 0 and total_grounds > 0:
        strong_pct = round((strength_dist["strong"] / total_grounds) * 100, 1)
        insights.append(f"{strong_pct}% of grounds in this filtered platform dataset are currently labelled strong")

    avg_grounds = round(total_grounds / total_cases, 1) if total_cases > 0 else 0
    if avg_grounds > 0:
        insights.append(f"Average {avg_grounds} grounds recorded per case in this filtered platform dataset")

    return {
        "total_cases_analyzed": total_cases,
        "total_cases": total_cases,
        "total_grounds_analyzed": total_grounds,
        "total_grounds": total_grounds,
        "suppressed": False,
        "filters_applied": {
            "offence_category": offence_category,
            "state": state,
            "ground_type": ground_type
        },
        "patterns": {
            "ground_type_distribution": dict(sorted_ground_types),
            "strength_distribution": strength_dist,
            "status_distribution": status_dist,
            "state_distribution": state_dist,
            "offence_distribution": offence_dist
        },
        "ground_type_distribution": dict(sorted_ground_types),
        "strength_distribution": strength_dist,
        "status_distribution": status_dist,
        "state_distribution": state_dist,
        "offence_distribution": offence_dist,
        "confirmed_in_app_rate": confirmed_grounds_platform_rate,
        "platform_indicators": {
            "confirmed_grounds_platform_rate": confirmed_grounds_platform_rate,
            "strong_grounds_count": strength_dist["strong"],
            "avg_grounds_per_case": avg_grounds
        },
        "insights": insights,
        "recommendations": [
            f"Review {sorted_ground_types[0][0]} issues because they appear most frequently in this filtered platform dataset" if sorted_ground_types else None,
            "Use these platform patterns as a descriptive research aid only",
            "Verify all identified grounds independently against documents, legislation, and case law"
        ],
        "assessment_note": (
            "These figures reflect anonymized platform records and statuses only. "
            "They are not Australian court outcome statistics and do not predict appeal success."
        ),
        "disclaimer": (
            "These patterns reflect internal platform usage data, not court outcomes or legal success metrics. "
            "Ground ratings are generated by the platform's analytical engine and require independent legal verification."
        )
    }


# ============================================================================
# PLATFORM PATTERN INDICATORS (BACKWARD COMPATIBLE — SERVES BOTH ROUTES)
# ============================================================================

async def _get_case_composition_data(request: Request, offence_category: Optional[str] = None):
    """Shared logic for case-composition / success-factors endpoints."""
    await get_current_user(request)

    case_filter = {}
    if offence_category:
        case_filter["offence_category"] = offence_category

    all_cases = await db.cases.find(
        case_filter,
        {"case_id": 1, "offence_category": 1, "state": 1, "_id": 0}
    ).to_list(10000)

    if not all_cases:
        return {
            "message": "No cases found",
            "total_cases": 0,
            "success_factors": [],
            "disclaimer": "This analysis reflects case preparation patterns within the platform, not legal merit or appeal prospects.",
            "assessment_note": "No platform records matched the selected filters."
        }

    if len(all_cases) < MIN_FACTOR_SAMPLE:
        return {
            "message": "Insufficient data for reliable pattern indicators",
            "total_cases": len(all_cases),
            "total_cases_analyzed": len(all_cases),
            "suppressed": True,
            "success_factors": [],
            "disclaimer": "This analysis reflects case preparation patterns within the platform, not legal merit or appeal prospects.",
            "assessment_note": (
                f"At least {MIN_FACTOR_SAMPLE} cases are required before platform pattern indicators "
                "are shown for this view."
            )
        }

    case_analyses = []
    for case in all_cases:
        case_id = case["case_id"]

        grounds = await db.grounds_of_merit.find(
            {"case_id": case_id},
            {"ground_type": 1, "strength": 1, "status": 1, "_id": 0}
        ).to_list(100)

        doc_count = await db.documents.count_documents({"case_id": case_id})
        event_count = await db.timeline_events.count_documents({"case_id": case_id})

        strong_count = len([g for g in grounds if g.get("strength") == "strong"])
        confirmed_count = len([g for g in grounds if g.get("status") == "confirmed"])

        case_analyses.append({
            "offence_category": case.get("offence_category"),
            "state": case.get("state"),
            "total_grounds": len(grounds),
            "strong_grounds": strong_count,
            "confirmed_grounds": confirmed_count,
            "documents": doc_count,
            "timeline_events": event_count,
            "docs_with_text": doc_count,
            "ground_types": [g.get("ground_type") for g in grounds if g.get("ground_type")]
        })

    higher_signal_cases = [c for c in case_analyses if c["strong_grounds"] >= 2 or c["confirmed_grounds"] >= 1]
    lightly_documented_cases = [c for c in case_analyses if c["documents"] < 3 or c["timeline_events"] < 5]
    well_documented_cases = [c for c in case_analyses if c["documents"] >= 3 and c["timeline_events"] >= 5]

    success_factors = []

    if higher_signal_cases:
        platform_ground_types = {}
        for case in higher_signal_cases:
            for gt in case["ground_types"]:
                platform_ground_types[gt] = platform_ground_types.get(gt, 0) + 1

        sorted_platform_grounds = sorted(platform_ground_types.items(), key=lambda x: x[1], reverse=True)

        if sorted_platform_grounds:
            success_factors.append({
                "factor": "Frequent Ground Type",
                "finding": f"Most frequent ground type among higher-signal platform cases: {sorted_platform_grounds[0][0]}",
                "recommendation": f"Review whether {sorted_platform_grounds[0][0]} issues arise in the current matter, then verify them independently"
            })

        avg_docs_higher_signal = sum(c["documents"] for c in higher_signal_cases) / len(higher_signal_cases)
        avg_docs_all = sum(c["documents"] for c in case_analyses) / len(case_analyses) if case_analyses else 0

        if avg_docs_higher_signal > avg_docs_all:
            success_factors.append({
                "factor": "Documentation Volume",
                "finding": f"Higher-signal platform cases average {round(avg_docs_higher_signal, 1)} documents versus {round(avg_docs_all, 1)} across all matched cases",
                "recommendation": "More complete document sets may improve issue identification and preparation completeness"
            })

        avg_events_higher_signal = sum(c["timeline_events"] for c in higher_signal_cases) / len(higher_signal_cases)
        avg_events_all = sum(c["timeline_events"] for c in case_analyses) / len(case_analyses) if case_analyses else 0

        if avg_events_higher_signal > avg_events_all:
            success_factors.append({
                "factor": "Timeline Detail",
                "finding": f"Higher-signal platform cases average {round(avg_events_higher_signal, 1)} timeline events versus {round(avg_events_all, 1)} overall",
                "recommendation": "A more detailed timeline may improve preparation and issue visibility"
            })

    def avg_field(cases_list, field):
        if not cases_list:
            return 0
        return round(sum(c[field] for c in cases_list) / len(cases_list), 1)

    insights = []
    if well_documented_cases:
        insights.append(f"Well-documented cases average {avg_field(well_documented_cases, 'total_grounds')} identified grounds vs {avg_field(lightly_documented_cases, 'total_grounds')} in less-documented cases")
        insights.append(f"Well-documented cases average {avg_field(well_documented_cases, 'documents')} documents and {avg_field(well_documented_cases, 'timeline_events')} timeline events")

    return {
        "total_cases_analyzed": len(case_analyses),
        "total_cases": len(all_cases),
        "cases_with_higher_signal_indicators": len(higher_signal_cases),
        "well_documented_count": len(well_documented_cases),
        "lightly_documented_count": len(lightly_documented_cases),
        "suppressed": False,
        "success_factors": success_factors,
        "well_documented_profile": {
            "avg_grounds": avg_field(well_documented_cases, "total_grounds"),
            "avg_strong_grounds": avg_field(well_documented_cases, "strong_grounds"),
            "avg_documents": avg_field(well_documented_cases, "documents"),
            "avg_timeline_events": avg_field(well_documented_cases, "timeline_events"),
        },
        "lightly_documented_profile": {
            "avg_grounds": avg_field(lightly_documented_cases, "total_grounds"),
            "avg_documents": avg_field(lightly_documented_cases, "documents"),
            "avg_timeline_events": avg_field(lightly_documented_cases, "timeline_events"),
        },
        "insights": insights,
        "general_recommendations": [
            "Upload all available case documents",
            "Build a comprehensive timeline of events",
            "Review grounds with the clearest documentary support",
            "Treat platform indicators as descriptive only, not outcome predictions"
        ],
        "recommendations": [
            "Comprehensive documentation helps identify more potential issues for review",
            "Building a detailed timeline aids in identifying procedural irregularities",
            "All grounds require independent assessment by qualified counsel",
        ],
        "assessment_note": (
            "These are internal platform pattern indicators, not court success analytics. "
            "They describe characteristics of cases with more recorded strong or confirmed grounds within the platform dataset."
        ),
        "disclaimer": (
            "This analysis reflects case preparation patterns within the platform, not legal merit or appeal prospects. "
            "More documentation or more identified grounds does not necessarily indicate stronger appeal viability."
        )
    }


@router.get("/success-factors")
async def get_success_factors(request: Request, offence_category: Optional[str] = None):
    """Platform pattern indicators (hardened endpoint)."""
    return await _get_case_composition_data(request, offence_category)


@router.get("/case-composition")
async def get_case_composition_patterns(request: Request, offence_category: Optional[str] = None, state: Optional[str] = None):
    """Backward-compatible alias for case-composition endpoint used by frontend."""
    return await _get_case_composition_data(request, offence_category)
