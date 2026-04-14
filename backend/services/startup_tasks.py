# DO NOT UNDO — startup_tasks.py. All startup logic extracted from server.py.
"""
Startup and shutdown tasks for the Criminal Appeal AI application.
- Database index creation
- Orphan report recovery
- Duplicate grounds cleanup
- Undersized report flagging
"""

from datetime import datetime, timezone, timedelta
from pymongo.errors import OperationFailure
from config import db, logger, client


async def _safe_create_index(collection, keys, **kwargs):
    """Create an index, dropping any conflicting index with the same name first."""
    try:
        await collection.create_index(keys, **kwargs)
    except OperationFailure:
        # Build the default index name MongoDB would use (e.g. "field1_1_field2_1")
        index_name = kwargs.get("name") or "_".join(f"{k}_{d}" for k, d in keys)
        try:
            await collection.drop_index(index_name)
        except OperationFailure:
            pass
        await collection.create_index(keys, **kwargs)


async def create_database_indexes():
    """Create indexes for ALL collections used by the app.
    MongoDB creates collections automatically on first write, but indexes
    must be ensured at startup to guarantee query performance in deployment.
    """
    # Core collections
    await _safe_create_index(db.users, [("user_id", 1)], unique=True)
    await _safe_create_index(db.users, [("email", 1)], unique=True)
    await _safe_create_index(db.cases, [("case_id", 1)], unique=True)
    await _safe_create_index(db.cases, [("user_id", 1)])
    await _safe_create_index(db.reports, [("report_id", 1)], unique=True)
    await _safe_create_index(db.reports, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.reports, [("case_id", 1), ("report_type", 1)])
    await _safe_create_index(db.documents, [("document_id", 1)], unique=True)
    await _safe_create_index(db.documents, [("case_id", 1), ("user_id", 1)])

    # Grounds and analysis
    await _safe_create_index(db.grounds_of_merit, [("ground_id", 1)], unique=True)
    await _safe_create_index(db.grounds_of_merit, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.grounds_of_merit, [("case_id", 1), ("priority_order", 1)])
    await _safe_create_index(db.issue_arguments, [("case_id", 1)])

    # Pipeline collections — compound indexes for query performance
    # DO NOT add unique indexes on *_id fields unless the model always generates them
    await _safe_create_index(db.document_extracts, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.document_extracts, [("document_id", 1), ("case_id", 1)], unique=True)
    await _safe_create_index(db.case_extracts, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.issue_classifications, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.issue_verifications, [("issue_id", 1), ("case_id", 1)])
    await _safe_create_index(db.pipeline_tasks, [("case_id", 1), ("user_id", 1), ("task_type", 1)])
    await _safe_create_index(db.pipeline_tasks, [("task_id", 1)], unique=True)

    # Auth and sessions
    await _safe_create_index(db.user_sessions, [("session_token", 1)], unique=True)
    await _safe_create_index(db.user_sessions, [("user_id", 1)])
    # TTL index removed - session cleanup handled manually
    await _safe_create_index(db.password_reset_tokens, [("token", 1)], unique=True)
    await _safe_create_index(db.password_reset_tokens, [("expires_at", 1)], expireAfterSeconds=0)

    # Case features
    await _safe_create_index(db.notes, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.timeline_events, [("case_id", 1)])
    await _safe_create_index(db.deadlines, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.checklist_items, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.submissions_drafts, [("case_id", 1), ("user_id", 1)])
    await _safe_create_index(db.activities, [("case_id", 1)])
    await _safe_create_index(db.contradiction_scans, [("case_id", 1)])

    # Payments
    await _safe_create_index(db.payments, [("user_id", 1)])
    await _safe_create_index(db.payments, [("case_id", 1)])
    await _safe_create_index(db.payments, [("payment_id", 1)], unique=True)

    # Sharing
    await _safe_create_index(db.case_shares, [("case_id", 1)])
    await _safe_create_index(db.share_links, [("link_id", 1)], unique=True)

    # Analytics
    await _safe_create_index(db.visits, [("timestamp", 1)])
    await _safe_create_index(db.visit_stats, [("date", 1)])
    await _safe_create_index(db.contact_messages, [("created_at", 1)])

    # Notifications
    await _safe_create_index(db.notifications, [("user_id", 1), ("read", 1)])
    await _safe_create_index(db.case_messages, [("case_id", 1)])

    # Counters
    await _safe_create_index(db.counters, [("name", 1)], unique=True)


