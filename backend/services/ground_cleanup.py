"""
ground_cleanup.py

Jurisdiction-aware cleanup layer applied after:
  1. ground normalisation
  2. realism scoring

Purpose:
  - remove mixed-category remnants from sub-particulars
  - apply final viability uplift where the scoring profile supports it
  - fix liability / mitigation terminology in narrative text
    so liability concepts (s 23A NSW, s 304A QLD, mental impairment, etc.)
    are never misdescribed as sentencing mitigation.

Per counsel feedback 23 Feb 2026 — jurisdiction-aware across all states,
territories and Commonwealth matters.
"""

from __future__ import annotations

from typing import Iterable

from services.ground_normaliser import Ground, SubParticular, normalise


LIABILITY_TERMS = (
    "mens rea",
    "intent",
    "intention",
    "unsafe verdict",
    "unreasonable verdict",
    "substantial impairment",
    "diminished responsibility",
    "mental impairment defence",
    "defence of mental impairment",
    "mental impairment",
    "unsoundness of mind",
    "abnormality of mind",
    "partial defence",
)

SENTENCE_TERMS = (
    "sentencing",
    "sentence",
    "rehabilitation",
    "non-parole",
    "parole",
    "manifestly excessive",
    "manifest excess",
    "mitigation",
    "moral culpability",
    "totality",
)

PROCEDURE_TERMS = (
    "jury",
    "juror",
    "judge-alone",
    "judge alone",
    "mode of trial",
    "pretrial publicity",
    "pre-trial publicity",
    "bias",
    "procedural unfairness",
)

INEFFECTIVE_COUNSEL_TERMS = (
    "ineffective counsel",
    "ineffective assistance",
    "failed to preserve",
    "failed to argue",
    "failure to preserve appellate rights",
    "appellate rights",
    "post-sentencing advice",
    "counsel failed",
)

# Jurisdiction-specific liability concepts that must never be described
# as mere sentencing mitigation.
PARTIAL_DEFENCE_MAP: dict[str, tuple[str, ...]] = {
    "NSW": (
        "s 23a",
        "section 23a",
        "substantial impairment",
        "abnormality of mind",
    ),
    "QLD": (
        "diminished responsibility",
        "section 304a",
        "s 304a",
        "unsoundness of mind",
    ),
    "VIC": (
        "defence of mental impairment",
        "mental impairment",
    ),
    "WA": (
        "unsoundness of mind",
    ),
    "SA": (
        "mental incompetence",
        "mental impairment",
    ),
    "TAS": (
        "insanity",
    ),
    "NT": (
        "mental impairment",
        "criminal responsibility",
    ),
    "ACT": (
        "mental impairment",
    ),
    "CTH": (
        "fault elements",
        "mental impairment",
        "unsoundness of mind",
    ),
}


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    t = normalise(text)
    return any(n in t for n in needles)


def _log(ground: Ground, msg: str) -> None:
    if ground.reasoning_trail is None:
        ground.reasoning_trail = []
    ground.reasoning_trail.append(msg)


