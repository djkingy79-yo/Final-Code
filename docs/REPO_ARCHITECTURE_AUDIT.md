# Repository Architecture Audit

**Project:** Criminal Law Appeal Management (Appeal Case Manager)  
**Domain:** `criminallawappealmanagement.com.au`  
**Audit Date:** 2026-04-24  
**Scope:** Full repository — backend, frontend, frameworks, services, pipelines, tests, docs

---

## 1. Full Repository Tree (Grouped by Role)

### Backend Core
```
backend/
├── server.py               FastAPI app factory, middleware, health checks, router registration
├── config.py               MongoDB client, env validation, logging, admin helper
├── auth_utils.py           Shared auth: session cookie/header/download-token resolver
├── offence_framework.py    Back-compat shim → `from frameworks import *`
├── pyproject.toml          Ruff lint config
├── pytest.ini              Pytest config (asyncio mode, test paths)
├── requirements.txt        Python dependencies (~100 packages)
└── Procfile                Gunicorn start command for Railway/Heroku
```

### Backend Models
```
backend/models/
└── __init__.py             All Pydantic models: User, Case, Report, Ground, Document,
                            Timeline, ReportRequest, FEATURE_PRICES, etc.
```

### Backend Frameworks Package (Legal Data)
```
backend/frameworks/
├── __init__.py             Aggregated re-export of all symbols
├── jurisdictions.py        LEGISLATION_CURRENCY, AUSTRALIAN_STATES (9 jurisdictions)
├── states.py               NSW/VIC/QLD/SA/WA/TAS/NT/ACT _CRIMINAL_FRAMEWORK dicts
├── federal.py              FEDERAL_CRIMINAL_FRAMEWORK, FEDERAL_FAULT_ELEMENTS,
│                           PROCEEDS_OF_CRIME_FRAMEWORK
├── appeal.py               APPEAL_FRAMEWORK (per-jurisdiction procedures, time limits,
│                           forms), APPEAL_GROUNDS_ACCESSIBILITY
├── sentencing.py           SENTENCING_FRAMEWORK (per-jurisdiction acts, key provisions)
├── evidence.py             EVIDENCE_FRAMEWORK (uniform evidence + state-specific)
├── mental_impairment.py    MENTAL_IMPAIRMENT_FRAMEWORK (per-jurisdiction acts/tests)
├── procedure.py            INDICTABLE/HYBRID/SUMMARY_PROCEDURE_FLOW, MENS_REA_FRAMEWORK
├── offences.py             OFFENCE_CATEGORIES (18 categories with elements and refs)
├── common_grounds.py       COMMON_APPEAL_GROUNDS
├── human_rights.py         HUMAN_RIGHTS_FRAMEWORK
├── landmark_cases.py       LANDMARK_CASES
├── recent_updates.py       RECENT_LEGISLATION_UPDATES
└── legislation_registry.py Legislation currency registry (AustLII URLs, verification dates)
```

### Backend Routers (API Layer)
```
backend/routers/
├── __init__.py             Centralised router registration (register_all_routers)
├── auth.py                 Email/password + Google OAuth sign-in, sign-out, sessions
├── password_reset.py       Email-based password reset flow
├── cases.py                Case CRUD (create, read, update, delete)
├── documents.py            Document upload, extraction, listing, deletion
├── timeline.py             Timeline entry management, AI generation
├── grounds.py              Grounds of merit CRUD, AI identification, pathway info
├── notes.py                Case notes CRUD + WebSocket real-time collaboration
├── reports.py              Report generation triggers, CRUD, status polling
├── report_exports.py       PDF and DOCX export of reports
├── export.py               ZIP export of full case package (Quick Export)
├── pipeline.py             Staged pipeline: extract/classify/verify/argue/submit
├── pipeline_staged.py      Extended staged pipeline with dedicated endpoints
├── analysis.py             On-demand case analysis endpoint
├── barrister_pack.py       Barrister Acceptance Pack PDF generator
├── barrister_tools.py      Crown Response Simulator + Fresh Evidence (Gallagher) Wizard
├── compare.py              Side-by-side case comparison
├── contradictions.py       Contradiction detection between documents
├── caselaw.py              Case law search (AustLII URL generation)
├── legislation.py          Legislation framework viewer
├── legislation_alerts.py   Legislation amendment alerts (weekly AI scan results)
├── translate.py            Report translation via LLM
├── collaboration.py        Case sharing and access-link management
├── deadlines.py            Deadline tracker
├── admin.py                Admin dashboard: user management, stats, DB tools
├── analytics.py            Signup source tracking, conversion analytics
├── statistics.py           Aggregated appeal statistics
├── payments.py             PayID payment recording and case unlocking
├── payment_history.py      Payment history listing
├── resources.py            Legal resources (static/semi-static reference data)
└── utilities.py            Misc utilities (download token generation, etc.)
```

### Backend Services (Business Logic)
```
backend/services/
├── __init__.py             Empty init

# ── LLM Gateway ──
├── llm_service.py          Core LLM interface: call_llm_structured, call_llm_with_fallback,
│                           call_llm_for_json, call_llm_for_report (model fallback, retry)
├── ai_service.py           LEGACY — call_llm_with_retry (not used in production code)
├── ai_usage_tracker.py     Fire-and-forget token/cost recorder → ai_usage MongoDB collection

# ── Report Generation ──
├── report_generator.py     Main report engine: multi-pass AI report generation (8/10 passes)
├── report_quality.py       Text cleanup: anchor terms, dedup, strip placeholders, sanitise
├── barrister_generator.py  Appellate Research Brief (Barrister View) generation

# ── Pipeline (Staged) ──
├── pipeline_models.py      Pydantic models: DocumentExtract, CaseExtract,
│                           IssueClassification, IssueVerification
├── pipeline_orchestrator.py Pipeline coordination helpers (freshness, arg loading)
├── pipeline/
│   ├── __init__.py         Re-exports all pipeline step functions
│   ├── extract.py          Step 1: Extract facts/events/findings from documents
│   ├── classify.py         Step 2: Classify extracted issues into ground types
│   ├── verify.py           Step 3: Verify issues (legitimacy scoring, supporting/undermining)
│   ├── draft.py            Step 4: Draft report sections from verified material
│   ├── argue.py            Step 5: Build counsel-style argument per ground
│   └── submit.py           Step 6: Draft formal submissions document

# ── Jurisdiction & Legal Framework Engines ──
├── national_framework.py        Jurisdiction-accurate system prompts; build_full_system_prompt()
├── national_framework_engine.py Full context builder from frameworks/ package;
│                                 build_national_case_context()
├── jurisdiction_rules.py        Per-jurisdiction rule sets (appellate tests, procedure)
├── offence_helpers.py           LLM context assembler using frameworks/ data

# ── Ground Processing Chain ──
├── ground_normaliser.py    Normalise AI-generated grounds (type, viability, jurisdiction)
├── ground_cleanup.py       Post-normalisation cleanup (terminology, liability vs mitigation)
├── ground_dedup.py         Duplicate ground prevention (fuzzy + topic classification)
├── appeal_strength.py      Realism scoring (record support, proviso risk, Crown response)
├── barrister_mode.py       Strategy ranking: primary / secondary / tertiary / abandon
├── proviso_engine.py       Proviso exposure narrative (Weiss v The Queen)
├── outcome_predictor.py    Outcome category prediction (conviction/sentence/procedure)
├── legitimacy_engine.py    Three-axis viability scoring (outcome × legal alignment × evidence)
├── attack_plan.py          Counsel-style attack plan per ground (strategy, gaps, steps)

# ── Document & Evidence ──
├── document_helpers.py     Text extraction (PDF/DOCX/images/TXT), OCR, context builder
├── evidence_builder.py     Affidavit templates, document request plans per ground

# ── Legislation ──
├── legislation_checker.py  AustLII/legislation.gov.au section reference validator
├── legislation_currency.py Dashboard build + AI currency cross-check
├── weekly_legislation_scan.py Scheduled Monday 09:00 AEST scan for amendments

# ── Misc Services ──
├── caselaw_search.py       AustLII/state DB search URL generator
├── case_validation.py      Soft metadata validation + citation hallucination detection
├── email_service.py        Payment notification emails via Resend
├── export_footer.py        Shared PDF/DOCX footer formatting (Times New Roman 7pt)
├── md_normaliser.py        Markdown whitespace normalisation (mirrors frontend mdRender.js)
├── notes_helpers.py        WebSocket connection tracking for live notes collaboration
├── startup_tasks.py        DB indexes, orphan recovery, dedup, markdown backfill on startup
└── proviso_engine.py       (see Ground Processing Chain above)
```

