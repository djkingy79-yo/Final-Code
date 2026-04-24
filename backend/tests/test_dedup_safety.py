"""
Dedup safety regression suite (locked 24 Feb 2026).

Pure read-only assertions against the existing dedup logic. NO behaviour
changes, NO threshold tweaks, NO refactoring. If any assertion fails, the
fix is NEVER to modify the assertion — it is to restore the behaviour the
assertion documents.

Covers the five highest-risk paths identified by the 24 Feb 2026 dedup
audit:

    1. cleanup_duplicate_grounds must not merge distinct legal grounds merely
       because they share psychiatric / procedural / sentencing topic words.
    2. cleanup_duplicate_issues must preserve distinct issues.
    3. report_quality._dedupe_report_content must not remove valid
       paid-report paragraphs at the current 0.97 threshold.
    4. Timeline fuzzy dedup (routers/documents.py:158) must not merge
       distinct events with similar titles.
    5. dedup_grounds_on_startup must NEVER delete across unrelated
       cases/users.
"""
from __future__ import annotations

import os
import uuid
import pytest


# ---------------------------------------------------------------------------
# Mongo-required marker (mirrors tests/test_ground_dedup.py pattern).
# ---------------------------------------------------------------------------

def _mongo_available() -> bool:
    try:
        import motor.motor_asyncio  # noqa: F401
        # Test connection by trying to instantiate a client
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=500)
        # Blocking check is done async elsewhere; we only verify import.
        _ = client
        return True
    except Exception:
        return False


requires_mongo = pytest.mark.skipif(
    os.environ.get("MONGO_URL", "mongodb://localhost:27017") is None or not _mongo_available(),
    reason="Requires running MongoDB instance",
)


# ---------------------------------------------------------------------------
# Shared helpers.
# ---------------------------------------------------------------------------

def _fresh_case_and_user():
    """Returns a (case_id, user_id) pair unique to this test invocation."""
    token = uuid.uuid4().hex[:12]
    return (f"case_safety_{token}", f"user_safety_{token}")


async def _get_test_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client["test_dedup_safety"], client


# ---------------------------------------------------------------------------
# TEST 1 — cleanup_duplicate_grounds must preserve distinct legal arguments
# that merely share a topic word (psychiatric / procedural / sentencing).
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_cleanup_preserves_distinct_psychiatric_grounds():
    """A psychiatric liability ground and a psychiatric sentencing ground
    are DIFFERENT legal arguments. Despite sharing the "psychiatric" /
    "mental" topic word, is_ground_duplicate is structured so they should
    NOT be collapsed by cleanup_duplicate_grounds.

    Note: `collapse_duplicate_psychiatric_grounds` in ground_cleanup.py is
    the aggressive collapser — that runs on the in-memory normaliser path.
    This test covers the DB-layer cleanup_duplicate_grounds path, which is
    the one that physically deletes rows.
    """
    from services.ground_dedup import cleanup_duplicate_grounds

    db, client = await _get_test_db()
    case_id, user_id = _fresh_case_and_user()
    await db.grounds_of_merit.delete_many({"case_id": case_id})

    try:
        await db.grounds_of_merit.insert_many([
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Trial Judge Failure to Consider Section 23A Substantial Impairment Partial Defence (Liability)",
                "ground_type": "miscarriage_of_justice",
                "created_at": "2026-01-01T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Manifest Excess in Non-Parole Period Due to Failure to Weight Fitzgerald Factors",
                "ground_type": "sentencing_error",
                "created_at": "2026-01-02T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Unreasonable Verdict - Identification Evidence Unsafe",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-03T00:00:00",
                "status": "identified",
            },
        ])
        before = await db.grounds_of_merit.count_documents({"case_id": case_id})
        assert before == 3

        result = await cleanup_duplicate_grounds(db, case_id, user_id)
        after = await db.grounds_of_merit.count_documents({"case_id": case_id})

        assert after == 3, (
            f"cleanup_duplicate_grounds OVER-MERGED distinct legal grounds. "
            f"Expected 3 to survive, got {after}. Removed: {result['removed']}"
        )
        assert result["removed"] == 0
    finally:
        await db.grounds_of_merit.delete_many({"case_id": case_id})
        client.close()


