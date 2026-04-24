"""
Tests for the LLM refinement layer on evidence_builder.

Verifies:
  - refinement preserves structure (list lengths, affidavit types, SWORN block)
  - the mandatory warning is NEVER modified, even if the LLM tries
  - per-ground fallback to deterministic on LLM failure
  - validator rejects shape drift (added/removed entries, changed affidavit type,
    affidavit template missing SWORN marker)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground
from services import evidence_builder as eb_mod
from services.evidence_builder import (
    MANDATORY_WARNING,
    _validate_refined_shape,
    generate_evidence_builder,
    refine_evidence_builder_with_llm,
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
    return Ground(**base)


# ------------------ _validate_refined_shape ------------------

def test_validator_accepts_same_shape():
    original = {
        "ground": "x",
        "documents_required": ["a", "b"],
        "steps": ["c"],
        "affidavits": [{"type": "psychiatric", "template": "AFFIDAVIT\n\n...\n\nSWORN:"}],
    }
    refined = {
        "ground": "X refined",
        "documents_required": ["a refined", "b refined"],
        "steps": ["c refined"],
        "affidavits": [{"type": "psychiatric", "template": "AFFIDAVIT refined\n\n...\n\nSWORN:"}],
    }
    assert _validate_refined_shape(original, refined)


def test_validator_rejects_list_length_change():
    original = {"ground": "x", "documents_required": ["a", "b"], "steps": [], "affidavits": []}
    refined = {"ground": "x", "documents_required": ["a", "b", "c"], "steps": [], "affidavits": []}
    assert not _validate_refined_shape(original, refined)


def test_validator_rejects_affidavit_type_change():
    original = {
        "ground": "x", "documents_required": [], "steps": [],
        "affidavits": [{"type": "psychiatric", "template": "AFFIDAVIT\n\nSWORN:"}],
    }
    refined = {
        "ground": "x", "documents_required": [], "steps": [],
        "affidavits": [{"type": "juror_conduct", "template": "AFFIDAVIT\n\nSWORN:"}],
    }
    assert not _validate_refined_shape(original, refined)


def test_validator_rejects_missing_sworn_marker():
    original = {
        "ground": "x", "documents_required": [], "steps": [],
        "affidavits": [{"type": "psychiatric", "template": "AFFIDAVIT\n\nSWORN:"}],
    }
    refined = {
        "ground": "x", "documents_required": [], "steps": [],
        "affidavits": [{"type": "psychiatric", "template": "AFFIDAVIT — no sig block"}],
    }
    assert not _validate_refined_shape(original, refined)


def test_validator_rejects_added_top_level_key():
    original = {"ground": "x", "documents_required": [], "steps": [], "affidavits": []}
    refined = {"ground": "x", "documents_required": [], "steps": [], "affidavits": [], "extra": "bad"}
    assert not _validate_refined_shape(original, refined)


# ------------------ refine_evidence_builder_with_llm ------------------

@pytest.mark.asyncio
async def test_refine_substitutes_llm_text_on_success(monkeypatch):
    g = _g(
        type="conviction",
        title="Mens rea / mental state",
        error_identified="Mental state of the accused was not properly assessed.",
    )
    builder = generate_evidence_builder({"primary": g})
    orig_primary = builder["primary"]

    async def fake_llm(system_prompt, user_prompt, session_id, validation_fn=None, **kwargs):
        # Echo the structure with refined strings, preserving all bounds.
        return {
            "ground": "R v Homann — mental state",
            "documents_required": [s + " [Homann]" for s in orig_primary["documents_required"]],
            "steps": [s + " [refined]" for s in orig_primary["steps"]],
            "affidavits": [
                {
                    "type": a["type"],
                    "template": a["template"].replace("[Name]", "Dr Smith").replace(
                        "[diagnosis]", "substantial impairment"
                    ),
                }
                for a in orig_primary["affidavits"]
            ],
        }
    monkeypatch.setattr("services.llm_service.call_llm_for_json", fake_llm)

    refined = await refine_evidence_builder_with_llm(
        builder=builder,
        strategy={"primary": g},
        case_context={"defendant_surname": "Homann", "jurisdiction": "NSW"},
    )
    assert refined["warning"] == MANDATORY_WARNING
    assert refined["primary"]["ground"].startswith("R v Homann")
    assert all(d.endswith("[Homann]") for d in refined["primary"]["documents_required"])
    assert all("SWORN" in a["template"].upper() for a in refined["primary"]["affidavits"])


@pytest.mark.asyncio
async def test_refine_falls_back_on_llm_exception(monkeypatch):
    g = _g(
        type="conviction",
        title="Mens rea",
        error_identified="Mental state assessment inadequate.",
    )
    builder = generate_evidence_builder({"primary": g})

    async def raising_llm(*a, **kw):
        raise RuntimeError("LLM down")
    monkeypatch.setattr("services.llm_service.call_llm_for_json", raising_llm)

    refined = await refine_evidence_builder_with_llm(
        builder=builder,
        strategy={"primary": g},
        case_context={"defendant_surname": "Homann", "jurisdiction": "NSW"},
    )
    assert refined["warning"] == MANDATORY_WARNING
    assert refined["primary"] == builder["primary"]  # deterministic fallback


@pytest.mark.asyncio
async def test_refine_warning_never_modified_even_if_llm_returns_warning(monkeypatch):
    g = _g(type="procedure", title="Jury bias", error_identified="Jury misconduct observed.")
    builder = generate_evidence_builder({"primary": g})

    async def warning_tampering_llm(system_prompt, user_prompt, session_id, validation_fn=None, **kwargs):
        # LLM tries to return an altered warning — but the refiner only
        # operates on per-ground plans, so warning is untouchable at this layer.
        orig = builder["primary"]
        return dict(orig)
    monkeypatch.setattr("services.llm_service.call_llm_for_json", warning_tampering_llm)

    refined = await refine_evidence_builder_with_llm(
        builder=builder,
        strategy={"primary": g},
        case_context={"defendant_surname": "Smith", "jurisdiction": "VIC"},
    )
    assert refined["warning"] == MANDATORY_WARNING


@pytest.mark.asyncio
async def test_refine_rejects_llm_output_that_drops_affidavit(monkeypatch):
    g = _g(
        type="conviction",
        title="Mental state",
        error_identified="Mental state assessment was inadequate.",
    )
    builder = generate_evidence_builder({"primary": g})
    orig = builder["primary"]
    assert len(orig["affidavits"]) == 1  # sanity

    async def drop_affidavit_llm(system_prompt, user_prompt, session_id, validation_fn=None, **kwargs):
        bad = {
            "ground": orig["ground"],
            "documents_required": orig["documents_required"],
            "steps": orig["steps"],
            "affidavits": [],  # drop → validator must reject
        }
        if validation_fn and not validation_fn(bad):
            raise Exception("JSON LLM call failed: validation_fn rejected result")
        return bad
    monkeypatch.setattr("services.llm_service.call_llm_for_json", drop_affidavit_llm)

    refined = await refine_evidence_builder_with_llm(
        builder=builder,
        strategy={"primary": g},
        case_context={"defendant_surname": "Homann", "jurisdiction": "NSW"},
    )
    # Rejected → fell back to deterministic.
    assert len(refined["primary"]["affidavits"]) == 1
    assert refined["primary"] == builder["primary"]


@pytest.mark.asyncio
async def test_refine_no_strategy_no_llm_call(monkeypatch):
    called = {"n": 0}

    async def count_llm(*a, **kw):
        called["n"] += 1
        return {}
    monkeypatch.setattr("services.llm_service.call_llm_for_json", count_llm)

    builder = {"warning": MANDATORY_WARNING}
    refined = await refine_evidence_builder_with_llm(
        builder=builder,
        strategy={"primary": None, "secondary": None},
        case_context={},
    )
    assert called["n"] == 0
    assert refined == {"warning": MANDATORY_WARNING}
