"""
Regression tests for the P2 refactor that split offence_framework.py into
/app/backend/frameworks/ submodules. Locks in:

  - Every expected public symbol is reachable from BOTH
    `offence_framework` (back-compat shim) AND `frameworks` (new package).
  - Symbols are identity-equal (same object) between the two import paths.
  - `frameworks.__all__` covers every legacy symbol so `from
    offence_framework import *` still works.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import offence_framework as of  # noqa: E402
import frameworks as fw  # noqa: E402


EXPECTED_SYMBOLS = [
    # jurisdictions
    "LEGISLATION_CURRENCY", "AUSTRALIAN_STATES",
    # procedure + mens rea
    "INDICTABLE_PROCEDURE_FLOW", "HYBRID_PROCEDURE_FLOW", "SUMMARY_PROCEDURE_FLOW", "MENS_REA_FRAMEWORK",
    # offences
    "OFFENCE_CATEGORIES",
    # common grounds
    "COMMON_APPEAL_GROUNDS",
    # human rights
    "HUMAN_RIGHTS_FRAMEWORK",
    # appeal
    "APPEAL_FRAMEWORK", "APPEAL_GROUNDS_ACCESSIBILITY",
    # state criminal frameworks
    "NSW_CRIMINAL_FRAMEWORK", "VIC_CRIMINAL_FRAMEWORK", "QLD_CRIMINAL_FRAMEWORK",
    "SA_CRIMINAL_FRAMEWORK", "WA_CRIMINAL_FRAMEWORK", "TAS_CRIMINAL_FRAMEWORK",
    "NT_CRIMINAL_FRAMEWORK", "ACT_CRIMINAL_FRAMEWORK",
    # federal
    "FEDERAL_CRIMINAL_FRAMEWORK", "FEDERAL_FAULT_ELEMENTS", "PROCEEDS_OF_CRIME_FRAMEWORK",
    # recent updates / sentencing / evidence / mental impairment / cases
    "RECENT_LEGISLATION_UPDATES", "SENTENCING_FRAMEWORK", "EVIDENCE_FRAMEWORK",
    "MENTAL_IMPAIRMENT_FRAMEWORK", "LANDMARK_CASES",
]


def test_every_symbol_reachable_both_ways():
    for sym in EXPECTED_SYMBOLS:
        assert hasattr(of, sym), f"offence_framework missing {sym}"
        assert hasattr(fw, sym), f"frameworks missing {sym}"


def test_symbols_are_identity_equal():
    for sym in EXPECTED_SYMBOLS:
        a = getattr(of, sym)
        b = getattr(fw, sym)
        assert a is b, f"{sym}: identity mismatch between offence_framework and frameworks"


def test_frameworks_all_covers_every_symbol():
    for sym in EXPECTED_SYMBOLS:
        assert sym in fw.__all__, f"{sym} missing from frameworks.__all__"


def test_star_import_still_works():
    # Emulate `from offence_framework import *` — must bring in all public names.
    ns = {}
    exec("from offence_framework import *", ns)
    for sym in EXPECTED_SYMBOLS:
        assert sym in ns, f"star-import from offence_framework missing {sym}"


def test_critical_data_intact_after_split():
    # Spot-check the most important structures.
    assert len(of.OFFENCE_CATEGORIES) == 18
    assert len(of.INDICTABLE_PROCEDURE_FLOW) == 13
    assert "intention" in of.MENS_REA_FRAMEWORK
    assert "nsw" in of.AUSTRALIAN_STATES
    assert of.OFFENCE_CATEGORIES["homicide"]["procedural_flow"] is of.INDICTABLE_PROCEDURE_FLOW
