#  — Sentencing (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



SENTENCING_FRAMEWORK = {
    "nsw": {
        "act": "Crimes (Sentencing Procedure) Act 1999 (NSW)",
        "key_provisions": [
            "s 3A — Purposes of sentencing (just punishment, deterrence, rehabilitation, denunciation, community protection)",
            "s 21A — Aggravating, mitigating, and other factors in sentencing",
            "s 44 — Setting the non-parole period",
            "s 54A-54D — Standard non-parole periods (Table, Division 1A)",
            "Part 4 Div 2 — Intensive correction orders",
            "Part 4 Div 3 — Community correction orders",
            "Part 7 — Victim impact statements",
            "s 22 — Sentencing discount for guilty pleas",
            "s 53A — Cumulative and concurrent sentences",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess — sentence outside the range reasonably available to the sentencing judge",
            "Manifest inadequacy — Crown appeal where sentence unreasonably lenient",
            "Specific error — identifiable error in sentencing reasoning (e.g., wrong Act cited, wrong maximum penalty applied)",
            "Failure to apply standard non-parole period correctly",
            "Failure to give proper weight to mitigating factors under s 21A(3)",
            "Error in assessment of totality (total effective sentence disproportionate to overall offending)",
            "Failure to properly apply sentencing discount for guilty plea under s 22",
        ],
        "last_verified": "2026-02",
    },
    "vic": {
        "act": "Sentencing Act 1991 (Vic)",
        "key_provisions": [
            "s 5(1) — Sentencing purposes (just punishment, deterrence, rehabilitation, denunciation, community protection)",
            "s 5(2) — Sentencing factors (nature/gravity, culpability, victim impact, guilty plea, prior character)",
            "s 5(2C) — Standard sentence for offence (if applicable)",
            "Part 2A — Sentencing guidelines and guideline judgments",
            "Part 3 — Community correction orders (ss 36-48Q)",
            "Part 3A — Aggregate sentences",
            "Part 3 Div 2 — Imprisonment (parsimony principle)",
            "Part 9 — Parole (interaction with Corrections Act 1986)",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess — sentence outside the range available to a reasonable sentencing judge",
            "Manifest inadequacy — Crown appeal",
            "Specific error in sentencing reasoning",
            "Failure to apply parsimony principle",
            "Error in totality assessment",
            "Failure to give proper weight to relevant considerations under s 5(2)",
        ],
        "last_verified": "2026-02",
    },
    "qld": {
        "act": "Penalties and Sentences Act 1992 (Qld)",
        "key_provisions": [
            "s 3 — Purposes of sentencing (punishment, rehabilitation, deterrence, denunciation, community protection)",
            "s 9 — Sentencing guidelines (seriousness, harm, history, remorse, intoxication not mitigating if voluntary)",
            "s 9(2)(a) — Imprisonment as last resort",
            "Part 5 — Imprisonment",
            "Part 9A — Serious violent offences (SVOs): s 161A automatic SVO, s 161B discretionary SVO",
            "Part 9D — Indefinite sentences",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy — Attorney-General appeal",
            "Specific error (e.g., SVO declaration wrongly made or omitted)",
            "Failure to have regard to mandatory considerations under s 9",
            "Error in parole eligibility date (80% for SVO)",
        ],
        "last_verified": "2026-02",
    },
    "sa": {
        "act": "Sentencing Act 2017 (SA)",
        "key_provisions": [
            "s 10 — Purposes of sentencing (punishment, deterrence, rehabilitation, denunciation, community protection)",
            "s 11 — Primary sentencing considerations",
            "Part 3 Div 2 — Imprisonment",
            "Part 3 Div 3 — Non-parole periods",
            "Part 4 — Sentence discount for guilty pleas (up to 40% Magistrates, up to 35% higher courts)",
            "Part 5 — Serious repeat offenders (non-parole at least four-fifths of sentence)",
            "s 53 — Cumulative and concurrent sentences",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy — DPP appeal",
            "Specific error in applying guilty plea discount under Part 4",
            "Error in non-parole period calculation",
            "Failure to consider relevant mitigating/aggravating factors under s 11",
        ],
        "last_verified": "2026-02",
    },
    "wa": {
        "act": "Sentencing Act 1995 (WA)",
        "key_provisions": [
            "s 6 — Principles of sentencing (proportionality, consistency, community protection)",
            "s 6(4) — Imprisonment as last resort",
            "s 7 — Aggravating factors",
            "s 8 — Mitigating factors",
            "s 86 — Prohibition on imprisonment of 6 months or less",
            "s 88 — Concurrent, cumulative, and partly cumulative sentences",
            "Part 3 — Imprisonment",
            "Part 8 — Parole (s 89 eligibility)",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy — State appeal",
            "Specific error in sentencing reasoning",
            "Failure to apply imprisonment as last resort under s 6(4)",
            "Error in totality",
        ],
        "last_verified": "2026-02",
    },
    "tas": {
        "act": "Sentencing Act 1997 (Tas)",
        "key_provisions": [
            "s 3 — Purposes of sentencing (community protection primary)",
            "s 11 — Matters to be considered (nature/circumstances, offender character, prior convictions, victim impact)",
            "Part 3 — Imprisonment (s 12 imprisonment as last resort, s 17 minimum non-parole periods)",
            "Part 4 — Community service orders",
            "Part 5 — Probation (max 5 years)",
            "Part 7 — Suspended sentences",
            "Part 3A — Dangerous criminal declarations",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy — DPP appeal",
            "Specific error in sentencing reasoning",
            "Failure to have regard to matters in s 11",
            "Error in dangerous criminal declaration",
        ],
        "last_verified": "2026-02",
    },
    "nt": {
        "act": "Sentencing Act 1995 (NT)",
        "key_provisions": [
            "s 5 — Purposes of sentencing (just punishment, rehabilitation, deterrence, denunciation, community protection)",
            "s 6 — Sentencing factors (culpability, prevalence, guilty plea, custody time served, cultural considerations)",
            "s 5(2)(j) — Cultural background of offender (Aboriginal customary law — must not excuse violence)",
            "s 78A — Mandatory sentencing for property offences (three-strikes)",
            "s 78D — Mandatory sentencing for assaults on police/emergency workers",
            "Part 5 — Community-based orders",
            "Part 7 — Indefinite sentences",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy",
            "Specific error (e.g., mandatory sentencing incorrectly applied or not applied)",
            "Failure to consider cultural background under s 5(2)(j)",
            "Error in totality for cumulative sentences under s 55",
        ],
        "last_verified": "2026-02",
    },
    "act": {
        "act": "Crimes (Sentencing) Act 2005 (ACT)",
        "key_provisions": [
            "Part 4 — Sentencing purposes and considerations",
            "Part 5 — Imprisonment (imprisonment only if no other sentence appropriate)",
            "Part 6 — Good behaviour orders",
            "Part 7 — Community service orders",
            "s 33 — Aggravating and mitigating factors",
            "s 34 — Discount for guilty pleas",
            "s 33A — Hate crime aggravation",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy — DPP appeal",
            "Specific error in reasoning",
            "Failure to consider human rights under Human Rights Act 2004 (ACT)",
            "Improper application of hate crime aggravation under s 33A",
        ],
        "last_verified": "2026-02",
    },
    "federal": {
        "act": "Crimes Act 1914 (Cth) Part IB",
        "key_provisions": [
            "s 16A — Matters to which court must have regard when sentencing federal offenders",
            "s 16B — Court must warn of possible imprisonment",
            "s 16C — Fines (proportionality to seriousness)",
            "s 16E — Reparation orders",
            "s 17A — Non-parole periods for federal offenders",
            "s 19B — Discharge without conviction (spent conviction scheme)",
        ],
        "sentencing_appeal_grounds": [
            "Manifest excess",
            "Manifest inadequacy — Commonwealth DPP appeal",
            "Specific error under s 16A considerations",
            "Error in non-parole period calculation under s 17A",
            "Inconsistency between federal and state sentencing principles",
        ],
        "note": "Federal offences are sentenced in state courts but MUST apply Crimes Act 1914 (Cth) Part IB, NOT the state sentencing Act. The state sentencing Act applies only to state offences.",
        "last_verified": "2026-02",
    },
}
