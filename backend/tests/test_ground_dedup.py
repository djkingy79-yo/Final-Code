"""
Comprehensive ground deduplication test.
Verifies that:
1. Topic-based matching catches all known duplicate patterns
2. Cleanup function correctly merges duplicates
3. Multiple sync runs don't multiply grounds
"""
import asyncio
import sys
import os
sys.path.insert(0, '/app/backend')

from services.ground_dedup import (
    is_ground_duplicate, _extract_topics, normalise_au_spelling,
    cleanup_duplicate_grounds, cleanup_duplicate_issues, LEGAL_TOPICS
)


def test_topic_coverage():
    """Verify ALL legal topics have sufficient keyword coverage."""
    print("=== TEST 1: Topic Coverage ===")
    test_titles = {
        "psychiatric_evidence": [
            "Psychiatric Evidence Not Properly Considered",
            "Psychological report excluded from sentencing",
            "Mental health defence not raised at trial",
            "Diminished responsibility ignored",
            "Mental impairment as mitigating factor",
        ],
        "sentencing_error": [
            "Sentencing Error Related to Non-Parole Period",
            "Manifestly excessive sentence imposed",
            "Sentence disproportion with comparable cases",
            "Double-counting of aggravating features",
            "Sentencing approach to moral culpability",
            "Sentence: possible error in approach to psychosis",
        ],
        "judicial_direction": [
            "Misdirection on burden of proof",
            "Inadequate jury directions on provocation",
            "Judicial error in summing up",
            "Prejudicial comments by trial judge",
            "Unfair trial due to judge conduct",
        ],
        "unreasonable_verdict": [
            "Unreasonable verdict given the evidence",
            "Unsafe and unsatisfactory verdict",
            "Verdict cannot be supported by evidence",
            "Unreliable identification evidence",
            "Key witness inconsistency undermines verdict",
        ],
        "ineffective_counsel": [
            "Ineffective assistance of counsel",
            "Incompetence in cross-examination",
            "Failure to call available witnesses",
            "Inadequate legal representation at trial",
            "Failure to object to inadmissible evidence",
        ],
        "evidence_admissibility": [
            "Improper admission of DNA evidence",
            "Wrongful admission of hearsay",
            "Exclusion of evidence was erroneous",
            "Chain of custody deficiencies",
            "Forensic evidence unreliable",
        ],
        "fresh_evidence": [
            "Fresh evidence: new witness available",
            "Post-trial evidence discovered",
            "Uncalled witness now available",
            "Newly discovered forensic evidence",
        ],
        "jury_misconduct": [
            "Jury irregularity during deliberations",
            "Juror misconduct discovered post-trial",
            "Non-sequestration of jury despite media",
            "Juror bias from external contact",
        ],
        "media_coverage": [
            "Prejudicial media coverage influenced jurors",
            "Pre-trial publicity affected fair trial",
            "Media saturation of case details",
        ],
        "prosecutorial_misconduct": [
            "Prosecutorial misconduct in closing",
            "Crown failure to disclose evidence",
            "DPP error in presenting case",
        ],
        "procedural_error": [
            "Procedural error in trial process",
            "Refusal of judge-alone trial application",
            "Procedural unfairness in hearing",
        ],
    }
    
    failures = 0
    for expected_topic, titles in test_titles.items():
        for title in titles:
            topics = _extract_topics(title)
            if expected_topic not in topics:
                print(f"  FAIL: '{title}' should match topic '{expected_topic}' but got {topics}")
                failures += 1
    
    if failures == 0:
        print(f"  PASS: All {sum(len(v) for v in test_titles.values())} titles correctly classified")
    else:
        print(f"  FAILED: {failures} titles misclassified")
    return failures == 0