### Backend Tests
```
backend/tests/               50 test files covering all major features
├── conftest.py              Shared pytest fixtures
├── test_api.py              General API smoke tests
├── test_health_api.py       Health endpoint tests
├── test_legal_framework.py  Framework data integrity
├── test_offence_framework.py           Offence category tests
├── test_offence_framework_integrity.py Integrity checks on all 18 categories
├── test_frameworks_refactor.py         P2 refactor regression
├── test_framework_gap_fill_20260214.py 12 new tests from Feb 2026 gap fill
├── test_legislation_framework.py       Legislation registry tests
├── test_legislation_currency.py        Currency service tests
├── test_ground_dedup.py                Dedup algorithm tests
├── test_ground_cleanup.py              Cleanup layer tests
├── test_ground_cleanup_round2.py       Second-round cleanup tests
├── test_ground_counsel_round3.py       Counsel round 3 tests
├── test_ground_invariants.py           Ground field invariants
├── test_ground_pipeline.py             Full pipeline ground flow
├── test_grounds_pipeline_iteration132.py  Regression test iter 132
├── test_pipeline_endpoints.py          Pipeline API endpoint tests
├── test_pipeline_verification_iteration133.py  Verification regression
├── test_staged_pipeline_iteration131.py        Staged pipeline regression
├── test_national_framework.py          National framework module tests
├── test_national_framework_engine.py   Engine module tests
├── test_legitimacy_engine.py           Legitimacy scoring tests
├── test_outcome_predictor.py           Outcome prediction tests
├── test_proviso_and_barrister_mode.py  Proviso + strategy tests
├── test_report_generation.py           Full report generation flow
├── test_report_prompt_quality.py       Prompt quality checks
├── test_report_progress_iteration203.py Streaming progress tests
├── test_ai_usage_tracker.py            Token/cost tracking tests
├── test_document_exports.py            PDF/DOCX export tests
├── test_export_endpoints_iteration201.py Export endpoint regression
├── test_extract_all_text_iteration202.py Text extraction regression
├── test_barrister_pack_pipeline.py     Barrister pack tests
├── test_barrister_view_iteration27.py  Barrister view tests
├── test_counsel_briefing.py            Counsel briefing tests
├── test_attack_plan_refine.py          Attack plan tests
├── test_evidence_builder_refine.py     Evidence builder tests
├── test_collaboration_features.py      Sharing/collaboration tests
├── test_compare_contradictions.py      Compare + contradiction tests
├── test_ai_features_iteration26.py     AI feature regression
├── test_auto_identify_background.py    Background identification tests
├── test_comprehensive_iteration_199.py Comprehensive regression
├── test_iteration193_bugfixes.py       Bug fix regression iter 193
├── test_iteration_208_features.py      Feature regression iter 208
├── test_state_offence_framework.py     State framework tests
├── test_signup_source_tracking.py      Analytics tracking tests
├── test_openai_costs_endpoint.py       OpenAI cost endpoint tests
└── test_translate_parallel_recovery.py Translation recovery tests
```

### Backend Scripts
```
backend/scripts/
├── repair_report.py              Targeted LLM repair of thin/missing report sections
├── normalise_db.py               Idempotent DB migration to strict Pydantic structures
└── backfill_markdown_normalise.py One-off markdown normalisation on existing DB records
```

### Frontend
```
frontend/
├── src/App.js                  Main React entry: routing, Google OAuth, axios interceptor
├── src/index.js                React DOM render, PWA service worker registration
├── src/App.css / index.css     Global + component styles
├── src/pages/                  35 page components (see section below)
├── src/components/             50+ shared components (see section below)
├── src/components/ui/          40 Shadcn/Radix UI primitives
├── src/contexts/ThemeContext.jsx  Dark/light mode context (forced light in production)
├── src/hooks/use-toast.js      Toast notification hook
├── src/lib/utils.js            Tailwind class merge utility
├── src/lib/oauthState.js       Google OAuth CSRF state management
├── src/utils/exportHtml.js     Shared HTML export builder (PDF/print wrapper)
├── src/utils/mdRender.js       Markdown normaliser + renderer (marked + auSpelling)
├── src/utils/auSpelling.js     Australian spelling normaliser (no regex on iOS Safari)
├── src/utils/downloadToken.js  Short-lived download token helper
├── src/utils/isIOS.js          iOS detection utility
├── src/native/                 Capacitor native bridge modules (see below)
├── public/                     Static assets, index.html, manifest, service-worker
├── package.json                React 19, React Router 7, Radix UI, Capacitor 7, etc.
├── tailwind.config.js          Tailwind configuration
├── craco.config.js             CRACO build override (REACT_APP_BACKEND_URL required)
├── capacitor.config.json       Capacitor app ID + server config
└── build-mobile.sh             Mobile build script (npx cap sync + open iOS/Android)
```

