# Appeal Case Manager - Changelog

## 30 March 2026 — Tiered Auto-Verification in Report Generation

### Summary
Added priority-ranked auto-verification of classified issues during report generation, scaled by report tier.

### New Helpers
- `_issue_priority_rank()` — Sorts issues by ground type importance then confidence
- `_select_issues_for_auto_verification()` — Selects unverified issues up to a tier limit
- `_auto_verify_selected_issues()` — Runs pipeline verify on selected issues
- `_auto_verification_limit_for_report_type()` — `quick_summary`=0, `full_detailed`=3, `extensive_log`=6

### Behaviour
- `quick_summary`: No auto-verification (speed priority)
- `full_detailed`: Top 3 unverified issues auto-verified before draft
- `extensive_log`: Top 6 unverified issues auto-verified before draft
- Even when pipeline artifacts already exist, paid tiers still run auto-verification for unverified issues
- Result metadata attached: `pipeline_refresh_before_draft.auto_verify_result`

### Testing
- `quick_summary`: auto_verify_limit=0, attempted=0, verified=0 ✅
- `full_detailed`: auto_verify_limit=3, attempted=3, verified=3 ✅

---

## 30 March 2026 — Report Generation Pipeline Integration

### Summary
Patched `server.py` to refresh pipeline artifacts before report generation. Added staleness check so extraction/classification only runs when needed.

### What Changed
- Added 6 pipeline helpers to `server.py`: `_ensure_document_extracts_for_case`, `_refresh_case_extract_for_case`, `_ensure_issue_classifications`, `_pipeline_artifacts_missing_or_stale`, `_sync_pipeline_projection_to_grounds`, `_refresh_pipeline_for_reporting`
- `_run_report_generation` now runs a pipeline refresh (extract → classify → sync) before calling `analyze_case_with_ai` — only when artifacts are missing or stale
- Pipeline refresh result stored in report metadata (`pipeline_refresh_before_draft`)
- Non-fatal: if pipeline refresh fails, report generation still proceeds via legacy path

### Testing
- Report generation confirmed working with pipeline metadata attached
- Staleness check correctly skips when artifacts already exist
- All regression tests pass (health, cases, upload, grounds, barrister pack)

---

## 30 March 2026 — Grounds Router Pipeline Delegation

### Summary
Patched `grounds.py` to delegate `auto-identify` and `investigate` through the staged pipeline instead of raw single-pass LLM calls.

### What Changed
- `auto_identify_grounds()`: Now runs extract → refresh → classify → sync to grounds
- `investigate_ground_of_merit()`: Now runs pipeline verify → sync back to grounds
- `get_grounds_of_merit()`: Backfills `ground_id` for pipeline-synced grounds, enriches with `source_mode` and `verification_status`
- `get_ground_of_merit()`: Enriches legacy grounds with `source_mode` and `verification_status`
- Added 7 pipeline delegation helpers (`_ensure_document_extracts`, `_refresh_case_extract_from_pipeline`, `_classify_pipeline_issues`, `_sync_pipeline_issues_to_grounds`, `_ensure_pipeline_identification`, `_verify_issue_and_sync`)

### Architecture
- Pipeline collections (`document_extracts`, `case_extracts`, `issue_classifications`, `issue_verifications`) = **truth layer**
- `grounds_of_merit` = **compatibility/presentation layer** (projected from pipeline data)

### Testing
- Backend: 29/29 tests passed (100%) — iteration_132.json
- All CRUD operations verified (create, update, delete)
- All regression tests pass

---

## 30 March 2026 — 5-Stage Staged Pipeline Architecture

### Summary
Implemented decomposed pipeline service modules replacing monolithic inline LLM calls. New `/api/pipeline` router runs in parallel with existing `/api/cases` routes.

### New Files Created
- `backend/services/pipeline_models.py` — Strict Pydantic models (DocumentExtract, CaseExtract, IssueClassification, IssueVerification)
- `backend/services/pipeline/extract.py` — Document artifact extraction (facts, events, findings)
- `backend/services/pipeline/classify.py` — Appellate issue classification
- `backend/services/pipeline/verify.py` — Issue verification with legitimacy scoring
- `backend/services/pipeline/draft.py` — Report drafting from verified materials
- `backend/routers/pipeline_staged.py` — New router at `/api/pipeline` prefix

### Endpoints
- `POST /api/pipeline/cases/{id}/documents/{doc_id}/extract`
- `POST /api/pipeline/cases/{id}/extract/refresh`
- `POST /api/pipeline/cases/{id}/issues/classify`
- `POST /api/pipeline/cases/{id}/issues/{issue_id}/verify`
- `POST /api/pipeline/cases/{id}/grounds/sync-from-issues`
- `POST /api/pipeline/cases/{id}/reports/draft`

### Bug Fixes
- Fixed `missing_items` type error in Barrister Acceptance Pack PDF (strings vs dicts)
- Updated LLM task configs: `document_extraction` (8000 tokens, 90s), `issue_verification` (10000 tokens, 120s)

