# DO NOT UNDO — Mental Impairment (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



MENTAL_IMPAIRMENT_FRAMEWORK = {
    "nsw": {
        "act": "Mental Health and Cognitive Impairment Forensic Provisions Act 2020 (NSW)",
        "replaces": "Mental Health (Forensic Provisions) Act 1990 (NSW)",
        "key_provisions": [
            "Part 3 — Defence of mental health impairment (replaces 'not guilty by reason of mental illness')",
            "Part 4 — Fitness to be tried (s 36 — unfit if unable to understand proceedings, plead, instruct counsel, or challenge jurors)",
            "Part 5 — Special hearings (where accused found unfit — limited finding of guilt or acquittal)",
            "Part 6 — Forensic patients (supervision orders, conditions, Mental Health Review Tribunal reviews)",
            "s 28 — Partial defence of substantial impairment by mental health impairment or cognitive impairment (reduces murder to manslaughter, Crimes Act s 23A)",
        ],
        "appeal_relevance": "Appeals involving mental health: fitness to stand trial, defence of mental health impairment, whether cognitive impairment was properly assessed, forensic patient orders, and interaction with mens rea",
        "last_verified": "2026-02",
    },
    "vic": {
        "act": "Crimes (Mental Impairment and Unfitness to be Tried) Act 1997 (Vic)",
        "key_provisions": [
            "s 20 — Defence of mental impairment (accused must prove on balance of probabilities that at the time of the offence they did not know the nature and quality of the conduct, or did not know the conduct was wrong)",
            "Part 3 — Investigations of fitness to stand trial",
            "Part 5 — Supervision orders (custodial and non-custodial)",
            "Part 5A — Forensic Leave Panel",
            "s 21 — Special hearings (where accused unfit — determine on available evidence whether conduct established)",
        ],
        "appeal_relevance": "Appeals involving mental impairment in Victoria: fitness, NGMI defence threshold, supervision order reviews",
        "last_verified": "2026-02",
    },
    "qld": {
        "act": "Mental Health Act 2016 (Qld) — Chapter 12 (Mental Health Court)",
        "key_provisions": [
            "Chapter 12 — Mental Health Court (determines fitness and unsoundness of mind references)",
            "s 645 — Reference to Mental Health Court (by court, DPP, or accused)",
            "s 651 — Determination of fitness for trial",
            "s 653 — Determination of unsoundness of mind (NGMI equivalent)",
            "Criminal Code Act 1899 (Qld) s 27 — Insanity (common law McNaghten defence codified)",
        ],
        "appeal_relevance": "Appeals from Mental Health Court decisions: fitness determination, unsoundness of mind finding, forensic order conditions",
        "last_verified": "2026-02",
    },
    "sa": {
        "act": "Criminal Law Consolidation Act 1935 (SA) — Part 8A",
        "key_provisions": [
            "s 269C — Defence of mental impairment (accused did not know nature/quality of conduct or could not reason with moderate sense and composure whether conduct was wrong)",
            "s 269H — Fitness to stand trial (unfit if unable to understand nature of charge, plead, exercise challenges, instruct counsel, follow proceedings)",
            "s 269I — Investigation of fitness",
            "s 269O — Supervision orders for persons found mentally unfit or NGMI",
        ],
        "appeal_relevance": "Appeals involving mental impairment in SA: fitness determination, NGMI defence, supervision order duration and conditions",
        "last_verified": "2026-02",
    },
    "wa": {
        "act": "Criminal Law (Mentally Impaired Accused) Act 1996 (WA)",
        "key_provisions": [
            "s 9 — Court may refer question of fitness to stand trial",
            "s 16 — Custody orders (indefinite detention in authorised hospital or declared place)",
            "s 19 — Mentally Impaired Accused Review Board reviews",
            "s 22 — Community-based supervision orders",
            "Criminal Code Act Compilation Act 1913 (WA) s 27 — Insanity defence",
        ],
        "appeal_relevance": "Appeals in WA: custody order duration (potentially indefinite), Review Board recommendations, fitness assessments",
        "last_verified": "2026-02",
    },
    "tas": {
        "act": "Criminal Justice (Mental Impairment) Act 1999 (Tas)",
        "key_provisions": [
            "Part 2 — Fitness to stand trial",
            "Part 3 — Defence of mental impairment (not guilty by reason of insanity)",
            "Part 4 — Supervision orders (restriction orders, forensic orders)",
            "Part 5 — Review of orders (Mental Health Tribunal)",
        ],
        "appeal_relevance": "Appeals involving mental impairment in Tasmania: fitness, NGMI, supervision/forensic order reviews",
        "last_verified": "2026-02",
    },
    "nt": {
        "act": "Criminal Code Act 1983 (NT) — ss 43A-43P",
        "key_provisions": [
            "s 43C — Defence of mental impairment",
            "s 43D — Investigation of fitness to stand trial",
            "s 43F — Special hearings (where accused unfit)",
            "s 43H — Supervision orders",
            "s 43P — Review of supervision orders by Supreme Court",
        ],
        "appeal_relevance": "Appeals involving mental impairment in NT: fitness determination, special hearing outcomes, supervision order reviews",
        "last_verified": "2026-02",
    },
    "act": {
        "act": "Mental Health Act 2015 (ACT) and Criminal Code 2002 (ACT) Chapter 13",
        "key_provisions": [
            "Criminal Code 2002 Chapter 13 — Mental impairment (defence, fitness to plead)",
            "Mental Health Act 2015 — Forensic mental health orders (psychiatric treatment orders, community care orders)",
            "ACAT review of forensic orders",
        ],
        "appeal_relevance": "Appeals involving mental impairment in ACT: fitness, NGMI defence, forensic order reviews, interaction with Human Rights Act 2004 (ACT)",
        "last_verified": "2026-02",
    },
}
