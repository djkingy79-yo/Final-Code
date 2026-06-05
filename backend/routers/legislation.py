#  — Legislation currency verification endpoint
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.legislation_checker import (
    check_section_currency,
    batch_check_sections,
    get_currency_warnings,
)

router = APIRouter(prefix="/api/legislation", tags=["legislation"])


class SectionCheckRequest(BaseModel):
    act: str
    section: str
    jurisdiction: str = ""


class BatchCheckRequest(BaseModel):
    sections: list[dict]


@router.post("/check-currency")
async def check_currency(req: SectionCheckRequest):
    """Check whether a specific legislative section reference is current."""
    result = await check_section_currency(
        act_name=req.act,
        section=req.section,
        jurisdiction=req.jurisdiction,
    )
    return result


@router.post("/batch-check")
async def batch_check(req: BatchCheckRequest):
    """Check multiple section references in parallel."""
    if len(req.sections) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 sections per batch request.")
    results = await batch_check_sections(req.sections)
    warnings = get_currency_warnings(results)
    return {
        "results": results,
        "warnings": warnings,
        "total_checked": len(results),
        "total_current": sum(1 for r in results if r.get("status") == "current"),
        "total_outdated": sum(1 for r in results if r.get("status") == "possibly_outdated"),
        "total_unverified": sum(1 for r in results if r.get("status") == "unverified"),
        "total_errors": sum(1 for r in results if r.get("status") == "error"),
    }