### Frontend Pages
```
frontend/src/pages/
├── LandingPage.jsx             Public home page with CTA
├── Dashboard.jsx               Case list, new case creation
├── CaseDetail.jsx              Full case detail: documents, timeline, grounds, reports
├── ReportView.jsx              Standard report viewer + export (PDF/Word/Print)
├── BarristerView.jsx           Appellate Research Brief viewer + custom export builder
├── AdminDashboard.jsx          Admin: user management, legislation currency, AI costs
├── AdminStats.jsx              Admin statistics overview
├── SignupSourceAnalytics.jsx   Conversion tracking dashboard
├── LegalFrameworkPage.jsx      Legal framework viewer (all jurisdictions)
├── LegislationCurrency.jsx     Legislation currency dashboard
├── CaselawSearchPage.jsx       Case law search interface
├── AppealStatisticsPage.jsx    Appeal outcome statistics
├── CompareCasesPage.jsx        Case comparison tool
├── HelpPage.jsx                Help content
├── HowToUsePage.jsx            Step-by-step usage guide (with screenshots)
├── HowItWorksPage.jsx          How the app works explanation
├── AboutPage.jsx               About / founder info
├── LegalResourcesPage.jsx      Legal resources directory
├── ResourcesPage.jsx           General resources
├── LegalGlossary.jsx           Legal term glossary
├── LawyerDirectory.jsx         Lawyer directory (static/semi-static)
├── FormTemplates.jsx           Downloadable form templates
├── FAQPage.jsx                 FAQ page
├── SuccessStories.jsx          Success stories
├── Statistics.jsx              Public statistics page
├── PaymentHistoryPage.jsx      User payment history
├── ProfessionalSummary.jsx     Professional summary view
├── DocumentPreviewPage.jsx     In-browser document preview
├── AcceptShareLink.jsx         Accept a shared case invitation
├── ForgotPasswordPage.jsx      Forgot password form
├── ResetPasswordPage.jsx       Password reset form
└── TermsOfService.jsx          Terms of service
```

### Frontend Components (Key)
```
frontend/src/components/
├── ActivityFeed.jsx            Recent case activity feed
├── AiCostBadge.jsx             AI cost display badge
├── AppFooter.jsx               Site footer with branding
├── AppealChecklist.jsx         Appeal preparation checklist
├── AuthModal.jsx               Login/signup modal
├── BarristerToolsPanel.jsx     Crown Response + Fresh Evidence tools panel
├── CaseChat.jsx                In-case AI chat interface
├── CaseLawPanel.jsx            Case law search results panel
├── CasePipelineSummary.jsx     Pipeline status in case context
├── CaseStrengthMeter.jsx       Visual appeal strength meter
├── CounselBriefingBlock.jsx    Counsel briefing display block
├── DashboardPipelineSummary.jsx Pipeline summary on dashboard
├── DeadlineTracker.jsx         Deadline tracking component
├── DocumentBundler.jsx         Multi-document bundle manager
├── DocumentScanner.jsx         Document scanning UI
├── DocumentsSection.jsx        Document list + upload
├── EvidenceProfilePanel.jsx    Evidence profile display
├── EvidenceSummary.jsx         Evidence summary component
├── ExportOptionsModal.jsx      Section picker for exports
├── GroundsOfMerit.jsx          Grounds list + management
├── LegalFrameworkViewer.jsx    Legal framework data display
├── LegitimacyPanel.jsx         Legitimacy score display
├── NotesSection.jsx            Case notes with real-time collab
├── OpenAICostsPanel.jsx        AI cost dashboard for admin
├── PipelineProgress.jsx        Pipeline step progress display
├── PipelineStalenessAlert.jsx  Alert for stale pipeline data
├── QuickExport.jsx             One-click ZIP export
├── ReportMetadataPanel.jsx     Report metadata display
├── ReportTranslator.jsx        In-app report translation
├── ReportsSection.jsx          Reports list + generation trigger
├── ShareCaseModal.jsx          Case sharing modal
├── StateAppealStats.jsx        State-specific appeal statistics
├── StrengthBadge.jsx           Appeal strength badge
├── TimelineAnalysis.jsx        Timeline with AI analysis
├── TimelineEnhanced.jsx        Enhanced timeline view
├── VerificationBadge.jsx       Pipeline verification status badge
└── WebDocumentScanner.jsx      Web-based document scanner
```

### Frontend Native (Capacitor)
```
frontend/src/native/
├── index.js            Platform detection + capability exports
├── platform.js         Native vs web platform resolver
├── appLifecycle.js     Capacitor App plugin (resume/pause events)
├── camera.js           Camera capture (Capacitor Camera plugin)
├── haptics.js          Haptic feedback
├── network.js          Network status monitoring
├── notifications.js    Push/local notification wrappers
├── offlineStorage.js   Capacitor Preferences for offline data
└── share.js            Native share sheet
```

### Infrastructure & Docs
```
Dockerfile                  Multi-stage build: Node (frontend) + Python (backend) + static serve
docker-compose.yml          App + MongoDB container setup
Procfile (root)             Railway/Heroku: uvicorn backend + static serve
backend/Procfile            Backend-only process
.env.example                Environment variable template
.github/workflows/ci.yml    CI: backend-lint, backend-tests, backend-integration-tests,
                             frontend-build, security-check
.github/workflows/openai-codex.yml  OpenAI Codex integration workflow
.gitignore / .gitconfig     Git config
design_guidelines.json      UI design rules
scripts/sync-lockfile.sh    Yarn lockfile sync helper
memory/                     PRD, CHANGELOG, ROADMAP, IDENTITY_LOCK, SELF_HOSTING_GUIDE
docs/                       User-facing docs + this audit
.screenshots/               Sample screenshots and test documents
```

---

## 2. Every Python / JS / TS File — Purpose Summary