def test_duplicate_detection():
    """Test that known duplicate pairs are detected."""
    print("\n=== TEST 2: Duplicate Detection ===")
    # These MUST be detected as duplicates
    must_match = [
        ("Sentencing Error Related to Non-Parole Period",
         "Sentencing Error Due to Misapplication of Psychological Evidence"),
        ("Prejudicial Media Coverage",
         "Media Influence on Jury"),
        ("Ineffective Counsel Regarding Expert Witnesses",
         "Inadequate Legal Representation at Trial"),
        ("Unreasonable verdict / verdict cannot be supported",
         "Unsafe and unsatisfactory verdict"),
        ("Misdirection on provocation",
         "Inadequate jury directions"),
        ("Fresh evidence: new forensic material",
         "Fresh evidence: uncalled witness"),
        ("Improper admission of DNA evidence",
         "Wrongful admission or exclusion of evidence"),
        ("Judicial conduct: prejudicial comments",
         "Unfair trial risk: prejudicial comments by trial judge"),
        ("Jury irregularity / non-sequestration",
         "Jury irregularity / risk of prejudice"),
        ("Incompetence / failure to call character witnesses",
         "Ineffective assistance: failure to call witnesses"),
        ("Sentence: manifest excess (30 years)",
         "Sentencing Error Related to Non-Parole Period"),
        ("Trial procedure: refusal of judge-alone trial",
         "Procedural error in trial application"),
    ]
    
    failures = 0
    for t1, t2 in must_match:
        result = is_ground_duplicate(t1, t2)
        if not result:
            print(f"  FAIL: Should be duplicate but wasn't:")
            print(f"    '{t1}'")
            print(f"    '{t2}'")
            t1_topics = _extract_topics(t1)
            t2_topics = _extract_topics(t2)
            print(f"    Topics: {t1_topics} & {t2_topics}")
            failures += 1
    
    if failures == 0:
        print(f"  PASS: All {len(must_match)} duplicate pairs detected")
    else:
        print(f"  FAILED: {failures} pairs NOT detected as duplicates")
    return failures == 0


def test_non_duplicates():
    """Test that genuinely different grounds are NOT falsely merged."""
    print("\n=== TEST 3: Non-Duplicate Protection ===")
    must_not_match = [
        ("Sentencing Error Related to Non-Parole Period",
         "Prejudicial Media Coverage"),
        ("Ineffective Counsel Regarding Expert Witnesses",
         "Fresh Evidence from New Forensic Analysis"),
        ("Jury Misconduct During Deliberations",
         "Prosecutorial Misconduct in Closing"),
        ("Procedural Error in Trial Process",
         "Sentencing Error Due to Double-Counting"),
        ("Psychiatric Evidence Not Considered",
         "Unreasonable Verdict Given Evidence"),
    ]
    
    failures = 0
    for t1, t2 in must_not_match:
        result = is_ground_duplicate(t1, t2)
        if result:
            print(f"  FAIL: Should NOT be duplicate but was:")
            print(f"    '{t1}'")
            print(f"    '{t2}'")
            t1_topics = _extract_topics(t1)
            t2_topics = _extract_topics(t2)
            print(f"    Topics: {t1_topics} & {t2_topics}")
            failures += 1
    
    if failures == 0:
        print(f"  PASS: All {len(must_not_match)} non-duplicate pairs correctly distinguished")
    else:
        print(f"  FAILED: {failures} pairs falsely matched as duplicates")
    return failures == 0


def test_australian_spelling():
    """Test Australian spelling normalisation."""
    print("\n=== TEST 4: Australian Spelling ===")
    tests = [
        ("Characterization of Evidence", "Characterisation of Evidence"),
        ("Defense Counsel Error", "Defence Counsel Error"),
        ("Analyzing the Verdict", "Analysing the Verdict"),
        ("Utilized Expert Testimony", "Utilised Expert Testimony"),
    ]
    
    failures = 0
    for input_text, expected in tests:
        result = normalise_au_spelling(input_text)
        if result != expected:
            print(f"  FAIL: '{input_text}' → '{result}' (expected '{expected}')")
            failures += 1
    
    if failures == 0:
        print(f"  PASS: All {len(tests)} spelling conversions correct")
    else:
        print(f"  FAILED: {failures} conversions incorrect")
    return failures == 0


