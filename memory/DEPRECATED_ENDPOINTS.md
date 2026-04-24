# Deprecated Pipeline Endpoints — Tracking Log

**Created:** 24 February 2026
**Scope:** Pipeline router endpoints on `/api/cases/*` that now have canonical twins on `/api/pipeline/*`
**Policy:** Marked deprecated — NOT deleted. Follow-up caller audit after a few commits before any removal.

---

## 1. Deprecated routes (6)

Each route below lives in `backend/routers/pipeline.py` and carries:
- `deprecated=True` on its `@router` decorator (surfaces as a strikethrough in FastAPI `/docs`)
- `[DEPRECATED 24 Feb 2026 → …]` banner at the top of its docstring

| # | Legacy route (deprecated) | Canonical twin |
|---|---|---|
| 1 | `POST /api/cases/{id}/documents/{doc}/extract` | `POST /api/pipeline/cases/{id}/documents/{doc}/extract` |
| 2 | `POST /api/cases/{id}/extract/refresh` | `POST /api/pipeline/cases/{id}/extract/refresh` |
| 3 | `POST /api/cases/{id}/issues/classify` | `POST /api/pipeline/cases/{id}/issues/classify` |
| 4 | `POST /api/cases/{id}/issues/{issue_id}/verify` | `POST /api/pipeline/cases/{id}/issues/{issue_id}/verify` |
| 5 | `POST /api/cases/{id}/issues/verify-batch` | `POST /api/pipeline/cases/{id}/issues/verify-batch` |
| 6 | `POST /api/cases/{id}/grounds/sync-from-issues` | `POST /api/pipeline/cases/{id}/grounds/sync-from-issues` |

## 2. Endpoints in `routers/pipeline.py` NOT deprecated (no staged twin exists)

Left untouched; still live:

- `GET /api/cases/{id}/extract`
- `GET /api/cases/{id}/issues`
- `POST /api/cases/{id}/issues/verify-all`
- `GET /api/cases/{id}/issues/{issue_id}/verification`
- `POST /api/cases/{id}/issues/{issue_id}/argue`
- `POST /api/cases/{id}/issues/argue-batch`
- `POST /api/cases/{id}/submissions-draft`
- `GET /api/cases/{id}/submissions-draft-view`
- `GET /api/cases/{id}/pipeline/status`

## 3. Current caller snapshot (as of 24 Feb 2026)

Frontend: **zero callers** on any of the 6 deprecated routes. Last migration (`verify-batch`) moved `frontend/src/components/PipelineProgress.jsx` and `frontend/src/components/ReportsSection.jsx` to the staged URL the same day.

Backend tests: **still referenced** in

- `tests/test_pipeline_endpoints.py` — integration tests against routes 1/2/3/6 + `verify-all` (non-deprecated) + `pipeline/status` (non-deprecated)
- `tests/test_pipeline_verification_iteration133.py` — integration tests against route 5
- `tests/test_verify_batch_staged.py::TestStagedLegacyParity` — intentionally tests route 5 to prove the legacy URL is preserved

These test references are NOT stale — they deliberately exercise the legacy routes to keep them alive until the removal decision.

## 4. Removal gate (must pass ALL before deletion)

Run the audit again with the following greps **after a few commits** and ONLY remove a deprecated route if it passes every gate:

```bash
# Gate A — frontend has zero callers of the deprecated URL
grep -rnE "api/cases/\\\$\{[^}]+\}/(documents/[^'\"]+/extract|extract/refresh|issues/classify|issues/[^/]+/verify\"|issues/verify-batch|grounds/sync-from-issues)" frontend/src --include="*.js" --include="*.jsx"

# Gate B — no non-test backend code calls the deprecated route internally
grep -rnE "api/cases/.+/(documents/.+/extract|extract/refresh|issues/classify|issues/.+/verify|issues/verify-batch|grounds/sync-from-issues)" backend --include="*.py" | grep -v "tests/" | grep -v "routers/pipeline.py"

# Gate C — the canonical twin has passing contract tests (see tests/test_verify_batch_staged.py + tests/test_pipeline_endpoints.py)

# Gate D — owner sign-off
```

## 5. Related supporting files

- `backend/services/pipeline_actions.py` — shared service-layer helpers both routers use (24 Feb 2026 refactor).
- `backend/services/pipeline_orchestrator.py` — imports helpers from the service layer, no longer from a router.
- `backend/tests/test_verify_batch_staged.py` — contract tests that assert both routes return the same response shape (regression guard during the deprecation window).

## 6. Log

- **24 Feb 2026** — 6 routes marked deprecated in code. Frontend fully migrated. Backend tests intentionally retained to keep legacy alive until audit re-run.
- **(pending)** — follow-up caller audit, Gate A+B+C+D, then per-route removal.
