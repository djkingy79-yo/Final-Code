"""
services/dedup_archive.py — archive-before-delete safety layer.

Added 24 Feb 2026 to make the three dedup code paths that physically delete
rows recoverable. The matching logic, thresholds, and delete calls are
UNCHANGED — this module adds one write per deleted row into a new
`dedup_archive` collection BEFORE the delete fires.

Every archive record has the locked shape:
    archive_id       : unique id for this archive row
    source_collection: 'grounds_of_merit' | 'issue_classifications' | 'document_extracts'
    case_id          : originating case_id (may be None for aggregation deletes)
    user_id          : originating user_id (may be None)
    original_id      : ground_id / issue_id / document_id (or Mongo _id fallback)
    original_record  : the full pre-delete document (no _id — JSON-safe copy)
    archived_at      : ISO-8601 UTC timestamp
    reason           : short tag describing why the record was archived
    dedup_run_id     : groups every archive row written in the same dedup pass

All three call sites use the same helper, so recovery tooling only has to
understand one schema.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Iterable


logger = logging.getLogger(__name__)


def new_dedup_run_id() -> str:
    """Generate a fresh run id per dedup invocation so all archive rows
    created in the same pass can be looked up as a group."""
    return f"ddr_{uuid.uuid4().hex[:16]}"


def _clean_record(doc: dict) -> dict:
    """Strip Mongo-local fields that are not JSON-safe. Returns a shallow
    copy — the original caller document is NOT mutated."""
    if not isinstance(doc, dict):
        return {"raw": str(doc)}
    out = {k: v for k, v in doc.items() if k != "_id"}
    return out


async def archive_records_before_delete(
    db,
    *,
    source_collection: str,
    records: Iterable[dict],
    id_field: str,
    reason: str,
    dedup_run_id: str,
) -> int:
    """Persist `records` to `db.dedup_archive` before the caller deletes them.

    Parameters
    ----------
    db                  : the Motor database handle the caller is about to delete from.
    source_collection   : 'grounds_of_merit' / 'issue_classifications' / 'document_extracts'.
    records             : iterable of full pre-delete documents.
    id_field            : which field of the record is the original business id
                          ('ground_id' / 'issue_id' / 'document_id'). When the
                          source collection uses only a Mongo _id (e.g. the
                          document_extracts startup dedup), callers should
                          pass id_field='_id' and include the stringified
                          _id in the record dict under '_id_str'.
    reason              : short human-readable label recorded on every row.
    dedup_run_id        : groups every archive row from this pass.

    Returns
    -------
    count of archive rows inserted.
    """
    records_list = list(records or [])
    if not records_list:
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    batch = []
    for doc in records_list:
        cleaned = _clean_record(doc)
        original_id = (
            cleaned.get(id_field)
            or cleaned.get("_id_str")
            or str(doc.get("_id"))  # final fallback — uses the untouched _id
        )
        batch.append({
            "archive_id": f"arc_{uuid.uuid4().hex[:16]}",
            "source_collection": source_collection,
            "case_id": cleaned.get("case_id"),
            "user_id": cleaned.get("user_id"),
            "original_id": original_id,
            "original_record": cleaned,
            "archived_at": now_iso,
            "reason": reason,
            "dedup_run_id": dedup_run_id,
        })

    if batch:
        try:
            await db.dedup_archive.insert_many(batch)
        except Exception as e:  # noqa: BLE001 — archive must not break dedup
            logger.error(
                f"dedup_archive insert failed ({source_collection}, "
                f"run={dedup_run_id}, n={len(batch)}): {e}"
            )
            # Do NOT re-raise — delete must still proceed. The archive is a
            # safety net, not a critical path. A persistent archive failure
            # surfaces as an error-level log that operators can monitor.
            return 0
    return len(batch)
