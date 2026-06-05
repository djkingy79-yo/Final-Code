#  — Database normalisation script.
# Migrates legacy loose-dict DB entries to the strict Pydantic structures.
# Safe to run multiple times (idempotent).
"""
Criminal Appeal AI — Database Normalisation Script
===================================================
Fixes missing fields, inconsistent data, and legacy structures across all collections.
Run via: python3 scripts/normalise_db.py
Or triggered via: POST /api/admin/normalise-db
"""
import asyncio
import os
import sys
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


async def normalise_cases(db) -> dict:
    """Normalise cases collection — add missing fields with safe defaults."""
    stats = {"updated": 0, "skipped": 0}
    now_iso = datetime.now(timezone.utc).isoformat()

    async for case in db.cases.find({}):
        updates = {}

        # Missing state → None (auto-detect will fill it on next doc upload)
        if "state" not in case:
            updates["state"] = None
        if "offence_category" not in case:
            updates["offence_category"] = None
        if "offence_type" not in case:
            updates["offence_type"] = None
        if "sentence" not in case:
            updates["sentence"] = None
        if "updated_at" not in case:
            updates["updated_at"] = case.get("created_at", now_iso)
        if "status" not in case:
            updates["status"] = "active"
        if "summary" not in case and "description" in case:
            updates["summary"] = case["description"]

        if updates:
            await db.cases.update_one({"_id": case["_id"]}, {"$set": updates})
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    logger.info(f"Cases: {stats['updated']} updated, {stats['skipped']} already normalised")
    return stats


async def normalise_grounds(db) -> dict:
    """Normalise grounds_of_merit — add missing source_mode, verification_status."""
    stats = {"updated": 0, "skipped": 0}

    async for ground in db.grounds_of_merit.find({}):
        updates = {}

        if "source_mode" not in ground:
            updates["source_mode"] = "legacy"
        if "verification_status" not in ground:
            updates["verification_status"] = "unverified"
        if "requires_human_review" not in ground:
            updates["requires_human_review"] = True
        if "legitimacy_scores" not in ground:
            updates["legitimacy_scores"] = {}
        if "supporting_evidence" not in ground:
            updates["supporting_evidence"] = []
        if "law_sections" not in ground:
            updates["law_sections"] = []
        if "similar_cases" not in ground:
            updates["similar_cases"] = []
        if "status" not in ground:
            updates["status"] = "identified"
        if "strength" not in ground:
            updates["strength"] = "moderate"
        if "updated_at" not in ground:
            updates["updated_at"] = ground.get("created_at", datetime.now(timezone.utc).isoformat())

        if updates:
            await db.grounds_of_merit.update_one({"_id": ground["_id"]}, {"$set": updates})
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    logger.info(f"Grounds: {stats['updated']} updated, {stats['skipped']} already normalised")
    return stats


async def normalise_reports(db) -> dict:
    """Normalise reports — add missing status field."""
    stats = {"updated": 0, "skipped": 0}

    async for report in db.reports.find({}):
        updates = {}

        if "status" not in report:
            # If it has content with analysis, it's completed
            content = report.get("content", {})
            if isinstance(content, dict) and content.get("analysis"):
                updates["status"] = "completed"
            elif report.get("verification_status") == "generated":
                updates["status"] = "completed"
            elif report.get("error"):
                updates["status"] = "failed"
            else:
                updates["status"] = "completed"

        if updates:
            await db.reports.update_one({"_id": report["_id"]}, {"$set": updates})
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    logger.info(f"Reports: {stats['updated']} updated, {stats['skipped']} already normalised")
    return stats


async def normalise_documents(db) -> dict:
    """Normalise documents — copy uploaded_at to created_at if missing."""
    stats = {"updated": 0, "skipped": 0}

    async for doc in db.documents.find({}):
        updates = {}

        if "created_at" not in doc:
            # Use uploaded_at as fallback
            uploaded_at = doc.get("uploaded_at")
            if uploaded_at:
                updates["created_at"] = uploaded_at
            else:
                updates["created_at"] = datetime.now(timezone.utc).isoformat()

        if "updated_at" not in doc:
            updates["updated_at"] = doc.get("created_at", doc.get("uploaded_at", datetime.now(timezone.utc).isoformat()))

        if updates:
            await db.documents.update_one({"_id": doc["_id"]}, {"$set": updates})
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    logger.info(f"Documents: {stats['updated']} updated, {stats['skipped']} already normalised")
    return stats


