# DO NOT UNDO - Compare Analytics Router
# Reframed: presents internal platform patterns, NOT legal success analytics
"""
Criminal Appeal AI - Compare & Analytics Router
Handles case comparison and anonymised aggregate pattern analysis.

IMPORTANT DESIGN RULES:
  - "Success factors" are renamed to "case composition patterns"
  - "Confirmed grounds rate" is renamed to "proportion of grounds marked confirmed in-app"
  - Minimum sample thresholds prevent misleading small-cohort outputs
  - All pattern outputs carry a provenance disclaimer
"""
from fastapi import APIRouter, HTTPException, Request
from collections import Counter
from datetime import datetime, timezone
import logging

from config import db
from auth_utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/compare", tags=["compare"])

MINIMUM_SAMPLE_SIZE = 5  # Suppress detailed pattern reporting below this threshold


@router.post("/my-cases")
async def compare_my_cases(request: Request):
    """Compare 2-5 of the user's own cases side by side."""
    user = await get_current_user(request)
    body = await request.json()
    case_ids = body.get("case_ids", [])
    if len(case_ids) < 2 or len(case_ids) > 5:
        raise HTTPException(status_code=400, detail="Select 2-5 cases to compare")

    comparison = {
        "cases": [],
        "common_ground_types": [],
        "jurisdiction_summary": "",
        "insights": [],
        "disclaimer": "This comparison reflects case data stored in the platform. It is not a determination of legal merit."
    }

    all_ground_types = []
    all_states = []
    total_events = 0
    total_docs = 0
    total_grounds_count = 0

    for cid in case_ids:
        case = await db.cases.find_one({"case_id": cid, "user_id": user.user_id}, {"_id": 0})
        if not case:
            raise HTTPException(status_code=404, detail=f"Case not found: {cid}")

        grounds = await db.grounds_of_merit.find({"case_id": cid}, {"_id": 0}).to_list(100)
        timeline = await db.timeline_events.find({"case_id": cid}, {"_id": 0}).to_list(500)
        documents = await db.documents.find({"case_id": cid}, {"_id": 0, "file_data": 0}).to_list(500)

        ground_types = [g.get("ground_type", "other") for g in grounds]
        all_ground_types.extend(ground_types)
        all_states.append(case.get("state", "unknown"))
        total_events += len(timeline)
        total_docs += len(documents)
        total_grounds_count += len(grounds)

        strength_dist = Counter(g.get("strength", "moderate") for g in grounds)

        comparison["cases"].append({
            "case_id": cid,
            "title": case.get("title", "Untitled"),
            "state": case.get("state", "unknown"),
            "offence_category": case.get("offence_category", "unknown"),
            "grounds_count": len(grounds),
            "strength_distribution": dict(strength_dist),
            "ground_types": list(set(ground_types)),
            "timeline_events": len(timeline),
            "documents": len(documents),
            "created_at": case.get("created_at", "")
        })

    type_counts = Counter(all_ground_types)
    common_types = [t for t, c in type_counts.items() if c >= 2]
    comparison["common_ground_types"] = common_types

    unique_states = list(set(all_states))
    if len(unique_states) == 1 and unique_states[0] != "unknown":
        comparison["jurisdiction_summary"] = f"All cases are in {unique_states[0].upper()} — same jurisdiction applies, though appellate tests may differ by offence type"
    else:
        comparison["jurisdiction_summary"] = f"Cases span {len(unique_states)} jurisdictions: {', '.join(s.upper() for s in unique_states)} — note that appellate tests and legislation differ between jurisdictions"

    if common_types:
        comparison["insights"].append(f"Common ground types across cases: {', '.join(common_types)}")
    if total_grounds_count > 0:
        avg_grounds = total_grounds_count / len(case_ids)
        comparison["insights"].append(f"Average of {avg_grounds:.1f} grounds identified per case")
    if total_docs > 0:
        avg_docs = total_docs / len(case_ids)
        comparison["insights"].append(f"Average of {avg_docs:.1f} documents per case")

    return comparison