async def test_cleanup_function():
    """Test the cleanup function against real DB data."""
    print("\n=== TEST 5: DB Cleanup Function ===")
    from motor.motor_asyncio import AsyncIOMotorClient
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    # Create a test case with known duplicates
    test_case_id = "test_dedup_verification"
    test_user_id = "test_dedup_user"
    
    # Clean up any previous test data
    await db.grounds_of_merit.delete_many({"case_id": test_case_id})
    
    # Insert grounds with known duplicates
    test_grounds = [
        {"ground_id": "gnd_test_1", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Sentencing Error Related to Non-Parole Period", "ground_type": "sentencing_error",
         "created_at": "2026-01-01T00:00:00", "status": "identified"},
        {"ground_id": "gnd_test_2", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Sentencing Error Due to Misapplication of Psychological Evidence", "ground_type": "sentencing_error",
         "created_at": "2026-01-02T00:00:00", "status": "investigated", "supporting_evidence": [{"quote": "test"}]},
        {"ground_id": "gnd_test_3", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Prejudicial Media Coverage", "ground_type": "other",
         "created_at": "2026-01-01T00:00:00", "status": "identified"},
        {"ground_id": "gnd_test_4", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Media Influence on Jury Deliberations", "ground_type": "jury_irregularity",
         "created_at": "2026-01-02T00:00:00", "status": "identified"},
        {"ground_id": "gnd_test_5", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Ineffective Assistance of Counsel", "ground_type": "ineffective_counsel",
         "created_at": "2026-01-01T00:00:00", "status": "identified"},
        {"ground_id": "gnd_test_6", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Failure to Call Key Witnesses by Defence", "ground_type": "ineffective_counsel",
         "created_at": "2026-01-02T00:00:00", "status": "identified"},
        {"ground_id": "gnd_test_7", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Unreasonable Verdict — Weight of Evidence", "ground_type": "other",
         "created_at": "2026-01-01T00:00:00", "status": "identified"},
    ]
    
    for g in test_grounds:
        await db.grounds_of_merit.insert_one(g)
    
    before_count = await db.grounds_of_merit.count_documents({"case_id": test_case_id})
    print(f"  Before cleanup: {before_count} grounds")
    
    result = await cleanup_duplicate_grounds(db, test_case_id, test_user_id)
    
    after_count = await db.grounds_of_merit.count_documents({"case_id": test_case_id})
    print(f"  After cleanup: {after_count} grounds (removed {result['removed']})")
    
    # Expected: 7 → 4 (sentencing=1, media=1, counsel=1, verdict=1)
    remaining = await db.grounds_of_merit.find(
        {"case_id": test_case_id}, {"_id": 0, "ground_id": 1, "title": 1, "status": 1, "supporting_evidence": 1}
    ).to_list(100)
    
    for g in remaining:
        has_evidence = bool(g.get("supporting_evidence"))
        print(f"    [{g['ground_id']}] {g['title'][:60]} (status={g.get('status')}, has_evidence={has_evidence})")
    
    # Verify the keeper for sentencing has the merged evidence from the investigated duplicate
    sentencing_ground = next((g for g in remaining if "Sentencing" in g.get("title", "")), None)
    if sentencing_ground and sentencing_ground.get("supporting_evidence"):
        print(f"  PASS: Sentencing ground correctly merged evidence from investigated duplicate")
    elif sentencing_ground:
        print(f"  INFO: Sentencing ground kept (status={sentencing_ground.get('status')})")
    
    # Clean up test data
    await db.grounds_of_merit.delete_many({"case_id": test_case_id})
    
    success = after_count == 4
    if success:
        print(f"  PASS: Reduced from {before_count} to {after_count} (expected 4)")
    else:
        print(f"  FAIL: Expected 4 remaining, got {after_count}")
    return success


