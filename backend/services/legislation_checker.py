# DO NOT UNDO — Legislation Currency Checker
# Queries AustLII / legislation.gov.au to verify section references are current.
# Used as a background validation layer — results cached per-session.

import asyncio
import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger("legislation_checker")

# AustLII and legislation.gov.au base URLs for searching
AUSTLII_SEARCH_URL = "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi"
LEGISLATION_GOV_AU = "https://www.legislation.gov.au"

# Map jurisdiction codes to AustLII database codes
AUSTLII_DB_MAP = {
    "nsw": "nswleg",
    "vic": "vicleg",
    "qld": "qldleg",
    "sa": "saleg",
    "wa": "waleg",
    "tas": "tasleg",
    "nt": "ntleg",
    "act": "actleg",
    "cth": "cthleg",
    "federal": "cthleg",
}

# Cache results to avoid repeated lookups
_currency_cache: dict = {}


async def check_section_currency(
    act_name: str,
    section: str,
    jurisdiction: str = "",
) -> dict:
    """
    Check whether a legislative section reference appears current by searching
    AustLII. Returns a dict with:
      - status: 'current' | 'possibly_outdated' | 'unverified' | 'error'
      - message: human-readable summary
      - checked_at: ISO timestamp
      - source: 'austlii' | 'cache' | 'none'
    """
    cache_key = f"{jurisdiction}:{act_name}:{section}"
    if cache_key in _currency_cache:
        cached = _currency_cache[cache_key].copy()
        cached["source"] = "cache"
        return cached

    result = {
        "act": act_name,
        "section": section,
        "jurisdiction": jurisdiction,
        "status": "unverified",
        "message": "",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": "none",
    }

    # Normalise jurisdiction
    jur_key = jurisdiction.lower().strip() if jurisdiction else ""
    db_code = AUSTLII_DB_MAP.get(jur_key, "")

    if not db_code:
        result["message"] = f"No AustLII database mapping for jurisdiction '{jurisdiction}'. Manual verification required."
        _currency_cache[cache_key] = result
        return result

    # Build search query
    search_term = f'"{act_name}" "{section}"'

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Search AustLII for the Act + section reference
            resp = await client.get(
                AUSTLII_SEARCH_URL,
                params={
                    "query": search_term,
                    "meta": f"/au/legis/{db_code}",
                    "mask_path": "",
                    "method": "auto",
                    "results": "5",
                },
                follow_redirects=True,
            )

            if resp.status_code == 200:
                body = resp.text.lower()
                result["source"] = "austlii"

                # Check if the search returned results mentioning the Act
                act_name_lower = act_name.lower()
                if act_name_lower in body and section.lower() in body:
                    # Found references — section appears to exist in current legislation
                    if "repealed" in body or "omitted" in body:
                        result["status"] = "possibly_outdated"
                        result["message"] = (
                            f"{section} of {act_name} appears in AustLII results but "
                            f"'repealed' or 'omitted' was also found. Manual verification recommended."
                        )
                    else:
                        result["status"] = "current"
                        result["message"] = f"{section} of {act_name} found in current AustLII {jur_key.upper()} legislation index."
                elif act_name_lower in body:
                    result["status"] = "possibly_outdated"
                    result["message"] = (
                        f"The {act_name} was found in AustLII but {section} was not located. "
                        f"The section may have been renumbered or repealed. Manual verification required."
                    )
                else:
                    result["status"] = "unverified"
                    result["message"] = f"No AustLII results found for {act_name} in {jur_key.upper()} legislation. The Act name may be incorrect or may not be indexed."
            else:
                result["status"] = "error"
                result["message"] = f"AustLII returned HTTP {resp.status_code}. Manual verification required."

    except httpx.TimeoutException:
        result["status"] = "error"
        result["message"] = "AustLII query timed out. Manual verification required."
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Legislation currency check failed: {str(e)}"

    _currency_cache[cache_key] = result
    return result


async def batch_check_sections(sections: list) -> list:
    """
    Check multiple section references in parallel.
    Each item in `sections` should be a dict with: act, section, jurisdiction.
    Returns list of results.
    """
    tasks = []
    for s in sections:
        tasks.append(
            check_section_currency(
                act_name=s.get("act", ""),
                section=s.get("section", ""),
                jurisdiction=s.get("jurisdiction", ""),
            )
        )
    results = await asyncio.gather(*tasks, return_exceptions=True)
    output = []
    for r in results:
        if isinstance(r, Exception):
            output.append({"status": "error", "message": str(r)})
        else:
            output.append(r)
    return output


def get_currency_warnings(check_results: list) -> list:
    """Extract only the warnings/outdated results from a batch check."""
    warnings = []
    for r in check_results:
        if r.get("status") in ("possibly_outdated", "error"):
            warnings.append(
                f"LEGISLATION CURRENCY WARNING: {r.get('section', '?')} of "
                f"{r.get('act', '?')} ({r.get('jurisdiction', '?').upper()}) — "
                f"{r.get('message', 'verification needed')}"
            )
    return warnings


def clear_cache():
    """Clear the currency check cache."""
    _currency_cache.clear()
