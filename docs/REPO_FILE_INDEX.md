# Repository File Index

**Project:** Criminal Law Appeal Management (Appeal Case Manager)  
**Index Date:** 2026-04-24  
**Scope:** All non-binary, non-generated files excluding `.git/` internals

Key for **Status** column:
- **active** — in active use by production code
- **legacy** — superseded but deliberately retained (shim / back-compat)
- **duplicate** — overlaps another file's functionality
- **test** — test-only file
- **script** — CLI / one-off maintenance script
- **documentation** — docs / config / spec
- **asset** — images, fonts, static files
- **unknown** — not clearly categorised

---

## Backend — Core

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/server.py` | Python | FastAPI app factory; CORS, security headers, health checks, startup tasks, router wiring | `config`, `auth_utils`, `routers`, `services/startup_tasks`, `services/weekly_legislation_scan`, `fastapi`, `slowapi`, `starlette` | Entry point (Procfile/Dockerfile) | active |
| `backend/config.py` | Python | Env var validation, MongoDB async client, JSON logger, admin helpers, rate limiter | `motor`, `dotenv`, `os`, `logging` | `server.py`, virtually all routers and services | active |
| `backend/auth_utils.py` | Python | `get_current_user()`, `verify_case_ownership()`, download-token resolver | `config`, `models`, `fastapi` | All routers that require authentication | active |
| `backend/offence_framework.py` | Python | Back-compat shim: `from frameworks import *` | `frameworks` | `services/offence_helpers.py`, `services/report_generator.py` | legacy |
| `backend/models/__init__.py` | Python | All Pydantic data models (User, Case, Report, Ground, Document, ReportRequest, etc.) | `pydantic`, `typing`, `datetime`, `uuid` | Virtually all routers and services | active |
| `backend/pyproject.toml` | TOML | Ruff lint configuration | — | CI (`ruff check`) | documentation |
| `backend/pytest.ini` | INI | Pytest configuration (asyncio mode, test paths) | — | Test runner | documentation |
| `backend/requirements.txt` | Text | Python dependency list (~100 packages) | — | CI, Docker | documentation |
| `backend/Procfile` | Text | `uvicorn server:app` start command for Railway/Heroku | — | Platform process manager | documentation |

---

## Backend — Frameworks Package (Legal Data)

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/frameworks/__init__.py` | Python | Aggregated re-export of all framework symbols | All `frameworks/` submodules | `offence_framework.py` (shim), `national_framework_engine.py` | active |
| `backend/frameworks/jurisdictions.py` | Python | `AUSTRALIAN_STATES` (9 jurisdictions, court URLs), `LEGISLATION_CURRENCY` | — | `frameworks/__init__.py` | active |
| `backend/frameworks/states.py` | Python | `NSW/VIC/QLD/SA/WA/TAS/NT/ACT_CRIMINAL_FRAMEWORK` — primary legislation per state | — | `frameworks/__init__.py` | active |
| `backend/frameworks/federal.py` | Python | `FEDERAL_CRIMINAL_FRAMEWORK`, `FEDERAL_FAULT_ELEMENTS`, `PROCEEDS_OF_CRIME_FRAMEWORK` | — | `frameworks/__init__.py` | active |
| `backend/frameworks/appeal.py` | Python | `APPEAL_FRAMEWORK` (per-jurisdiction procedures, time limits, forms), `APPEAL_GROUNDS_ACCESSIBILITY` | — | `frameworks/__init__.py` | active |
| `backend/frameworks/sentencing.py` | Python | `SENTENCING_FRAMEWORK` — sentencing acts and key provisions per jurisdiction | — | `frameworks/__init__.py` | active |
| `backend/frameworks/evidence.py` | Python | `EVIDENCE_FRAMEWORK` — uniform evidence law + state-specific acts | — | `frameworks/__init__.py` | active |
| `backend/frameworks/mental_impairment.py` | Python | `MENTAL_IMPAIRMENT_FRAMEWORK` — per-jurisdiction tests and legislation | — | `frameworks/__init__.py` | active |
| `backend/frameworks/procedure.py` | Python | Procedural flows (indictable/hybrid/summary, 13 stages), `MENS_REA_FRAMEWORK` | — | `frameworks/__init__.py` | active |
| `backend/frameworks/offences.py` | Python | `OFFENCE_CATEGORIES` — 18 offence categories with elements, legislation, fault elements | — | `frameworks/__init__.py` | active |
| `backend/frameworks/common_grounds.py` | Python | `COMMON_APPEAL_GROUNDS` — standard appellate grounds | — | `frameworks/__init__.py` | active |
| `backend/frameworks/human_rights.py` | Python | `HUMAN_RIGHTS_FRAMEWORK` — human rights instruments relevant to appeals | — | `frameworks/__init__.py` | active |
| `backend/frameworks/landmark_cases.py` | Python | `LANDMARK_CASES` — key Australian criminal appeal precedents | — | `frameworks/__init__.py` | active |
| `backend/frameworks/recent_updates.py` | Python | `RECENT_LEGISLATION_UPDATES` — recent legislative amendments | — | `frameworks/__init__.py` | active |
| `backend/frameworks/legislation_registry.py` | Python | Legislation currency registry: per-Act verification dates, AustLII URLs | — | `services/legislation_currency.py` | active |

---