@router.get("/patterns")
async def get_anonymized_patterns(request: Request, offence_category: str = None, state: str = None):
    """
    Anonymised aggregate patterns from platform case data.

    NOTE: These patterns reflect internal platform usage, NOT court outcomes
    or empirical appeal statistics. Pattern analysis is suppressed for
    cohorts below the minimum sample threshold.
    """
    await get_current_user(request)

    query = {}
    if offence_category:
        query["offence_category"] = offence_category
    if state:
        query["state"] = state

    matching_cases = await db.cases.find(query, {"_id": 0, "case_id": 1, "state": 1, "offence_category": 1}).to_list(1000)
    total_cases = len(matching_cases)

    # Minimum sample threshold — suppress detailed analysis for small cohorts
    if total_cases < MINIMUM_SAMPLE_SIZE:
        return {
            "total_cases": total_cases,
            "suppressed": True,
            "message": f"Detailed pattern analysis requires at least {MINIMUM_SAMPLE_SIZE} cases in this category. Currently {total_cases} case(s) available.",
            "disclaimer": "These patterns reflect internal platform usage data, not court outcomes or legal success metrics.",
            "ground_type_distribution": {},
            "strength_distribution": {},
            "status_distribution": {},
            "insights": [],
            "recommendations": []
        }

    case_ids = [c["case_id"] for c in matching_cases]
    all_grounds = await db.grounds_of_merit.find({"case_id": {"$in": case_ids}}, {"_id": 0}).to_list(5000)
    total_grounds = len(all_grounds)

    type_dist = Counter(g.get("ground_type", "other") for g in all_grounds)
    strength_dist = Counter(g.get("strength", "moderate") for g in all_grounds)
    status_dist = Counter(g.get("status", "identified") for g in all_grounds)

    state_dist = Counter(c.get("state", "unknown") for c in matching_cases)
    offence_dist = Counter(c.get("offence_category", "other") for c in matching_cases)

    insights = []
    if type_dist:
        most_common_type = type_dist.most_common(1)[0][0]
        insights.append(f"Most frequently identified ground type in this dataset: {most_common_type.replace('_', ' ')}")
    if strength_dist:
        insights.append(f"Ground strength distribution: {dict(strength_dist)}")
    if total_grounds > 0:
        avg = total_grounds / total_cases
        insights.append(f"Average of {avg:.1f} grounds identified per case")

    # Proportion of grounds marked confirmed (NOT a success rate)
    confirmed_count = status_dist.get("confirmed", 0)
    if total_grounds > 0:
        confirmed_pct = round((confirmed_count / total_grounds) * 100, 1)
        insights.append(f"{confirmed_pct}% of grounds have been marked as confirmed within the platform")

    recommendations = []
    if total_grounds / max(total_cases, 1) < 2:
        recommendations.append("Consider running AI grounds identification on cases with fewer identified issues")
    recommendations.append("All identified grounds require independent assessment by qualified counsel before reliance")

    return {
        "total_cases": total_cases,
        "total_grounds": total_grounds,
        "suppressed": False,
        "disclaimer": "These patterns reflect internal platform usage data, not court outcomes or legal success metrics. Ground ratings are generated by the platform's analytical engine and require independent legal verification.",
        "ground_type_distribution": dict(type_dist),
        "strength_distribution": dict(strength_dist),
        "status_distribution": dict(status_dist),
        "state_distribution": dict(state_dist),
        "offence_distribution": dict(offence_dist),
        "confirmed_in_app_rate": round((confirmed_count / max(total_grounds, 1)) * 100, 1),
        "insights": insights,
        "recommendations": recommendations
    }


