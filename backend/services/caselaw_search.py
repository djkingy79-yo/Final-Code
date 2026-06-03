"""
Verified Case Law Search Service
Generates smart search URLs for AustLII and state-specific databases.
All searches open in the user's browser for verified, official results.

 — Provides verified case law search across all Australian jurisdictions.
"""
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# ============================================================================
# STATE-SPECIFIC DATABASE CONFIGURATION
# ============================================================================
STATE_DATABASES = {
    "nsw": {
        "state_name": "New South Wales",
        "primary_court": "NSW Court of Criminal Appeal",
        "databases": [
            {
                "id": "nsw_caselaw",
                "name": "NSW CaseLaw",
                "icon": "scale",
                "url": "https://www.caselaw.nsw.gov.au",
                "description": "Official NSW Courts — judgments from 1988 onwards",
                "search_template": "https://www.caselaw.nsw.gov.au/search/advanced?query={query}",
                "coverage": "Supreme Court, District Court, Court of Criminal Appeal"
            },
            {
                "id": "austlii_nsw",
                "name": "AustLII — NSW",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive NSW case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/nsw&rank=on",
                "coverage": "All NSW courts and tribunals"
            }
        ]
    },
    "qld": {
        "state_name": "Queensland",
        "primary_court": "Queensland Court of Appeal",
        "databases": [
            {
                "id": "qld_judgments",
                "name": "Queensland Judgments",
                "icon": "scale",
                "url": "https://www.queenslandjudgments.com.au",
                "description": "Authorised reports and unreported judgments",
                "search_template": "https://www.queenslandjudgments.com.au/caselaw/search?keyword={query}",
                "coverage": "Court of Appeal, Supreme Court, District Court, Magistrates Court"
            },
            {
                "id": "sclqld",
                "name": "Supreme Court Library QLD",
                "icon": "library",
                "url": "https://www.sclqld.org.au",
                "description": "Sentencing information, case summaries, public remarks",
                "search_template": "https://www.sclqld.org.au/caselaw/search?keyword={query}",
                "coverage": "Queensland sentencing data and decisions"
            },
            {
                "id": "austlii_qld",
                "name": "AustLII — QLD",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive QLD case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/qld&rank=on",
                "coverage": "All Queensland courts and tribunals"
            }
        ]
    },
    "vic": {
        "state_name": "Victoria",
        "primary_court": "Victorian Court of Appeal",
        "databases": [
            {
                "id": "vic_sc",
                "name": "Supreme Court of Victoria",
                "icon": "scale",
                "url": "https://www.supremecourt.vic.gov.au",
                "description": "Judgments and sentences from Victoria's highest court",
                "search_template": "https://www.supremecourt.vic.gov.au/law-and-practice/judgments-and-sentences",
                "coverage": "Supreme Court, Court of Appeal"
            },
            {
                "id": "austlii_vic",
                "name": "AustLII — VIC",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive VIC case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/vic&rank=on",
                "coverage": "All Victorian courts and tribunals"
            }
        ]
    },
    "sa": {
        "state_name": "South Australia",
        "primary_court": "SA Supreme Court",
        "databases": [
            {
                "id": "courts_sa",
                "name": "Courts SA",
                "icon": "scale",
                "url": "https://www.courts.sa.gov.au",
                "description": "South Australian courts judgments database",
                "search_template": "https://www.courts.sa.gov.au/search-judgments/",
                "coverage": "Supreme Court, District Court, Magistrates Court"
            },
            {
                "id": "austlii_sa",
                "name": "AustLII — SA",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive SA case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/sa&rank=on",
                "coverage": "All SA courts and tribunals"
            }
        ]
    },
    "wa": {
        "state_name": "Western Australia",
        "primary_court": "WA Supreme Court of Appeal",
        "databases": [
            {
                "id": "ecourts_wa",
                "name": "eCourts WA",
                "icon": "scale",
                "url": "https://ecourts.justice.wa.gov.au",
                "description": "Western Australian courts decisions portal",
                "search_template": "https://ecourts.justice.wa.gov.au/eCourtsPortal/Decisions/Search",
                "coverage": "Supreme Court, District Court, Court of Appeal"
            },
            {
                "id": "austlii_wa",
                "name": "AustLII — WA",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive WA case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/wa&rank=on",
                "coverage": "All WA courts and tribunals"
            }
        ]
    },
    "tas": {
        "state_name": "Tasmania",
        "primary_court": "Tasmania Court of Criminal Appeal",
        "databases": [
            {
                "id": "austlii_tas",
                "name": "AustLII — TAS",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive TAS case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/tas&rank=on",
                "coverage": "All Tasmanian courts and tribunals"
            }
        ]
    },
    "nt": {
        "state_name": "Northern Territory",
        "primary_court": "NT Supreme Court",
        "databases": [
            {
                "id": "austlii_nt",
                "name": "AustLII — NT",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive NT case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/nt&rank=on",
                "coverage": "All NT courts and tribunals"
            }
        ]
    },
    "act": {
        "state_name": "Australian Capital Territory",
        "primary_court": "ACT Court of Appeal",
        "databases": [
            {
                "id": "act_courts",
                "name": "ACT Courts",
                "icon": "scale",
                "url": "https://www.courts.act.gov.au",
                "description": "ACT Supreme Court judgments",
                "search_template": "https://www.courts.act.gov.au/supreme/judgments",
                "coverage": "Supreme Court, Court of Appeal"
            },
            {
                "id": "austlii_act",
                "name": "AustLII — ACT",
                "icon": "book",
                "url": "https://www.austlii.edu.au",
                "description": "Free comprehensive ACT case law database",
                "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/act&rank=on",
                "coverage": "All ACT courts and tribunals"
            }
        ]
    }
}