| File | Language | Purpose |
|------|----------|---------|
| `backend/server.py` | Python | FastAPI app factory, CORS, security headers, health checks, router wiring, startup tasks |
| `backend/config.py` | Python | Env var validation, MongoDB client, logging (JSON), admin helpers, rate limiter |
| `backend/auth_utils.py` | Python | `get_current_user()` — resolves session cookie/header/download-token |
| `backend/offence_framework.py` | Python | Back-compat shim: `from frameworks import *` |
| `backend/models/__init__.py` | Python | All Pydantic data models for the application |
| `backend/frameworks/__init__.py` | Python | Aggregated re-export of all legal framework symbols |
| `backend/frameworks/jurisdictions.py` | Python | `AUSTRALIAN_STATES` (9 jurisdictions, court URLs, legal aid links), `LEGISLATION_CURRENCY` |
| `backend/frameworks/states.py` | Python | `NSW/VIC/QLD/SA/WA/TAS/NT/ACT_CRIMINAL_FRAMEWORK` — primary legislation per state |
| `backend/frameworks/federal.py` | Python | `FEDERAL_CRIMINAL_FRAMEWORK`, fault elements, proceeds of crime framework |
| `backend/frameworks/appeal.py` | Python | `APPEAL_FRAMEWORK` — procedures, time limits, forms per jurisdiction |
| `backend/frameworks/sentencing.py` | Python | `SENTENCING_FRAMEWORK` — sentencing acts and key provisions per jurisdiction |
| `backend/frameworks/evidence.py` | Python | `EVIDENCE_FRAMEWORK` — uniform evidence law + state-specific evidence acts |
| `backend/frameworks/mental_impairment.py` | Python | `MENTAL_IMPAIRMENT_FRAMEWORK` — legislation and tests per jurisdiction |
| `backend/frameworks/procedure.py` | Python | Procedural flows (indictable/hybrid/summary), `MENS_REA_FRAMEWORK` |
| `backend/frameworks/offences.py` | Python | `OFFENCE_CATEGORIES` — 18 categories with elements, legislation, fault elements |
| `backend/frameworks/common_grounds.py` | Python | `COMMON_APPEAL_GROUNDS` — standard grounds with descriptions |
| `backend/frameworks/human_rights.py` | Python | `HUMAN_RIGHTS_FRAMEWORK` — human rights instruments relevant to appeals |
| `backend/frameworks/landmark_cases.py` | Python | `LANDMARK_CASES` — key Australian criminal appeal precedents |
| `backend/frameworks/recent_updates.py` | Python | `RECENT_LEGISLATION_UPDATES` — recent legislative amendments |
| `backend/frameworks/legislation_registry.py` | Python | Per-Act currency registry for the legislation dashboard |
| `backend/routers/__init__.py` | Python | Centralised router registry + `register_all_routers()` |
| `backend/routers/auth.py` | Python | Email/password auth, Google OAuth, sign-out, download tokens |
| `backend/routers/password_reset.py` | Python | Password reset email flow |
| `backend/routers/cases.py` | Python | Case CRUD endpoints |
| `backend/routers/documents.py` | Python | Document upload, OCR extraction, listing |
| `backend/routers/timeline.py` | Python | Timeline entry management and AI generation |
| `backend/routers/grounds.py` | Python | Grounds CRUD, AI identification, pathway display |
| `backend/routers/notes.py` | Python | Notes CRUD + WebSocket real-time collaboration |
| `backend/routers/reports.py` | Python | Report generation (triggers, streaming progress, CRUD) |
| `backend/routers/report_exports.py` | Python | PDF and DOCX export of reports (ReportLab + python-docx) |
| `backend/routers/export.py` | Python | ZIP export of full case package |
| `backend/routers/pipeline.py` | Python | Staged pipeline API (extract/classify/verify/argue/submit) |
| `backend/routers/pipeline_staged.py` | Python | Extended staged pipeline with finer-grained endpoints |
| `backend/routers/analysis.py` | Python | On-demand case analysis endpoint |
| `backend/routers/barrister_pack.py` | Python | Barrister Acceptance Pack PDF generator |
| `backend/routers/barrister_tools.py` | Python | Crown Response Simulator + Fresh Evidence Gallagher Wizard |
| `backend/routers/compare.py` | Python | Side-by-side case comparison |
| `backend/routers/contradictions.py` | Python | Contradiction detection between documents |
| `backend/routers/caselaw.py` | Python | Case law search URL generation |
| `backend/routers/legislation.py` | Python | Legal framework data endpoint |
| `backend/routers/legislation_alerts.py` | Python | Legislation amendment alerts/listing |
| `backend/routers/translate.py` | Python | LLM-powered report translation |
| `backend/routers/collaboration.py` | Python | Case sharing and access links |
| `backend/routers/deadlines.py` | Python | Deadline CRUD |
| `backend/routers/admin.py` | Python | Admin: users, stats, DB tools, legislation management |
| `backend/routers/analytics.py` | Python | Signup source tracking, conversion analytics |
| `backend/routers/statistics.py` | Python | Appeal statistics aggregation |
| `backend/routers/payments.py` | Python | PayID payment recording + case feature unlocking |
| `backend/routers/payment_history.py` | Python | Payment history endpoints |
| `backend/routers/resources.py` | Python | Legal resources data |
| `backend/routers/utilities.py` | Python | Misc utilities (download token generation) |
| `backend/services/llm_service.py` | Python | Core LLM gateway: model selection, retry, JSON/report extraction |
| `backend/services/ai_service.py` | Python | Legacy `call_llm_with_retry()` — **not imported in production** |
| `backend/services/ai_usage_tracker.py` | Python | Token/cost tracking → `ai_usage` MongoDB collection |
| `backend/services/report_generator.py` | Python | Multi-pass AI report generation engine (8 and 10-pass modes) |
| `backend/services/report_quality.py` | Python | Post-generation text cleanup and quality enforcement |
| `backend/services/barrister_generator.py` | Python | Appellate Research Brief (Barrister View) generation |
| `backend/services/pipeline_models.py` | Python | Pipeline-specific Pydantic models (DocumentExtract, CaseExtract, etc.) |
| `backend/services/pipeline_orchestrator.py` | Python | Pipeline orchestration helpers (freshness, arg loading) |
| `backend/services/pipeline/__init__.py` | Python | Re-exports all pipeline step functions |
| `backend/services/pipeline/extract.py` | Python | Pipeline Step 1: extract facts/events/findings from documents |
| `backend/services/pipeline/classify.py` | Python | Pipeline Step 2: classify issues into canonical ground types |
| `backend/services/pipeline/verify.py` | Python | Pipeline Step 3: verify issues with legitimacy scoring |
| `backend/services/pipeline/draft.py` | Python | Pipeline Step 4: draft report sections from verified material |
| `backend/services/pipeline/argue.py` | Python | Pipeline Step 5: build argument per ground |
| `backend/services/pipeline/submit.py` | Python | Pipeline Step 6: draft formal submissions document |
| `backend/services/national_framework.py` | Python | Jurisdiction-accurate system prompts; `build_full_system_prompt()` (inline data) |
| `backend/services/national_framework_engine.py` | Python | Full prompt-context builder from `frameworks/`; `build_national_case_context()` |
| `backend/services/jurisdiction_rules.py` | Python | Per-jurisdiction rule sets for ground normalisation |
| `backend/services/offence_helpers.py` | Python | LLM context assembler; surfaces offence, mens rea, procedure, framework into prompts |
| `backend/services/ground_normaliser.py` | Python | Normalise AI-generated grounds (type, viability, jurisdiction-aware pathway) |
| `backend/services/ground_cleanup.py` | Python | Post-normalisation cleanup of terminology and mixed-category artifacts |
| `backend/services/ground_dedup.py` | Python | Duplicate ground prevention (fuzzy matching + topic classification) |
| `backend/services/appeal_strength.py` | Python | Realism scoring: record support, proviso risk, Crown response strength |
| `backend/services/barrister_mode.py` | Python | Strategy ranking: primary / secondary / tertiary / abandon |
| `backend/services/proviso_engine.py` | Python | Proviso exposure narrative (Weiss v The Queen) |
| `backend/services/outcome_predictor.py` | Python | Appellate outcome prediction by ground type and strategy |
| `backend/services/legitimacy_engine.py` | Python | Three-axis viability scoring (outcome × legal alignment × evidence) |
| `backend/services/attack_plan.py` | Python | Counsel-style attack plan per ground |
| `backend/services/document_helpers.py` | Python | PDF/DOCX/image text extraction, OCR, context builder |
| `backend/services/evidence_builder.py` | Python | Affidavit templates and document request plans |
| `backend/services/legislation_checker.py` | Python | AustLII section reference validator (async HTTP) |
| `backend/services/legislation_currency.py` | Python | Legislation currency dashboard and AI cross-check |
| `backend/services/weekly_legislation_scan.py` | Python | Scheduled Monday 09:00 AEST legislation amendment scan |
| `backend/services/caselaw_search.py` | Python | Case law search URL generator for AustLII and state databases |
| `backend/services/case_validation.py` | Python | Soft metadata validation + citation hallucination detection |
| `backend/services/email_service.py` | Python | Payment notification emails via Resend API |
| `backend/services/export_footer.py` | Python | Shared PDF/DOCX footer utilities (Times New Roman 7pt, page numbers) |
| `backend/services/md_normaliser.py` | Python | Markdown whitespace normaliser (mirrors `frontend/src/utils/mdRender.js`) |
| `backend/services/notes_helpers.py` | Python | WebSocket connection tracking for real-time notes collaboration |
| `backend/services/startup_tasks.py` | Python | DB index creation, orphan recovery, dedup, markdown backfill on startup |
| `backend/scripts/repair_report.py` | Python | CLI: targeted LLM repair of thin/missing report sections |
| `backend/scripts/normalise_db.py` | Python | CLI: idempotent DB migration to strict Pydantic structures |
| `backend/scripts/backfill_markdown_normalise.py` | Python | CLI: one-off markdown normalisation on all DB records |
| `frontend/src/App.js` | JS | Root React component: routing, Google OAuth CSRF, axios interceptor, layout |
| `frontend/src/index.js` | JS | React DOM render, PWA service worker registration |
| `frontend/src/pages/LandingPage.jsx` | JSX | Public home page with features, CTAs |
| `frontend/src/pages/Dashboard.jsx` | JSX | Case list, new case creation, pipeline summary |
| `frontend/src/pages/CaseDetail.jsx` | JSX | Master case page: all tabs (docs, timeline, grounds, notes, reports, barrister) |
| `frontend/src/pages/ReportView.jsx` | JSX | Standard report viewer with PDF/Word/Print export |
| `frontend/src/pages/BarristerView.jsx` | JSX | Appellate Research Brief viewer with custom export builder |
| `frontend/src/pages/AdminDashboard.jsx` | JSX | Admin panel: users, legislation, AI costs, analytics |
| `frontend/src/pages/AdminStats.jsx` | JSX | High-level admin statistics |
| `frontend/src/pages/SignupSourceAnalytics.jsx` | JSX | Conversion tracking dashboard |
| `frontend/src/pages/LegalFrameworkPage.jsx` | JSX | Legal framework viewer (all jurisdictions and offence categories) |
| `frontend/src/pages/LegislationCurrency.jsx` | JSX | Legislation currency dashboard (amendment alerts) |
| `frontend/src/pages/CaselawSearchPage.jsx` | JSX | Case law search interface |
| `frontend/src/pages/AppealStatisticsPage.jsx` | JSX | Appeal outcome statistics |
| `frontend/src/pages/CompareCasesPage.jsx` | JSX | Side-by-side case comparison |
| `frontend/src/pages/HelpPage.jsx` | JSX | Help content |
| `frontend/src/pages/HowToUsePage.jsx` | JSX | Step-by-step usage guide (with screenshots) |
| `frontend/src/pages/HowItWorksPage.jsx` | JSX | How the app works explanation |
| `frontend/src/pages/AboutPage.jsx` | JSX | About / Deb King founder info |
| `frontend/src/pages/LegalResourcesPage.jsx` | JSX | Legal resources directory |
| `frontend/src/pages/ResourcesPage.jsx` | JSX | General resources |
| `frontend/src/pages/LegalGlossary.jsx` | JSX | Legal term glossary |
| `frontend/src/pages/LawyerDirectory.jsx` | JSX | Lawyer directory |
| `frontend/src/pages/FormTemplates.jsx` | JSX | Downloadable form templates |
| `frontend/src/pages/FAQPage.jsx` | JSX | FAQ |
| `frontend/src/pages/SuccessStories.jsx` | JSX | Success stories |
| `frontend/src/pages/Statistics.jsx` | JSX | Public statistics |
| `frontend/src/pages/PaymentHistoryPage.jsx` | JSX | User payment history |
| `frontend/src/pages/ProfessionalSummary.jsx` | JSX | Professional summary view |
| `frontend/src/pages/DocumentPreviewPage.jsx` | JSX | In-browser document preview |
| `frontend/src/pages/AcceptShareLink.jsx` | JSX | Accept a shared case invitation |
| `frontend/src/pages/ForgotPasswordPage.jsx` | JSX | Forgot password form |
| `frontend/src/pages/ResetPasswordPage.jsx` | JSX | Password reset form |
| `frontend/src/pages/TermsOfService.jsx` | JSX | Terms of service |
| `frontend/src/utils/exportHtml.js` | JS | Shared HTML export builder (branded PDF/print wrapper) |
| `frontend/src/utils/mdRender.js` | JS | Markdown normaliser + renderer (marked + auSpelling) |
| `frontend/src/utils/auSpelling.js` | JS | Australian spelling normaliser (iOS Safari safe — no g-flag regex) |
| `frontend/src/utils/downloadToken.js` | JS | Short-lived download token generation |
| `frontend/src/utils/isIOS.js` | JS | iOS device detection |
| `frontend/src/lib/oauthState.js` | JS | Google OAuth CSRF state management (localStorage + cookie) |
| `frontend/src/lib/utils.js` | JS | Tailwind class merge utility (`cn`) |
| `frontend/src/hooks/use-toast.js` | JS | Toast notification hook |
| `frontend/src/contexts/ThemeContext.jsx` | JSX | Theme context (forced light in production) |
| `frontend/src/native/index.js` | JS | Native capability exports |
| `frontend/src/native/platform.js` | JS | Capacitor vs web platform detection |
| `frontend/src/native/appLifecycle.js` | JS | Capacitor App plugin lifecycle events |
| `frontend/src/native/camera.js` | JS | Camera capture (Capacitor Camera) |
| `frontend/src/native/haptics.js` | JS | Haptic feedback |
| `frontend/src/native/network.js` | JS | Network status monitoring |
| `frontend/src/native/notifications.js` | JS | Push/local notifications |
| `frontend/src/native/offlineStorage.js` | JS | Capacitor Preferences for offline data |
| `frontend/src/native/share.js` | JS | Native share sheet |