@requires_mongo
@pytest.mark.asyncio
async def test_cleanup_preserves_distinct_procedural_grounds():
    """Distinct procedural errors (jury separation vs judge-alone refusal
    vs prejudicial voir-dire material) must remain separate rows after
    cleanup_duplicate_grounds — the DB-layer fuzzy match should not
    collapse three different procedural complaints into one."""
    from services.ground_dedup import cleanup_duplicate_grounds

    db, client = await _get_test_db()
    case_id, user_id = _fresh_case_and_user()
    await db.grounds_of_merit.delete_many({"case_id": case_id})

    try:
        await db.grounds_of_merit.insert_many([
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Irregularity in Jury Separation Over the Trial Weekend",
                "ground_type": "procedural_error",
                "created_at": "2026-01-01T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Refusal of Judge-Alone Trial Application Under s132 Criminal Procedure Act",
                "ground_type": "procedural_error",
                "created_at": "2026-01-02T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Prejudicial Voir-Dire Ruling Admitted Tendency Evidence of Prior Uncharged Acts",
                "ground_type": "procedural_error",
                "created_at": "2026-01-03T00:00:00",
                "status": "identified",
            },
        ])

        result = await cleanup_duplicate_grounds(db, case_id, user_id)
        after = await db.grounds_of_merit.count_documents({"case_id": case_id})

        assert after == 3, (
            f"cleanup_duplicate_grounds OVER-MERGED distinct procedural grounds. "
            f"Expected 3 to survive, got {after}. Removed: {result['removed']}"
        )
    finally:
        await db.grounds_of_merit.delete_many({"case_id": case_id})
        client.close()


@requires_mongo
@pytest.mark.asyncio
async def test_cleanup_preserves_distinct_sentencing_grounds():
    """Three legitimately different sentencing challenges (quantum manifest
    excess vs non-parole period calculation vs failure to apply Bugmy
    principles) must all survive cleanup_duplicate_grounds."""
    from services.ground_dedup import cleanup_duplicate_grounds

    db, client = await _get_test_db()
    case_id, user_id = _fresh_case_and_user()
    await db.grounds_of_merit.delete_many({"case_id": case_id})

    try:
        await db.grounds_of_merit.insert_many([
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Manifest Excess of Head Sentence Compared to Comparable Range",
                "ground_type": "sentencing_error",
                "created_at": "2026-01-01T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Non-Parole Period Calculation Error Under s44 Crimes Sentencing Procedure Act",
                "ground_type": "sentencing_error",
                "created_at": "2026-01-02T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Failure to Apply Bugmy v The Queen Background Principles in Mitigation",
                "ground_type": "sentencing_error",
                "created_at": "2026-01-03T00:00:00",
                "status": "identified",
            },
        ])

        result = await cleanup_duplicate_grounds(db, case_id, user_id)
        after = await db.grounds_of_merit.count_documents({"case_id": case_id})

        assert after == 3, (
            f"cleanup_duplicate_grounds OVER-MERGED distinct sentencing grounds. "
            f"Expected 3 to survive, got {after}. Removed: {result['removed']}"
        )
    finally:
        await db.grounds_of_merit.delete_many({"case_id": case_id})
        client.close()


# ---------------------------------------------------------------------------
# TEST 2 — cleanup_duplicate_issues preserves distinct issues.
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_cleanup_duplicate_issues_preserves_distinct_arguments():
    """Five distinct issue classifications (different ground types + distinct
    titles) must all survive cleanup_duplicate_issues."""
    from services.ground_dedup import cleanup_duplicate_issues

    db, client = await _get_test_db()
    case_id, user_id = _fresh_case_and_user()
    await db.issue_classifications.delete_many({"case_id": case_id})

    try:
        distinct_issues = [
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Trial Judge Failed to Give Liebmann Direction on Circumstantial Evidence",
                "ground_type": "judicial_error",
                "created_at": "2026-01-01T00:00:00",
            },
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Unreasonable Verdict: Inconsistent Eyewitness Identifications by Crown Witnesses 4 and 7",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-02T00:00:00",
            },
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Fresh Evidence: Post-Trial Witness Recantation by Complainant's Partner",
                "ground_type": "fresh_evidence",
                "created_at": "2026-01-03T00:00:00",
            },
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Counsel Failure to Cross-Examine on Call Log Contradictions",
                "ground_type": "ineffective_counsel",
                "created_at": "2026-01-04T00:00:00",
            },
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id,
                "user_id": user_id,
                "title": "Sentence Manifestly Excessive Having Regard to Objective Gravity",
                "ground_type": "sentencing_error",
                "created_at": "2026-01-05T00:00:00",
            },
        ]
        await db.issue_classifications.insert_many(distinct_issues)
        before = await db.issue_classifications.count_documents({"case_id": case_id})
        assert before == 5

        result = await cleanup_duplicate_issues(db, case_id, user_id)
        after = await db.issue_classifications.count_documents({"case_id": case_id})

        assert after == 5, (
            f"cleanup_duplicate_issues OVER-MERGED distinct issues. "
            f"Expected 5 to survive, got {after}. Removed: {result['removed']}"
        )
        assert result["removed"] == 0, (
            f"cleanup_duplicate_issues removed {result['removed']} distinct issues; expected 0."
        )
    finally:
        await db.issue_classifications.delete_many({"case_id": case_id})
        client.close()


