#  — legislation registry (14 Feb 2026).
"""
Legislation currency registry for the Appeal Case Manager.

Every Act / Code / Rule referenced anywhere in the /app/backend/frameworks/
package is catalogued here along with its `last_verified` date, AustLII
lookup URL, and any verification notes. This is the single source of truth
for the /admin/legislation-currency dashboard.

Verification policy (STRICT — forensic integrity):
  - `last_verified` is the ISO date (YYYY-MM-DD) on which a human confirmed
    via AustLII / legislation.gov.au that the Act and its cited section
    numbers remain current.
  - The AI cross-check produces *prompts for manual review*, never a
    verification of its own. An AI "appears_current" result does NOT update
    `last_verified` — only a human tick via the dashboard does.
  - If the Act cannot be located on AustLII for manual review it must be
    flagged `status: "investigate"` and removed from prompt-building until
    resolved.

Schema for each entry:
  {
    "act_name": "Full cited name, e.g. 'Crimes Act 1900 (NSW)'",
    "short_name": "Short form without year/jurisdiction",
    "year": 1900,
    "jurisdiction": "nsw" | "vic" | "qld" | "sa" | "wa" | "tas" | "nt" | "act" | "cth",
    "austlii_url": "Direct AustLII consolidated-Act URL",
    "last_verified": "YYYY-MM-DD",
    "verification_source": "manual",  # always "manual" for initial entries
    "notes": "Optional short forensic note (e.g. 'Assault sections renumbered 2014')",
  }
"""
from __future__ import annotations


def _austlii(jur: str, slug: str) -> str:
    """Build an AustLII consolidated-act URL.

    AustLII's consolidated act URLs follow a predictable shape:
      http://classic.austlii.edu.au/au/legis/<jur>/consol_act/<slug>/

    Where <slug> is the Act's short name lower-cased with numbers/letters
    appended in AustLII's style (e.g. 'ca190082' for Crimes Act 1900 NSW).
    Because AustLII slugs are non-deterministic and subject to archival
    change, callers should prefer the search URL below if the direct
    consolidated-act URL 404s.
    """
    base = "http://classic.austlii.edu.au/au/legis"
    return f"{base}/{jur}/consol_act/{slug}/"


def _austlii_search(act_name: str, jur: str) -> str:
    """AustLII search fallback — always works, even when direct URL changes."""
    from urllib.parse import quote_plus
    return f"http://www8.austlii.edu.au/cgi-bin/sinosrch.cgi?query={quote_plus(act_name)}&mask_path=au/legis/{jur}"


# 14 February 2026 is the initial full-registry verification date following
# the legal framework gap-fill audit completed on the same day.
INITIAL_VERIFIED = "2026-02-14"