### Testing
- Backend: 27/27 tests passed (100%) — iteration_131.json
- All regression tests pass (health, cases, old pipeline, barrister pack)

---

## 30 March 2026 — Document Upload Timeout Fix (CRITICAL)

### Root Cause
The document upload endpoint (`POST /api/cases/{case_id}/documents`) was running an LLM metadata detection call **synchronously** within the upload request. This 60-second blocking call caused proxy/ingress timeouts and "Network Error" on mobile devices.

### Fix
- Moved LLM metadata detection into `_background_auto_detect_metadata()` background task
- Upload now returns immediately after saving to MongoDB (~200-500ms)
- Metadata detection runs asynchronously and updates case data in the background
- File: `/app/backend/routers/documents.py`

### Before vs After
- **Before:** Upload → Read file → Extract text → Insert to DB → **LLM call (60s)** → Return response = **60+ seconds**
- **After:** Upload → Read file → Extract text → Insert to DB → Return response → *(background: LLM call)* = **~200-500ms**

---

## 30 March 2026 — Barrister Acceptance Pack & Pipeline Progress Widget

### Summary
Completed and tested two P0 features: Barrister Acceptance Pack PDF export and Pipeline Progress widget.

### Barrister Acceptance Pack
- Backend: `GET /api/cases/{case_id}/barrister-pack/generate` returns downloadable PDF
- PDF contains: cover page, ranked grounds of merit, procedural timeline, evidence annexures, verification summary
- Frontend: Teal "Acceptance Pack" button added to BarristerView header toolbar
- iOS-compatible download via `iosShareOrDownload` utility

### Pipeline Progress Widget
- `PipelineProgress.jsx` verified rendering in CaseDetail Progress tab
- Displays 4 stages: Extract, Classify, Verify, Project
- Per-stage Run/Re-run buttons + "Run Full Pipeline" batch button
- Fetches live status from `/api/cases/{case_id}/pipeline/status`

### Testing
- Backend: 12/12 tests passed (100%) — iteration_130.json
- Frontend: All UI elements verified via Playwright

---

## 30 March 2026 — 5-Stage Pipeline Implementation

### Summary
Implemented the Extract → Classify → Verify → Project → Draft pipeline with 5 new MongoDB collections and 12 new API endpoints.

### New Collections
1. **document_extracts** — Per-document structured extraction (facts, events, findings)
2. **case_extracts** — Case-level merged extraction from all documents
3. **issue_classifications** — Candidate appeal issues after classification
4. **issue_verifications** — Structured support/undermine/missing verification layer

### New Endpoints (pipeline.py)
- `POST /api/cases/{case_id}/documents/{document_id}/extract` — per-doc extraction
- `POST /api/cases/{case_id}/extract/refresh` — merge to case-level
- `GET /api/cases/{case_id}/extract` — view merged extract
- `POST /api/cases/{case_id}/issues/classify` — classify issues
- `GET /api/cases/{case_id}/issues` — list issues
- `POST /api/cases/{case_id}/issues/{issue_id}/verify` — verify single issue
- `POST /api/cases/{case_id}/issues/verify-all` — batch verify
- `GET /api/cases/{case_id}/issues/{issue_id}/verification` — inspect verification
- `POST /api/cases/{case_id}/grounds/sync-from-issues` — project to grounds_of_merit
- `GET /api/cases/{case_id}/pipeline/status` — pipeline progress

### Pipeline Guardrails
- Extract stage: never classifies
- Classify stage: never verifies
- Verify stage: never drafts prose
- Draft stage: never invents new issues

### Testing
- Backend: 19/19 tests passed (100%)
- Pipeline verified with real case data: 2 docs extracted → 20 facts, 5 events, 5 findings → 5 issues classified → all verified → 5 grounds synced

## 30 March 2026 — Frontend Hardening Patch (Forensic Barrister Review)

### Summary
Implemented comprehensive frontend hardening patch in 3 phases. Created 6 reusable shared components and patched 9 existing files to display legitimacy scores, verification badges, evidence summaries, assessment notes, and report metadata.

### Components Created
1. **StrengthBadge.jsx**: STRONG/MODERATE/WEAK coloured badge
2. **VerificationBadge.jsx**: Draft/Unverified/Reviewed/Verified status
3. **LegitimacyPanel.jsx**: Legal basis, Evidence support, Appellate viability scores (X/3)
4. **EvidenceSummary.jsx**: Supporting evidence with filename + quote preview
5. **AssessmentNote.jsx**: Reusable disclaimer/assessment note block
6. **ReportMetadataPanel.jsx**: Model, fallback, documents analysed, verification status

### Phase 1 (Highest Credibility Impact)
- **GroundsOfMerit.jsx**: StrengthBadge, VerificationBadge, LegitimacyPanel, EvidenceSummary per ground card + detail dialog
- **CaseStrengthMeter.jsx**: Safe rendering (readinessLevel/readinessScore/assessmentNote), Appeal Preparation Readiness block
- **ReportsSection.jsx**: ReportMetadataPanel + AI-analysis warning per report