def remove_misclassified_subs(ground: Ground) -> Ground:
    """
    Strip sub-particulars that plainly belong to a different pathway.
    Runs regardless of jurisdiction — purely content-based triage.
    """
    if not ground.sub_particulars:
        return ground

    cleaned: list[SubParticular] = []
    dropped: list[str] = []

    for sp in ground.sub_particulars:
        t = normalise(sp.text)
        drop = False

        if ground.type == "conviction":
            if _contains_any(t, SENTENCE_TERMS) or _contains_any(t, INEFFECTIVE_COUNSEL_TERMS):
                drop = True

        elif ground.type == "sentence":
            if _contains_any(t, LIABILITY_TERMS) or _contains_any(t, INEFFECTIVE_COUNSEL_TERMS):
                drop = True

        elif ground.type == "procedure":
            # allow jury / judge-alone; reject sentencing / liability contamination
            if _contains_any(t, SENTENCE_TERMS) or (
                _contains_any(t, LIABILITY_TERMS)
                and not _contains_any(t, PROCEDURE_TERMS)
            ):
                drop = True

        elif ground.type == "ineffective_counsel":
            if (
                _contains_any(t, SENTENCE_TERMS)
                and not _contains_any(t, INEFFECTIVE_COUNSEL_TERMS)
            ):
                drop = True
            if (
                _contains_any(t, LIABILITY_TERMS)
                and not _contains_any(t, INEFFECTIVE_COUNSEL_TERMS)
            ):
                drop = True

        elif ground.type == "evidence":
            if _contains_any(t, SENTENCE_TERMS) or _contains_any(t, INEFFECTIVE_COUNSEL_TERMS):
                drop = True

        if drop:
            dropped.append(f"({sp.label}) {sp.text[:80]}" if sp.label else sp.text[:80])
        else:
            cleaned.append(sp)

    ground.sub_particulars = cleaned
    if dropped:
        _log(
            ground,
            f"Cleanup: removed {len(dropped)} misclassified sub-particular(s) "
            f"not matching ground type '{ground.type}'.",
        )
    return ground


def uplift_if_core_metrics_favour_ground(ground: Ground) -> Ground:
    """
    Prevent over-downgrading where realism metrics strongly favour the ground.

    If a conviction ground has strong record support, a verdict that is weak
    or balanced on the record, and the Crown response is weak (or moderate
    when robustness is weak), the viability should not sit at the bottom of
    the scale just because one sub-factor trigged an earlier cap.
    """
    record_support = getattr(ground, "record_support", None)
    verdict_robustness = getattr(ground, "verdict_robustness", None)
    crown_strength = getattr(ground, "crown_strength", None)

    if ground.type != "conviction":
        return ground

    uplifted = False

    if (
        record_support == "strong"
        and verdict_robustness in {"weak", "balanced"}
        and crown_strength == "weak"
        and ground.viability == "requires_development"
    ):
        ground.viability = "arguable_moderate"
        uplifted = True

    elif (
        record_support == "strong"
        and verdict_robustness == "weak"
        and crown_strength == "moderate"
        and ground.viability == "requires_development"
    ):
        ground.viability = "arguable_moderate"
        uplifted = True

    if uplifted:
        _log(
            ground,
            "Cleanup uplift: strong record support + weak/balanced verdict "
            f"robustness + {crown_strength} Crown response → viability "
            "'requires_development' → 'arguable_moderate'.",
        )

    return ground


def soften_timing_sensitive_jury_language(text: str) -> str:
    """
    Avoid overstatement where alleged juror conduct occurred after verdict.
    Post-verdict juror behaviour may raise an appearance concern but does
    not by itself establish deliberative bias.
    """
    if not text:
        return text

    t = normalise(text)
    if "after the verdict" not in t:
        return text

    out = text
    out = out.replace(
        "clear misconduct undermining impartiality",
        "conduct raising concern but requiring proof of material effect on trial fairness",
    )
    out = out.replace(
        "showing partiality",
        "raising an appearance issue requiring closer examination",
    )
    out = out.replace(
        "undermining impartiality",
        "requiring proof of material impact on deliberative impartiality",
    )
    return out