---

## 3. Duplicated or Overlapping Files / Functions

### 3.1 Dual National Framework Engines

| Item | File | Notes |
|------|------|-------|
| `get_jurisdiction_framework()` | `services/national_framework.py:144` | Resolves jurisdiction key from inline `NATIONAL_CRIMINAL_FRAMEWORK` dict |
| `normalise_jurisdiction()` | `services/national_framework_engine.py:95` | Resolves jurisdiction key from `VALID_JURISDICTIONS` map |
| `build_national_appellate_context()` | `services/national_framework.py:160` | Builds context from inline data |
| `build_national_case_context()` | `services/national_framework_engine.py:635` | Builds context from `frameworks/` package |
| `build_full_system_prompt()` | `services/national_framework.py:252` | Used by `report_generator.py` |
| `build_national_case_context()` | `services/national_framework_engine.py:635` | Used by `offence_helpers.py` |

**Verdict:** Both are active (used in different call paths) but solve the same problem with different source data. `national_framework.py` keeps its own inline jurisdiction matrix; `national_framework_engine.py` imports from `frameworks/`. The inline matrix in `national_framework.py` is a subset of what's in `frameworks/states.py` — this is a duplication risk if either is updated independently.

### 3.2 Dual Pipeline Routers

| Item | Notes |
|------|-------|
| `routers/pipeline.py` | Original pipeline router with combined endpoints |
| `routers/pipeline_staged.py` | Extended staged pipeline with finer-grained endpoints |

