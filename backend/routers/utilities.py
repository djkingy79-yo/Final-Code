# DO NOT UNDO — utilities router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Utilities Router
Helper endpoints: Australian states, offence framework, categories
"""
from fastapi import APIRouter, HTTPException

from offence_framework import (
    OFFENCE_CATEGORIES,
    COMMON_APPEAL_GROUNDS,
    HUMAN_RIGHTS_FRAMEWORK,
    APPEAL_FRAMEWORK,
    AUSTRALIAN_STATES
)

router = APIRouter(prefix="/api", tags=["utilities"])

# ============ AUSTRALIAN STATES ============

@router.get("/states")
async def get_australian_states():
    """Get all Australian states and territories"""
    states = []
    for key, value in AUSTRALIAN_STATES.items():
        states.append({
            "id": key,
            "name": value["name"],
            "abbreviation": value["abbreviation"]
        })
    return {"states": states}

# ============ OFFENCE FRAMEWORK ============

@router.get("/offence-framework")
async def get_offence_framework():
    """Get all offence categories and legal framework"""
    return {
        "categories": OFFENCE_CATEGORIES,
        "common_appeal_grounds": COMMON_APPEAL_GROUNDS,
        "human_rights": HUMAN_RIGHTS_FRAMEWORK,
        "appeal_framework": APPEAL_FRAMEWORK,
        "states": AUSTRALIAN_STATES
    }

@router.get("/offence-categories")
async def get_offence_categories():
    """Get simplified list of offence categories for dropdowns"""
    categories = []
    for key, value in OFFENCE_CATEGORIES.items():
        categories.append({
            "id": key,
            "name": value["name"],
            "description": value["description"],
            "offences": value["offences"]
        })
    return {"categories": categories}

@router.get("/offence-framework/{category}")
async def get_offence_category_details(category: str, state: str = ""):
    """Get detailed framework for a specific offence category and state"""
    if category not in OFFENCE_CATEGORIES:
        raise HTTPException(status_code=404, detail="Offence category not found")
    
    category_data = OFFENCE_CATEGORIES[category]
    
    # Get state-specific legislation
    state_leg_key = f"{state}_legislation"
    state_legislation = category_data.get(state_leg_key, {})
    
    # Build response with state-specific data
    response_category = {
        "name": category_data["name"],
        "description": category_data["description"],
        "offences": category_data["offences"],
        "defences": category_data["defences"],
        "key_elements": category_data["key_elements"],
        "state_legislation": state_legislation,
        "cth_legislation": category_data.get("cth_legislation", {}),
    }
    
    # Get appeal framework for the state — do NOT silently default to NSW
    state_appeal = APPEAL_FRAMEWORK.get(state)
    if not state_appeal:
        state_appeal = {"note": "Appeal framework not available for the specified jurisdiction. Please verify the state is set correctly."}
    
    return {
        "category": response_category,
        "common_appeal_grounds": COMMON_APPEAL_GROUNDS,
        "human_rights": HUMAN_RIGHTS_FRAMEWORK,
        "appeal_framework": state_appeal,
        "state": AUSTRALIAN_STATES.get(state, {"name": state.upper() if state else "Unspecified", "abbreviation": state.upper() if state else "N/A"})
    }