# ---------------------------------------------------------------------------
# TEST 3 — _dedupe_report_content must not remove valid paid-report
#          paragraphs at the current 0.97 threshold.
# ---------------------------------------------------------------------------

def _build_paid_report_sample() -> str:
    """A realistic paid-report section with semantically related but
    distinct paragraphs. Each paragraph covers a different legal point;
    none should be stripped at the 0.97 threshold."""
    return (
        "## 4. GROUNDS OF MERIT — APPELLATE PATHWAY ANALYSIS\n\n"
        "The first ground alleges that the trial judge misdirected the jury on "
        "the elements of intent under s 18 of the Crimes Act 1900 (NSW). The "
        "misdirection is material because intent was the only live issue at "
        "trial; the Crown accepted that the act was done by the accused. "
        "If the appellate court finds that the direction was erroneous, the "
        "verdict cannot stand under the test in R v Coulter.\n\n"
        "The second ground concerns the admission of tendency evidence of "
        "prior uncharged conduct over objection under s 97 of the Evidence "
        "Act 1995 (NSW). The prejudicial effect of this evidence substantially "
        "outweighed its probative value and no adequate limiting direction "
        "was given. This is a distinct and independent ground from the first; "
        "even if the first is dismissed, this ground alone may sustain the appeal.\n\n"
        "The third ground turns on the sentencing remarks and alleges manifest "
        "excess of the non-parole period. The quantum imposed exceeds the "
        "upper bound of the comparable range by approximately 18 months. The "
        "appellate court is invited to re-sentence under s 44 of the Crimes "
        "(Sentencing Procedure) Act 1999 (NSW).\n\n"
        "The fourth ground invokes fresh evidence in the form of post-trial "
        "witness recantation. Under Mickelberg v The Queen the evidence must "
        "be credible, cogent, and capable of affecting the verdict; the "
        "recanting witness meets all three limbs.\n\n"
        "The fifth ground relates to ineffective assistance of counsel at "
        "trial. Trial counsel failed to call the accused's psychiatrist, who "
        "would have given evidence going directly to capacity under s 23A of "
        "the Crimes Act 1900 (NSW). This failure materially prejudiced the "
        "defence and falls within the Strickland standard as applied in TKWJ "
        "v The Queen.\n"
    )


def test_dedupe_report_content_preserves_distinct_paragraphs_at_097_threshold():
    """_dedupe_report_content must leave a 5-paragraph Grounds Of Merit
    section intact when each paragraph is semantically distinct.

    Threshold under test: 0.97 (full_detailed / extensive_log).
    DO NOT CHANGE THE THRESHOLD — the test protects that exact value."""
    from services.report_quality import _dedupe_report_content, _build_anchor_terms

    original = _build_paid_report_sample()
    # A realistic anchor-term set for a NSW murder appeal.
    anchor_terms = _build_anchor_terms(
        case={"state": "nsw", "defendant_name": "Smith", "offence_type": "murder"},
        documents=[],
        timeline=[],
        grounds=[],
    )

    deduped = _dedupe_report_content(original, "full_detailed", anchor_terms)

    # The key assertion: every distinct sentence-level anchor must survive.
    required_anchors = [
        "s 18 of the Crimes Act",
        "tendency evidence",
        "s 97 of the Evidence",
        "manifest excess of the non-parole period",
        "fresh evidence",
        "Mickelberg",
        "ineffective assistance of counsel",
        "Strickland",
        "TKWJ",
    ]
    missing = [a for a in required_anchors if a not in deduped]
    assert not missing, (
        f"_dedupe_report_content STRIPPED paid-report content at 0.97 threshold. "
        f"Missing anchors: {missing}\n"
        f"Output was:\n{deduped}"
    )

    # And the paragraph count must be preserved (5 content paragraphs).
    non_empty_paras = [p for p in deduped.split("\n\n") if p.strip() and not p.startswith("## ")]
    assert len(non_empty_paras) == 5, (
        f"Expected 5 distinct paragraphs to survive dedup at 0.97; got "
        f"{len(non_empty_paras)}.\nOutput:\n{deduped}"
    )