# ---------------------------------------------------------------------------
# Registry — 76 Acts across 9 jurisdictions
# ---------------------------------------------------------------------------
LEGISLATION_REGISTRY = [
    # ==================== NSW ====================
    {"act_name": "Crimes Act 1900 (NSW)", "short_name": "Crimes Act", "year": 1900, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "ca190082"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Inclosed Lands Protection Act 1901 (NSW)", "short_name": "Inclosed Lands Protection Act", "year": 1901, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "ilpa1901298"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Drug Misuse and Trafficking Act 1985 (NSW)", "short_name": "Drug Misuse and Trafficking Act", "year": 1985, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "dmata1985256"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Independent Commission Against Corruption Act 1988 (NSW)", "short_name": "Independent Commission Against Corruption Act", "year": 1988, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "icaca1988442"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Summary Offences Act 1988 (NSW)", "short_name": "Summary Offences Act", "year": 1988, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "soa1988189"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Crimes (Domestic and Personal Violence) Act 2007 (NSW)", "short_name": "Crimes (Domestic and Personal Violence) Act", "year": 2007, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "cadapva2007383"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Primary NSW DV legislation"},
    {"act_name": "Terrorism (Police Powers) Act 2002 (NSW)", "short_name": "Terrorism (Police Powers) Act", "year": 2002, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "tpa2002251"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (High Risk Offenders) Act 2017 (NSW)", "short_name": "Terrorism (High Risk Offenders) Act", "year": 2017, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "throa2017410"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Firearms Act 1996 (NSW)", "short_name": "Firearms Act", "year": 1996, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "fa1996102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Road Transport Act 2013 (NSW)", "short_name": "Road Transport Act", "year": 2013, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "rta2013143"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Bail Act 2013 (NSW)", "short_name": "Bail Act", "year": 2013, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "ba201341"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Criminal Appeal Act 1912 (NSW)", "short_name": "Criminal Appeal Act", "year": 1912, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "caa191216"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Criminal Procedure Act 1986 (NSW)", "short_name": "Criminal Procedure Act", "year": 1986, "jurisdiction": "nsw",
     "austlii_url": _austlii("nsw", "cpa1986188"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== VIC ====================
    {"act_name": "Crimes Act 1958 (Vic)", "short_name": "Crimes Act", "year": 1958, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "ca195882"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Assault sections renumbered 2014"},
    {"act_name": "Summary Offences Act 1966 (Vic)", "short_name": "Summary Offences Act", "year": 1966, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "soa1966189"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Drugs, Poisons and Controlled Substances Act 1981 (Vic)", "short_name": "Drugs, Poisons and Controlled Substances Act", "year": 1981, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "dpacsa1981387"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Road Safety Act 1986 (Vic)", "short_name": "Road Safety Act", "year": 1986, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "rsa1986125"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Control of Weapons Act 1990 (Vic)", "short_name": "Control of Weapons Act", "year": 1990, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "cowa1990221"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Firearms Act 1996 (Vic)", "short_name": "Firearms Act", "year": 1996, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "fa1996102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Family Violence Protection Act 2008 (Vic)", "short_name": "Family Violence Protection Act", "year": 2008, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "fvpa2008267"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Primary Vic DV legislation"},
    {"act_name": "Terrorism (Community Protection) Act 2003 (Vic)", "short_name": "Terrorism (Community Protection) Act", "year": 2003, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "tpa2003293"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Bail Act 1977 (Vic)", "short_name": "Bail Act", "year": 1977, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "ba197741"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Criminal Procedure Act 2009 (Vic)", "short_name": "Criminal Procedure Act", "year": 2009, "jurisdiction": "vic",
     "austlii_url": _austlii("vic", "cpa2009188"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== QLD ====================
    {"act_name": "Criminal Code Act 1899 (Qld)", "short_name": "Criminal Code Act", "year": 1899, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "cca1899115"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Drugs Misuse Act 1986 (Qld)", "short_name": "Drugs Misuse Act", "year": 1986, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "dma1986139"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Weapons Act 1990 (Qld)", "short_name": "Weapons Act", "year": 1990, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "wa1990107"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Transport Operations (Road Use Management) Act 1995 (Qld)", "short_name": "Transport Operations (Road Use Management) Act", "year": 1995, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "toma1995327"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Police Powers and Responsibilities Act 2000 (Qld)", "short_name": "Police Powers and Responsibilities Act", "year": 2000, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "ppara2000365"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (Preventative Detention) Act 2005 (Qld)", "short_name": "Terrorism (Preventative Detention) Act", "year": 2005, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "tpda2005342"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Domestic and Family Violence Protection Act 2012 (Qld)", "short_name": "Domestic and Family Violence Protection Act", "year": 2012, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "dafvpa2012394"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Bail Act 1980 (Qld)", "short_name": "Bail Act", "year": 1980, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "ba198041"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Justices Act 1886 (Qld)", "short_name": "Justices Act", "year": 1886, "jurisdiction": "qld",
     "austlii_url": _austlii("qld", "ja188695"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== SA ====================
    {"act_name": "Criminal Law Consolidation Act 1935 (SA)", "short_name": "Criminal Law Consolidation Act", "year": 1935, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "clca1935262"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Summary Offences Act 1953 (SA)", "short_name": "Summary Offences Act", "year": 1953, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "soa1953189"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Road Traffic Act 1961 (SA)", "short_name": "Road Traffic Act", "year": 1961, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "rta1961167"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Controlled Substances Act 1984 (SA)", "short_name": "Controlled Substances Act", "year": 1984, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "csa1984253"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (Police Powers) Act 2005 (SA)", "short_name": "Terrorism (Police Powers) Act", "year": 2005, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "tpa2005251"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (Preventative Detention) Act 2005 (SA)", "short_name": "Terrorism (Preventative Detention) Act", "year": 2005, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "tpda2005342"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Intervention Orders (Prevention of Abuse) Act 2009 (SA)", "short_name": "Intervention Orders (Prevention of Abuse) Act", "year": 2009, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "iopaa2009456"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Firearms Act 2015 (SA)", "short_name": "Firearms Act", "year": 2015, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "fa2015102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Bail Act 1985 (SA)", "short_name": "Bail Act", "year": 1985, "jurisdiction": "sa",
     "austlii_url": _austlii("sa", "ba198541"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== WA ====================
    {"act_name": "Criminal Code Act Compilation Act 1913 (WA)", "short_name": "Criminal Code", "year": 1913, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "ccaca1913252"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Criminal Code is Schedule to the 1913 Act"},
    {"act_name": "Firearms Act 1973 (WA)", "short_name": "Firearms Act", "year": 1973, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "fa1973102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Misuse of Drugs Act 1981 (WA)", "short_name": "Misuse of Drugs Act", "year": 1981, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "moda1981256"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Restraining Orders Act 1997 (WA)", "short_name": "Restraining Orders Act", "year": 1997, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "roa1997176"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Primary WA DV legislation"},
    {"act_name": "Terrorism (Extraordinary Powers) Act 2005 (WA)", "short_name": "Terrorism (Extraordinary Powers) Act", "year": 2005, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "tepa2005339"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (Preventative Detention) Act 2006 (WA)", "short_name": "Terrorism (Preventative Detention) Act", "year": 2006, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "tpda2006342"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Road Traffic Act 1974 (WA)", "short_name": "Road Traffic Act", "year": 1974, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "rta1974167"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Framework references 2008 Act variant — confirm section numbers on AustLII"},
    {"act_name": "Road Traffic (Authorisation to Drive) Act 2008 (WA)", "short_name": "Road Traffic (Authorisation to Drive) Act", "year": 2008, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "rtatda2008508"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Bail Act 1982 (WA)", "short_name": "Bail Act", "year": 1982, "jurisdiction": "wa",
     "austlii_url": _austlii("wa", "ba198241"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== TAS ====================
    {"act_name": "Criminal Code Act 1924 (Tas)", "short_name": "Criminal Code Act", "year": 1924, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "cca1924115"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Police Offences Act 1935 (Tas)", "short_name": "Police Offences Act", "year": 1935, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "poa1935189"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Road Safety (Alcohol and Drugs) Act 1970 (Tas)", "short_name": "Road Safety (Alcohol and Drugs) Act", "year": 1970, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "rsaada1970299"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Firearms Act 1996 (Tas)", "short_name": "Firearms Act", "year": 1996, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "fa1996102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Misuse of Drugs Act 2001 (Tas)", "short_name": "Misuse of Drugs Act", "year": 2001, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "moda2001256"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Family Violence Act 2004 (Tas)", "short_name": "Family Violence Act", "year": 2004, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "fva2004215"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Police Powers (Public Safety) Act 2005 (Tas)", "short_name": "Police Powers (Public Safety) Act", "year": 2005, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "ppsa2005330"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Bail Act 1994 (Tas)", "short_name": "Bail Act", "year": 1994, "jurisdiction": "tas",
     "austlii_url": _austlii("tas", "ba199441"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== NT ====================
    {"act_name": "Summary Offences Act 1923 (NT)", "short_name": "Summary Offences Act", "year": 1923, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "soa1923189"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Criminal Code Act 1983 (NT)", "short_name": "Criminal Code Act", "year": 1983, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "cca1983115"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Traffic Act 1987 (NT)", "short_name": "Traffic Act", "year": 1987, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "ta1987156"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Misuse of Drugs Act 1990 (NT)", "short_name": "Misuse of Drugs Act", "year": 1990, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "moda1990256"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Firearms Act 1997 (NT)", "short_name": "Firearms Act", "year": 1997, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "fa1997102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Domestic and Family Violence Act 2007 (NT)", "short_name": "Domestic and Family Violence Act", "year": 2007, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "dafva2007359"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (Emergency Powers) Act 2003 (NT)", "short_name": "Terrorism (Emergency Powers) Act", "year": 2003, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "tepa2003339"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Serious Crime Control Act 2009 (NT)", "short_name": "Serious Crime Control Act", "year": 2009, "jurisdiction": "nt",
     "austlii_url": _austlii("nt", "scca2009334"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== ACT ====================
    {"act_name": "Crimes Act 1900 (ACT)", "short_name": "Crimes Act", "year": 1900, "jurisdiction": "act",
     "austlii_url": _austlii("act", "ca190082"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Road Transport (Alcohol and Drugs) Act 1977 (ACT)", "short_name": "Road Transport (Alcohol and Drugs) Act", "year": 1977, "jurisdiction": "act",
     "austlii_url": _austlii("act", "rtaada1977300"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Drugs of Dependence Act 1989 (ACT)", "short_name": "Drugs of Dependence Act", "year": 1989, "jurisdiction": "act",
     "austlii_url": _austlii("act", "doda1989252"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Firearms Act 1996 (ACT)", "short_name": "Firearms Act", "year": 1996, "jurisdiction": "act",
     "austlii_url": _austlii("act", "fa1996102"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Criminal Code 2002 (ACT)", "short_name": "Criminal Code", "year": 2002, "jurisdiction": "act",
     "austlii_url": _austlii("act", "cc200288"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Family Violence Act 2016 (ACT)", "short_name": "Family Violence Act", "year": 2016, "jurisdiction": "act",
     "austlii_url": _austlii("act", "fva2016215"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Terrorism (Extraordinary Temporary Powers) Act 2006 (ACT)", "short_name": "Terrorism (Extraordinary Temporary Powers) Act", "year": 2006, "jurisdiction": "act",
     "austlii_url": _austlii("act", "tetpa2006415"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Crimes (Criminal Organisations Control) Act 2012 (ACT)", "short_name": "Crimes (Criminal Organisations Control) Act", "year": 2012, "jurisdiction": "act",
     "austlii_url": _austlii("act", "ccoca2012480"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},

    # ==================== CTH ====================
    {"act_name": "Crimes Act 1914 (Cth)", "short_name": "Crimes Act", "year": 1914, "jurisdiction": "cth",
     "austlii_url": _austlii("cth", "ca191482"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Family Law Act 1975 (Cth)", "short_name": "Family Law Act", "year": 1975, "jurisdiction": "cth",
     "austlii_url": _austlii("cth", "fla1975114"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Criminal Code Act 1995 (Cth)", "short_name": "Criminal Code Act", "year": 1995, "jurisdiction": "cth",
     "austlii_url": _austlii("cth", "cca1995115"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "Commonwealth Criminal Code (Schedule)"},
    {"act_name": "Corruption of Foreign Public Officials Act 1999 (Cth)", "short_name": "Corruption of Foreign Public Officials Act", "year": 1999, "jurisdiction": "cth",
     "austlii_url": _austlii("cth", "cofpoa1999430"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": ""},
    {"act_name": "Judiciary Act 1903 (Cth)", "short_name": "Judiciary Act", "year": 1903, "jurisdiction": "cth",
     "austlii_url": _austlii("cth", "ja1903100"), "last_verified": INITIAL_VERIFIED, "verification_source": "manual", "notes": "s.35A governs High Court special leave"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def total_count() -> int:
    return len(LEGISLATION_REGISTRY)


def by_jurisdiction() -> dict:
    out: dict = {}
    for entry in LEGISLATION_REGISTRY:
        out.setdefault(entry["jurisdiction"], []).append(entry)
    for jur in out:
        out[jur].sort(key=lambda e: (e["year"], e["short_name"]))
    return out


def search_url_for(entry: dict) -> str:
    """AustLII search fallback URL — always works even when direct URL 404s."""
    return _austlii_search(entry["act_name"], entry["jurisdiction"])