def fix_liability_vs_mitigation_language(text: str, jurisdiction: str) -> str:
    """
    Replace misleading mitigation language where the concept is actually
    liability / partial defence / mental impairment / fault elements.
    Jurisdiction-aware — triggers only when the text references a concept
    from PARTIAL_DEFENCE_MAP for the case's jurisdiction.
    """
    if not text:
        return text

    code = (jurisdiction or "").upper().strip()
    if code == "FEDERAL":
        code = "CTH"

    triggers = PARTIAL_DEFENCE_MAP.get(code, ())
    if not triggers or not _contains_any(text, triggers):
        return text

    replacements = {
        "mitigated culpability": "affected criminal responsibility",
        "mitigate culpability": "affect criminal responsibility",
        "did not mitigate culpability": "did not engage the asserted liability issue",
        "did not mitigate the accused's mental culpability": "did not engage the asserted liability issue",
        "did not mitigate the offender's mental culpability": "did not engage the asserted liability issue",
        "treated as mitigation": "treated as a liability issue",
        "mitigating factor": "liability issue",
        "mitigation factor": "liability issue",
        "mitigation under": "liability question under",
        "not mitigating": "not sufficient to engage the asserted defence or liability issue",
    }

    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)

    # NSW-specific phrasing
    if code == "NSW":
        out = out.replace(
            "under section 23A of the Crimes Act 1900 (NSW), which addresses substantial impairment by abnormality of mind",
            "under section 23A of the Crimes Act 1900 (NSW), which provides a partial defence of substantial impairment by abnormality of mind",
        )
        out = out.replace(
            "did not mitigate the accused's mental culpability under section 23A",
            "did not engage the asserted partial defence under section 23A",
        )
        out = out.replace(
            "did not mitigate the offender's mental culpability under section 23A",
            "did not engage the asserted partial defence under section 23A",
        )

    # QLD-specific phrasing
    if code == "QLD":
        out = out.replace(
            "treated as mere mitigation",
            "treated as a question of diminished responsibility or criminal responsibility",
        )

    return out


def clean_ground_narrative_language(ground: Ground, jurisdiction: str) -> Ground:
    """
    Apply softening + terminology fixes to every narrative section.
    """
    original_trail_len = len(ground.reasoning_trail or [])

    def _clean(s):
        if not s:
            return s
        return fix_liability_vs_mitigation_language(
            soften_timing_sensitive_jury_language(s),
            jurisdiction,
        )

    before_tf = ground.trial_finding
    before_ei = ground.error_identified
    before_mat = ground.materiality
    before_con = ground.consequence

    ground.trial_finding = _clean(ground.trial_finding)
    ground.error_identified = _clean(ground.error_identified)
    ground.materiality = _clean(ground.materiality)
    ground.consequence = _clean(ground.consequence)

    ground.supporting_evidence = [_clean(item) for item in (ground.supporting_evidence or [])]

    if (
        before_tf != ground.trial_finding
        or before_ei != ground.error_identified
        or before_mat != ground.materiality
        or before_con != ground.consequence
    ):
        _log(
            ground,
            f"Cleanup narrative: liability / post-verdict language corrected "
            f"for jurisdiction {jurisdiction or 'unspecified'}.",
        )

    # Suppress empty growth of the trail if nothing changed.
    if ground.reasoning_trail and len(ground.reasoning_trail) == original_trail_len:
        pass

    return ground


def enforce_type_title_consistency(ground: Ground) -> Ground:
    """
    Resolve internal contradiction between ground.type and ground.title.
    Liability terminology in the title (mens rea, mental state, substantial
    impairment, partial defence, etc.) wins over any 'sentencing' framing
    because liability ≠ sentencing — a common drafting slip the splitter
    sometimes leaves behind.

    Order: sentence-words set 'sentence' first, then liability-words flip
    to 'conviction' (liability wins). Mirrors counsel feedback 23 Feb 2026.
    """
    title = normalise(ground.title or "")
    before = ground.type

    if "sentencing" in title or "manifestly excessive" in title:
        ground.type = "sentence"

    liability_title_tokens = (
        "mens rea",
        "mental state",
        "substantial impairment",
        "abnormality of mind",
        "partial defence",
        "diminished responsibility",
        "mental impairment",
        "unsoundness of mind",
        "fault elements",
    )
    if any(t in title for t in liability_title_tokens):
        ground.type = "conviction"

    if ground.type != before:
        _log(
            ground,
            f"Cleanup type-title consistency: type '{before}' → '{ground.type}' "
            f"based on ground title tokens.",
        )

    return ground


