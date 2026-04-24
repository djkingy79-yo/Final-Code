"""
jurisdiction_rules.py

Jurisdiction-aware classification and pathway rules for Australian criminal appeals.

Supported: NSW, VIC, QLD, SA, WA, TAS, NT, ACT, CTH (Commonwealth / Federal).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Jurisdiction = Literal["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "CTH"]
GroundType = Literal["conviction", "sentence", "procedure", "evidence", "ineffective_counsel"]


@dataclass(frozen=True)
class JurisdictionRuleSet:
    code: Jurisdiction
    conviction_pathway: str
    sentence_pathway: str
    procedure_pathway: str
    evidence_pathway: str
    ineffective_counsel_pathway: str
    conviction_terms: set[str]
    sentence_terms: set[str]
    procedure_terms: set[str]
    evidence_terms: set[str]
    ineffective_counsel_terms: set[str]
    hard_conviction_terms: set[str]
    hard_sentence_terms: set[str]
    hard_procedure_terms: set[str]


COMMON_CONVICTION_TERMS = {
    "mens rea", "intent", "intention", "unsafe verdict", "unreasonable verdict",
    "mental state", "psychosis", "psychiatric evidence", "reckless indifference",
    "beyond reasonable doubt", "partial defence", "mental illness", "mental impairment",
    "fault elements", "knowledge", "recklessness", "negligence",
    # Counsel feedback 23 Feb 2026 — Issue 1: mens-rea misdirection / probability
    # vs possibility directions / element-of-offence errors are conviction-level
    # concepts; add explicit terms so sub-particulars framed this way don't
    # fall through to the (new) procedure default.
    "misdirection", "probability versus possibility", "element of offence",
    "element of the offence",
}

COMMON_SENTENCE_TERMS = {
    "manifestly excessive", "manifest excess", "rehabilitation", "mitigation",
    "sentencing error", "non-parole", "parole", "moral culpability", "totality",
    "discount", "sentence excessive", "sentence manifestly excessive",
}

COMMON_PROCEDURE_TERMS = {
    "judge-alone", "judge alone", "jury integrity", "juror", "jury misconduct",
    "jury bias", "pretrial publicity", "pre-trial publicity", "procedural unfairness",
    "fair trial", "mode of trial",
}

COMMON_EVIDENCE_TERMS = {
    "admissibility", "probative", "prejudicial", "inadmissible",
    "wrongly admitted", "wrongly excluded", "evidence act", "s 137", "section 137",
}

COMMON_INEFFECTIVE_COUNSEL_TERMS = {
    "ineffective counsel", "ineffective assistance", "failed to argue",
    "failed to preserve", "lacked vigour", "lacked vigor", "incompetent representation",
    "tkwj", "birks", "counsel failed", "failure of counsel",
}


JURISDICTION_RULES: dict[Jurisdiction, JurisdictionRuleSet] = {
    "NSW": JurisdictionRuleSet(
        code="NSW",
        conviction_pathway="s 5(1) and s 6(1) Criminal Appeal Act 1912 (NSW)",
        sentence_pathway="s 5(1)(c) and s 6(3) Criminal Appeal Act 1912 (NSW)",
        procedure_pathway="s 6(1) Criminal Appeal Act 1912 (NSW) — miscarriage of justice limb",
        evidence_pathway="s 6(1) Criminal Appeal Act 1912 (NSW) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 6(1) Criminal Appeal Act 1912 (NSW) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {
            "s 18", "section 18", "s 23a", "section 23a",
            "substantial impairment", "abnormality of mind",
            "mental illness defence", "beyond reasonable doubt",
        },
        sentence_terms=COMMON_SENTENCE_TERMS | {
            "s 21a", "section 21a", "s 3a", "section 3a",
            "sentencing procedure", "house v the king", "house v king",
        },
        procedure_terms=COMMON_PROCEDURE_TERMS | {"s 132", "section 132", "jury act"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={
            "s 23a", "section 23a", "substantial impairment", "abnormality of mind",
            "unsafe verdict", "mens rea", "mental illness defence",
            "beyond reasonable doubt",
        },
        hard_sentence_terms={
            "manifestly excessive", "manifest excess", "rehabilitation",
            "s 21a", "section 21a", "s 3a", "section 3a",
            "house v the king", "house v king",
        },
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "VIC": JurisdictionRuleSet(
        code="VIC",
        conviction_pathway="s 274 Criminal Procedure Act 2009 (Vic)",
        sentence_pathway="s 278 Criminal Procedure Act 2009 (Vic)",
        procedure_pathway="s 276(1)(b) Criminal Procedure Act 2009 (Vic) — substantial miscarriage of justice limb",
        evidence_pathway="s 276(1)(b) Criminal Procedure Act 2009 (Vic) — substantial miscarriage of justice limb",
        ineffective_counsel_pathway="s 276(1)(b) Criminal Procedure Act 2009 (Vic) — substantial miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental impairment", "defence of mental impairment"},
        sentence_terms=COMMON_SENTENCE_TERMS | {"sentencing act 1991"},
        procedure_terms=COMMON_PROCEDURE_TERMS | {"judge alone"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental impairment", "defence of mental impairment"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "QLD": JurisdictionRuleSet(
        code="QLD",
        conviction_pathway="s 668D and s 668E Criminal Code 1899 (Qld)",
        sentence_pathway="s 668D(1)(c) and s 668E(3) Criminal Code 1899 (Qld)",
        procedure_pathway="s 668E(1) Criminal Code 1899 (Qld) — miscarriage of justice limb",
        evidence_pathway="s 668E(1) Criminal Code 1899 (Qld) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 668E(1) Criminal Code 1899 (Qld) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"unsoundness of mind", "diminished responsibility"},
        sentence_terms=COMMON_SENTENCE_TERMS | {"penalties and sentences act"},
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"unsoundness of mind", "diminished responsibility"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "SA": JurisdictionRuleSet(
        code="SA",
        conviction_pathway="s 352 and s 353 Criminal Procedure Act 1921 (SA)",
        sentence_pathway="s 352(1) Criminal Procedure Act 1921 (SA)",
        procedure_pathway="s 353(1)(c) Criminal Procedure Act 1921 (SA) — miscarriage of justice limb",
        evidence_pathway="s 353(1)(c) Criminal Procedure Act 1921 (SA) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 353(1)(c) Criminal Procedure Act 1921 (SA) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental incompetence", "mental impairment"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental incompetence", "mental impairment"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "WA": JurisdictionRuleSet(
        code="WA",
        conviction_pathway="s 7 and s 30 Criminal Appeals Act 2004 (WA)",
        sentence_pathway="s 8 and s 31 Criminal Appeals Act 2004 (WA)",
        procedure_pathway="s 30(4)(a) Criminal Appeals Act 2004 (WA) — miscarriage of justice limb",
        evidence_pathway="s 30(4)(a) Criminal Appeals Act 2004 (WA) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 30(4)(a) Criminal Appeals Act 2004 (WA) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"unsoundness of mind"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS | {"judge alone"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"unsoundness of mind"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "TAS": JurisdictionRuleSet(
        code="TAS",
        conviction_pathway="s 401 and s 402 Criminal Code Act 1924 (Tas)",
        sentence_pathway="s 401(2) Criminal Code Act 1924 (Tas)",
        procedure_pathway="s 402(1)(c) Criminal Code Act 1924 (Tas) — miscarriage of justice limb",
        evidence_pathway="s 402(1)(c) Criminal Code Act 1924 (Tas) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 402(1)(c) Criminal Code Act 1924 (Tas) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"insanity"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"insanity"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"juror", "jury integrity", "jury misconduct"},
    ),
    "NT": JurisdictionRuleSet(
        code="NT",
        conviction_pathway="s 410 and s 411 Criminal Code Act 1983 (NT)",
        sentence_pathway="s 412 Criminal Code Act 1983 (NT)",
        procedure_pathway="s 411(1)(c) Criminal Code Act 1983 (NT) — miscarriage of justice limb",
        evidence_pathway="s 411(1)(c) Criminal Code Act 1983 (NT) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 411(1)(c) Criminal Code Act 1983 (NT) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental impairment", "criminal responsibility", "s 156", "section 156"},
        sentence_terms=COMMON_SENTENCE_TERMS | {"sentencing act 1995"},
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental impairment", "criminal responsibility"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "ACT": JurisdictionRuleSet(
        code="ACT",
        conviction_pathway="s 37E Supreme Court Act 1933 (ACT)",
        sentence_pathway="s 37E Supreme Court Act 1933 (ACT)",
        procedure_pathway="s 37E Supreme Court Act 1933 (ACT) — miscarriage of justice limb",
        evidence_pathway="s 37E Supreme Court Act 1933 (ACT) — miscarriage of justice limb",
        ineffective_counsel_pathway="s 37E Supreme Court Act 1933 (ACT) — miscarriage of justice limb",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental impairment"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS | {"judge alone"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental impairment"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "CTH": JurisdictionRuleSet(
        code="CTH",
        conviction_pathway="s 35A Judiciary Act 1903 (Cth) — first-tier appeal via the State/Territory Court of Criminal Appeal of the trial court",
        sentence_pathway="s 35A Judiciary Act 1903 (Cth) — first-tier appeal via the State/Territory Court of Criminal Appeal of the trial court",
        procedure_pathway="s 35A Judiciary Act 1903 (Cth) — first-tier appeal via the State/Territory Court of Criminal Appeal of the trial court (miscarriage of justice limb)",
        evidence_pathway="s 35A Judiciary Act 1903 (Cth) — first-tier appeal via the State/Territory Court of Criminal Appeal of the trial court (miscarriage of justice limb)",
        ineffective_counsel_pathway="s 35A Judiciary Act 1903 (Cth) — first-tier appeal via the State/Territory Court of Criminal Appeal of the trial court (miscarriage of justice limb)",
        conviction_terms=COMMON_CONVICTION_TERMS | {"criminal code act 1995", "fault elements", "intention", "knowledge", "recklessness", "negligence"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"fault elements", "intention", "knowledge", "recklessness", "negligence"},
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"},
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
}


def get_rules(jurisdiction: str) -> JurisdictionRuleSet:
    code = (jurisdiction or "").upper().strip()
    if code == "FEDERAL":
        code = "CTH"
    if code not in JURISDICTION_RULES:
        raise ValueError(f"Unsupported jurisdiction: {jurisdiction}")
    return JURISDICTION_RULES[code]


def infer_pathway(jurisdiction: str, ground_type: GroundType) -> str:
    rules = get_rules(jurisdiction)
    mapping = {
        "conviction": rules.conviction_pathway,
        "sentence": rules.sentence_pathway,
        "procedure": rules.procedure_pathway,
        "evidence": rules.evidence_pathway,
        "ineffective_counsel": rules.ineffective_counsel_pathway,
    }
    return mapping[ground_type]
