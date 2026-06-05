#  — Appeal (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



# Appeal procedural framework for each state
APPEAL_FRAMEWORK = {
    "nsw": {
        "legislation": "Criminal Appeal Act 1912 (NSW)",
        "court": "Court of Criminal Appeal (NSW)",
        "time_limits": {
            "notice_of_intention": "28 days from conviction/sentence",
            "grounds_of_appeal": "As directed by Registrar"
        },
        "forms": [
            {"form": "Form 74C", "purpose": "Notice of Intention to Appeal"},
            {"form": "Form 74D", "purpose": "Notice of Appeal (Conviction)"},
            {"form": "Form 74E", "purpose": "Notice of Appeal (Sentence)"}
        ]
    },
    "vic": {
        "legislation": "Criminal Procedure Act 2009 (Vic)",
        "court": "Court of Appeal (Supreme Court of Victoria)",
        "time_limits": {
            "notice_of_appeal": "28 days from sentence",
            "application_for_leave": "28 days from sentence"
        },
        "forms": [
            {"form": "Form 6-2A", "purpose": "Notice of Application for Leave to Appeal Against Conviction"},
            {"form": "Form 6-2C", "purpose": "Notice of Application for Leave to Appeal Against Sentence"}
        ]
    },
    "qld": {
        "legislation": "Criminal Code Act 1899 (Qld) Part 10",
        "court": "Court of Appeal (Supreme Court of Queensland)",
        "time_limits": {
            "notice_of_appeal": "1 month from conviction/sentence"
        },
        "forms": [
            {"form": "Form 26", "purpose": "Notice of Appeal or Application for Leave to Appeal (Conviction or Sentence)"},
            {"form": "Form 28", "purpose": "Notice of Application for Extension of Time to Appeal"}
        ]
    },
    "sa": {
        "legislation": "Criminal Law Consolidation Act 1935 (SA) Part 11",
        "court": "South Australian Court of Appeal (established 1 January 2021 under Supreme Court (Court of Appeal) Amendment Act 2019)",
        "time_limits": {
            "notice_of_appeal": "21 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "wa": {
        "legislation": "Criminal Appeals Act 2004 (WA)",
        "court": "Court of Appeal (Supreme Court of Western Australia)",
        "time_limits": {
            "notice_of_appeal_summary": "28 days from conviction/sentence (appeals from Magistrates Court)",
            "notice_of_appeal_indictable": "21 days from conviction/sentence (appeals from District/Supreme Court to Court of Appeal)"
        },
        "forms": [
            {"form": "Form 1", "purpose": "Notice of Appeal"}
        ]
    },
    "tas": {
        "legislation": "Criminal Code Act 1924 (Tas) Part XA",
        "court": "Court of Criminal Appeal (Tasmania)",
        "time_limits": {
            "notice_of_appeal": "14 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "nt": {
        "legislation": "Local Court (Criminal Procedure) Act 1928 (NT) Part VI; Supreme Court Rules (NT) for Court of Criminal Appeal",
        "court": "Court of Criminal Appeal (NT)",
        "time_limits": {
            "notice_of_appeal": "28 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal from Local Court to Supreme Court"},
            {"form": "Form 86G", "purpose": "Application for Leave to Appeal to Court of Criminal Appeal"}
        ]
    },
    "act": {
        "legislation": "Supreme Court Act 1933 (ACT) Part 2A (Court of Appeal, ss 37E-37S); Court Procedures Rules 2006 (ACT)",
        "court": "Court of Appeal (ACT)",
        "time_limits": {
            "notice_of_appeal": "28 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "federal": {
        "legislation": "Judiciary Act 1903 (Cth) Part X; High Court of Australia Act 1979 (Cth); Federal Court of Australia Act 1976 (Cth)",
        "court": "High Court of Australia (appeals via state/territory Court of Criminal Appeal; Full Federal Court for limited federal matters)",
        "special_leave": "Required for all appeals to the High Court (s 35A Judiciary Act 1903)",
        "note": "Federal criminal offences are tried in state/territory courts under Judiciary Act 1903 Part X. Appeals follow the appellate pathway of the state/territory where the trial occurred. Further appeal to the High Court requires special leave. The Federal Court of Australia has limited criminal jurisdiction in specific statutory contexts (e.g., contempt, regulatory prosecutions)."
    }
}

APPEAL_GROUNDS_ACCESSIBILITY = {
    "unsafe_verdict": {
        "plain_language": "The jury's verdict was wrong — the evidence at trial was not strong enough to prove guilt beyond reasonable doubt.",
        "who_can_use": "Conviction appeal only",
        "leave_required": "Yes — leave to appeal required in most jurisdictions",
        "typical_threshold": "The appellate court must be satisfied the jury 'must have entertained a doubt' on all the evidence (M v The Queen (1994))",
    },
    "sentencing_error": {
        "plain_language": "The sentence was too harsh (manifestly excessive) or the judge made a specific legal error in deciding the sentence.",
        "who_can_use": "Sentence appeal only (may be brought by accused OR prosecution)",
        "leave_required": "Yes — leave to appeal required",
        "typical_threshold": "Must show the sentence was outside the range open to a reasonable sentencing judge, or identify a specific legal error in reasoning",
    },
    "misdirection": {
        "plain_language": "The judge gave the jury wrong or misleading instructions about the law they had to apply.",
        "who_can_use": "Conviction appeal only",
        "leave_required": "No — appeal as of right on question of law",
        "typical_threshold": "Must show the direction was wrong in law and the error was material (not merely theoretical)",
    },
    "fresh_evidence": {
        "plain_language": "Important new evidence has come to light after the trial that was not available at the time, and it could have changed the outcome.",
        "who_can_use": "Conviction appeal only",
        "leave_required": "Yes — leave to appeal required",
        "typical_threshold": "Evidence must be (1) fresh (not available with reasonable diligence at trial), (2) credible, and (3) capable of producing a different verdict",
    },
    "prosecution_misconduct": {
        "plain_language": "The prosecution acted unfairly during the trial — for example, hiding evidence from the defence or making improper statements to the jury.",
        "who_can_use": "Conviction appeal (occasionally sentence appeal if misconduct affected sentencing submissions)",
        "leave_required": "Depends on nature — may be as of right if framed as question of law",
        "typical_threshold": "Must show the misconduct was material and caused a miscarriage of justice",
    },
    "ineffective_counsel": {
        "plain_language": "The defence lawyer made serious errors that affected the outcome of the trial — for example, failing to call an important witness or failing to object to inadmissible evidence.",
        "who_can_use": "Conviction appeal only",
        "leave_required": "Yes — leave to appeal required. Extremely high threshold.",
        "typical_threshold": "Must show counsel's errors deprived the accused of a chance of acquittal that was 'fairly open' (TKWJ v The Queen). Requires affidavit from accused and usually a response from trial counsel.",
    },
    "procedural_error": {
        "plain_language": "A serious procedural mistake was made during the trial — for example, important evidence was wrongly admitted or excluded, or the jury was improperly selected.",
        "who_can_use": "Conviction appeal only",
        "leave_required": "Depends — may be as of right if framed as question of law",
        "typical_threshold": "Must show the procedural error was material to the outcome",
    },
    "jury_irregularity": {
        "plain_language": "Something went wrong with the jury — for example, a juror had a conflict of interest, the jury received improper information, or there was jury misconduct.",
        "who_can_use": "Conviction appeal only",
        "leave_required": "Depends — may be as of right if irregularity is established",
        "typical_threshold": "Must show actual irregularity affecting the verdict, not merely speculation",
    },
    "miscarriage_of_justice": {
        "plain_language": "The trial was fundamentally unfair in a way that means the conviction cannot be relied upon — this is the broadest ground and can capture errors not covered by other specific grounds.",
        "who_can_use": "Conviction appeal (sometimes sentence appeal)",
        "leave_required": "Yes — leave to appeal required",
        "typical_threshold": "Must show a departure from accepted standards of fairness that was material to the outcome",
    },
    "constitutional_violation": {
        "plain_language": "A constitutional right was breached during the trial — for example, the right to trial by jury under s 80 of the Constitution, or the right not to be tried twice for the same offence.",
        "who_can_use": "Either conviction or sentence appeal",
        "leave_required": "Depends on the constitutional issue — may be as of right on a question of law",
        "typical_threshold": "Rarely the operative pathway in state criminal appeals. Consider reframing under miscarriage of justice or procedural unfairness.",
    },
}