def downgrade_speculative_procedure(ground: Ground) -> Ground:
    """
    Procedure grounds resting on inference ('implication', 'no direct
    evidence', etc.) without affidavit/transcript material are cosmetic —
    the Court will ask "where is the evidence of prejudice?" and strike
    them out. Cap at requires_development so they are clearly flagged as
    needing record support before filing.
    """
    if ground.type != "procedure":
        return ground

    blob = normalise(
        " ".join([
            ground.materiality or "",
            ground.error_identified or "",
            ground.consequence or "",
            " ".join(ground.supporting_evidence or []),
        ])
    )

    speculative_markers = (
        "implication that",
        "implied that",
        "no direct evidence",
        "there is no transcript",
        "no affidavit",
        "inference only",
    )

    if any(m in blob for m in speculative_markers):
        prior = ground.viability
        ground.viability = "requires_development"
        if ground.viability != prior:
            _log(
                ground,
                f"Cleanup: procedure ground rests on inference / lacks "
                f"record support — viability '{prior}' → 'requires_development'.",
            )

    return ground


# ---------------------------------------------------------------------------
# Authority preferences — jurisdiction-neutral but ground-type specific.
# Counsel feedback 23 Feb 2026.
# ---------------------------------------------------------------------------

PROCEDURE_AUTHORITIES = (
    "ebner",
    "gittany",
    "belghar",
)

SENTENCE_AUTHORITIES = (
    "house v the king",
    "house v king",
    "hili",
    "dinsdale",
    "muldrock",
    "barbaro",
)


def _prefer_authorities(authorities: list[str], preferred_tokens: tuple[str, ...]) -> list[str]:
    """
    Keep any authority matching a preferred-token; if none match, fall back
    to the first three of the supplied list so we never return an empty
    authorities list.
    """
    if not authorities:
        return authorities
    preferred: list[str] = []
    fallback: list[str] = []
    for a in authorities:
        t = normalise(a)
        if any(tok in t for tok in preferred_tokens):
            preferred.append(a)
        else:
            fallback.append(a)
    return preferred or fallback[:3]


def apply_authority_preferences(ground: Ground) -> Ground:
    """
    Apply ground-type-specific authority preference filters. Avoids citing
    Weiss / M v The Queen on a jury-misconduct ground, where the Court will
    expect Ebner / Gittany / Belghar instead. Same pattern for sentencing —
    House v The King / Hili / Dinsdale / Muldrock.
    """
    if not ground.authorities:
        return ground

    before = list(ground.authorities)
    if ground.type == "procedure":
        ground.authorities = _prefer_authorities(ground.authorities, PROCEDURE_AUTHORITIES)
    elif ground.type == "sentence":
        ground.authorities = _prefer_authorities(ground.authorities, SENTENCE_AUTHORITIES)

    if ground.authorities != before:
        _log(
            ground,
            f"Cleanup: authorities filtered for ground type '{ground.type}' — "
            f"kept {len(ground.authorities)} of {len(before)} to prefer "
            f"ground-type-appropriate precedent.",
        )

    return ground


# ---------------------------------------------------------------------------
# List-level passes — run after the per-ground pipeline has finished.
# Counsel feedback 23 Feb 2026.
# ---------------------------------------------------------------------------

_PSYCHIATRIC_DUP_TOKENS = (
    "substantial impairment",
    "psychiatric",
    "mental state",
    "mens rea",
    "psychosis",
    "partial defence",
    "diminished responsibility",
    "mental impairment",
    "abnormality of mind",
)


def _merge_into(base: Ground, dup: Ground) -> None:
    """
    Merge unique sub-particulars + supporting evidence from dup into base
    without creating duplicate text entries.
    """
    seen_sub = {normalise(sp.text) for sp in (base.sub_particulars or [])}
    for sp in (dup.sub_particulars or []):
        key = normalise(sp.text)
        if key and key not in seen_sub:
            base.sub_particulars = (base.sub_particulars or []) + [sp]
            seen_sub.add(key)

    seen_ev = {normalise(e) for e in (base.supporting_evidence or [])}
    for e in (dup.supporting_evidence or []):
        key = normalise(e)
        if key and key not in seen_ev:
            base.supporting_evidence = (base.supporting_evidence or []) + [e]
            seen_ev.add(key)