async def test_idempotent_sync():
    """Test that running sync multiple times doesn't create duplicates."""
    print("\n=== TEST 6: Idempotent Sync Simulation ===")
    from motor.motor_asyncio import AsyncIOMotorClient
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    test_case_id = "test_idempotent"
    test_user_id = "test_idempotent_user"
    
    # Clean up
    await db.grounds_of_merit.delete_many({"case_id": test_case_id})
    await db.issue_classifications.delete_many({"case_id": test_case_id})
    
    # Create mock issues (simulates what LLM would generate)
    issues = [
        {"issue_id": "iss_t1", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Sentencing Error: Manifestly Excessive", "ground_type": "sentencing_error",
         "description": "The sentence was manifestly excessive", "created_at": "2026-01-01T00:00:00"},
        {"issue_id": "iss_t2", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Inadequate Jury Directions on Provocation", "ground_type": "judicial_error",
         "description": "The judge failed to properly direct the jury", "created_at": "2026-01-01T00:00:00"},
        {"issue_id": "iss_t3", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Fresh Evidence: Previously Unavailable Witness", "ground_type": "fresh_evidence",
         "description": "A new witness has come forward", "created_at": "2026-01-01T00:00:00"},
    ]
    
    for iss in issues:
        await db.issue_classifications.insert_one(iss)
    
    # Import the sync function and simulate
    from services.ground_dedup import is_ground_duplicate as igd, normalise_au_spelling as nau
    import uuid
    from datetime import datetime, timezone
    
    async def simulate_sync():
        """Simulates _sync_pipeline_issues_to_grounds logic."""
        db_issues = await db.issue_classifications.find(
            {"case_id": test_case_id, "user_id": test_user_id}, {"_id": 0}
        ).to_list(500)
        
        all_existing_grounds = await db.grounds_of_merit.find(
            {"case_id": test_case_id, "user_id": test_user_id},
            {"_id": 0, "ground_id": 1, "title": 1},
        ).to_list(200)
        
        for issue in db_issues:
            issue_title = nau((issue.get("title") or "").strip())
            existing_ground = None
            for eg in all_existing_grounds:
                eg_title = (eg.get("title") or "").strip()
                if igd(issue_title, eg_title):
                    existing_ground = eg
                    break
            
            if existing_ground:
                await db.grounds_of_merit.update_one(
                    {"ground_id": existing_ground["ground_id"]},
                    {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
                )
            else:
                new_id = f"gnd_{uuid.uuid4().hex[:12]}"
                await db.grounds_of_merit.insert_one({
                    "ground_id": new_id,
                    "case_id": test_case_id,
                    "user_id": test_user_id,
                    "title": issue_title,
                    "ground_type": issue.get("ground_type", "other"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
                all_existing_grounds.append({"ground_id": new_id, "title": issue_title})
    
    # Run sync 5 times
    counts = []
    for i in range(5):
        await simulate_sync()
        count = await db.grounds_of_merit.count_documents({"case_id": test_case_id})
        counts.append(count)
    
    print(f"  Ground counts across 5 syncs: {counts}")
    
    # Now simulate with slightly different titles (LLM variation)
    variant_issues = [
        {"issue_id": "iss_v1", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Sentencing Error Due to Non-Parole Period Calculation", "ground_type": "sentencing_error",
         "description": "Non-parole period incorrectly calculated", "created_at": "2026-01-02T00:00:00"},
        {"issue_id": "iss_v2", "case_id": test_case_id, "user_id": test_user_id,
         "title": "Misdirection of Jury on Self-Defence Provocation", "ground_type": "judicial_error",
         "description": "Jury was misdirected on provocation", "created_at": "2026-01-02T00:00:00"},
        {"issue_id": "iss_v3", "case_id": test_case_id, "user_id": test_user_id,
         "title": "New Evidence: Uncalled Witness Now Available", "ground_type": "fresh_evidence",
         "description": "Witness not called at trial", "created_at": "2026-01-02T00:00:00"},
    ]
    
    # Replace issues with variants
    await db.issue_classifications.delete_many({"case_id": test_case_id})
    for iss in variant_issues:
        await db.issue_classifications.insert_one(iss)
    
    # Run sync again
    for i in range(3):
        await simulate_sync()
        count = await db.grounds_of_merit.count_documents({"case_id": test_case_id})
        counts.append(count)
    
    print(f"  After variant sync (3 more runs): {counts}")
    
    # Clean up
    await db.grounds_of_merit.delete_many({"case_id": test_case_id})
    await db.issue_classifications.delete_many({"case_id": test_case_id})
    
    # All counts should be 3
    success = all(c == 3 for c in counts)
    if success:
        print(f"  PASS: Ground count stayed at 3 across all {len(counts)} sync runs (including variant titles)")
    else:
        print(f"  FAIL: Ground count varied: {counts} (expected all 3)")
    return success


async def main():
    print("=" * 60)
    print("GROUND DEDUPLICATION VERIFICATION TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(("Topic Coverage", test_topic_coverage()))
    results.append(("Duplicate Detection", test_duplicate_detection()))
    results.append(("Non-Duplicate Protection", test_non_duplicates()))
    results.append(("Australian Spelling", test_australian_spelling()))
    results.append(("DB Cleanup Function", await test_cleanup_function()))
    results.append(("Idempotent Sync", await test_idempotent_sync()))
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False
    
    if all_pass:
        print("\nALL TESTS PASSED — Deduplication is bulletproof.")
    else:
        print("\nSOME TESTS FAILED — Fix before deploying.")
    
    return all_pass

if __name__ == "__main__":
    asyncio.run(main())