async def normalise_timeline_events(db) -> dict:
    """Normalise timeline_events — ensure date field exists (may use event_date)."""
    stats = {"updated": 0, "skipped": 0}

    async for event in db.timeline_events.find({}):
        updates = {}

        # Some events use event_date, the model expects date or event_date
        if "event_date" not in event and "date" in event:
            updates["event_date"] = event["date"]
        elif "event_date" not in event and "date" not in event:
            updates["event_date"] = datetime.now(timezone.utc).isoformat()

        if "event_type" not in event:
            updates["event_type"] = "other"

        if updates:
            await db.timeline_events.update_one({"_id": event["_id"]}, {"$set": updates})
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    logger.info(f"Timeline events: {stats['updated']} updated, {stats['skipped']} already normalised")
    return stats


async def normalise_issue_classifications(db) -> dict:
    """Normalise issue_classifications — add missing fields."""
    stats = {"updated": 0, "skipped": 0}

    async for issue in db.issue_classifications.find({}):
        updates = {}

        if "ground_type" not in issue:
            updates["ground_type"] = "other"
        if "status" not in issue:
            updates["status"] = "identified"
        if "classification_confidence" not in issue:
            updates["classification_confidence"] = "moderate"
        if "source_mode" not in issue:
            updates["source_mode"] = "ai_generated"
        if "verification_status" not in issue:
            updates["verification_status"] = "unverified"
        if "created_at" not in issue:
            updates["created_at"] = datetime.now(timezone.utc).isoformat()

        if updates:
            await db.issue_classifications.update_one({"_id": issue["_id"]}, {"$set": updates})
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    logger.info(f"Issue classifications: {stats['updated']} updated, {stats['skipped']} already normalised")
    return stats


async def cleanup_stale_sessions(db) -> dict:
    """Remove user sessions older than 30 days."""
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    result = await db.user_sessions.delete_many({"created_at": {"$lt": cutoff}})
    count = result.deleted_count

    # Also remove sessions without created_at (legacy)
    result2 = await db.user_sessions.delete_many({"created_at": {"$exists": False}})
    count += result2.deleted_count

    logger.info(f"Sessions: removed {count} stale/legacy sessions")
    return {"removed": count}


async def run_ground_dedup(db) -> dict:
    """Run the fuzzy dedup cleanup across all cases."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues

    pipeline_result = await db.grounds_of_merit.aggregate([
        {"$group": {"_id": {"case_id": "$case_id", "user_id": "$user_id"}}},
    ]).to_list(500)

    total_grounds_removed = 0
    total_issues_removed = 0

    for pair in pipeline_result:
        cid = pair["_id"]["case_id"]
        uid = pair["_id"]["user_id"]
        g_result = await cleanup_duplicate_grounds(db, cid, uid)
        i_result = await cleanup_duplicate_issues(db, cid, uid)
        total_grounds_removed += g_result["removed"]
        total_issues_removed += i_result["removed"]

    logger.info(f"Dedup: removed {total_grounds_removed} duplicate grounds, {total_issues_removed} duplicate issues")
    return {"grounds_removed": total_grounds_removed, "issues_removed": total_issues_removed}


async def normalise_all():
    """Run all normalisation steps."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    logger.info("=" * 60)
    logger.info("DATABASE NORMALISATION — Starting")
    logger.info("=" * 60)

    results = {}
    results["cases"] = await normalise_cases(db)
    results["grounds"] = await normalise_grounds(db)
    results["reports"] = await normalise_reports(db)
    results["documents"] = await normalise_documents(db)
    results["timeline_events"] = await normalise_timeline_events(db)
    results["issue_classifications"] = await normalise_issue_classifications(db)
    results["sessions"] = await cleanup_stale_sessions(db)
    results["dedup"] = await run_ground_dedup(db)

    logger.info("=" * 60)
    logger.info("DATABASE NORMALISATION — Complete")
    logger.info("=" * 60)

    total_updated = sum(r.get("updated", 0) for r in results.values())
    total_removed = results["sessions"].get("removed", 0) + results["dedup"].get("grounds_removed", 0) + results["dedup"].get("issues_removed", 0)
    logger.info(f"Total: {total_updated} documents updated, {total_removed} stale entries removed")

    return results


if __name__ == "__main__":
    asyncio.run(normalise_all())
