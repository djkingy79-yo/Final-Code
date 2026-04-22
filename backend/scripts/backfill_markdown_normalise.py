"""
One-off backfill: normalise markdown in every existing report and ground.

Idempotent — safe to run multiple times. Skips documents that are already
clean (no "inline ## Heading" or "- **Bullet:**" glued-to-prose patterns).

Run:
    cd /app/backend && python3 scripts/backfill_markdown_normalise.py
"""
import asyncio
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402
from services.md_normaliser import normalise_markdown  # noqa: E402


# Quick signature for "definitely-broken" markdown so we can count repairs
BROKEN_SIG = re.compile(
    r"[a-zA-Z0-9.][\s]{1,4}#{2,6}\s+[A-Z0-9]|[:.!?]\s*-\s\*\*[A-Z]"
)


async def run() -> None:
    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # ── Reports ──
    reports_total = reports_fixed = reports_already_clean = 0
    async for report in db.reports.find({"content.analysis": {"$exists": True}}):
        reports_total += 1
        content = report.get("content") or {}
        original = content.get("analysis") or ""
        if not original:
            continue
        normalised = normalise_markdown(original)
        if normalised == original:
            reports_already_clean += 1
            continue
        was_broken = bool(BROKEN_SIG.search(original))
        await db.reports.update_one(
            {"report_id": report["report_id"]},
            {"$set": {"content.analysis": normalised}},
        )
        reports_fixed += 1
        if was_broken:
            print(f"  REPAIRED report {report['report_id']} ({report.get('report_type')}): "
                  f"{len(original)} → {len(normalised)} chars")

    # ── Grounds (deep_analysis.full_analysis + analysis) ──
    grounds_total = grounds_fixed = 0
    async for g in db.grounds_of_merit.find(
        {"$or": [
            {"deep_analysis.full_analysis": {"$exists": True}},
            {"analysis": {"$exists": True, "$ne": ""}},
        ]}
    ):
        grounds_total += 1
        updates = {}
        deep = g.get("deep_analysis") or {}
        full_orig = deep.get("full_analysis") if isinstance(deep, dict) else None
        if full_orig:
            full_norm = normalise_markdown(full_orig)
            if full_norm != full_orig:
                updates["deep_analysis.full_analysis"] = full_norm
        analysis_orig = g.get("analysis")
        if analysis_orig:
            analysis_norm = normalise_markdown(analysis_orig)
            if analysis_norm != analysis_orig:
                updates["analysis"] = analysis_norm
        if updates:
            await db.grounds_of_merit.update_one(
                {"ground_id": g["ground_id"]},
                {"$set": updates},
            )
            grounds_fixed += 1

    print()
    print("=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"Reports scanned:  {reports_total}")
    print(f"Reports repaired: {reports_fixed}")
    print(f"Reports already clean: {reports_already_clean}")
    print(f"Grounds scanned:  {grounds_total}")
    print(f"Grounds repaired: {grounds_fixed}")


if __name__ == "__main__":
    asyncio.run(run())
