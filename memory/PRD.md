# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your". Conditional language only.
- **Branding:** "Created and Designed by Deb King" at BOTTOM of prints/exports. Legal disclaimer on all reports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown.
- **Language:** Australian English throughout (analyse, organise, defence, offence, colour).
- **Terminology:** "Appeal Preparation Readiness" (not "Case Strength"), "Platform Pattern Indicators" (not "Likelihood of Success").

## Architecture
```
/app/
├── backend/
│   ├── server.py, config.py, auth_utils.py
│   ├── models/__init__.py     # Pydantic models (Case, CaseCreate, Pipeline models)
│   ├── routers/               # 20+ route modules (auth, cases, documents, pipeline, etc.)
│   ├── services/
│   │   ├── legitimacy_engine.py  # 3-layer forensic scoring
│   │   ├── llm_service.py        # Task-type aware LLM calls
│   │   ├── offence_helpers.py    # Jurisdiction-aware prompts
│   │   ├── document_helpers.py   # OCR, page provenance
│   │   └── pipeline/             # extract.py, classify.py, verify.py, draft.py, argue.py, submit.py
│   └── tests/
└── frontend/
    └── src/
        ├── components/           # PipelineProgress, CasePipelineSummary, SubmissionsDraftPanel, etc.
        ├── pages/                # Dashboard, CaseDetail, BarristerView, ReportView, etc.
        ├── utils/
        └── App.js
```

## What's Been Implemented

### Session 5 — 30 Mar 2026 (Pipeline + Auto-Detect Fix)
- **5-Stage Pipeline (Extract → Classify → Verify → Project → Draft)** with Argue + Submit extensions
- **Pipeline Dashboard & Staleness Engine**: Real-time pipeline status, freshness checks
- **One-Click Orchestration**: `/refresh-all` route for sequential pipeline execution
- **Pipeline Guards**: High-value reports enforce pipeline freshness before generation
- **Case Creation Auto-Detect Fix (P0 BUG FIX)**: Removed hardcoded NSW/Homicide defaults. `state` and `offence_category` are now `Optional[None]` in CaseCreate. Frontend strips empty strings. Background LLM auto-detection populates metadata from uploaded documents. **VERIFIED 12/12 tests passing.**

### Session 4 — 30 Mar 2026 (Backend + Frontend Hardening)
- Backend hardening: 7 patches to server.py
- Frontend hardening: 6 shared components, 9 files patched
- Pipeline models + 12 API endpoints + DB indexes

### Session 3 — 30 Mar 2026 (Forensic Barrister Review)
- Legitimacy Engine (3-layer scoring)
- Access Control fixes, Case Readiness reframe
- Anti-Hallucination controls, Grounds validation
- Compare Analytics reframe, LLM Service upgrade
- Document Provenance, Unverified Case badges

### Previous Sessions
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe preview
- Barrister View with teal UI + Issue Matrix
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth, Email via Resend
- Landing page, stats page, How It Works page

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time Collaboration/Chat for Notes
- P2: Case Sharing between users
- P2: Verified Case Law Database integration
- P3: Database normalisation for legacy records
- P3: Backend refactoring (decompose server.py)