Both are registered in `routers/__init__.py`. `pipeline_orchestrator.py` calls private functions from `pipeline_staged.py`. The two routers share overlapping endpoint semantics (both expose extract/classify/verify step triggers). This is functional but creates ambiguity about which router is authoritative for pipeline control.

### 3.3 Legacy AI Service vs Active LLM Service

| Item | File | Status |
|------|------|--------|
| `call_llm_with_retry()` | `services/ai_service.py` | **Dead code in production** — zero production imports found |
| `call_llm_structured()`, `call_llm_with_fallback()`, `call_llm_for_json()`, `call_llm_for_report()` | `services/llm_service.py` | Active — imported by all production services |

`ai_service.py` is only imported by test files. The production call chain has fully migrated to `llm_service.py`. `ai_service.py` is a legacy stub.

### 3.4 `offence_framework.py` Shim vs `frameworks/` Package

`offence_framework.py` is intentionally a shim (`from frameworks import *`). It exists solely for backwards compatibility. Any new code should import directly from `frameworks`. The shim itself is not dead — it's still referenced by `offence_helpers.py` and `report_generator.py` via their `from offence_framework import ...` statements. This creates an unnecessary indirection.

### 3.5 Markdown Normaliser Duplication

| File | Language | Note |
|------|----------|------|
| `backend/services/md_normaliser.py` | Python | Backend normaliser (runs at save time) |
| `frontend/src/utils/mdRender.js` | JS | Frontend normaliser (runs at render time) |

These are intentional mirrors of each other (documented in `md_normaliser.py`). They are not bugs but must be kept in sync. Any rule change in one must be reflected in the other.

---

## 4. Legal Framework Files and What Each Controls

| File | Controls |
|------|---------|
| `frameworks/jurisdictions.py` | Court identities (name, appeal court, AustLII URL, legal aid URL, court forms URL) for all 9 jurisdictions. `LEGISLATION_CURRENCY` metadata for the entire framework package. |
| `frameworks/states.py` | Primary legislation lists for each state (acts, key provisions, penalties). Each state framework is timestamped with `last_verified`. Covers NSW (last verified 2026-04-14), VIC, QLD, SA, WA, TAS, NT, ACT. |
| `frameworks/federal.py` | Commonwealth criminal law: `Criminal Code Act 1995` structure, federal fault elements (s 5.2–5.6), proceeds of crime framework. |
| `frameworks/appeal.py` | Appellate procedure per jurisdiction: governing legislation, court identity, time limits (notice of intention, grounds), required forms (form numbers), cost/leave requirements. |
| `frameworks/sentencing.py` | Sentencing legislation and key provisions per jurisdiction: sentencing purposes, aggravating/mitigating factors, standard non-parole periods, intensive correction orders, victim impact statements, guilty-plea discounts. |
| `frameworks/evidence.py` | Evidence law framework: uniform evidence law jurisdictions (NSW, VIC, TAS, ACT, NT, CTH), key uniform provisions (relevance, hearsay, opinion, admissions, tendency/coincidence, s 137 mandatory exclusion, s 138 illegally obtained), state-specific evidence acts (SA, WA, QLD). |
| `frameworks/mental_impairment.py` | Mental impairment regime per jurisdiction: governing legislation, fitness-to-plead tests, not guilty by reason of mental impairment tests, court disposal options. |
| `frameworks/procedure.py` | 13-stage forensic procedural flows (indictable, hybrid, summary): Incident → Arrest → Charge → Bail → First Mention → Committal → Indictment → Trial Prep → Trial → Verdict → Sentencing → Intermediate Appeal → High Court. `MENS_REA_FRAMEWORK` for all fault element types with authorities and application examples. |
| `frameworks/offences.py` | 18 offence categories with: description, elements, state-specific legislation (all 9 jurisdictions), key provisions, maximum penalties, defence considerations, required fault elements, recommended procedural flow, and relevant sections. |
| `frameworks/common_grounds.py` | Standard appellate grounds with descriptions and applicable jurisdictions. |
| `frameworks/human_rights.py` | Human rights instruments: Charter of Rights and Responsibilities Act 2006 (VIC), Human Rights Act 2019 (QLD), Human Rights Act 2004 (ACT), and Commonwealth constitutional rights relevant to appeals. |
| `frameworks/landmark_cases.py` | Key Australian criminal appeal precedents with citation, principle, and jurisdiction applicability. |
| `frameworks/recent_updates.py` | Recent legislative amendments affecting criminal appeals (e.g., coercive control, affirmative consent). |
| `frameworks/legislation_registry.py` | Single source of truth for legislation currency: every Act referenced in the framework package with `last_verified` date, AustLII URL, and notes. Powers the `/admin/legislation-currency` dashboard. |
| `services/national_framework.py` | Inline jurisdiction matrix for system-prompt injection: appellate tests, mens rea source, mental impairment regime, sentencing act, evidence act, proviso status. Used by `report_generator.py` to build the top-of-prompt `APPELLATE FRAMEWORK` block. |
| `services/national_framework_engine.py` | Full context engine that imports from `frameworks/`: builds rich prompt blocks (legislation, Commonwealth overlay, offence elements, mens rea, mental impairment, appeal pathway, sentencing, evidence, procedural flow, record integrity, anti-hallucination rules). Used by `offence_helpers.py`. |
| `services/jurisdiction_rules.py` | Machine-readable rule sets per jurisdiction for use by `ground_normaliser.py`: appellate tests, proviso availability, appeal types (conviction/sentence/procedure). |

---

## 5. Report-Generation Pipeline — Files and Data Flow

```
                      User clicks "Generate Report"
                              │
                    routers/reports.py
                    POST /api/cases/{id}/reports
                              │
                    services/report_generator.py
                    analyze_case_with_ai()
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
   services/offence_         services/       services/pipeline_
   helpers.py                report_         orchestrator.py
   get_offence_context()     quality.py      _enforce_pipeline_
   get_offence_system_       (post-gen        freshness()
   prompt()                  cleanup)        _load_issue_arguments()
              │                               _load_submission_draft()
              ▼
   services/national_
   framework_engine.py
   build_national_case_context()
              │
              ▼
   services/national_
   framework.py
   build_full_system_prompt()
              │
              ▼
   services/llm_service.py
   call_llm_for_report()  ←──── OpenAI GPT-4o
              │
              ▼
   services/ai_usage_tracker.py
   (fire-and-forget cost record)
              │
              ▼
   services/report_quality.py
   _strip_placeholders() / _dedupe() / _sanitise()
              │
              ▼
   db.reports (MongoDB)
              │
              ▼
   frontend: ReportView.jsx / BarristerView.jsx
              │
              ▼
   Export paths:
   ├── routers/report_exports.py  → PDF (ReportLab) / DOCX (python-docx)
   ├── routers/export.py          → ZIP (Quick Export package)
   └── frontend: exportHtml.js    → Print / inline HTML
```