def collapse_duplicate_psychiatric_grounds(grounds: list[Ground]) -> list[Ground]:
    """
    Ensure no more than one psychiatric / liability ground survives.
    A second "Sentencing Error: Failure to Consider Substantial Impairment"
    is the SAME issue re-framed as mitigation — that's legally wrong in NSW
    (s 23A is a partial defence, not sentencing mitigation) and the Court
    will strike it as duplicative. Merge the dropped ground's unique
    sub-particulars / evidence into the survivor before discarding.
    """
    kept: list[Ground] = []
    survivor: Ground | None = None

    for g in grounds:
        blob = normalise(
            (g.title or "") + " " + (g.error_identified or "") + " " + (g.materiality or "")
        )
        is_psych = any(tok in blob for tok in _PSYCHIATRIC_DUP_TOKENS)
        if is_psych:
            if survivor is None:
                survivor = g
                kept.append(g)
            else:
                _merge_into(survivor, g)
                _log(
                    survivor,
                    f"Cleanup: merged duplicate psychiatric / liability ground "
                    f"'{g.title}' into this ground — same issue, different framing.",
                )
                continue
        else:
            kept.append(g)

    return kept


def merge_procedural_grounds(grounds: list[Ground]) -> list[Ground]:
    """
    Procedural unfairness fragmented across multiple grounds (e.g. jury
    separation + judge-alone refusal + prejudicial material) should be one
    consolidated 'Procedural Unfairness (Jury / Trial Integrity)' ground
    with sub-particulars. The Court prefers a single integrated challenge,
    not three thin ones — counsel feedback 23 Feb 2026.
    """
    procedural = [g for g in grounds if g.type == "procedure"]
    if len(procedural) <= 1:
        return grounds

    base = procedural[0]
    for dup in procedural[1:]:
        _merge_into(base, dup)
        _log(
            base,
            f"Cleanup: merged fragmented procedural ground '{dup.title}' "
            f"into consolidated procedural-unfairness ground.",
        )

    # Preserve original list order, minus the dropped procedure grounds.
    dropped_ids = {id(g) for g in procedural[1:]}
    return [g for g in grounds if id(g) not in dropped_ids]


def apply_cleanup(grounds: list[Ground], jurisdiction: str) -> list[Ground]:
    """
    Final cleanup pass — run AFTER realism scoring (appeal_strength).

    Per-ground order:
      1. enforce_type_title_consistency   (title vs type mismatches first,
         so downstream steps see the corrected type)
      2. remove_misclassified_subs        (strip cross-pathway contamination)
      3. uplift_if_core_metrics_favour_ground  (rescue over-downgraded conviction grounds)
      4. downgrade_speculative_procedure  (cap speculative procedure grounds)
      5. clean_ground_narrative_language  (NSW s 23A + post-verdict jury language)
      6. apply_authority_preferences      (ground-type-appropriate precedent)

    List-level passes (after per-ground loop):
      7. merge_procedural_grounds         (consolidate fragmented procedure)
      8. collapse_duplicate_psychiatric_grounds  (no Ground 2 + Ground 4 twins)
    """
    cleaned: list[Ground] = []
    for ground in grounds:
        ground = enforce_type_title_consistency(ground)
        ground = remove_misclassified_subs(ground)
        ground = uplift_if_core_metrics_favour_ground(ground)
        ground = downgrade_speculative_procedure(ground)
        ground = clean_ground_narrative_language(ground, jurisdiction)
        ground = apply_authority_preferences(ground)
        cleaned.append(ground)

    cleaned = merge_procedural_grounds(cleaned)
    cleaned = collapse_duplicate_psychiatric_grounds(cleaned)

    # Final invariant sweep — the list-level merges above may have pulled
    # sub-particulars / evidence across pathway boundaries (e.g. a sentence-
    # typed psychiatric twin merges into a conviction-typed survivor carrying
    # a "mitigation at sentence" sub). Re-run the scrubber once so the two
    # cross-jurisdictional invariants still hold after merging:
    #   INV1: no conviction ground retains a sentencing sub
    #   INV2: no sentence ground retains a liability sub
    cleaned = [remove_misclassified_subs(g) for g in cleaned]
    return cleaned
