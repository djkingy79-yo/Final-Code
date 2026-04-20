# DO NOT UNDO — frameworks package (P2 refactor 2026-02-14).
"""
Legal framework package — previously a single 4000-line file.
Every symbol is re-exported here so existing imports continue to work:
    from offence_framework import OFFENCE_CATEGORIES    # still works
    from frameworks import OFFENCE_CATEGORIES           # preferred
"""

from .jurisdictions import (
    LEGISLATION_CURRENCY,
    AUSTRALIAN_STATES,
)

from .procedure import (
    INDICTABLE_PROCEDURE_FLOW,
    HYBRID_PROCEDURE_FLOW,
    SUMMARY_PROCEDURE_FLOW,
    MENS_REA_FRAMEWORK,
)

from .offences import (
    OFFENCE_CATEGORIES,
)

from .common_grounds import (
    COMMON_APPEAL_GROUNDS,
)

from .human_rights import (
    HUMAN_RIGHTS_FRAMEWORK,
)

from .appeal import (
    APPEAL_FRAMEWORK,
    APPEAL_GROUNDS_ACCESSIBILITY,
)

from .states import (
    NSW_CRIMINAL_FRAMEWORK,
    VIC_CRIMINAL_FRAMEWORK,
    QLD_CRIMINAL_FRAMEWORK,
    SA_CRIMINAL_FRAMEWORK,
    WA_CRIMINAL_FRAMEWORK,
    TAS_CRIMINAL_FRAMEWORK,
    NT_CRIMINAL_FRAMEWORK,
    ACT_CRIMINAL_FRAMEWORK,
)

from .federal import (
    FEDERAL_CRIMINAL_FRAMEWORK,
    FEDERAL_FAULT_ELEMENTS,
    PROCEEDS_OF_CRIME_FRAMEWORK,
)

from .recent_updates import (
    RECENT_LEGISLATION_UPDATES,
)

from .sentencing import (
    SENTENCING_FRAMEWORK,
)

from .evidence import (
    EVIDENCE_FRAMEWORK,
)

from .mental_impairment import (
    MENTAL_IMPAIRMENT_FRAMEWORK,
)

from .landmark_cases import (
    LANDMARK_CASES,
)

__all__ = [
    "LEGISLATION_CURRENCY",
    "AUSTRALIAN_STATES",
    "INDICTABLE_PROCEDURE_FLOW",
    "HYBRID_PROCEDURE_FLOW",
    "SUMMARY_PROCEDURE_FLOW",
    "MENS_REA_FRAMEWORK",
    "OFFENCE_CATEGORIES",
    "COMMON_APPEAL_GROUNDS",
    "HUMAN_RIGHTS_FRAMEWORK",
    "APPEAL_FRAMEWORK",
    "APPEAL_GROUNDS_ACCESSIBILITY",
    "NSW_CRIMINAL_FRAMEWORK",
    "VIC_CRIMINAL_FRAMEWORK",
    "QLD_CRIMINAL_FRAMEWORK",
    "SA_CRIMINAL_FRAMEWORK",
    "WA_CRIMINAL_FRAMEWORK",
    "TAS_CRIMINAL_FRAMEWORK",
    "NT_CRIMINAL_FRAMEWORK",
    "ACT_CRIMINAL_FRAMEWORK",
    "FEDERAL_CRIMINAL_FRAMEWORK",
    "FEDERAL_FAULT_ELEMENTS",
    "PROCEEDS_OF_CRIME_FRAMEWORK",
    "RECENT_LEGISLATION_UPDATES",
    "SENTENCING_FRAMEWORK",
    "EVIDENCE_FRAMEWORK",
    "MENTAL_IMPAIRMENT_FRAMEWORK",
    "LANDMARK_CASES",
]