### Staged Pipeline (Pre-Processing)

```
Documents uploaded
      │
routers/pipeline_staged.py
      │
services/pipeline/extract.py     → db.document_extracts
      │
services/pipeline/classify.py    → db.issue_classifications
      │  (ground type taxonomy → 5 canonical buckets)
      │
services/pipeline/verify.py      → db.issue_verifications
      │  (legitimacy scoring via services/legitimacy_engine.py)
      │
services/pipeline/argue.py       → db.issue_arguments
      │
services/pipeline/submit.py      → db.submission_drafts
      │
Ground Normalisation Chain:
  services/ground_normaliser.py
  services/ground_cleanup.py
  services/ground_dedup.py
  services/appeal_strength.py
  services/barrister_mode.py
  services/proviso_engine.py
  services/outcome_predictor.py
      │
services/report_generator.py (draws on pipeline results)
```

---

## 6. Import Relationships Between Framework / Service / Report Files

```
report_generator.py
  ├── from offence_framework import OFFENCE_CATEGORIES, AUSTRALIAN_STATES
  ├── from services.llm_service import call_llm_for_json, call_llm_structured
  ├── from services.offence_helpers import get_offence_context, get_offence_system_prompt
  ├── from services.document_helpers import build_document_context
  ├── from services.report_quality import _build_anchor_terms, _split_report_sections, …
  ├── from services.pipeline_orchestrator import _enforce_pipeline_freshness, …
  └── (lazy) from services.national_framework import build_full_system_prompt

offence_helpers.py
  ├── from offence_framework import OFFENCE_CATEGORIES, AUSTRALIAN_STATES, …
  │    (all 18 framework symbols via back-compat shim)
  └── (lazy) from services.national_framework_engine import build_national_case_context

national_framework_engine.py
  ├── from frameworks.offences import OFFENCE_CATEGORIES
  ├── from frameworks.jurisdictions import AUSTRALIAN_STATES
  ├── from frameworks.appeal import APPEAL_FRAMEWORK
  ├── from frameworks.sentencing import SENTENCING_FRAMEWORK
  ├── from frameworks.evidence import EVIDENCE_FRAMEWORK
  ├── from frameworks.mental_impairment import MENTAL_IMPAIRMENT_FRAMEWORK
  └── from frameworks.procedure import MENS_REA_FRAMEWORK

pipeline/classify.py
  └── from services.offence_helpers import _build_recent_legislation_context,
        _build_state_framework_context, _build_federal_framework_context

pipeline/verify.py
  └── from services.legitimacy_engine import calculate_ground_rating

pipeline_orchestrator.py
  ├── from services.pipeline import extract_document_artifacts, classify_case_issues, verify_issue
  └── from routers.pipeline_staged import _ensure_document_extracts, _refresh_case_extract, …

ground_normaliser.py
  └── from services.jurisdiction_rules import get_rules, infer_pathway

ground_cleanup.py
  └── from services.ground_normaliser import Ground, SubParticular, normalise

proviso_engine.py
  └── from services.ground_normaliser import Ground

barrister_mode.py
  └── from services.ground_normaliser import Ground

report_quality.py
  └── from services.offence_helpers import enforce_forensic_language

offence_framework.py (shim)
  └── from frameworks import *
```

---

## 7. NSW-Only Defaults and Jurisdiction Risks

### Explicit Anti-NSW-Default Guards

The codebase contains multiple layers of protection against silent NSW defaulting:

1. **`services/national_framework.py`**: `get_jurisdiction_framework()` returns `None` if no state supplied. `build_full_system_prompt()` returns `"ERROR: Jurisdiction must be specified..."` on missing/unknown state.

2. **`services/national_framework_engine.py`**: `normalise_jurisdiction()` raises `ValueError` on unknown jurisdiction. Comment: `# Never default to NSW.`

3. **`services/pipeline/draft.py`**: Explicitly checks `if not case.get('state'):` and injects `"JURISDICTION NOT CONFIRMED — Do NOT default to NSW legislation."` into the system prompt.

4. **`services/offence_helpers.py`**: `get_offence_context()` builds jurisdiction-specific blocks and emits a warning if no state is supplied.

5. **LLM system prompts** (in `report_generator.py`): Every system prompt ends with `"DO NOT: Default to NSW"`.

### Residual Jurisdiction Risks

| Risk | Location | Severity |
|------|----------|---------|
| `national_framework.py` inline matrix (9 entries) may drift from `frameworks/states.py` data if states are updated separately | `services/national_framework.py:10–140` | Medium — both are manually maintained, no automated sync |
| `models/__init__.py` `StateType` literal includes `"federal"` not `"cth"` but `national_framework_engine.py` normalises `"federal"` → `"cth"` | `models/__init__.py`, `national_framework_engine.py:95` | Low — normalised at the engine layer |
| New router endpoints that accept `state` from user input without validation could still reach LLM with no-jurisdiction case | Various routers | Low — soft gate via `case_validation.py` |
| `LEGISLATION_CURRENCY.last_verified = "2026-02"` — the inline review date in `frameworks/jurisdictions.py` is not automatically updated | `frameworks/jurisdictions.py:9` | Low — informational only |

---

## 8. Dead Code, Unused Files, Duplicate Engines, Old Shims, Conflicting Logic

### Dead Code / Unused in Production

| File / Symbol | Status | Evidence |
|---------------|--------|---------|
| `backend/services/ai_service.py` | **Dead in production** | Zero `from services.ai_service import` calls in any non-test file. `call_llm_with_retry()` is effectively superseded by `llm_service.py`. |
| `docs/audit/FULL_AUDIT_REPORT.txt` | Internal audit log | Historical git log / debug artifact — not application code |
| `docs/audit/COMPLETE_JOB_AUDIT.txt` | Internal audit log | Same |
| `docs/audit/FULL_JOB_AUDIT.txt` | Internal audit log | Same |
| `frontend/public/mockups.html`, `frontend/public/mockups-mobile.html` | Development mockups | Not linked from app; exist in `public/` but are not part of the app |
| Some `frontend/src/components/ui/` primitives | Potentially unused | Many Shadcn/Radix primitives (e.g. `aspect-ratio.jsx`, `carousel.jsx`, `drawer.jsx`, `input-otp.jsx`, `menubar.jsx`, `resizable.jsx`) may not be referenced by any page component. A full tree-shake would confirm. |

### Old Shims (Intentionally Kept)

| File | Shim Role | Can it be removed? |
|------|-----------|--------------------|
| `backend/offence_framework.py` | `from frameworks import *` back-compat shim | Not yet — `offence_helpers.py` and `report_generator.py` still import from `offence_framework` directly. Safe to retire after updating those two files. |

### Duplicate Engines (Functional Overlap)

