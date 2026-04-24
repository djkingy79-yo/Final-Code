"""
Tests for services/proviso_engine.py and services/barrister_mode.py.
Counsel feedback 23 Feb 2026 — bottom-line: the legal engines must
DRIVE the brief, not sit alongside it.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground
from services.proviso_engine import apply_proviso_engine, case_proviso_summary
from services.barrister_mode import build_strategy_summary


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


# ---------- proviso_engine ----------

def test_proviso_engine_appends_high_reasoning_on_conviction():
    g = _g(type="conviction")
    g.proviso_risk = "high"
    apply_proviso_engine([g])
    assert g.reasoning_trail
    assert any("Weiss v The Queen" in r for r in g.reasoning_trail)
    assert any("dismiss the appeal under the proviso" in r for r in g.reasoning_trail)


def test_proviso_engine_appends_moderate_reasoning():
    g = _g(type="conviction")
    g.proviso_risk = "moderate"
    apply_proviso_engine([g])
    assert any("moderate proviso exposure" in r for r in (g.reasoning_trail or []))


def test_proviso_engine_low_reasoning():
    g = _g(type="conviction")
    g.proviso_risk = "low"
    apply_proviso_engine([g])
    assert any("low proviso exposure" in r for r in (g.reasoning_trail or []))


def test_proviso_engine_skips_non_conviction():
    g = _g(type="sentence")
    g.proviso_risk = "high"
    apply_proviso_engine([g])
    assert g.reasoning_trail is None or all(
        "Weiss" not in r for r in g.reasoning_trail
    )


def test_case_proviso_summary_returns_worst_case():
    g1 = _g(type="conviction"); g1.proviso_risk = "low"
    g2 = _g(type="conviction"); g2.proviso_risk = "moderate"
    g3 = _g(type="conviction"); g3.proviso_risk = "high"
    summary = case_proviso_summary([g1, g2, g3])
    assert summary["risk"] == "high"


def test_case_proviso_summary_no_conviction_ground():
    g = _g(type="sentence")
    summary = case_proviso_summary([g])
    assert summary["risk"] == "n/a"


# ---------- barrister_mode ----------

def test_build_strategy_picks_conviction_primary():
    conv = _g(type="conviction", viability="arguable_strong", title="Mens rea")
    proc = _g(type="procedure", viability="arguable_moderate", title="Procedural")
    sent = _g(type="sentence", viability="arguable_moderate", title="Manifest excess")
    strategy = build_strategy_summary([proc, conv, sent])
    assert strategy["primary"] is conv
    # Secondary must be a different type
    assert strategy["secondary"].type != conv.type


def test_build_strategy_type_priority_breaks_viability_ties():
    conv = _g(type="conviction", viability="arguable_moderate", title="C")
    proc = _g(type="procedure", viability="arguable_moderate", title="P")
    strategy = build_strategy_summary([proc, conv])
    assert strategy["primary"] is conv


def test_build_strategy_abandons_weak_and_requires_development():
    strong_conv = _g(type="conviction", viability="arguable_strong", title="Strong conv")
    weak_proc = _g(type="procedure", viability="weak", title="Weak proc")
    rd_sent = _g(type="sentence", viability="requires_development", title="Speculative sent")
    strategy = build_strategy_summary([strong_conv, weak_proc, rd_sent])
    assert strategy["primary"] is strong_conv
    # Whichever two don't make primary/secondary/tertiary and have
    # weak/requires_development viability should be abandoned.
    abandoned = strategy["abandon"]
    assert all(g.viability in {"weak", "requires_development"} for g in abandoned)


def test_build_strategy_empty_list():
    out = build_strategy_summary([])
    assert out == {"primary": None, "secondary": None, "tertiary": None, "abandon": []}


def test_build_strategy_single_ground_only_primary():
    conv = _g(type="conviction", viability="arguable_strong", title="Single")
    out = build_strategy_summary([conv])
    assert out["primary"] is conv
    assert out["secondary"] is None
    assert out["tertiary"] is None
    assert out["abandon"] == []