async def recover_orphaned_reports():
    """Auto-fail or recover reports stuck in 'generating' from server restarts.

    DO_NOT_UNDO — Recovery uses minimum character targets to decide whether a partial
    report is complete enough to mark as finished, or needs re-generation.
    """
    min_recovery_targets = {
        "quick_summary": 10000,
        "full_detailed": 70000,
        "extensive_log": 120000,
    }

    five_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    async for report in db.reports.find({"status": "generating", "generated_at": {"$lt": five_min_ago}}):
        partial = report.get("content", {}).get("analysis", "") or report.get("content", {}).get("partial_analysis", "")
        report_type = report.get("report_type", "quick_summary")
        min_target = min_recovery_targets.get(report_type, 10000)

        if partial and len(partial) > 5000:
            if len(partial) >= min_target:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {"status": "completed", "content.analysis": partial, "content.partial": False}}
                )
                logger.info(f"Recovered complete report {report['report_id']} ({len(partial)} chars)")
            else:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {
                        "status": "failed",
                        "error": f"Generation interrupted after {report.get('content', {}).get('passes_completed', '?')}/8 passes ({len(partial)} chars). Click Generate to resume from where it stopped.",
                        "content.analysis": partial,
                        "content.partial": True,
                        "content.partial_analysis": partial,
                    }}
                )
                logger.info(f"Partial report {report['report_id']} below target ({len(partial)} < {min_target}), marked as failed for resume")
        else:
            # DO_NOT_UNDO — Restore from backup if available. When a user regenerates
            # a completed report and the generation fails, restore the old content
            # so they never lose their existing report.
            backup = report.get("content", {}).get("backup_analysis", "")
            if backup and len(backup) > 5000:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {
                        "status": "completed",
                        "error": None,
                        "content.analysis": backup,
                        "content.partial": False,
                    },
                    "$unset": {"content.backup_analysis": 1}}
                )
                logger.info(f"Restored report {report['report_id']} from backup ({len(backup)} chars)")
            else:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {"status": "failed", "error": "Generation interrupted by server restart. Please try again."}}
                )
                logger.info(f"Failed orphaned report {report['report_id']}")


async def flag_undersized_reports():
    """Flag existing undersized 'completed' reports (non-destructive).

    Add a flag to undersized reports so the UI can show a 'Regenerate for full depth' option.
    DO NOT change status from 'completed' — the user must still be able to VIEW their existing reports.
    """
    min_completed_targets = {
        "full_detailed": 70000,
        "extensive_log": 120000,
    }
    flagged_count = 0
    for rtype, min_chars in min_completed_targets.items():
        async for report in db.reports.find({"status": "completed", "report_type": rtype}):
            analysis = (report.get("content", {}).get("analysis") or "")
            if len(analysis) < min_chars:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {"content.below_target": True, "content.actual_chars": len(analysis), "content.target_chars": min_chars}}
                )
                flagged_count += 1
    if flagged_count:
        logger.info(f"Flagged {flagged_count} undersized reports on startup")

    # Also restore any reports that were accidentally set to "failed" by a previous migration
    # DO_NOT_UNDO — Only restore if the report actually meets the minimum target.
    # Reports below the target MUST stay failed so the user can regenerate them.
    for rtype, min_chars in min_completed_targets.items():
        async for report in db.reports.find({"status": "failed", "report_type": rtype}):
            analysis = (report.get("content", {}).get("analysis") or report.get("content", {}).get("partial_analysis") or "")
            if analysis and len(analysis) >= min_chars:
                await db.reports.update_one(
                    {"report_id": report["report_id"]},
                    {"$set": {
                        "status": "completed",
                        "content.analysis": analysis,
                        "content.partial": False,
                        "content.below_target": False,
                        "content.actual_chars": len(analysis),
                        "content.target_chars": min_chars,
                        "error": None,
                    }}
                )
                logger.info(f"Restored report {report['report_id']} to completed ({len(analysis)} chars >= {min_chars} target)")


async def dedup_grounds_on_startup():
    """DO_NOT_UNDO — Auto-cleanup duplicate grounds on every server start.

    Runs the fuzzy deduplication cleanup across ALL cases to merge any duplicates
    that slipped through before the dedup logic was fully applied.
    This prevents the recurring 'grounds multiplying' bug from ever persisting.
    """
    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues

    try:
        pipeline = [
            {"$group": {"_id": {"case_id": "$case_id", "user_id": "$user_id"}}},
        ]
        case_pairs = await db.grounds_of_merit.aggregate(pipeline).to_list(500)

        total_removed = 0
        for pair in case_pairs:
            cid = pair["_id"]["case_id"]
            uid = pair["_id"]["user_id"]
            result = await cleanup_duplicate_grounds(db, cid, uid)
            if result["removed"] > 0:
                total_removed += result["removed"]
            await cleanup_duplicate_issues(db, cid, uid)

        if total_removed > 0:
            logger.info(f"Startup dedup: removed {total_removed} duplicate grounds across {len(case_pairs)} cases")
        else:
            logger.info(f"Startup dedup: no duplicates found across {len(case_pairs)} cases")
    except Exception as e:
        logger.error(f"Startup dedup failed (non-fatal): {e}")


def shutdown_db():
    """Close the MongoDB client on shutdown."""
    client.close()
