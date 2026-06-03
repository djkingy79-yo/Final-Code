#  — Common Grounds (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



# Common appeal grounds applicable across all offences
COMMON_APPEAL_GROUNDS = [
    {
        "ground": "Unsafe and unsatisfactory verdict",
        "description": "The verdict was unreasonable or cannot be supported by the evidence",
        "applicable_to": "all"
    },
    {
        "ground": "Misdirection by trial judge",
        "description": "The judge gave incorrect or inadequate directions to the jury on the law",
        "applicable_to": "all"
    },
    {
        "ground": "Fresh evidence",
        "description": "New evidence has emerged that was not available at trial and could have affected the verdict",
        "applicable_to": "all"
    },
    {
        "ground": "Procedural unfairness",
        "description": "The trial was conducted unfairly or there was a denial of natural justice",
        "applicable_to": "all"
    },
    {
        "ground": "Ineffective assistance of counsel",
        "description": "Defence counsel's conduct was so deficient that it affected the outcome",
        "applicable_to": "all"
    },
    {
        "ground": "Wrongful admission of evidence",
        "description": "Evidence was admitted that should have been excluded",
        "applicable_to": "all"
    },
    {
        "ground": "Wrongful exclusion of evidence",
        "description": "Evidence was excluded that should have been admitted",
        "applicable_to": "all"
    },
    {
        "ground": "Judicial bias or misconduct",
        "description": "The judge showed bias or behaved inappropriately during the trial",
        "applicable_to": "all"
    },
    {
        "ground": "Jury irregularity",
        "description": "There was misconduct or irregularity in the jury's conduct or deliberations",
        "applicable_to": "all"
    },
    {
        "ground": "Sentence manifestly excessive",
        "description": "The sentence imposed was unreasonably harsh given the circumstances",
        "applicable_to": "all"
    },
    {
        "ground": "Error in sentencing discretion",
        "description": "The judge made an error in exercising sentencing discretion",
        "applicable_to": "all"
    },
    {
        "ground": "Prosecution misconduct",
        "description": "The prosecution acted improperly during the trial",
        "applicable_to": "all"
    }
]
