# DO NOT UNDO — Evidence (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



EVIDENCE_FRAMEWORK = {
    "uniform_evidence_jurisdictions": {
        "note": "NSW, VIC, TAS, ACT, and CTH have adopted the uniform evidence law (based on the Evidence Act 1995 (Cth)). NT adopted it in 2011. Key provisions are substantively the same across these jurisdictions.",
        "key_uniform_provisions": [
            "ss 55-56 — Relevance (evidence relevant if it could rationally affect assessment of probability of a fact in issue)",
            "ss 59-75 — Hearsay (general exclusion with specified exceptions: first-hand hearsay, business records, contemporaneous statements)",
            "ss 76-80 — Opinion evidence (general exclusion; expert opinion admissible under s 79)",
            "ss 81-90 — Admissions (admissions by accused generally admissible; exclusion for involuntary confessions s 84, unreliable confessions s 85, improperly obtained admissions s 90)",
            "ss 97-98 — Tendency and coincidence evidence (admissible only if significant probative value substantially outweighs prejudice; s 97A for child sexual offence proceedings — NSW/VIC/ACT)",
            "ss 101-101A — Further restrictions on tendency/coincidence in criminal proceedings (striking similarity)",
            "s 137 — Discretion to EXCLUDE prosecution evidence if probative value outweighed by danger of unfair prejudice (MANDATORY exclusion in criminal proceedings)",
            "s 138 — Discretion to EXCLUDE improperly or illegally obtained evidence (balancing test)",
            "s 139 — Cautioning requirements for admission of statements by suspects",
            "Part 4.3 — Privilege (client legal privilege s 118-119; privilege against self-incrimination s 128)",
        ],
    },
    "nsw": {
        "act": "Evidence Act 1995 (NSW)",
        "type": "uniform",
        "key_local_provisions": [
            "s 97A — Tendency evidence in child sexual offence proceedings (2020 amendment — lowered threshold)",
            "s 293 Criminal Procedure Act 1986 — Restriction on evidence of sexual reputation/experience (complainant protections)",
        ],
        "last_verified": "2026-02",
    },
    "vic": {
        "act": "Evidence Act 2008 (Vic)",
        "type": "uniform",
        "key_local_provisions": [
            "s 97A — Tendency evidence in child sexual offence proceedings",
            "Jury Directions Act 2015 (Vic) — Directions on evidence (tendency, delay, reliability, Murray direction)",
        ],
        "last_verified": "2026-02",
    },
    "qld": {
        "act": "Evidence Act 1977 (Qld)",
        "type": "non-uniform",
        "note": "Queensland has NOT adopted the uniform evidence law. It retains its own distinct evidence regime.",
        "key_provisions": [
            "Part 2 — Witnesses (competency, compellability, oaths)",
            "Part 2A — Evidence of special witnesses (children, vulnerable persons)",
            "s 93 — Admissibility of statements in documents",
            "s 93A — Admissibility of business records",
            "Part 3 — Documentary evidence",
            "s 130 — Privilege against self-incrimination",
            "Note: Queensland uses common law rules for tendency/similar fact evidence (Pfennig v The Queen (1995), HML v The Queen (2008)), not statutory provisions",
        ],
        "last_verified": "2026-02",
    },
    "sa": {
        "act": "Evidence Act 1929 (SA)",
        "type": "non-uniform",
        "note": "South Australia has NOT adopted the uniform evidence law. Recent 2024 amendments relate to Aboriginal evidence.",
        "key_provisions": [
            "Part 3 — Witnesses (competency, compellability)",
            "Part 6 — Evidence in sexual offence cases",
            "Part 7 — Tendency and coincidence evidence (SA-specific provisions — uses propensity test)",
            "s 34P — Audio visual evidence from vulnerable witnesses",
            "2024 amendments — Aboriginal traditional law/customs evidence",
        ],
        "last_verified": "2026-02",
    },
    "wa": {
        "act": "Evidence Act 1906 (WA)",
        "type": "non-uniform",
        "note": "Western Australia has NOT adopted the uniform evidence law. A 2025 Bill proposes replacement with uniform evidence laws.",
        "key_provisions": [
            "Part II — Witnesses (competency, compellability)",
            "Part III — Documentary evidence",
            "Part IV — Various evidentiary matters",
            "s 36A-36BD — Evidence of children and vulnerable witnesses",
            "Note: WA uses common law rules for tendency/similar fact evidence",
        ],
        "last_verified": "2026-02",
    },
    "tas": {
        "act": "Evidence Act 2001 (Tas)",
        "type": "uniform",
        "key_local_provisions": [
            "Mirrors Commonwealth Evidence Act 1995 including hearsay, tendency/coincidence, and exclusionary discretions",
        ],
        "last_verified": "2026-02",
    },
    "nt": {
        "act": "Evidence (National Uniform Legislation) Act 2011 (NT)",
        "type": "uniform",
        "key_local_provisions": [
            "Adopted uniform evidence law in 2011",
        ],
        "last_verified": "2026-02",
    },
    "act": {
        "act": "Evidence Act 2011 (ACT)",
        "type": "uniform",
        "key_local_provisions": [
            "Mirrors Commonwealth Evidence Act 1995",
        ],
        "last_verified": "2026-02",
    },
    "federal": {
        "act": "Evidence Act 1995 (Cth)",
        "type": "uniform",
        "note": "The source Act for the uniform evidence law. Applies in federal courts and ACT courts.",
        "last_verified": "2026-02",
    },
    "common_evidence_appeal_grounds": [
        "Wrongful admission of tendency/coincidence evidence — failure to apply s 97/98 threshold (uniform) or common law Pfennig test (QLD/WA/SA)",
        "Wrongful admission of hearsay evidence — failure to apply hearsay exclusion or establish exception",
        "Wrongful exclusion of defence evidence — refusal to admit relevant evidence without proper basis",
        "Failure to exclude unfairly prejudicial evidence under s 137 (uniform) or common law discretion",
        "Admission of improperly or illegally obtained evidence — failure to apply s 138 balancing test or common law principles",
        "Wrongful admission of confession/admission — involuntary (s 84), unreliable (s 85), or improperly obtained (s 90)",
        "Improper cross-examination of complainant in sexual offence proceedings",
        "Failure to warn jury about unreliable evidence (Longman/Markuleski directions)",
    ],
}
