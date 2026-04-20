# DO NOT UNDO — Jurisdictions (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



LEGISLATION_CURRENCY = {
    "last_full_review": "2026-02",
    "last_verified": "2026-02-14",
    "known_outdated": [],
    "review_notes": "All section references verified against current legislation as of February 2026. WA road traffic legislation updated from 1974 Act to 2008 Acts. VIC Crimes Act assault sections updated to post-2014 numbering. Coverage matrix regenerated 14 Feb 2026 — terrorism state stubs added for all 8 states; organised_crime completed for TAS/NT/ACT; Commonwealth references added for extortion, arson, DV, public order, robbery_theft; procedural flow and mens rea considerations injected into every offence category.",
}

AUSTRALIAN_STATES = {
    "nsw": {
        "name": "New South Wales", "abbreviation": "NSW",
        "legal_aid_url": "https://www.legalaid.nsw.gov.au/",
        "court_forms_url": "https://www.supremecourt.justice.nsw.gov.au/Pages/forms_fees.aspx",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/",
        "appeal_court": "NSW Court of Criminal Appeal (NSWCCA)"
    },
    "vic": {
        "name": "Victoria", "abbreviation": "VIC",
        "legal_aid_url": "https://www.legalaid.vic.gov.au/",
        "court_forms_url": "https://www.supremecourt.vic.gov.au/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/vic/VSCA/",
        "appeal_court": "Victorian Supreme Court - Court of Appeal (VSCA)"
    },
    "qld": {
        "name": "Queensland", "abbreviation": "QLD",
        "legal_aid_url": "https://www.legalaid.qld.gov.au/",
        "court_forms_url": "https://www.courts.qld.gov.au/court-users/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/qld/QCA/",
        "appeal_court": "Queensland Court of Appeal (QCA)"
    },
    "sa": {
        "name": "South Australia", "abbreviation": "SA",
        "legal_aid_url": "https://www.lsc.sa.gov.au/",
        "court_forms_url": "https://www.courts.sa.gov.au/forms-and-fees/",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/sa/SASCFC/",
        "appeal_court": "South Australian Court of Appeal (established 1 January 2021 under Supreme Court (Court of Appeal) Amendment Act 2019; formerly the Full Court of the Supreme Court (SASCFC))"
    },
    "wa": {
        "name": "Western Australia", "abbreviation": "WA",
        "legal_aid_url": "https://www.legalaid.wa.gov.au/",
        "court_forms_url": "https://www.supremecourt.wa.gov.au/F/forms.aspx",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/wa/WASCA/",
        "appeal_court": "Western Australian Supreme Court - Court of Appeal (WASCA)"
    },
    "tas": {
        "name": "Tasmania", "abbreviation": "TAS",
        "legal_aid_url": "https://www.legalaid.tas.gov.au/",
        "court_forms_url": "https://www.supremecourt.tas.gov.au/practice-and-procedure/forms/",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/tas/TASCCA/",
        "appeal_court": "Tasmanian Court of Criminal Appeal (TASCCA)"
    },
    "nt": {
        "name": "Northern Territory", "abbreviation": "NT",
        "legal_aid_url": "https://www.ntlac.nt.gov.au/",
        "court_forms_url": "https://supremecourt.nt.gov.au/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nt/NTCCA/",
        "appeal_court": "Northern Territory Court of Criminal Appeal (NTCCA)"
    },
    "act": {
        "name": "Australian Capital Territory", "abbreviation": "ACT",
        "legal_aid_url": "https://www.legalaidact.org.au/",
        "court_forms_url": "https://www.courts.act.gov.au/supreme/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/act/ACTCA/",
        "appeal_court": "ACT Court of Appeal (ACTCA)"
    },
    "federal": {
        "name": "Commonwealth/Federal", "abbreviation": "CTH",
        "legal_aid_url": "https://www.ag.gov.au/legal-system/legal-assistance-services",
        "court_forms_url": "https://www.fedcourt.gov.au/forms-and-fees/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/cth/HCA/",
        "appeal_court": "High Court of Australia (HCA) / Full Federal Court (where applicable)"
    },
}