| Pair | Overlap | Action Needed |
|------|---------|---------------|
| `services/national_framework.py` vs `services/national_framework_engine.py` | Both build jurisdiction-aware LLM prompt context. The former uses an inline matrix; the latter imports from `frameworks/`. Both are actively used in different call paths. | Merge into one engine that sources all data from `frameworks/`. Retire the inline matrix in `national_framework.py`. |
| `routers/pipeline.py` vs `routers/pipeline_staged.py` | Both expose pipeline endpoints. `pipeline_orchestrator.py` calls private `_` functions from `pipeline_staged`. | Consolidate: either rename `pipeline_staged` as the single pipeline router, or clearly document which router owns which step. |

### Conflicting Logic

| Issue | Location | Notes |
|-------|----------|-------|
| Ground dedup threshold has oscillated: was 65, then 85, then combined three-method approach | `services/ground_dedup.py` (commit history) | Now stable at three-method. No current conflict, but the iterative tuning history creates fragility — any future change risks re-introducing multiplication. |
| `_ensure_issue_classifications()` skips re-classification if ≥8 issues exist, but re-classifies if <8 | `services/pipeline_orchestrator.py:~60` | The `8` threshold is a magic number embedded in code without a named constant. |
| `StateType` in `models/__init__.py` lists `"federal"` but framework engines normalise `"federal"` to `"cth"` internally | `models/__init__.py`, `national_framework_engine.py` | Low impact but creates an inconsistency in what the DB stores vs what the engine uses. |

---

## 9. Plain-English Summary: Keep, Merge, Retire, Refactor

### Keep As-Is

- **`backend/frameworks/`** — The split into 13 themed modules is clean, tested, and correct. All 9 jurisdictions are covered. Do not consolidate back.
- **`backend/services/llm_service.py`** — The authoritative LLM gateway. Well-structured with model fallback, retry, JSON extraction, and report streaming. Keep.
- **`backend/services/ground_dedup.py`** (current version) — Three-method dedup is working. Keep frozen. Only add new `LEGAL_TOPICS` keywords; never remove.
- **Full pipeline chain** (`extract → classify → verify → argue → submit`) — This is the core AI pipeline. Clean, staged, and well-tested.
- **Ground processing chain** (`normaliser → cleanup → appeal_strength → barrister_mode → proviso → outcome_predictor`) — Each step has a single responsibility. Keep.
- **Auth pattern** (session cookie + Google OAuth with CSRF state) — Sound implementation. Keep.
- **`backend/services/export_footer.py`** — Protected file with explicit owner approval. Keep.
- **`backend/services/md_normaliser.py` + `frontend/src/utils/mdRender.js`** — Intentional mirrors. Keep both; update together.

### Merge

- **`national_framework.py` into `national_framework_engine.py`** — Both solve the same jurisdiction-to-prompt problem. The inline matrix in `national_framework.py` is a subset of `frameworks/states.py`. Migrate `report_generator.py` to use `national_framework_engine.build_national_case_context()` and retire the inline copy in `national_framework.py`. The `build_full_system_prompt()` wrapper can be recreated on top of the engine.
- **`offence_helpers.py` direct imports** — Change `from offence_framework import ...` to `from frameworks import ...` to eliminate the shim indirection.

### Retire

- **`backend/services/ai_service.py`** — Not imported by any production code. A relic of the pre-`llm_service` era. Safe to delete after confirming test-only usage.
- **`backend/offence_framework.py` shim** — Once `offence_helpers.py` and `report_generator.py` are updated to import directly from `frameworks`, this file can be deleted.
- **`docs/audit/` directory** — Contains historical git-log artifacts. Not application code or user docs. Can be deleted or archived.
- **Frontend mockup files** (`public/mockups.html`, `public/mockups-mobile.html`) — Development artifacts not linked from the app.

### Refactor

- **Pipeline router consolidation** — Decide whether `pipeline.py` or `pipeline_staged.py` is the authoritative router. Move all pipeline endpoints into one file, deprecate the other.
- **Magic number `8` in `pipeline_orchestrator.py`** — Replace with a named constant `MIN_HEALTHY_ISSUE_COUNT = 8` with a comment explaining the design choice.
- **`StateType` inconsistency** — Align `models/__init__.py` `StateType` to use `"cth"` instead of `"federal"` to match what the framework engines actually store/use, or vice versa.
- **Shadcn/UI tree-shake** — Audit which `frontend/src/components/ui/` primitives are actually imported and remove unused ones to reduce bundle size.

---

## 10. Priority Action Plan

### 🔴 Critical

| # | Action | Rationale |
|---|--------|-----------|
| C1 | **Retire `services/ai_service.py`** | Dead production code — creates confusion about which LLM interface to use. Risk of an agent or developer accidentally wiring it back up, bypassing `ai_usage_tracker.py` and `llm_service`'s model fallback. |
| C2 | **Align `StateType` in `models/__init__.py` with `"cth"` vs `"federal"` inconsistency** | Silent mismatch between DB-stored values and what the engine normalises. Could cause framework lookups to fail for Commonwealth cases on edge paths. |

### 🟡 Important

| # | Action | Rationale |
|---|--------|-----------|
| I1 | **Merge `national_framework.py` into `national_framework_engine.py`** | Two independent copies of the jurisdiction matrix create a drift risk. If `frameworks/states.py` is updated but `national_framework.py` is not (or vice versa), LLM prompts for `report_generator` will silently use stale legislation. |
| I2 | **Update `offence_helpers.py` and `report_generator.py` to import from `frameworks` directly** (then retire `offence_framework.py` shim) | The shim adds an indirection layer and a confusingly named file. New developers commonly mistake the shim for the source of truth. |
| I3 | **Consolidate pipeline routers** (`pipeline.py` + `pipeline_staged.py`) | Two registered routers with overlapping semantics creates endpoint ambiguity. `pipeline_orchestrator.py` calling private `_` functions from `pipeline_staged` is a code smell (tight coupling to internal implementations). |
| I4 | **Name the magic constant `8`** in `pipeline_orchestrator.py` | The `if len(existing_issues) >= 8` threshold is undocumented logic that directly controls LLM re-classification behaviour. A named constant with a comment prevents future mis-tuning. |

### 🟢 Later

| # | Action | Rationale |
|---|--------|-----------|
| L1 | **Delete `docs/audit/` directory** | Historical debug artifacts. Not user-facing documentation. |
| L2 | **Remove frontend mockup files** (`public/mockups.html`, `public/mockups-mobile.html`) | Development artifacts served from `public/` unnecessarily increase the production build size and could confuse visitors. |
| L3 | **Audit and tree-shake unused Shadcn/UI primitives** in `frontend/src/components/ui/` | Reduces frontend bundle size. Low risk — Shadcn components are self-contained. |
| L4 | **Keep `md_normaliser.py` and `mdRender.js` in sync** by adding a test that runs both on the same input and asserts identical output | These files are intentionally mirrored but have no automated sync check. A divergence would cause backend-saved text to render differently on the frontend. |
| L5 | **Add a `MIN_HEALTHY_ISSUE_COUNT` constant to `pipeline_orchestrator.py`** and document the rationale | Low-effort, high-clarity improvement. |

---

*Audit generated 2026-04-24. No application logic was modified.*
