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
    Returns database-specific URLs that open in the user's browser,
    plus AI-suggested authorities from grounds analysis.
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

    # Gather AI-suggested authorities from all grounds
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "title": 1, "similar_cases": 1, "law_sections": 1}
    ).to_list(20)
    suggested_authorities = _extract_authorities(grounds)

    return {
        "query": q,
        "state": state,
        "state_name": db_info["state_name"],
        "primary_court": db_info["primary_court"],
        "search_links": search_links,
        "suggested_authorities": suggested_authorities,
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
    suggested_authorities = _extract_authorities([ground])

    return {
        "query": query,
        "ground_id": ground_id,
        "ground_title": ground.get("title"),
        "state": state,
        "search_links": search_links,
        "suggested_authorities": suggested_authorities,
    }


def _extract_authorities(grounds):
    """Extract unique case authorities and legislation from grounds."""
    cases_seen = set()
    authorities = []
    for g in grounds:
        ground_title = g.get("title", "")
        for sc in (g.get("similar_cases") or []):
            if not isinstance(sc, dict):
                continue
            name = sc.get("case_name", "")
            if not name or name in ("Case name", "None", "optional") or "[Surname]" in name or name in cases_seen:
                continue
            cases_seen.add(name)
            authorities.append({
                "type": "case",
                "name": name,
                "citation": sc.get("citation", ""),
                "relevance": sc.get("relevance_note", ""),
                "ground": ground_title,
                "search_url": f"https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={name.replace(' ', '+')}&rank=on",
            })
        for ls in (g.get("law_sections") or []):
            if isinstance(ls, dict) and ls.get("act"):
                act_name = f"s {ls.get('section', '')} {ls.get('act', '')}"
                if act_name not in cases_seen:
                    cases_seen.add(act_name)
                    authorities.append({
                        "type": "legislation",
                        "name": act_name,
                        "citation": "",
                        "relevance": ls.get("title", ""),
                        "ground": ground_title,
                        "jurisdiction": (ls.get("jurisdiction") or "").upper(),
                    })
    return authorities


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
