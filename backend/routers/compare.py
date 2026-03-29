# DO NOT UNDO — compare router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Compare Cases Router
Allows users to compare their own cases and see anonymized patterns from all users
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel

from config import db
from auth_utils import get_current_user

router = APIRouter(prefix="/api/compare", tags=["compare"])


class CaseComparisonRequest(BaseModel):
    case_ids: List[str]  # List of case IDs to compare (user's own cases)


class PatternFilter(BaseModel):
    offence_category: Optional[str] = None
    state: Optional[str] = None
    ground_type: Optional[str] = None


@router.post("/my-cases")
async def compare_my_cases(comparison: CaseComparisonRequest, request: Request):
    """
    Compare multiple cases from the user's own account.
    Highlights similarities, differences, and patterns across selected cases.
    """
    user = await get_current_user(request)
    
    if len(comparison.case_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 cases to compare")
    
    if len(comparison.case_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 cases can be compared at once")
    
    # Fetch all selected cases (verify ownership)
    cases = []
    for case_id in comparison.case_ids:
        case = await db.cases.find_one(
            {"case_id": case_id, "user_id": user.user_id},
            {"_id": 0}
        )
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        cases.append(case)
    
    # Fetch grounds for each case
    case_grounds = {}
    for case in cases:
        grounds = await db.grounds_of_merit.find(
            {"case_id": case["case_id"]},
            {"_id": 0}
        ).to_list(100)
        case_grounds[case["case_id"]] = grounds
    
    # Fetch timeline events for each case
    case_timelines = {}
    for case in cases:
        events = await db.timeline_events.find(
            {"case_id": case["case_id"]},
            {"_id": 0}
        ).sort("event_date", 1).to_list(500)
        case_timelines[case["case_id"]] = events
    
    # Fetch documents for each case
    case_docs = {}
    for case in cases:
        docs = await db.documents.find(
            {"case_id": case["case_id"]},
            {"_id": 0, "file_data": 0}
        ).to_list(500)
        case_docs[case["case_id"]] = docs
    
    # Analyze similarities
    comparison_result = {
        "cases": [],
        "ground_comparison": {
            "common_grounds": [],
            "unique_grounds": {},
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
        "insights": []
    }
    
    # Build case summaries
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
            "ground_types": list(set(g.get("ground_type") for g in grounds)),
            "ground_strengths": {
                "strong": len([g for g in grounds if g.get("strength") == "strong"]),
                "moderate": len([g for g in grounds if g.get("strength") == "moderate"]),
                "weak": len([g for g in grounds if g.get("strength") == "weak"])
            }
        })
    
    # Find common ground types
    all_ground_types = []
    for case_id, grounds in case_grounds.items():
        for ground in grounds:
            all_ground_types.append(ground.get("ground_type"))
    
    # Count ground type occurrences
    ground_type_counts = {}
    for gt in all_ground_types:
        ground_type_counts[gt] = ground_type_counts.get(gt, 0) + 1
    
    comparison_result["ground_comparison"]["ground_type_distribution"] = ground_type_counts
    
    # Find grounds that appear in multiple cases
    common_types = [gt for gt, count in ground_type_counts.items() if count >= 2]
    comparison_result["ground_comparison"]["common_grounds"] = common_types
    
    # Calculate averages
    total_events = sum(len(events) for events in case_timelines.values())
    total_docs = sum(len(docs) for docs in case_docs.values())
    num_cases = len(cases)
    
    comparison_result["timeline_comparison"]["avg_events_per_case"] = round(total_events / num_cases, 1) if num_cases > 0 else 0
    comparison_result["document_comparison"]["avg_documents_per_case"] = round(total_docs / num_cases, 1) if num_cases > 0 else 0
    
    # Generate insights
    insights = []
    
    if common_types:
        insights.append(f"Common ground types across cases: {', '.join(common_types)}")
    
    # Check for strong grounds
    total_strong = sum(cs["ground_strengths"]["strong"] for cs in comparison_result["cases"])
    if total_strong > 0:
        insights.append(f"Total strong grounds across all cases: {total_strong}")
    
    # Check offence patterns
    offence_categories = [c.get("offence_category") for c in cases]
    if len(set(offence_categories)) == 1:
        insights.append(f"All cases involve {offence_categories[0]} offences - consider looking for common precedents")
    
    # State consistency
    states = [c.get("state") for c in cases]
    if len(set(states)) == 1:
        insights.append(f"All cases are in {states[0].upper()} - same legislation applies")
    else:
        insights.append(f"Cases span multiple jurisdictions ({', '.join(set(s.upper() for s in states))}) - different legislation may apply")
    
    comparison_result["insights"] = insights
    
    return comparison_result


@router.get("/patterns")
async def get_anonymized_patterns(
    request: Request,
    offence_category: Optional[str] = None,
    state: Optional[str] = None,
    ground_type: Optional[str] = None
):
    """
    Get anonymized patterns from all users' cases.
    Provides aggregate insights without revealing individual case details.
    """
    await get_current_user(request)  # Require authentication
    
    # Build filter for cases
    case_filter = {}
    if offence_category:
        case_filter["offence_category"] = offence_category
    if state:
        case_filter["state"] = state
    
    # Get total case count matching filter
    total_cases = await db.cases.count_documents(case_filter)
    
    if total_cases == 0:
        return {
            "total_cases_analyzed": 0,
            "message": "No cases found matching the specified criteria",
            "patterns": {}
        }
    
    # Aggregate ground patterns
    ground_filter = {}
    if ground_type:
        ground_filter["ground_type"] = ground_type
    
    # Get all case IDs matching filter
    matching_cases = await db.cases.find(case_filter, {"case_id": 1, "_id": 0}).to_list(10000)
    case_ids = [c["case_id"] for c in matching_cases]
    
    if ground_filter:
        ground_filter["case_id"] = {"$in": case_ids}
    else:
        ground_filter = {"case_id": {"$in": case_ids}}
    
    # Aggregate grounds
    grounds = await db.grounds_of_merit.find(ground_filter, {"_id": 0}).to_list(10000)
    
    # Calculate patterns
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
    
    # Sort ground types by frequency
    sorted_ground_types = sorted(ground_type_dist.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate success indicators (approximate based on status)
    total_grounds = len(grounds)
    confirmed_grounds = status_dist.get("confirmed", 0)
    success_rate = round((confirmed_grounds / total_grounds) * 100, 1) if total_grounds > 0 else 0
    
    # State distribution
    state_dist = {}
    for case in matching_cases:
        case_full = await db.cases.find_one({"case_id": case["case_id"]}, {"state": 1, "_id": 0})
        if case_full:
            s = case_full.get("state", "nsw")
            state_dist[s] = state_dist.get(s, 0) + 1
    
    # Offence category distribution
    offence_dist = {}
    for case in matching_cases:
        case_full = await db.cases.find_one({"case_id": case["case_id"]}, {"offence_category": 1, "_id": 0})
        if case_full:
            oc = case_full.get("offence_category", "other")
            offence_dist[oc] = offence_dist.get(oc, 0) + 1
    
    # Generate insights
    insights = []
    
    if sorted_ground_types:
        top_ground = sorted_ground_types[0]
        insights.append(f"Most common appeal ground: {top_ground[0]} ({top_ground[1]} cases)")
    
    if strength_dist["strong"] > 0:
        strong_pct = round((strength_dist["strong"] / total_grounds) * 100, 1) if total_grounds > 0 else 0
        insights.append(f"{strong_pct}% of identified grounds are rated as strong")
    
    # Average grounds per case
    avg_grounds = round(total_grounds / total_cases, 1) if total_cases > 0 else 0
    if avg_grounds > 0:
        insights.append(f"Average {avg_grounds} grounds identified per case")
    
    return {
        "total_cases_analyzed": total_cases,
        "total_grounds_analyzed": total_grounds,
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
        "success_indicators": {
            "confirmed_grounds_rate": success_rate,
            "strong_grounds_count": strength_dist["strong"],
            "avg_grounds_per_case": avg_grounds
        },
        "insights": insights,
        "recommendations": [
            f"Focus on {sorted_ground_types[0][0]} grounds - most commonly identified" if sorted_ground_types else None,
            "Consider similar cases for precedent research",
            "Strong grounds have highest success potential on appeal"
        ]
    }


@router.get("/success-factors")
async def get_success_factors(request: Request, offence_category: Optional[str] = None):
    """
    Get anonymized success factors based on case outcomes.
    Shows which ground types and case characteristics correlate with successful appeals.
    """
    await get_current_user(request)  # Require authentication
    
    # Build filter
    case_filter = {}
    if offence_category:
        case_filter["offence_category"] = offence_category
    
    # Get cases with high strong ground counts (proxy for potential success)
    all_cases = await db.cases.find(case_filter, {"case_id": 1, "offence_category": 1, "state": 1, "_id": 0}).to_list(10000)
    
    if not all_cases:
        return {
            "message": "No cases found",
            "success_factors": []
        }
    
    # Analyze each case
    case_analyses = []
    for case in all_cases:
        case_id = case["case_id"]
        
        # Get grounds for this case
        grounds = await db.grounds_of_merit.find(
            {"case_id": case_id},
            {"ground_type": 1, "strength": 1, "status": 1, "_id": 0}
        ).to_list(100)
        
        # Get documents count
        doc_count = await db.documents.count_documents({"case_id": case_id})
        
        # Get timeline events count
        event_count = await db.timeline_events.count_documents({"case_id": case_id})
        
        # Calculate strength score
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
            "ground_types": [g.get("ground_type") for g in grounds]
        })
    
    # Find patterns in successful cases (high strong/confirmed grounds)
    successful_cases = [c for c in case_analyses if c["strong_grounds"] >= 2 or c["confirmed_grounds"] >= 1]
    
    # Extract success factors
    success_factors = []
    
    if successful_cases:
        # Ground types in successful cases
        successful_ground_types = {}
        for case in successful_cases:
            for gt in case["ground_types"]:
                successful_ground_types[gt] = successful_ground_types.get(gt, 0) + 1
        
        sorted_success_grounds = sorted(successful_ground_types.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_success_grounds:
            success_factors.append({
                "factor": "Ground Type",
                "finding": f"Most successful ground type: {sorted_success_grounds[0][0]}",
                "recommendation": f"Focus on identifying {sorted_success_grounds[0][0]} grounds in your case"
            })
        
        # Document count correlation
        avg_docs_successful = sum(c["documents"] for c in successful_cases) / len(successful_cases)
        avg_docs_all = sum(c["documents"] for c in case_analyses) / len(case_analyses) if case_analyses else 0
        
        if avg_docs_successful > avg_docs_all:
            success_factors.append({
                "factor": "Documentation",
                "finding": f"Successful cases average {round(avg_docs_successful, 1)} documents vs {round(avg_docs_all, 1)} overall",
                "recommendation": "Comprehensive documentation improves appeal prospects"
            })
        
        # Timeline event correlation
        avg_events_successful = sum(c["timeline_events"] for c in successful_cases) / len(successful_cases)
        avg_events_all = sum(c["timeline_events"] for c in case_analyses) / len(case_analyses) if case_analyses else 0
        
        if avg_events_successful > avg_events_all:
            success_factors.append({
                "factor": "Timeline Detail",
                "finding": f"Successful cases average {round(avg_events_successful, 1)} timeline events vs {round(avg_events_all, 1)} overall",
                "recommendation": "Detailed timeline helps identify appeal grounds"
            })
    
    return {
        "total_cases_analyzed": len(case_analyses),
        "cases_with_strong_indicators": len(successful_cases),
        "success_factors": success_factors,
        "general_recommendations": [
            "Upload all available case documents",
            "Build a comprehensive timeline of events",
            "Focus on identifying strong grounds",
            "Consider multiple ground types for robust appeal"
        ]
    }