@router.get("/case-composition")
async def get_case_composition_patterns(request: Request, offence_category: str = None, state: str = None):
    """
    Case composition patterns — shows how cases with more identified grounds
    tend to be structured (documents, timeline events, etc.).

    IMPORTANT: This is a documentation/preparation pattern analysis,
    NOT a legal success prediction. More grounds does not necessarily
    mean stronger appeal prospects.
    """
    await get_current_user(request)

    query = {}
    if offence_category:
        query["offence_category"] = offence_category
    if state:
        query["state"] = state

    all_cases = await db.cases.find(query, {"_id": 0, "case_id": 1, "offence_category": 1, "state": 1}).to_list(1000)

    if len(all_cases) < MINIMUM_SAMPLE_SIZE:
        return {
            "total_cases": len(all_cases),
            "suppressed": True,
            "message": f"Composition analysis requires at least {MINIMUM_SAMPLE_SIZE} cases. Currently {len(all_cases)} available.",
            "disclaimer": "This analysis reflects case preparation patterns within the platform, not legal merit or appeal prospects."
        }

    well_documented_cases = []
    lightly_documented_cases = []

    for case in all_cases:
        cid = case["case_id"]
        grounds = await db.grounds_of_merit.find({"case_id": cid}, {"_id": 0}).to_list(100)
        documents = await db.documents.find({"case_id": cid}, {"_id": 0, "file_data": 0}).to_list(500)
        timeline = await db.timeline_events.find({"case_id": cid}, {"_id": 0}).to_list(500)

        strong_grounds = len([g for g in grounds if g.get("strength") == "strong"])
        confirmed_grounds = len([g for g in grounds if g.get("status") == "confirmed"])

        case_profile = {
            "total_grounds": len(grounds),
            "strong_grounds": strong_grounds,
            "confirmed_grounds": confirmed_grounds,
            "documents": len(documents),
            "docs_with_text": len([d for d in documents if d.get("content_text")]),
            "timeline_events": len(timeline),
            "ground_types": list(set(g.get("ground_type", "other") for g in grounds))
        }

        # Classify by documentation level, not by "success"
        if len(documents) >= 3 and len(timeline) >= 5:
            well_documented_cases.append(case_profile)
        else:
            lightly_documented_cases.append(case_profile)

    def avg_field(cases_list, field):
        if not cases_list:
            return 0
        return round(sum(c[field] for c in cases_list) / len(cases_list), 1)

    # Ground type frequency across well-documented cases
    well_doc_ground_types = Counter()
    for c in well_documented_cases:
        for gt in c["ground_types"]:
            well_doc_ground_types[gt] += 1

    insights = []
    if well_documented_cases:
        insights.append(f"Well-documented cases average {avg_field(well_documented_cases, 'total_grounds')} identified grounds vs {avg_field(lightly_documented_cases, 'total_grounds')} in less-documented cases")
        insights.append(f"Well-documented cases average {avg_field(well_documented_cases, 'documents')} documents and {avg_field(well_documented_cases, 'timeline_events')} timeline events")

    recommendations = [
        "Comprehensive documentation helps identify more potential issues for review",
        "Building a detailed timeline aids in identifying procedural irregularities",
        "All grounds require independent assessment by qualified counsel",
    ]

    return {
        "total_cases": len(all_cases),
        "well_documented_count": len(well_documented_cases),
        "lightly_documented_count": len(lightly_documented_cases),
        "suppressed": False,
        "disclaimer": "This analysis reflects case preparation patterns within the platform, not legal merit or appeal prospects. More documentation or more identified grounds does not necessarily indicate stronger appeal viability.",
        "well_documented_profile": {
            "avg_grounds": avg_field(well_documented_cases, "total_grounds"),
            "avg_strong_grounds": avg_field(well_documented_cases, "strong_grounds"),
            "avg_documents": avg_field(well_documented_cases, "documents"),
            "avg_timeline_events": avg_field(well_documented_cases, "timeline_events"),
            "common_ground_types": dict(well_doc_ground_types.most_common(5))
        },
        "lightly_documented_profile": {
            "avg_grounds": avg_field(lightly_documented_cases, "total_grounds"),
            "avg_documents": avg_field(lightly_documented_cases, "documents"),
            "avg_timeline_events": avg_field(lightly_documented_cases, "timeline_events"),
        },
        "insights": insights,
        "recommendations": recommendations
    }
