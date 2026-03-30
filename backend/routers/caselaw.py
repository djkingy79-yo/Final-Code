"""
Case Law Search Router
Provides verified case law search URLs and database metadata
for all Australian jurisdictions.

DO NOT UNDO — This router provides verified case law search across all
Australian jurisdictions. Endpoints are used by the CaseLawPanel component.
"""
import logging
from fastapi import APIRouter, Request, HTTPException
from auth_utils import get_current_user
from config import db
from services.caselaw_search import (
    get_databases_for_state,
    build_search_links,
    build_ground_query,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["caselaw"])


@router.get("/cases/{case_id}/caselaw/search")
async def search_case_law(case_id: str, request: Request, q: str = None):
    """
    Generate verified case law search links for a case.
    Returns database-specific URLs that open in the user's browser.
    """
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Build search query from case data if none provided
    if not q:
        parts = []
        if case.get("offence_type"):
            parts.append(case["offence_type"])
        elif case.get("offence_category"):
            parts.append(case["offence_category"].replace("_", " "))
        if case.get("defendant_name"):
            parts.append(case["defendant_name"].split()[-1])  # Surname
        parts.append("criminal appeal")
        if case.get("state"):
            parts.append(case["state"].upper())
        q = " ".join(parts)

    state = case.get("state")
    db_info = get_databases_for_state(state)
    search_links = build_search_links(q, state=state)

    return {
        "query": q,
        "state": state,
        "state_name": db_info["state_name"],
        "primary_court": db_info["primary_court"],
        "search_links": search_links,
        "databases": {
            "state": db_info["state_databases"],
            "national": db_info["national_databases"]
        }
    }


@router.get("/cases/{case_id}/caselaw/ground/{ground_id}")
async def search_case_law_for_ground(case_id: str, ground_id: str, request: Request):
    """
    Generate targeted case law search links for a specific ground of merit.
    """
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id}, {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground not found")

    query = build_ground_query(ground, case)
    state = case.get("state")
    search_links = build_search_links(query, state=state)

    return {
        "query": query,
        "ground_id": ground_id,
        "ground_title": ground.get("title"),
        "state": state,
        "search_links": search_links,
    }


@router.get("/caselaw/databases")
async def list_databases(state: str = None):
    """List all available case law databases, optionally filtered by state."""
    if state:
        return get_databases_for_state(state)
    # Return all
    from services.caselaw_search import STATE_DATABASES, NATIONAL_DATABASES
    return {
        "states": {k: v for k, v in STATE_DATABASES.items()},
        "national": NATIONAL_DATABASES
    }
