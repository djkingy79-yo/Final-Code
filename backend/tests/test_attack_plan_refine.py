"""
Tests for the LLM refinement layer on attack_plan.

Verifies:
  - refinement preserves the deterministic skeleton (no new keys, same list
    shapes, no invented grounds)
  - per-ground fallback to deterministic text on LLM failure
  - bounded validation rejects shape drift
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground
from services import attack_plan
from services.attack_plan import (
    _validate_refined_shape,
    generate_attack_plan,
    refine_attack_plan_with_llm,
)


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
    g = Ground(**base)
    g.record_support = "partial"
    g.crown_strength = "moderate"
    g.proviso_risk = "low"
    return g


# ------------------ _validate_refined_shape ------------------

def test_validator_accepts_same_keys_same_types():
    original = {
        "title": "x", "strategy": "y", "crown_response": "z",
        "counter_strategy": "q",
        "evidence_gaps": ["a"], "required_material": ["b"], "next_steps": ["c"],
    }
    refined = {k: (v if isinstance(v, list) else v + "!") for k, v in original.items()}
    assert _validate_refined_shape(original, refined)


def test_validator_rejects_new_keys():
    original = {"strategy": "a"}
    refined = {"strategy": "b", "injected_field": "bad"}
    assert not _validate_refined_shape(original, refined)


def test_validator_rejects_list_becoming_string():
    original = {"evidence_gaps": ["a", "b"]}
    refined = {"evidence_gaps": "a, b"}
    assert not _validate_refined_shape(original, refined)


def test_validator_rejects_string_becoming_list():
    original = {"strategy": "s"}
    refined = {"strategy": ["s"]}
    assert not _validate_refined_shape(original, refined)


def test_validator_rejects_non_string_list_items():
    original = {"next_steps": ["a"]}
    refined = {"next_steps": [{"nested": "bad"}]}
    assert not _validate_refined_shape(original, refined)


# ------------------ refine_attack_plan_with_llm ------------------

@pytest.mark.asyncio
async def test_refine_substitutes_llm_text_on_success(monkeypatch):
    g = _g(type="conviction", title="Mens rea", error_identified="Directions inadequate.")
    plan = generate_attack_plan({"primary": g})

    async def fake_llm(system_prompt, user_prompt, session_id, **kwargs):
        # Echo the plan back with slightly refined strings, preserving shape
        original_plan = plan["primary"]
        return {
            "title": original_plan["title"],
            "strategy": "[REFINED] " + original_plan["strategy"],
            "evidence_gaps": ["[REFINED] " + g for g in original_plan["evidence_gaps"]] or [],
            "required_material": original_plan["required_material"],
            "crown_response": "[REFINED] " + original_plan["crown_response"],
            "counter_strategy": "[REFINED] " + original_plan["counter_strategy"],
            "next_steps": original_plan["next_steps"],
        }
    monkeypatch.setattr("services.llm_service.call_llm_for_json", fake_llm)

    refined = await refine_attack_plan_with_llm(
        plan=plan,
        strategy={"primary": g},
        case_context={"defendant_surname": "Homann", "jurisdiction": "NSW"},
    )
    assert refined["primary"]["strategy"].startswith("[REFINED] ")
    assert refined["primary"]["crown_response"].startswith("[REFINED] ")
    assert refined["primary"]["title"] == plan["primary"]["title"]


@pytest.mark.asyncio
async def test_refine_falls_back_on_llm_exception(monkeypatch):
    g = _g(type="conviction", title="Mens rea", error_identified="Directions inadequate.")
    plan = generate_attack_plan({"primary": g})

    async def raising_llm(*a, **kw):
        raise RuntimeError("LLM down")
    monkeypatch.setattr("services.llm_service.call_llm_for_json", raising_llm)

    refined = await refine_attack_plan_with_llm(
        plan=plan,
        strategy={"primary": g},
        case_context={"defendant_surname": "Homann", "jurisdiction": "NSW"},
    )
    # Deterministic text preserved on failure.
    assert refined["primary"]["strategy"] == plan["primary"]["strategy"]
    assert refined["primary"]["crown_response"] == plan["primary"]["crown_response"]


@pytest.mark.asyncio
async def test_refine_rejects_llm_output_that_adds_new_key(monkeypatch):
    g = _g(type="conviction", title="Mens rea", error_identified="Directions inadequate.")
    plan = generate_attack_plan({"primary": g})
    original = plan["primary"]

    async def bad_llm(system_prompt, user_prompt, session_id, validation_fn=None, **kwargs):
        shape_drift = dict(original)
        shape_drift["viability_override"] = "arguable_strong"  # forbidden key
        # validation_fn is what the attack_plan module passes in — trigger the
        # production validator to reject this output.
        if validation_fn and not validation_fn(shape_drift):
            raise Exception("JSON LLM call failed: validation_fn rejected result")
        return shape_drift
    monkeypatch.setattr("services.llm_service.call_llm_for_json", bad_llm)

    refined = await refine_attack_plan_with_llm(
        plan=plan,
        strategy={"primary": g},
        case_context={"defendant_surname": "Homann", "jurisdiction": "NSW"},
    )
    # Rejected output → fell back to deterministic.
    assert "viability_override" not in refined["primary"]
    assert refined["primary"]["strategy"] == plan["primary"]["strategy"]


@pytest.mark.asyncio
async def test_refine_no_strategy_no_llm_call(monkeypatch):
    called = {"n": 0}

    async def count_llm(*a, **kw):
        called["n"] += 1
        return {}
    monkeypatch.setattr("services.llm_service.call_llm_for_json", count_llm)

    refined = await refine_attack_plan_with_llm(
        plan={},
        strategy={"primary": None, "secondary": None},
        case_context={},
    )
    assert called["n"] == 0
    assert refined == {}


@pytest.mark.asyncio
async def test_refine_only_primary_still_works(monkeypatch):
    g = _g(type="sentence", title="Manifest excess", viability="arguable_moderate")
    plan = generate_attack_plan({"primary": g})

    async def fake_llm(system_prompt, user_prompt, session_id, **kwargs):
        return dict(plan["primary"], strategy="REFINED SENTENCE STRATEGY")
    monkeypatch.setattr("services.llm_service.call_llm_for_json", fake_llm)

    refined = await refine_attack_plan_with_llm(
        plan=plan,
        strategy={"primary": g, "secondary": None},
        case_context={"defendant_surname": "Smith", "jurisdiction": "VIC"},
    )
    assert refined["primary"]["strategy"] == "REFINED SENTENCE STRATEGY"
    assert "secondary" not in refined
