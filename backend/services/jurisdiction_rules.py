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
    "mental impairment defence", "psychosis at time of offence",
}

COMMON_SENTENCE_TERMS = {
    "manifestly excessive", "manifest excess", "rehabilitation", "mitigation",
    "sentencing error", "non-parole", "parole", "moral culpability", "totality",
    "discount", "sentence excessive", "sentence manifestly excessive",
    "parity", "sentence severity",
}

# Hard-lock conviction terms that are unambiguously liability/conviction issues across
# all jurisdictions — applied BEFORE soft-scoring to ensure the mental impairment
# split fires reliably (the scorer must bite, not merely nudge).
COMMON_HARD_CONVICTION_TERMS = {
    "mens rea", "mental impairment defence", "psychosis at time of offence",
}

# Hard-lock sentence terms that are unambiguously sentencing issues across all
# jurisdictions — applied BEFORE soft-scoring so moral-culpability/totality/parity
# language always resolves to sentence, never conviction.
COMMON_HARD_SENTENCE_TERMS = {
    "moral culpability", "totality", "parity", "sentence severity",
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
        conviction_pathway="Conviction appeal / miscarriage of justice under s 6(1) Criminal Appeal Act 1912 (NSW). Where s 23A Crimes Act 1900 (NSW) is engaged, the ground operates as a PARTIAL DEFENCE reducing murder to manslaughter — NOT as sentencing mitigation.",
        sentence_pathway="Sentence appeal under s 6(1) Criminal Appeal Act 1912 (NSW)",
        procedure_pathway="Procedural unfairness under s 6(1) Criminal Appeal Act 1912 (NSW)",
        evidence_pathway="Evidentiary miscarriage of justice under s 6(1) Criminal Appeal Act 1912 (NSW)",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under s 6(1) Criminal Appeal Act 1912 (NSW)",
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
        } | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={
            "manifestly excessive", "manifest excess", "rehabilitation",
            "s 21a", "section 21a", "s 3a", "section 3a",
            "house v the king", "house v king",
        } | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "VIC": JurisdictionRuleSet(
        code="VIC",
        conviction_pathway="Conviction appeal under the Criminal Procedure Act 2009 (Vic)",
        sentence_pathway="Sentence appeal under the Criminal Procedure Act 2009 (Vic)",
        procedure_pathway="Procedural unfairness under the Criminal Procedure Act 2009 (Vic)",
        evidence_pathway="Evidentiary miscarriage of justice under the Criminal Procedure Act 2009 (Vic)",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under the Criminal Procedure Act 2009 (Vic)",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental impairment", "defence of mental impairment"},
        sentence_terms=COMMON_SENTENCE_TERMS | {"sentencing act 1991"},
        procedure_terms=COMMON_PROCEDURE_TERMS | {"judge alone"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental impairment", "defence of mental impairment"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "QLD": JurisdictionRuleSet(
        code="QLD",
        conviction_pathway="Conviction appeal under Queensland criminal appeal law",
        sentence_pathway="Sentence appeal under Queensland criminal appeal law",
        procedure_pathway="Procedural unfairness under Queensland criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under Queensland criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under Queensland criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"unsoundness of mind", "diminished responsibility"},
        sentence_terms=COMMON_SENTENCE_TERMS | {"penalties and sentences act"},
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"unsoundness of mind", "diminished responsibility"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "SA": JurisdictionRuleSet(
        code="SA",
        conviction_pathway="Conviction appeal under South Australian criminal appeal law",
        sentence_pathway="Sentence appeal under South Australian criminal appeal law",
        procedure_pathway="Procedural unfairness under South Australian criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under South Australian criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under South Australian criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental incompetence", "mental impairment"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental incompetence", "mental impairment"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "WA": JurisdictionRuleSet(
        code="WA",
        conviction_pathway="Conviction appeal under Western Australian criminal appeal law",
        sentence_pathway="Sentence appeal under Western Australian criminal appeal law",
        procedure_pathway="Procedural unfairness under Western Australian criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under Western Australian criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under Western Australian criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"unsoundness of mind"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS | {"judge alone"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"unsoundness of mind"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "TAS": JurisdictionRuleSet(
        code="TAS",
        conviction_pathway="Conviction appeal under Tasmanian criminal appeal law",
        sentence_pathway="Sentence appeal under Tasmanian criminal appeal law",
        procedure_pathway="Procedural unfairness under Tasmanian criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under Tasmanian criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under Tasmanian criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"insanity"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"insanity"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"juror", "jury integrity", "jury misconduct"},
    ),
    "NT": JurisdictionRuleSet(
        code="NT",
        conviction_pathway="Conviction appeal under Northern Territory criminal appeal law",
        sentence_pathway="Sentence appeal under Northern Territory criminal appeal law",
        procedure_pathway="Procedural unfairness under Northern Territory criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under Northern Territory criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under Northern Territory criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental impairment", "criminal responsibility", "s 156", "section 156"},
        sentence_terms=COMMON_SENTENCE_TERMS | {"sentencing act 1995"},
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental impairment", "criminal responsibility"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "ACT": JurisdictionRuleSet(
        code="ACT",
        conviction_pathway="Conviction appeal under ACT criminal appeal law",
        sentence_pathway="Sentence appeal under ACT criminal appeal law",
        procedure_pathway="Procedural unfairness under ACT criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under ACT criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under ACT criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"mental impairment"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS | {"judge alone"},
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"mental impairment"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
        hard_procedure_terms={"judge-alone", "judge alone", "juror", "jury integrity", "jury misconduct"},
    ),
    "CTH": JurisdictionRuleSet(
        code="CTH",
        conviction_pathway="Conviction appeal under applicable Commonwealth / federal criminal appeal law",
        sentence_pathway="Sentence appeal under applicable Commonwealth / federal criminal appeal law",
        procedure_pathway="Procedural unfairness under applicable Commonwealth / federal criminal appeal law",
        evidence_pathway="Evidentiary miscarriage of justice under applicable Commonwealth / federal criminal appeal law",
        ineffective_counsel_pathway="Miscarriage of justice arising from conduct of trial under applicable Commonwealth / federal criminal appeal law",
        conviction_terms=COMMON_CONVICTION_TERMS | {"criminal code act 1995", "fault elements", "intention", "knowledge", "recklessness", "negligence"},
        sentence_terms=COMMON_SENTENCE_TERMS,
        procedure_terms=COMMON_PROCEDURE_TERMS,
        evidence_terms=COMMON_EVIDENCE_TERMS,
        ineffective_counsel_terms=COMMON_INEFFECTIVE_COUNSEL_TERMS,
        hard_conviction_terms={"fault elements", "intention", "knowledge", "recklessness", "negligence"} | COMMON_HARD_CONVICTION_TERMS,
        hard_sentence_terms={"manifestly excessive", "manifest excess", "rehabilitation"} | COMMON_HARD_SENTENCE_TERMS,
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