### Phase 2 (Misleading Analytics Removal)
- **CaseComparison.jsx**: AssessmentNote at top, insufficient data handling
- **DeadlineTracker.jsx**: Explanatory note, per-deadline jurisdiction/verification/source metadata

### Phase 3 (Professional Defensibility)
- **BarristerView.jsx**: BarristerGroundBlock (per-ground: StrengthBadge, VerificationBadge, LegitimacyPanel, EvidenceSummary, similar_cases), ReportMetadataPanel, AI-analysis footer
- **ReportView.jsx**: VerificationBadge, ReportMetadataPanel, AI-analysis warning
- **CaseDetail.jsx**: Review Status widget (unverified grounds, AI timeline events, draft reports), CaseStrengthMeter on Progress tab
- **CompareCasesPage.jsx**: AssessmentNote, insufficient data handling, 'Platform Pattern Indicators' label

### Text Replacements
- 'Case Strength' → 'Appeal Preparation Readiness'
- 'Success Factors' → 'Platform Pattern Indicators'
- 'Strong Grounds' → 'Higher Preparation Grounds'

### Testing
- Backend: 13/13 tests passed (100%)
- Frontend: 12/12 features verified (100%)
- Iterations: 126 (backend), 127 (frontend)

## 30 March 2026 — Backend Schema Hardening (Forensic Barrister Additive Patches)

### Summary
Completed 7/7 additive backend patches from the forensic barrister review. All patches harden data models, LLM services, and routers with strict provenance tracking, JSON-safe AI calls, and backward-compatible structured data models.

### Changes Applied
1. **models/__init__.py**: Typed submodels (EvidenceItem, LawSection, SimilarCase, LegitimacyScores, ReportMetadata) with ConfigDict(extra='ignore'). Fixed _NormaliserMixin with check_fields=False.
2. **llm_service.py**: call_llm_for_json (strict JSON parsing + retry), call_llm_for_report, call_llm_structured (provider/model fallback with metadata return).
3. **grounds.py**: Compatibility wrappers (_wrap_evidence_items) bridging legacy List[str] to EvidenceItem objects. Legitimacy scores returned per-ground.
4. **deadlines.py**: Ownership hardening (user_id checks), "Case Readiness" framing with assessment_note and assessment_type fields.
5. **compare.py**: Platform pattern framing, disclaimers and assessment_note on all endpoints. Removed pseudo-success language.
6. **timeline.py**: JSON-safe extraction via call_llm_for_json, provenance fields (source_mode, verification_status) on events.
7. **server.py**: Metadata detection via call_llm_for_json, report generation via call_llm_structured, ReportMetadata provenance on all generated reports (models_used, fallback_used, documents_analyzed, verification_status).

### Testing
- Backend: 13/13 tests passed (100%)
- Frontend: Homepage, login, dashboard all verified working
- Backward compatibility: All existing frontend data contracts maintained

## 21 March 2026 - Report Content Quality Overhaul (P0 Final Fix)

### Root Cause
The AI was writing ABOUT the analysis instead of DOING the analysis. Generic consultant-speak like "Delve into aggravating factors" and filler sections like "URGENCY PRIORITY: HELPFUL" were filling up word counts without providing any actual legal analysis.

### Fixes Applied
1. **Added hard anti-pattern guardrails** to the AI system prompt:
   - Explicit examples of WRONG vs RIGHT content (e.g., "Delve into..." vs actually applying s.21A to Homann's specific facts)
   - Banned filler section titles (URGENCY PRIORITY, RELEVANCE, KEY TAKEAWAY)
   - Required every paragraph to reference specific names, dates, section numbers, case citations, or document names
   - Required legislation sections to APPLY provisions to THIS case, not just describe what the Act covers
2. **Removed hardcoded boilerplate** — generic "RELIEF OPTIONS / PIVOT STRATEGY" text removed
3. **Fixed frontend parsers** — ReportView and BarristerView now only split on `## N.` main sections (20 sections, not 55+)
4. **Strengthened per-pass instructions** — each multi-pass chunk demands CASE-SPECIFIC analysis

### Content Quality Verification
- Zero garbage patterns found in new reports ("Delve into", "Leverage legal databases", "URGENCY PRIORITY", "RELEVANCE", "empirical trends", "Collate case law data", "KEY TAKEAWAY" — all CLEAN)
- Section 10 (Statutory Framework) now APPLIES s.18 and s.19A to Homann specifically
- Section 9 (Precedent Matrix) has 15+ real cases with full citations and specific factual parallels
- Section 8 (Evidence Gaps) has specific remediation steps referencing Dr Allnutt

### All 6 Reports Regenerated
| Report | Mode | Words | Sections |
|---|---|---|---|
| Quick Summary | Standard | 1,547 | 7 |
| Quick Summary | Aggressive | 1,386 | 7 |
| Full Detailed | Standard | 5,037 | 15 |
| Full Detailed | Aggressive | 6,028 | 15 |
| Extensive Log | Standard | 8,315 | 20 |
| Extensive Log | Aggressive | 8,271 | 20 |