def test_dedupe_report_content_does_strip_true_duplicates():
    """Positive control: when two paragraphs ARE near-identical, the
    deduper must collapse them. This proves the threshold is still doing
    its intended job and isn't being trivially bypassed."""
    from services.report_quality import _dedupe_report_content, _build_anchor_terms

    duplicated_para = (
        "The first ground alleges that the trial judge misdirected the jury "
        "on the elements of intent under s 18 of the Crimes Act 1900 (NSW). "
        "The misdirection is material because intent was the only live issue "
        "at trial and the Crown accepted that the act was done by the accused. "
        "Even a small error in that direction would infect the verdict."
    )
    # Append identical paragraph three times.
    text = f"## 4. GROUNDS OF MERIT\n\n{duplicated_para}\n\n{duplicated_para}\n\n{duplicated_para}"

    anchor_terms = _build_anchor_terms(
        case={"state": "nsw", "defendant_name": "Smith", "offence_type": "murder"},
        documents=[], timeline=[], grounds=[],
    )

    deduped = _dedupe_report_content(text, "full_detailed", anchor_terms)

    # The identical paragraph should appear exactly once.
    sentence_marker = "The misdirection is material because intent was the only live issue"
    assert deduped.count(sentence_marker) == 1, (
        f"_dedupe_report_content failed to collapse 3 identical copies of the "
        f"same paragraph (sentinel appeared {deduped.count(sentence_marker)} "
        f"times). Threshold of 0.97 must still deduplicate exact-duplicate "
        f"content."
    )


# ---------------------------------------------------------------------------
# TEST 4 — Timeline fuzzy dedup must not merge distinct events with similar titles.
# ---------------------------------------------------------------------------

def _is_timeline_duplicate(new_title: str, existing_titles: list[str]) -> bool:
    """Mirrors the exact inline rule at routers/documents.py:158.
    Kept in the test file (not imported from the router) so the assertion
    can run without booting the full FastAPI stack."""
    from fuzzywuzzy import fuzz
    new_lower = new_title.lower().strip()
    existing_lower = [t.lower().strip() for t in existing_titles]
    return any(fuzz.token_set_ratio(new_lower, et) >= 65 for et in existing_lower)


@pytest.mark.parametrize(
    "new_title,existing_titles,description",
    [
        # Distinct procedural events that share 1-2 words must not merge.
        (
            "First arrest at 5 Castle Avenue on 14 March 2022",
            ["Second arrest at 12 King Street on 8 April 2022"],
            "two arrests on different dates and addresses",
        ),
        (
            "Plea of not guilty entered at Waverley Local Court",
            ["Committal hearing at Waverley Local Court listed for trial"],
            "plea vs committal at same court",
        ),
        (
            "Trial commenced before Justice Jones with jury of 12",
            ["Trial reserved judgement by Justice Jones after submissions",],
            "trial commence vs judgement reserved",
        ),
        (
            "Sentence imposed of 18 years with non-parole of 13 years",
            ["Sentence appealed to NSW Court of Criminal Appeal"],
            "sentencing vs sentence appeal",
        ),
    ],
)
def test_timeline_dedup_preserves_distinct_similar_events(new_title, existing_titles, description):
    """The inline 65% token_set_ratio fuzzy dedup must not collapse distinct
    events that only share a few words in common. Documented failure mode
    per audit: two legitimate procedural events with overlapping court /
    actor / offence-name words can silently collapse to one."""
    is_dup = _is_timeline_duplicate(new_title, existing_titles)
    assert not is_dup, (
        f"Timeline fuzzy dedup (>= 65 token_set_ratio) INCORRECTLY merged: "
        f"{description}. New title: {new_title!r} was flagged as duplicate "
        f"of existing: {existing_titles!r}"
    )


# ---------------------------------------------------------------------------
# KNOWN UNDER-TESTED REGRESSION RISK (recorded 24 Feb 2026).
#
# The 65% timeline fuzz threshold in routers/documents.py:158 CURRENTLY
# over-merges the following distinct events. This xfail(strict=True) is
# deliberate — it documents the existing bug WITHOUT changing behaviour.
# When a future remediation pass raises the threshold, adds actor/date
# disambiguation, or gates the rule on event_date equality, this xfail
# will flip to xpass and automatically fail CI, forcing attention.
# ---------------------------------------------------------------------------
@pytest.mark.xfail(
    strict=True,
    reason=(
        "KNOWN-RISK over-merge — the 65% token_set_ratio rule merges "
        "'First police interview by Detective A' with 'Second police interview "
        "by Detective B'. Will flip to xpass once a threshold or disambiguator "
        "fix is applied."
    ),
)
def test_timeline_dedup_distinct_police_interviews_is_known_over_merge():
    assert not _is_timeline_duplicate(
        "First police interview conducted by Detective A",
        ["Second police interview conducted by Detective B"],
    )


