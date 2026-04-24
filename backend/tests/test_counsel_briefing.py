"""
Tests for services/attack_plan.py and services/evidence_builder.py.
Counsel feedback 23 Feb 2026 — counsel attack plan + evidence builder.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground
from services.attack_plan import generate_attack_plan
from services.evidence_builder import generate_evidence_builder, MANDATORY_WARNING


def _g(**overrides) -> Ground:
    base = dict(
        title="Test",
        type="conviction",
        pathway="",
        viability="arguable_moderate",
        supporting_evidence=[],
        relevant_law_sections=[],
        authorities=[],
    )
    base.update(overrides)
    return Ground(**base)


# -------- attack_plan --------

def test_attack_plan_empty_strategy():
    assert generate_attack_plan({"primary": None, "secondary": None}) == {}


def test_attack_plan_primary_conviction_mens_rea():
    g = _g(
        type="conviction",
        title="Unsafe verdict: mens rea",
        error_identified="Mens rea directions were inadequate.",
    )
    g.record_support = "partial"
    g.crown_strength = "moderate"
    g.proviso_risk = "low"
    plan = generate_attack_plan({"primary": g})
    assert "primary" in plan
    p = plan["primary"]
    assert "mental element" in p["strategy"].lower()
    assert "full trial transcript" in [m.lower() for m in p["required_material"]]
    assert "jury was entitled" in p["crown_response"].lower()
    assert "undermines confidence" in p["counter_strategy"].lower()
    assert any("record" in s.lower() for s in p["next_steps"])


def test_attack_plan_secondary_procedure_strong_crown():
    g = _g(
        type="procedure",
        title="Procedural unfairness — jury separation",
        error_identified="Jury separation concerns.",
    )
    g.record_support = "limited"
    g.crown_strength = "strong"
    plan = generate_attack_plan({"secondary": g})
    s = plan["secondary"]
    assert "procedural fairness" in s["strategy"].lower()
    assert any("limited" in g.lower() for g in s["evidence_gaps"])
    assert "overwhelming" in s["crown_response"].lower()


def test_attack_plan_conviction_high_proviso_uses_weiss_counter():
    g = _g(
        type="conviction",
        title="Unsafe verdict",
        error_identified="Directional error.",
    )
    g.proviso_risk = "high"
    plan = generate_attack_plan({"primary": g})
    assert "proviso" in plan["primary"]["counter_strategy"].lower()
    assert "inevitable" in plan["primary"]["counter_strategy"].lower()


def test_attack_plan_sentence_steps():
    g = _g(type="sentence", title="Manifest excess", viability="arguable_moderate")
    plan = generate_attack_plan({"primary": g})
    p = plan["primary"]
    assert "sentencing discretion" in p["strategy"].lower()
    assert any("sentencing" in s.lower() for s in p["required_material"])
    assert any("comparable" in s.lower() for s in p["next_steps"])


# -------- evidence_builder --------

def test_evidence_builder_always_includes_warning():
    out = generate_evidence_builder({"primary": None, "secondary": None})
    assert out["warning"] == MANDATORY_WARNING


def test_evidence_builder_psychiatric_affidavit_for_mental_ground():
    g = _g(
        type="conviction",
        title="Unsafe verdict: mental state",
        error_identified="Mental state was not properly addressed at trial.",
    )
    out = generate_evidence_builder({"primary": g})
    p = out["primary"]
    assert any("psychiatric" in d.lower() for d in p["documents_required"])
    assert any("psychiatric" in s.lower() for s in p["steps"])
    assert any(a["type"] == "psychiatric" for a in p["affidavits"])
    assert "AFFIDAVIT" in p["affidavits"][0]["template"]


def test_evidence_builder_juror_affidavit_for_jury_ground():
    g = _g(
        type="procedure",
        title="Jury misconduct",
        error_identified="A juror was observed acting improperly during deliberations.",
    )
    out = generate_evidence_builder({"primary": g})
    p = out["primary"]
    assert any("voir dire" in d.lower() for d in p["documents_required"])
    assert any(a["type"] == "juror_conduct" for a in p["affidavits"])


def test_evidence_builder_sentence_steps_no_affidavits():
    g = _g(
        type="sentence",
        title="Manifest excess",
        error_identified="Sentence manifestly excessive; discretion miscarried.",
    )
    out = generate_evidence_builder({"primary": g})
    p = out["primary"]
    assert p["affidavits"] == []
    assert any("sentencing" in d.lower() for d in p["documents_required"])
    assert any("compare" in s.lower() for s in p["steps"])


def test_evidence_builder_primary_and_secondary_both_present():
    g1 = _g(type="conviction", title="Unsafe verdict", error_identified="Mens rea misdirection.")
    g2 = _g(type="procedure", title="Jury integrity", error_identified="Possible juror bias.")
    out = generate_evidence_builder({"primary": g1, "secondary": g2})
    assert "primary" in out and "secondary" in out
    assert out["primary"]["ground"] == "Unsafe verdict"
    assert out["secondary"]["ground"] == "Jury integrity"
