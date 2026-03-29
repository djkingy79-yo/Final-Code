# DO NOT UNDO — statistics router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Statistics Router
Handles public statistics and case comparison
"""
from fastapi import APIRouter, HTTPException, Request

from config import db
from auth_utils import get_current_user

router = APIRouter(prefix="/api", tags=["statistics"])

# Labels for display
OFFENCE_LABELS = {
    "homicide": "Homicide",
    "assault": "Assault",
    "sexual_offences": "Sexual Offences",
    "robbery_theft": "Robbery & Theft",
    "drug_offences": "Drug Offences",
    "fraud_dishonesty": "Fraud & Dishonesty",
    "firearms_weapons": "Firearms & Weapons",
    "domestic_violence": "Domestic Violence",
    "public_order": "Public Order",
    "terrorism": "Terrorism",
    "driving_offences": "Driving Offences"
}

STATE_LABELS = {
    "nsw": "New South Wales",
    "vic": "Victoria",
    "qld": "Queensland",
    "sa": "South Australia",
    "wa": "Western Australia",
    "tas": "Tasmania",
    "nt": "Northern Territory",
    "act": "ACT"
}

GROUND_TYPE_LABELS = {
    "procedural_error": "Procedural Error",
    "fresh_evidence": "Fresh Evidence",
    "incompetent_counsel": "Incompetent Counsel",
    "sentencing_error": "Sentencing Error",
    "jury_misdirection": "Jury Misdirection",
    "jury_irregularity": "Jury Irregularity",
    "insufficient_evidence": "Insufficient Evidence",
    "judicial_error": "Judicial Error",
    "miscarriage_of_justice": "Miscarriage of Justice",
    "ineffective_counsel": "Ineffective Counsel",
    "constitutional_violation": "Constitutional Violation",
    "prosecutorial_misconduct": "Prosecutorial Misconduct",
    "evidence_error": "Evidence Error",
    "other": "Other"
}


@router.get("/statistics/public")
async def get_public_statistics():
    """Get anonymized public statistics for the dashboard"""
    
    # Get total counts
    total_cases = await db.cases.count_documents({})
    total_documents = await db.documents.count_documents({})
    total_reports = await db.reports.count_documents({})
    total_grounds = await db.grounds_of_merit.count_documents({})
    
    # Cases by offence category
    offence_pipeline = [
        {"$group": {"_id": "$offence_category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    offence_stats = await db.cases.aggregate(offence_pipeline).to_list(20)
    
    # Cases by state
    state_pipeline = [
        {"$group": {"_id": "$state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_stats = await db.cases.aggregate(state_pipeline).to_list(10)
    
    # Reports by type
    report_pipeline = [
        {"$group": {"_id": "$report_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    report_stats = await db.reports.aggregate(report_pipeline).to_list(5)
    
    # Grounds by type
    ground_pipeline = [
        {"$group": {"_id": "$ground_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    ground_stats = await db.grounds_of_merit.aggregate(ground_pipeline).to_list(10)
    
    # Grounds by strength
    strength_pipeline = [
        {"$group": {"_id": "$strength", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    strength_stats = await db.grounds_of_merit.aggregate(strength_pipeline).to_list(5)
    
    # Average documents per case
    avg_docs = total_documents / total_cases if total_cases > 0 else 0
    
    return {
        "overview": {
            "total_cases": total_cases,
            "total_documents": total_documents,
            "total_reports": total_reports,
            "total_grounds_identified": total_grounds,
            "avg_documents_per_case": round(avg_docs, 1)
        },
        "cases_by_offence": [
            {"category": OFFENCE_LABELS.get(s["_id"], s["_id"]), "count": s["count"], "key": s["_id"]}
            for s in offence_stats if s["_id"]
        ],
        "cases_by_state": [
            {"state": STATE_LABELS.get(s["_id"], s["_id"]), "count": s["count"], "key": s["_id"]}
            for s in state_stats if s["_id"]
        ],
        "reports_by_type": [
            {"type": s["_id"].replace("_", " ").title() if s["_id"] else "Unknown", "count": s["count"]}
            for s in report_stats if s["_id"]
        ],
        "grounds_by_type": [
            {"type": GROUND_TYPE_LABELS.get(s["_id"], s["_id"]), "count": s["count"], "key": s["_id"]}
            for s in ground_stats if s["_id"]
        ],
        "grounds_by_strength": [
            {"strength": s["_id"].title() if s["_id"] else "Unknown", "count": s["count"]}
            for s in strength_stats if s["_id"]
        ],
        "insights": {
            "most_common_offence": OFFENCE_LABELS.get(offence_stats[0]["_id"], offence_stats[0]["_id"]) if offence_stats else "N/A",
            "most_common_ground": GROUND_TYPE_LABELS.get(ground_stats[0]["_id"], ground_stats[0]["_id"]) if ground_stats else "N/A",
            "busiest_state": STATE_LABELS.get(state_stats[0]["_id"], state_stats[0]["_id"]) if state_stats else "N/A"
        }
    }


@router.get("/cases/{case_id}/comparison")
async def get_case_comparison(case_id: str, request: Request):
    """Compare your case against similar cases (same offence type/state)"""
    user = await get_current_user(request)
    
    # Get the current case
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    offence_category = case.get("offence_category", "homicide")
    state = case.get("state", "nsw")
    
    # Get stats for similar cases
    similar_offence_count = await db.cases.count_documents({"offence_category": offence_category})
    same_state_count = await db.cases.count_documents({"state": state})
    exact_match_count = await db.cases.count_documents({
        "offence_category": offence_category,
        "state": state
    })
    
    # Get your case's document count
    your_docs = await db.documents.count_documents({"case_id": case_id})
    
    # Get average documents for similar cases
    doc_pipeline = [
        {"$match": {"offence_category": offence_category}},
        {"$lookup": {
            "from": "documents",
            "localField": "case_id",
            "foreignField": "case_id",
            "as": "docs"
        }},
        {"$project": {"doc_count": {"$size": "$docs"}}},
        {"$group": {"_id": None, "avg_docs": {"$avg": "$doc_count"}}}
    ]
    avg_docs_result = await db.cases.aggregate(doc_pipeline).to_list(1)
    avg_docs = round(avg_docs_result[0]["avg_docs"], 1) if avg_docs_result else 0
    
    # Get your grounds count
    your_grounds = await db.grounds_of_merit.count_documents({"case_id": case_id})
    
    # Get average grounds for similar cases
    grounds_pipeline = [
        {"$match": {"offence_category": offence_category}},
        {"$lookup": {
            "from": "grounds_of_merit",
            "localField": "case_id",
            "foreignField": "case_id",
            "as": "grounds"
        }},
        {"$project": {"ground_count": {"$size": "$grounds"}}},
        {"$group": {"_id": None, "avg_grounds": {"$avg": "$ground_count"}}}
    ]
    avg_grounds_result = await db.cases.aggregate(grounds_pipeline).to_list(1)
    avg_grounds = round(avg_grounds_result[0]["avg_grounds"], 1) if avg_grounds_result else 0
    
    # Get your reports count
    your_reports = await db.reports.count_documents({"case_id": case_id})
    
    # Get most common grounds for this offence type
    common_grounds_pipeline = [
        {"$lookup": {
            "from": "cases",
            "localField": "case_id",
            "foreignField": "case_id",
            "as": "case_info"
        }},
        {"$unwind": "$case_info"},
        {"$match": {"case_info.offence_category": offence_category}},
        {"$group": {"_id": "$ground_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    common_grounds = await db.grounds_of_merit.aggregate(common_grounds_pipeline).to_list(5)
    
    return {
        "your_case": {
            "offence_category": OFFENCE_LABELS.get(offence_category, offence_category),
            "state": STATE_LABELS.get(state, state),
            "documents": your_docs,
            "grounds_identified": your_grounds,
            "reports_generated": your_reports
        },
        "similar_cases": {
            "same_offence_count": similar_offence_count,
            "same_state_count": same_state_count,
            "exact_match_count": exact_match_count,
            "avg_documents": avg_docs,
            "avg_grounds": avg_grounds
        },
        "comparison": {
            "documents_vs_avg": "above" if your_docs > avg_docs else ("below" if your_docs < avg_docs else "average"),
            "documents_diff": round(your_docs - avg_docs, 1),
            "grounds_vs_avg": "above" if your_grounds > avg_grounds else ("below" if your_grounds < avg_grounds else "average"),
            "grounds_diff": round(your_grounds - avg_grounds, 1)
        },
        "common_grounds_for_offence": [
            {"type": GROUND_TYPE_LABELS.get(g["_id"], g["_id"]), "count": g["count"]}
            for g in common_grounds if g["_id"]
        ],
        "recommendations": []
    }