def test_timeline_dedup_still_catches_true_duplicates():
    """Positive control: identical event titles (same words, reordered) MUST
    still be caught as duplicates so the threshold isn't being trivially
    bypassed in the negative-control tests above."""
    is_dup = _is_timeline_duplicate(
        "Accused charged with murder on 15 March 2022",
        ["On 15 March 2022 accused charged with murder"],
    )
    assert is_dup, (
        "Timeline fuzzy dedup failed to catch a reordered-word duplicate. "
        "The 65% threshold is the current spec — do not lower it, but the "
        "reordered-word case MUST still match."
    )


# ---------------------------------------------------------------------------
# TEST 5 — dedup_grounds_on_startup must NEVER delete across unrelated cases/users.
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_startup_dedup_isolates_by_case_and_user():
    """Seed two unrelated cases, each owned by a different user. Each case
    has its own duplicate ground. After dedup_grounds_on_startup runs, each
    case must retain its own unique grounds; cross-case or cross-user
    bleeding would be a catastrophic data-loss bug."""
    from services.startup_tasks import dedup_grounds_on_startup
    import services.startup_tasks as st_mod

    db, client = await _get_test_db()

    case_a, user_a = _fresh_case_and_user()
    case_b, user_b = _fresh_case_and_user()

    # Clean any residue.
    await db.grounds_of_merit.delete_many({"case_id": {"$in": [case_a, case_b]}})

    try:
        # Case A — two duplicate grounds + one unique ground.
        seed_a = [
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_a, "user_id": user_a,
                "title": "Trial Judge Misdirection on Intent",
                "ground_type": "judicial_error",
                "created_at": "2026-01-01T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_a, "user_id": user_a,
                "title": "Trial Judge Misdirection on Intent",  # exact duplicate
                "ground_type": "judicial_error",
                "created_at": "2026-01-02T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_a, "user_id": user_a,
                "title": "Unreasonable Verdict — Identification Evidence",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-03T00:00:00",
                "status": "identified",
            },
        ]
        # Case B — one ground that shares topic words with case A's unique
        # ground but belongs to a totally different case/user.
        seed_b = [
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_b, "user_id": user_b,
                "title": "Trial Judge Misdirection on Intent",  # same title as A
                "ground_type": "judicial_error",
                "created_at": "2026-01-04T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_b, "user_id": user_b,
                "title": "Unreasonable Verdict — Identification Evidence",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-05T00:00:00",
                "status": "identified",
            },
        ]
        await db.grounds_of_merit.insert_many(seed_a + seed_b)

        before_a = await db.grounds_of_merit.count_documents({"case_id": case_a, "user_id": user_a})
        before_b = await db.grounds_of_merit.count_documents({"case_id": case_b, "user_id": user_b})
        assert before_a == 3 and before_b == 2, (
            f"Seed failed: A={before_a}, B={before_b}"
        )

        # dedup_grounds_on_startup uses the global `db` object inside
        # startup_tasks.py. Temporarily swap that module-level `db` for
        # our test client so the real server DB isn't touched.
        original_db = st_mod.db
        st_mod.db = db
        try:
            await dedup_grounds_on_startup()
        finally:
            st_mod.db = original_db

        after_a = await db.grounds_of_merit.count_documents({"case_id": case_a, "user_id": user_a})
        after_b = await db.grounds_of_merit.count_documents({"case_id": case_b, "user_id": user_b})

        # Case A: duplicate removed → 2 unique grounds left.
        assert after_a == 2, (
            f"Case A expected 2 grounds after dedup (1 duplicate should have "
            f"been removed). Got {after_a}."
        )
        # Case B: must still have 2 grounds — nothing belongs to Case A user.
        assert after_b == 2, (
            f"Case B was TOUCHED by case A's dedup run. Expected 2 grounds, "
            f"got {after_b}. Cross-case data loss is a critical bug."
        )

        # Belt-and-braces: assert both of Case B's original ground_ids
        # are still present.
        remaining_b_ids = set(
            d["ground_id"] for d in await db.grounds_of_merit.find(
                {"case_id": case_b, "user_id": user_b}, {"_id": 0, "ground_id": 1}
            ).to_list(10)
        )
        expected_b_ids = {g["ground_id"] for g in seed_b}
        assert remaining_b_ids == expected_b_ids, (
            f"Case B ground_ids mutated by cross-case dedup. "
            f"Expected {expected_b_ids}, got {remaining_b_ids}."
        )
    finally:
        await db.grounds_of_merit.delete_many({"case_id": {"$in": [case_a, case_b]}})
        client.close()