# National databases available regardless of state
NATIONAL_DATABASES = [
    {
        "id": "austlii_all",
        "name": "AustLII — All Jurisdictions",
        "icon": "globe",
        "url": "https://www.austlii.edu.au",
        "description": "500,000+ searchable case law documents across all Australian jurisdictions",
        "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&meta=%2Faustlii&rank=on",
        "coverage": "All Commonwealth, State, and Territory courts"
    },
    {
        "id": "hca",
        "name": "High Court of Australia",
        "icon": "landmark",
        "url": "https://www.hcourt.gov.au",
        "description": "Decisions of the highest court in the Australian judicial system",
        "search_template": "https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query={query}&mask_path=au/cases/cth/HCA&rank=on",
        "coverage": "High Court judgments"
    },
    {
        "id": "jade",
        "name": "JADE",
        "icon": "search",
        "url": "https://jade.io",
        "description": "Judgments and Decisions Enhanced — cross-jurisdiction awareness service",
        "search_template": "https://jade.io/search/?q={query}",
        "coverage": "Selected courts across all jurisdictions"
    },
    {
        "id": "google_scholar",
        "name": "Google Scholar (Australian Law)",
        "icon": "graduation",
        "url": "https://scholar.google.com.au",
        "description": "Academic and legal case search — useful for finding commentary",
        "search_template": "https://scholar.google.com.au/scholar?q={query}&hl=en&as_sdt=4",
        "coverage": "Academic papers and case citations"
    }
]


def get_databases_for_state(state: str) -> dict:
    """Get state-specific + national databases for a jurisdiction."""
    state_lower = (state or "").lower()
    state_info = STATE_DATABASES.get(state_lower, {})

    return {
        "state": state_lower,
        "state_name": state_info.get("state_name", state_lower.upper()),
        "primary_court": state_info.get("primary_court", ""),
        "state_databases": state_info.get("databases", []),
        "national_databases": NATIONAL_DATABASES
    }


def build_search_links(query: str, state: str = None) -> list:
    """Build direct search URLs for all relevant databases."""
    encoded = quote_plus(query)
    links = []

    db_info = get_databases_for_state(state)

    # State-specific databases first
    for db_entry in db_info["state_databases"]:
        url = db_entry["search_template"].replace("{query}", encoded)
        links.append({
            "id": db_entry["id"],
            "name": db_entry["name"],
            "url": url,
            "description": db_entry["description"],
            "coverage": db_entry.get("coverage", ""),
            "scope": "state"
        })

    # Then national databases
    for db_entry in db_info["national_databases"]:
        url = db_entry["search_template"].replace("{query}", encoded)
        links.append({
            "id": db_entry["id"],
            "name": db_entry["name"],
            "url": url,
            "description": db_entry["description"],
            "coverage": db_entry.get("coverage", ""),
            "scope": "national"
        })

    return links


def build_ground_query(ground: dict, case: dict) -> str:
    """Build an optimised search query from a ground of merit and case data."""
    parts = []

    # Use ground title as primary search term
    title = ground.get("title", "")
    if title:
        parts.append(title)

    # Add ground type context
    ground_type = (ground.get("ground_type") or "").replace("_", " ")
    if ground_type and ground_type not in title.lower():
        parts.append(ground_type)

    # Add offence type for context
    offence = case.get("offence_type", "")
    if offence and offence.lower() not in title.lower():
        parts.append(offence)

    # Always include "appeal" for relevance
    parts.append("criminal appeal")

    return " ".join(parts)