## Backend — Routers

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/routers/__init__.py` | Python | Centralised router registry; `register_all_routers()` | All `routers/*.py` | `server.py` | active |
| `backend/routers/auth.py` | Python | Email/password auth, Google OAuth, sign-out, session management | `config`, `auth_utils`, `fastapi`, `httpx`, `hashlib` | `routers/__init__.py` | active |
| `backend/routers/password_reset.py` | Python | Email-based password reset flow | `config`, `auth_utils`, `services/email_service` | `routers/__init__.py` | active |
| `backend/routers/cases.py` | Python | Case CRUD endpoints | `config`, `auth_utils`, `models` | `routers/__init__.py` | active |
| `backend/routers/documents.py` | Python | Document upload, OCR extraction, listing, deletion | `config`, `auth_utils`, `services/document_helpers` | `routers/__init__.py` | active |
| `backend/routers/timeline.py` | Python | Timeline entry management and AI generation | `config`, `auth_utils`, `services/llm_service` | `routers/__init__.py` | active |
| `backend/routers/grounds.py` | Python | Grounds CRUD, AI identification, pathway display, ground normalisation | `config`, `auth_utils`, `services/llm_service`, `services/ground_dedup`, `services/ground_normaliser`, `services/jurisdiction_rules` | `routers/__init__.py` | active |
| `backend/routers/notes.py` | Python | Notes CRUD + WebSocket real-time collaboration | `config`, `auth_utils`, `services/notes_helpers` | `routers/__init__.py` | active |
| `backend/routers/reports.py` | Python | Report generation triggers, streaming progress, CRUD | `config`, `auth_utils`, `models`, `services/report_generator`, `services/barrister_generator` | `routers/__init__.py` | active |
| `backend/routers/report_exports.py` | Python | PDF (ReportLab) and DOCX (python-docx) export of reports | `config`, `auth_utils`, `services/offence_helpers`, `services/report_quality`, `services/barrister_generator`, `reportlab`, `docx` | `routers/__init__.py` | active |
| `backend/routers/export.py` | Python | ZIP export of full case package (Quick Export) | `config`, `auth_utils`, `zipfile`, `io` | `routers/__init__.py` | active |
| `backend/routers/pipeline.py` | Python | Staged pipeline API (extract/classify/verify/argue/submit) | `config`, `auth_utils`, `services/llm_service`, `services/pipeline/verify`, `services/pipeline/argue`, `services/pipeline/submit` | `routers/__init__.py` | active |
| `backend/routers/pipeline_staged.py` | Python | Extended staged pipeline with finer-grained endpoints; private `_` helpers used by `pipeline_orchestrator` | `config`, `auth_utils`, `services/pipeline` | `routers/__init__.py`, `services/pipeline_orchestrator` | active |
| `backend/routers/analysis.py` | Python | On-demand case analysis endpoint | `config`, `auth_utils`, `services/llm_service` | `routers/__init__.py` | active |
| `backend/routers/barrister_pack.py` | Python | Barrister Acceptance Pack PDF generator | `config`, `auth_utils`, `reportlab` | `routers/__init__.py` | active |
| `backend/routers/barrister_tools.py` | Python | Crown Response Simulator + Fresh Evidence Gallagher Wizard | `config`, `auth_utils`, `services/llm_service` | `routers/__init__.py` | active |
| `backend/routers/compare.py` | Python | Side-by-side case comparison | `config`, `auth_utils`, `services/llm_service` | `routers/__init__.py` | active |
| `backend/routers/contradictions.py` | Python | Contradiction detection between documents | `config`, `auth_utils`, `services/llm_service` | `routers/__init__.py` | active |
| `backend/routers/caselaw.py` | Python | Case law search URL generation (AustLII + state databases) | `config`, `auth_utils`, `services/caselaw_search` | `routers/__init__.py` | active |
| `backend/routers/legislation.py` | Python | Legal framework data endpoint | `config`, `auth_utils`, `offence_framework` | `routers/__init__.py` | active |
| `backend/routers/legislation_alerts.py` | Python | Legislation amendment alerts listing | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/translate.py` | Python | LLM-powered report translation | `config`, `auth_utils`, `services/llm_service` | `routers/__init__.py` | active |
| `backend/routers/collaboration.py` | Python | Case sharing and access-link management | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/deadlines.py` | Python | Deadline CRUD | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/admin.py` | Python | Admin: user management, stats, DB tools, legislation management | `config`, `auth_utils`, `services/legislation_currency` | `routers/__init__.py` | active |
| `backend/routers/analytics.py` | Python | Signup source tracking, conversion analytics | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/statistics.py` | Python | Aggregated appeal statistics | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/payments.py` | Python | PayID payment recording and case feature unlocking | `config`, `auth_utils`, `models`, `services/email_service` | `routers/__init__.py` | active |
| `backend/routers/payment_history.py` | Python | Payment history endpoints | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/resources.py` | Python | Legal resources data | `config`, `auth_utils` | `routers/__init__.py` | active |
| `backend/routers/utilities.py` | Python | Misc utilities (download token generation) | `config`, `auth_utils` | `routers/__init__.py` | active |

---

## Backend — Services

### LLM Gateway

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/llm_service.py` | Python | Core LLM gateway: model selection, retry, fallback, JSON extraction, report streaming | `openai`, `os`, `asyncio`, `logging` | `report_generator`, `barrister_generator`, `pipeline/*`, all routers that call LLM directly | active |
| `backend/services/ai_service.py` | Python | Legacy `call_llm_with_retry()` wrapper | `os`, `asyncio`, `logging` | **Test files only** — zero production imports | legacy |
| `backend/services/ai_usage_tracker.py` | Python | Token/cost recording → `ai_usage` MongoDB collection | `config`, `openai`, `tiktoken`, `asyncio` | `services/llm_service` | active |

### Report Generation

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/report_generator.py` | Python | Multi-pass AI report generation engine (8-pass and 10-pass modes) | `config`, `services/llm_service`, `services/offence_helpers`, `services/document_helpers`, `services/report_quality`, `services/pipeline_orchestrator`, `offence_framework`, `models` | `routers/reports.py` | active |
| `backend/services/report_quality.py` | Python | Post-generation text cleanup (anchor terms, dedup, strip placeholders, sanitise authorities) | `services/offence_helpers` | `services/report_generator`, `services/barrister_generator`, `routers/report_exports` | active |
| `backend/services/barrister_generator.py` | Python | Appellate Research Brief (Barrister View) generation | `config`, `services/llm_service`, `services/offence_helpers`, `services/report_quality` | `routers/reports.py`, `routers/report_exports.py` | active |

### Pipeline (Staged)

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/pipeline_models.py` | Python | Pipeline-specific Pydantic models (DocumentExtract, CaseExtract, IssueClassification, IssueVerification) | `models`, `pydantic` | `services/pipeline/*`, `services/pipeline_orchestrator` | active |
| `backend/services/pipeline_orchestrator.py` | Python | Orchestration helpers (freshness enforcement, arg loading, submission loading) | `config`, `services/pipeline`, `services/pipeline_models`, `routers/pipeline_staged` | `services/report_generator` | active |
| `backend/services/pipeline/__init__.py` | Python | Re-exports all pipeline step functions | `services/pipeline/extract`, `services/pipeline/classify`, `services/pipeline/verify`, `services/pipeline/draft`, `services/pipeline/argue`, `services/pipeline/submit` | `services/pipeline_orchestrator`, `routers/pipeline.py`, `routers/pipeline_staged.py` | active |
| `backend/services/pipeline/extract.py` | Python | Step 1: extract facts/events/findings from documents via LLM | `services/llm_service`, `services/pipeline_models` | `services/pipeline/__init__` | active |
| `backend/services/pipeline/classify.py` | Python | Step 2: classify issues into 5 canonical ground types | `services/llm_service`, `services/pipeline_models`, `services/offence_helpers` | `services/pipeline/__init__` | active |
| `backend/services/pipeline/verify.py` | Python | Step 3: verify issues; legitimacy scoring | `services/llm_service`, `services/legitimacy_engine`, `services/pipeline_models` | `services/pipeline/__init__` | active |
| `backend/services/pipeline/draft.py` | Python | Step 4: draft report sections from verified material | `services/llm_service` | `services/pipeline/__init__` | active |
| `backend/services/pipeline/argue.py` | Python | Step 5: build counsel-style argument per ground | `services/llm_service` | `services/pipeline/__init__` | active |
| `backend/services/pipeline/submit.py` | Python | Step 6: draft formal submissions document | `services/llm_service` | `services/pipeline/__init__` | active |

### Jurisdiction & Legal Framework Engines

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/national_framework.py` | Python | Inline jurisdiction matrix; `build_full_system_prompt()`, `build_national_appellate_context()` | (self-contained — inline data) | `services/report_generator` (lazy import) | active / duplicate |
| `backend/services/national_framework_engine.py` | Python | Full context builder from `frameworks/`; `build_national_case_context()`, `build_framework_dict()` | `frameworks/offences`, `frameworks/jurisdictions`, `frameworks/appeal`, `frameworks/sentencing`, `frameworks/evidence`, `frameworks/mental_impairment`, `frameworks/procedure` | `services/offence_helpers` (lazy import) | active / duplicate |
| `backend/services/jurisdiction_rules.py` | Python | Per-jurisdiction rule sets for ground normalisation | — | `services/ground_normaliser` | active |
| `backend/services/offence_helpers.py` | Python | LLM context assembler; builds offence/procedure/mens rea context blocks from frameworks data | `offence_framework` (shim) | `services/report_generator`, `services/barrister_generator`, `services/pipeline/classify`, `services/report_quality`, `routers/report_exports` | active |

### Ground Processing Chain

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/ground_normaliser.py` | Python | Normalise AI-generated grounds (type, viability, pathway) | `services/jurisdiction_rules` | `services/ground_cleanup`, `services/proviso_engine`, `services/barrister_mode`, `services/appeal_strength`, `services/attack_plan` | active |
| `backend/services/ground_cleanup.py` | Python | Post-normalisation cleanup (terminology, mixed-category artifacts) | `services/ground_normaliser` | `routers/grounds.py` (ground processing) | active |
| `backend/services/ground_dedup.py` | Python | Duplicate ground prevention (three-method: fuzzy + word overlap + topic) | `fuzzywuzzy`, `re` | `routers/grounds.py`, `services/pipeline_orchestrator`, `services/startup_tasks` | active |
| `backend/services/appeal_strength.py` | Python | Realism scoring: record support, proviso risk, Crown response strength | `services/ground_normaliser` | Ground processing pipeline | active |
| `backend/services/barrister_mode.py` | Python | Strategy ranking: primary / secondary / tertiary / abandon | `services/ground_normaliser` | `services/attack_plan`, `services/proviso_engine`, `services/outcome_predictor` | active |
| `backend/services/proviso_engine.py` | Python | Proviso exposure narrative (Weiss v The Queen 2005) | `services/ground_normaliser` | Report rendering pipeline | active |
| `backend/services/outcome_predictor.py` | Python | Appellate outcome category prediction | — | Report rendering pipeline | active |
| `backend/services/legitimacy_engine.py` | Python | Three-axis viability scoring (outcome × legal alignment × evidence) | — | `services/pipeline/verify` | active |
| `backend/services/attack_plan.py` | Python | Counsel-style attack plan per ground (strategy, gaps, Crown counter, steps) | — | Report rendering pipeline | active |

### Document & Evidence

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/document_helpers.py` | Python | PDF/DOCX/image/TXT text extraction, OCR preprocessing, context builder | `pypdf`, `PIL`, `pytesseract`, `docx` | `services/report_generator`, `routers/documents` | active |
| `backend/services/evidence_builder.py` | Python | Affidavit templates and document request plans per ground | — | Report rendering pipeline | active |

### Legislation

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/legislation_checker.py` | Python | AustLII/legislation.gov.au section reference validator (async HTTP) | `httpx`, `asyncio` | `routers/admin` (on-demand validation) | active |
| `backend/services/legislation_currency.py` | Python | Legislation currency dashboard build + AI cross-check | `frameworks/legislation_registry`, `services/llm_service`, `config` | `routers/admin` | active |
| `backend/services/weekly_legislation_scan.py` | Python | Scheduled Monday 09:00 AEST amendment scan (asyncio background task) | `config`, `services/legislation_currency` | `server.py` (startup task) | active |

### Misc Services

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `backend/services/caselaw_search.py` | Python | AustLII + state DB search URL generator | `urllib.parse` | `routers/caselaw` | active |
| `backend/services/case_validation.py` | Python | Soft metadata validation + citation hallucination detection | `re` | `services/report_generator` | active |
| `backend/services/email_service.py` | Python | Payment notification emails via Resend API | `resend`, `config` | `routers/payments`, `routers/password_reset` | active |
| `backend/services/export_footer.py` | Python | Shared PDF/DOCX footer utilities (Times New Roman 7pt, page numbers, OOXML) | `datetime` | `routers/report_exports`, `routers/barrister_pack` | active |
| `backend/services/md_normaliser.py` | Python | Markdown whitespace normaliser (intentionally mirrors `frontend/src/utils/mdRender.js`) | `re` | `services/startup_tasks`, `scripts/backfill_markdown_normalise` | active |
| `backend/services/notes_helpers.py` | Python | WebSocket connection tracking for real-time notes | `fastapi`, `config` | `routers/notes` | active |
| `backend/services/startup_tasks.py` | Python | DB index creation, orphan report recovery, dedup, markdown backfill on startup | `config`, `services/ground_dedup`, `services/md_normaliser` | `server.py` | active |

---

## Backend — Tests

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `backend/tests/conftest.py` | Python | Shared pytest fixtures (DB mocking, test case fixtures) | test |
| `backend/tests/test_api.py` | Python | General API smoke tests | test |
| `backend/tests/test_health_api.py` | Python | Health endpoint tests | test |
| `backend/tests/test_legal_framework.py` | Python | Framework data integrity checks | test |
| `backend/tests/test_offence_framework.py` | Python | Offence category tests | test |
| `backend/tests/test_offence_framework_integrity.py` | Python | Integrity checks on all 18 offence categories (run in CI) | test |
| `backend/tests/test_frameworks_refactor.py` | Python | P2 refactor regression (frameworks/ package) | test |
| `backend/tests/test_framework_gap_fill_20260214.py` | Python | 12 tests for Feb 2026 framework gap fill | test |
| `backend/tests/test_legislation_framework.py` | Python | Legislation registry tests (run in CI) | test |
| `backend/tests/test_legislation_currency.py` | Python | Currency service tests | test |
| `backend/tests/test_ground_dedup.py` | Python | Dedup algorithm tests (run in CI, including integration tests) | test |
| `backend/tests/test_ground_cleanup.py` | Python | Cleanup layer tests | test |
| `backend/tests/test_ground_cleanup_round2.py` | Python | Second-round cleanup regression | test |
| `backend/tests/test_ground_counsel_round3.py` | Python | Counsel round 3 ground tests | test |
| `backend/tests/test_ground_invariants.py` | Python | Ground field invariant tests | test |
| `backend/tests/test_ground_pipeline.py` | Python | End-to-end ground pipeline tests | test |
| `backend/tests/test_grounds_pipeline_iteration132.py` | Python | Regression test iteration 132 | test |
| `backend/tests/test_pipeline_endpoints.py` | Python | Pipeline API endpoint tests | test |
| `backend/tests/test_pipeline_verification_iteration133.py` | Python | Verification regression iteration 133 | test |
| `backend/tests/test_staged_pipeline_iteration131.py` | Python | Staged pipeline regression iteration 131 | test |
| `backend/tests/test_national_framework.py` | Python | `national_framework.py` module tests | test |
| `backend/tests/test_national_framework_engine.py` | Python | `national_framework_engine.py` tests | test |
| `backend/tests/test_legitimacy_engine.py` | Python | Legitimacy scoring tests | test |
| `backend/tests/test_outcome_predictor.py` | Python | Outcome prediction tests | test |
| `backend/tests/test_proviso_and_barrister_mode.py` | Python | Proviso engine + strategy ranking tests | test |
| `backend/tests/test_report_generation.py` | Python | Full report generation flow tests | test |
| `backend/tests/test_report_prompt_quality.py` | Python | Prompt quality/format checks | test |
| `backend/tests/test_report_progress_iteration203.py` | Python | Streaming progress regression iteration 203 | test |
| `backend/tests/test_ai_usage_tracker.py` | Python | Token/cost tracking tests (24 tests) | test |
| `backend/tests/test_document_exports.py` | Python | PDF/DOCX export tests | test |
| `backend/tests/test_export_endpoints_iteration201.py` | Python | Export endpoint regression iteration 201 | test |
| `backend/tests/test_extract_all_text_iteration202.py` | Python | Text extraction regression iteration 202 | test |
| `backend/tests/test_barrister_pack_pipeline.py` | Python | Barrister pack generation tests | test |
| `backend/tests/test_barrister_view_iteration27.py` | Python | Barrister view regression iteration 27 | test |
| `backend/tests/test_counsel_briefing.py` | Python | Counsel briefing block tests | test |
| `backend/tests/test_attack_plan_refine.py` | Python | Attack plan tests | test |
| `backend/tests/test_evidence_builder_refine.py` | Python | Evidence builder tests | test |
| `backend/tests/test_collaboration_features.py` | Python | Case sharing/collaboration tests | test |
| `backend/tests/test_compare_contradictions.py` | Python | Compare and contradiction detection tests | test |
| `backend/tests/test_ai_features_iteration26.py` | Python | AI feature regression iteration 26 | test |
| `backend/tests/test_auto_identify_background.py` | Python | Background auto-identification tests | test |
| `backend/tests/test_comprehensive_iteration_199.py` | Python | Comprehensive regression iteration 199 | test |
| `backend/tests/test_iteration193_bugfixes.py` | Python | Bug fix regression iteration 193 | test |
| `backend/tests/test_iteration_208_features.py` | Python | Feature regression iteration 208 | test |
| `backend/tests/test_state_offence_framework.py` | Python | State-specific offence framework tests | test |
| `backend/tests/test_signup_source_tracking.py` | Python | Analytics tracking tests | test |
| `backend/tests/test_openai_costs_endpoint.py` | Python | OpenAI cost endpoint tests | test |
| `backend/tests/test_translate_parallel_recovery.py` | Python | Translation parallel recovery tests | test |

---

## Backend — Scripts

| Path | Language/Type | Purpose | Imports From | Status |
|------|---------------|---------|--------------|--------|
| `backend/scripts/repair_report.py` | Python | CLI: targeted LLM repair of thin/missing report sections | `config`, `services/llm_service`, `motor`, `dotenv` | script |
| `backend/scripts/normalise_db.py` | Python | CLI: idempotent DB migration to strict Pydantic structures | `config`, `motor` | script |
| `backend/scripts/backfill_markdown_normalise.py` | Python | CLI: one-off markdown normalisation on all DB records | `config`, `services/md_normaliser` | script |

---

## Frontend — Entry & Config

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `frontend/src/App.js` | JS/JSX | Root React component: routing (React Router 7), Google OAuth CSRF, global axios interceptor, layout shell | `react`, `react-router-dom`, `axios`, `sonner`, all page components (lazy), `components/ui/sonner`, `components/InstallPrompt`, `components/PageViewTracker`, `components/TermsAcceptance`, `components/FastScrollTop`, `contexts/ThemeContext`, `components/AppFooter`, `components/OfflineBanner`, `native/appLifecycle`, `lib/oauthState` | `index.js` | active |
| `frontend/src/index.js` | JS | React DOM render, PWA service worker registration | `react-dom`, `App`, service worker | App entry point | active |
| `frontend/src/App.css` | CSS | Global component styles | — | `App.js` | active |
| `frontend/src/index.css` | CSS | Tailwind base styles + global resets | — | `index.js` | active |
| `frontend/tailwind.config.js` | JS | Tailwind CSS configuration (design tokens, content paths) | — | Build system | documentation |
| `frontend/craco.config.js` | JS | CRACO build override (enforces `REACT_APP_BACKEND_URL` at build time) | — | Build system | documentation |
| `frontend/package.json` | JSON | NPM/Yarn dependencies and scripts | — | Package manager | documentation |
| `frontend/capacitor.config.json` | JSON | Capacitor app ID (`com.criminallawappeal.app`), server URL config | — | `npx cap sync` | documentation |
| `frontend/components.json` | JSON | Shadcn/UI component configuration | — | Shadcn CLI | documentation |
| `frontend/jsconfig.json` | JSON | JS path aliases for IDE support | — | IDE / build | documentation |
| `frontend/postcss.config.js` | JS | PostCSS config (Tailwind + Autoprefixer) | — | Build system | documentation |
| `frontend/.eslintrc.json` | JSON | ESLint config (legacy format) | — | Lint | documentation |
| `frontend/eslint.config.js` | JS | ESLint flat config | — | Lint | documentation |
| `frontend/build-mobile.sh` | Shell | Mobile build script: `npx cap sync` + open iOS/Android | — | Developer CLI | script |
| `frontend/MOBILE_BUILD.md` | Markdown | Mobile build instructions | — | — | documentation |

---

## Frontend — Pages

| Path | Language/Type | Purpose | Imports From | Status |
|------|---------------|---------|--------------|--------|
| `frontend/src/pages/LandingPage.jsx` | JSX | Public home page with feature highlights and CTAs | `axios`, UI components, `App` (API const) | active |
| `frontend/src/pages/Dashboard.jsx` | JSX | Case list, new case creation, pipeline summary | `axios`, `components/DashboardPipelineSummary`, `components/AiCostBadge` | active |
| `frontend/src/pages/CaseDetail.jsx` | JSX | Master case page: all tabs (documents, timeline, grounds, notes, reports, barrister) | `axios`, all case-section components, `utils/exportHtml`, `utils/downloadToken` | active |
| `frontend/src/pages/ReportView.jsx` | JSX | Standard report viewer with PDF/Word/Print export | `axios`, `utils/exportHtml`, `utils/mdRender`, `utils/downloadToken`, `components/ExportOptionsModal` | active |
| `frontend/src/pages/BarristerView.jsx` | JSX | Appellate Research Brief viewer with custom export builder | `axios`, `utils/exportHtml`, `utils/mdRender`, `utils/downloadToken` | active |
| `frontend/src/pages/AdminDashboard.jsx` | JSX | Admin panel: users, legislation, AI costs | `axios`, `components/OpenAICostsPanel` | active |
| `frontend/src/pages/AdminStats.jsx` | JSX | High-level admin statistics | `axios` | active |
| `frontend/src/pages/SignupSourceAnalytics.jsx` | JSX | Signup source + conversion tracking dashboard | `axios`, `recharts` | active |
| `frontend/src/pages/LegalFrameworkPage.jsx` | JSX | Legal framework viewer (all jurisdictions/categories) | `axios`, `components/LegalFrameworkViewer` | active |
| `frontend/src/pages/LegislationCurrency.jsx` | JSX | Legislation currency dashboard | `axios` | active |
| `frontend/src/pages/CaselawSearchPage.jsx` | JSX | Case law search interface | `axios` | active |
| `frontend/src/pages/AppealStatisticsPage.jsx` | JSX | Appeal outcome statistics | `axios`, `recharts` | active |
| `frontend/src/pages/CompareCasesPage.jsx` | JSX | Side-by-side case comparison | `axios` | active |
| `frontend/src/pages/HelpPage.jsx` | JSX | Help content | — | active |
| `frontend/src/pages/HowToUsePage.jsx` | JSX | Step-by-step usage guide with screenshots | — | active |
| `frontend/src/pages/HowItWorksPage.jsx` | JSX | How the app works explanation | — | active |
| `frontend/src/pages/AboutPage.jsx` | JSX | About / Deb King founder info | — | active |
| `frontend/src/pages/LegalResourcesPage.jsx` | JSX | Legal resources directory | `axios` | active |
| `frontend/src/pages/ResourcesPage.jsx` | JSX | General resources | — | active |
| `frontend/src/pages/LegalGlossary.jsx` | JSX | Legal term glossary | — | active |
| `frontend/src/pages/LawyerDirectory.jsx` | JSX | Lawyer directory | — | active |
| `frontend/src/pages/FormTemplates.jsx` | JSX | Downloadable form templates | — | active |
| `frontend/src/pages/FAQPage.jsx` | JSX | FAQ | — | active |
| `frontend/src/pages/SuccessStories.jsx` | JSX | Success stories | — | active |
| `frontend/src/pages/Statistics.jsx` | JSX | Public statistics | `axios`, `recharts` | active |
| `frontend/src/pages/PaymentHistoryPage.jsx` | JSX | User payment history | `axios` | active |
| `frontend/src/pages/ProfessionalSummary.jsx` | JSX | Professional summary view | `axios` | active |
| `frontend/src/pages/DocumentPreviewPage.jsx` | JSX | In-browser document preview | `axios`, `react-pdf` | active |
| `frontend/src/pages/AcceptShareLink.jsx` | JSX | Accept a shared case invitation | `axios` | active |
| `frontend/src/pages/ForgotPasswordPage.jsx` | JSX | Forgot password form | `axios` | active |
| `frontend/src/pages/ResetPasswordPage.jsx` | JSX | Password reset form (token from URL) | `axios` | active |
| `frontend/src/pages/TermsOfService.jsx` | JSX | Terms of service | — | active |

---

## Frontend — Components (Business)

| Path | Language/Type | Purpose | Imports From | Status |
|------|---------------|---------|--------------|--------|
| `frontend/src/components/ActivityFeed.jsx` | JSX | Recent case activity feed | `axios`, UI | active |
| `frontend/src/components/AiCostBadge.jsx` | JSX | Per-report AI cost display badge | `axios` | active |
| `frontend/src/components/AppFooter.jsx` | JSX | Site footer with branding ("Founded by Debra King") | UI | active |
| `frontend/src/components/AppealChecklist.jsx` | JSX | Appeal preparation checklist | `axios`, UI | active |
| `frontend/src/components/AssessmentNote.jsx` | JSX | Legal assessment note display | UI | active |
| `frontend/src/components/AuthModal.jsx` | JSX | Login/signup modal (email + Google OAuth) | `axios`, `lib/oauthState`, UI | active |
| `frontend/src/components/BarristerToolsPanel.jsx` | JSX | Crown Response Simulator + Fresh Evidence tools | `axios`, UI | active |
| `frontend/src/components/CaseChat.jsx` | JSX | In-case AI chat interface | `axios`, UI | active |
| `frontend/src/components/CaseLawPanel.jsx` | JSX | Case law search results panel | `axios`, UI | active |
| `frontend/src/components/CasePipelineSummary.jsx` | JSX | Pipeline status within case context | `axios`, UI | active |
| `frontend/src/components/CaseStrengthMeter.jsx` | JSX | Visual appeal strength meter | UI | active |
| `frontend/src/components/CounselBriefingBlock.jsx` | JSX | Counsel briefing section display | UI | active |
| `frontend/src/components/DashboardPipelineSummary.jsx` | JSX | Pipeline summary on dashboard | `axios`, UI | active |
| `frontend/src/components/DeadlineTracker.jsx` | JSX | Deadline tracking component | `axios`, UI | active |
| `frontend/src/components/DisclaimerReminder.jsx` | JSX | "Not legal advice" reminder | UI | active |
| `frontend/src/components/DocumentBundler.jsx` | JSX | Multi-document bundle manager | `axios`, UI | active |
| `frontend/src/components/DocumentScanner.jsx` | JSX | Document scanning UI (native camera trigger) | `native/camera`, UI | active |
| `frontend/src/components/DocumentsSection.jsx` | JSX | Document list + upload section | `axios`, `utils/downloadToken`, UI | active |
| `frontend/src/components/EvidenceProfilePanel.jsx` | JSX | Evidence profile display | `axios`, UI | active |
| `frontend/src/components/EvidenceSummary.jsx` | JSX | Evidence summary component | UI | active |
| `frontend/src/components/ExportOptionsModal.jsx` | JSX | Section picker for exports (PDF/Word/Print) | UI | active |
| `frontend/src/components/FastScrollTop.jsx` | JSX | Scroll-to-top button + navigation scroll reset | `react-router-dom` | active |
| `frontend/src/components/GroundsOfMerit.jsx` | JSX | Grounds list, management, AI identification trigger | `axios`, UI | active |
| `frontend/src/components/InstallPrompt.jsx` | JSX | PWA install prompt | `native/platform` | active |
| `frontend/src/components/LegalFrameworkViewer.jsx` | JSX | Legal framework data display | `axios`, UI | active |
| `frontend/src/components/LegitimacyPanel.jsx` | JSX | Legitimacy score display | UI | active |
| `frontend/src/components/MobileAppBanner.jsx` | JSX | Banner promoting mobile app | UI | active |
| `frontend/src/components/NotesSection.jsx` | JSX | Case notes with real-time collaboration | `axios`, UI | active |
| `frontend/src/components/NotificationBell.jsx` | JSX | Notification bell indicator | `axios`, UI | active |
| `frontend/src/components/OfflineBanner.jsx` | JSX | Offline state indicator | `native/network` | active |
| `frontend/src/components/OpenAICostsPanel.jsx` | JSX | AI cost dashboard for admin (sparklines, breakdowns) | `axios`, `recharts`, UI | active |
| `frontend/src/components/PageCTA.jsx` | JSX | Call-to-action block used across public pages | UI | active |
| `frontend/src/components/PageLogo.jsx` | JSX | Site logo component | — | active |
| `frontend/src/components/PageViewTracker.jsx` | JSX | Signup source + page view analytics tracking | `axios` | active |
| `frontend/src/components/PaymentModal.jsx` | JSX | PayID payment modal | `axios`, UI | active |
| `frontend/src/components/PipelineProgress.jsx` | JSX | Pipeline step progress display | `axios`, UI | active |
| `frontend/src/components/PipelineStalenessAlert.jsx` | JSX | Alert for stale pipeline data | UI | active |
| `frontend/src/components/QuickExport.jsx` | JSX | One-click ZIP export button | `axios`, `utils/downloadToken` | active |
| `frontend/src/components/ReportMetadataPanel.jsx` | JSX | Report metadata display | UI | active |
| `frontend/src/components/ReportTranslator.jsx` | JSX | In-app report translation UI | `axios`, UI | active |
| `frontend/src/components/ReportsSection.jsx` | JSX | Reports list + generation trigger | `axios`, UI | active |
| `frontend/src/components/SectionTranslatableReport.jsx` | JSX | Individual report section with translation support | `utils/mdRender`, UI | active |
| `frontend/src/components/ShareCaseModal.jsx` | JSX | Case sharing modal | `axios`, UI | active |
| `frontend/src/components/StateAppealStats.jsx` | JSX | State-specific appeal statistics | `axios`, `recharts` | active |
| `frontend/src/components/StrengthBadge.jsx` | JSX | Appeal strength colour badge | UI | active |
| `frontend/src/components/TermsAcceptance.jsx` | JSX | Terms of service acceptance prompt | `axios`, UI | active |
| `frontend/src/components/TimelineAnalysis.jsx` | JSX | Timeline with AI analysis annotations | `axios`, UI | active |
| `frontend/src/components/TimelineEnhanced.jsx` | JSX | Enhanced timeline view | `axios`, UI | active |
| `frontend/src/components/VerificationBadge.jsx` | JSX | Pipeline verification status badge | UI | active |
| `frontend/src/components/WebDocumentScanner.jsx` | JSX | Web-based document scanner (browser camera) | UI | active |

---

## Frontend — UI Primitives (Shadcn/Radix)

All files in `frontend/src/components/ui/` are Shadcn/Radix UI component wrappers. Status is **active** for those known to be used; marked **unknown** where usage was not verified.

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `accordion.jsx` | JSX | Accordion primitive | unknown |
| `alert-dialog.jsx` | JSX | Alert dialog primitive | active |
| `alert.jsx` | JSX | Alert component | active |
| `aspect-ratio.jsx` | JSX | Aspect ratio wrapper | unknown |
| `avatar.jsx` | JSX | Avatar component | active |
| `badge.jsx` | JSX | Badge component | active |
| `breadcrumb.jsx` | JSX | Breadcrumb navigation | unknown |
| `button.jsx` | JSX | Button component | active |
| `calendar.jsx` | JSX | Calendar date picker | active |
| `card.jsx` | JSX | Card container | active |
| `carousel.jsx` | JSX | Carousel component | unknown |
| `checkbox.jsx` | JSX | Checkbox input | active |
| `collapsible.jsx` | JSX | Collapsible section | active |
| `command.jsx` | JSX | Command palette | unknown |
| `context-menu.jsx` | JSX | Right-click context menu | unknown |
| `dialog.jsx` | JSX | Modal dialog | active |
| `drawer.jsx` | JSX | Slide-out drawer | unknown |
| `dropdown-menu.jsx` | JSX | Dropdown menu | active |
| `form.jsx` | JSX | Form with validation (react-hook-form) | active |
| `hover-card.jsx` | JSX | Hover card tooltip | unknown |
| `input-otp.jsx` | JSX | OTP input | unknown |
| `input.jsx` | JSX | Text input | active |
| `label.jsx` | JSX | Form label | active |
| `menubar.jsx` | JSX | Menubar component | unknown |
| `navigation-menu.jsx` | JSX | Navigation menu | unknown |
| `pagination.jsx` | JSX | Pagination controls | unknown |
| `popover.jsx` | JSX | Popover tooltip | active |
| `progress.jsx` | JSX | Progress bar | active |
| `radio-group.jsx` | JSX | Radio button group | active |
| `resizable.jsx` | JSX | Resizable panels | unknown |
| `scroll-area.jsx` | JSX | Scrollable area | active |
| `select.jsx` | JSX | Select dropdown | active |
| `separator.jsx` | JSX | Visual separator | active |
| `sheet.jsx` | JSX | Side sheet / panel | active |
| `skeleton.jsx` | JSX | Loading skeleton | active |
| `slider.jsx` | JSX | Slider input | unknown |
| `sonner.jsx` | JSX | Toast notifications (Sonner) | active |
| `switch.jsx` | JSX | Toggle switch | active |
| `table.jsx` | JSX | Table component | active |
| `tabs.jsx` | JSX | Tab navigation | active |
| `textarea.jsx` | JSX | Textarea input | active |
| `toast.jsx` | JSX | Toast primitive | active |
| `toaster.jsx` | JSX | Toast container | active |
| `toggle-group.jsx` | JSX | Toggle button group | unknown |
| `toggle.jsx` | JSX | Toggle button | unknown |
| `tooltip.jsx` | JSX | Tooltip | active |

---

## Frontend — Utils, Lib, Hooks, Contexts

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `frontend/src/utils/exportHtml.js` | JS | Shared HTML export builder (branded PDF/print wrapper with page numbers) | — | `pages/CaseDetail`, `pages/ReportView`, `pages/BarristerView` | active |
| `frontend/src/utils/mdRender.js` | JS | Markdown normaliser + renderer (marked + auSpelling); mirrors `backend/services/md_normaliser.py` | `marked`, `utils/auSpelling` | Multiple report-display components | active |
| `frontend/src/utils/auSpelling.js` | JS | Australian spelling normaliser (word-by-word, iOS Safari safe) | — | `utils/mdRender` | active |
| `frontend/src/utils/downloadToken.js` | JS | Get short-lived download token for secure file downloads | `axios`, `App` (API const) | `pages/CaseDetail`, `components/DocumentsSection`, `components/QuickExport` | active |
| `frontend/src/utils/isIOS.js` | JS | iOS device detection | — | Native bridge modules | active |
| `frontend/src/lib/oauthState.js` | JS | Google OAuth CSRF state: generate, save, read, clear, consume (localStorage + cookie) | — | `App.js`, `components/AuthModal` | active |
| `frontend/src/lib/utils.js` | JS | Tailwind class merge utility (`cn = clsx + twMerge`) | `clsx`, `tailwind-merge` | All UI components | active |
| `frontend/src/hooks/use-toast.js` | JS | Toast notification hook (wraps Radix Toast) | `react` | Some components | active |
| `frontend/src/contexts/ThemeContext.jsx` | JSX | Theme context provider (dark/light; forced light in production) | `react`, `next-themes` | `App.js`, UI primitives | active |

---

## Frontend — Native (Capacitor)

| Path | Language/Type | Purpose | Imports From | Imported By | Status |
|------|---------------|---------|--------------|-------------|--------|
| `frontend/src/native/index.js` | JS | Re-exports all native capabilities | All `native/*.js` | `App.js`, components using native features | active |
| `frontend/src/native/platform.js` | JS | `isNative()` — Capacitor vs web platform detection | `@capacitor/core` | `native/index`, components | active |
| `frontend/src/native/appLifecycle.js` | JS | Capacitor App plugin: resume/pause event listeners | `@capacitor/app` | `App.js` | active |
| `frontend/src/native/camera.js` | JS | Camera capture via Capacitor Camera plugin | `@capacitor/camera` | `components/DocumentScanner` | active |
| `frontend/src/native/haptics.js` | JS | Haptic feedback | `@capacitor/haptics` | Button/interaction components | active |
| `frontend/src/native/network.js` | JS | Network status monitoring | `@capacitor/network` | `components/OfflineBanner` | active |
| `frontend/src/native/notifications.js` | JS | Push and local notification wrappers | `@capacitor/push-notifications`, `@capacitor/local-notifications` | Notification components | active |
| `frontend/src/native/offlineStorage.js` | JS | Capacitor Preferences API for offline data | `@capacitor/preferences` | Offline-capable components | active |
| `frontend/src/native/share.js` | JS | Native share sheet | `@capacitor/share` | Export components | active |

---

## Infrastructure & Root Files

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `Dockerfile` | Dockerfile | Multi-stage build: Node (frontend build) + Python (backend) + static serve | active |
| `docker-compose.yml` | YAML | App + MongoDB container orchestration | active |
| `Procfile` | Text | Railway/Heroku root process (references backend Procfile) | active |
| `backend/Procfile` | Text | `uvicorn server:app --host 0.0.0.0 --port 8001` | active |
| `.env.example` | Text | Environment variable template (backend + frontend) | documentation |
| `backend/.env.example` | Text | Backend-specific env template | documentation |
| `design_guidelines.json` | JSON | UI design rules (colours, typography, component standards) | documentation |
| `scripts/sync-lockfile.sh` | Shell | Sync yarn.lock between environments | script |
| `.gitignore` | Text | Git ignore rules | documentation |
| `.gitconfig` | Text | Git config | documentation |

---

## CI / GitHub Actions

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `.github/workflows/ci.yml` | YAML | CI pipeline: backend-lint (ruff), backend-tests (pytest unit), backend-integration-tests (pytest + MongoDB), frontend-build (eslint + yarn build), security-check (credential scan + identity lock) | active |
| `.github/workflows/openai-codex.yml` | YAML | OpenAI Codex integration workflow | active |

---

## Memory / Product Docs

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `memory/PRD.md` | Markdown | Product Requirements Document with full feature history | documentation |
| `memory/CHANGELOG.md` | Markdown | Change log | documentation |
| `memory/ROADMAP.md` | Markdown | Product roadmap | documentation |
| `memory/IDENTITY_LOCK.md` | Markdown | Permanent non-negotiable rules: domain, LLM key, branding, Emergent purge | documentation |
| `memory/SELF_HOSTING_GUIDE.md` | Markdown | Self-hosting setup guide (Railway, MongoDB, env vars, Google OAuth) | documentation |
| `memory/.gitkeep` | Text | Keeps memory/ directory in git | documentation |

---

## User-Facing Docs

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `docs/APP_LAUNCH_GUIDE.md` | Markdown | App Store descriptions, mobile launch guide | documentation |
| `docs/BACKUP.md` | Markdown | Backup procedures | documentation |
| `docs/DEPLOYMENT.md` | Markdown | Deployment guide | documentation |
| `docs/DEVELOPER_HANDBOOK.md` | Markdown | Developer onboarding and conventions | documentation |
| `docs/DO_NOT_UNDO.md` | Markdown | Protected features and approved changes | documentation |
| `docs/MOBILE_APP_GUIDE.md` | Markdown | Mobile app guide | documentation |
| `docs/PRODUCTION_CHECKLIST.md` | Markdown | Pre-launch production checklist | documentation |
| `docs/SECURITY.md` | Markdown | Security documentation | documentation |
| `docs/USER_GUIDE.md` | Markdown | End-user guide | documentation |
| `docs/REPO_ARCHITECTURE_AUDIT.md` | Markdown | Full repository architecture audit (this session) | documentation |
| `docs/REPO_FILE_INDEX.md` | Markdown | This file — complete file index | documentation |
| `docs/audit/FULL_AUDIT_REPORT.txt` | Text | Historical ground-dedup debug audit log (Emergent platform artifact) | legacy |
| `docs/audit/COMPLETE_JOB_AUDIT.txt` | Text | Historical job audit log (Emergent platform artifact) | legacy |
| `docs/audit/FULL_JOB_AUDIT.txt` | Text | Historical full job audit log (Emergent platform artifact) | legacy |
| `README.md` | Markdown | Repository readme | documentation |

---

## Legacy / Platform Artifacts

| Path | Language/Type | Purpose | Status |
|------|---------------|---------|--------|
| `.emergent/emergent.yml` | YAML | Legacy Emergent platform config (inert — IDENTITY_LOCK prohibits Emergent usage) | legacy |
| `.emergent/summary.txt` | Text | Legacy Emergent platform summary (inert) | legacy |

---

## Static Assets (Frontend Public)

| Path | Type | Status |
|------|------|--------|
| `frontend/public/index.html` | HTML | App HTML shell | active |
| `frontend/public/manifest.json` | JSON | PWA manifest | active |
| `frontend/public/service-worker.js` | JS | PWA service worker | active |
| `frontend/public/logo.png` | Image | App logo | active |
| `frontend/public/logo-deb-king.jpg` | Image | Founder logo | active |
| `frontend/public/mockups.html` | HTML | Development mockup (not linked in app) | unknown |
| `frontend/public/mockups-mobile.html` | HTML | Mobile development mockup (not linked in app) | unknown |
| `frontend/public/images/howto/` | Images | How-to guide screenshots (step 1–8, live versions) | active |
| `frontend/public/images/stock/` | Images | Stock photography for landing page | active |

---

## Screenshots / Test Artefacts

| Path | Type | Status |
|------|------|--------|
| `.screenshots/Barrister_Brief_Joshua_Scott_Homann.doc` | Word doc | Sample barrister brief (test artefact) | test |
| `.screenshots/Quick_Brief_Joshua_Scott_Homann.pdf` | PDF | Sample quick brief (test artefact) | test |
| `.screenshots/R v Homann_full_detailed.pdf` | PDF | Sample full detailed report (test artefact) | test |
| `.screenshots/Receipt_ACM-8D5C33B8.pdf` | PDF | Sample payment receipt (test artefact) | test |
| `.screenshots/*.png / *.jpg` | Images | UI screenshots from QA and step-by-step verification | test |

---

*Index generated 2026-04-24. No application logic was modified.*
