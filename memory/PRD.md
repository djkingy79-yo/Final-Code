# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis via a 5-stage pipeline (Extract → Classify → Verify → Project → Draft), and a tiered reporting system.

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** "Created and Designed by Deb King" at BOTTOM of prints/exports. Legal disclaimer on all reports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown.
- **Language:** Australian English throughout (analyse, organise, defence, offence, colour).
- **Terminology:** "Appeal Preparation Readiness" (not "Case Strength"), "Platform Pattern Indicators" (not "Likelihood of Success").

## Architecture
```
/app/
├── backend/
│   ├── server.py, config.py, auth_utils.py
│   ├── models/__init__.py     # Pydantic models (DO NOT UNDO: state/offence = Optional[None])
│   ├── routers/               # 20+ route modules
│   ├── services/pipeline/     # extract, classify, verify, draft, argue, submit
│   └── tests/
└── frontend/
    └── src/
        ├── components/        # GroundsOfMerit, LegitimacyPanel, DashboardPipelineSummary, etc.
        ├── pages/             # Dashboard, CaseDetail, BarristerView, ReportView, etc.
        └── App.js
```

## What's Been Implemented

### Session 6 — 30 Mar 2026 (UI Bug Fixes + Grounds Fix)
- **Runtime Error FIX**: supporting_evidence objects (EvidenceItem dicts) were crashing React as children. Fixed in 3 locations in GroundsOfMerit.jsx to render item.quote/item.text.
- **Legitimacy Assessment Overlap FIX**: Changed grid-cols-3 → grid-cols-1 sm:grid-cols-3 in both LegitimacyPanel.jsx and LegitimacyBreakdown.
- **Dashboard Styling FIX**: Privacy notice → bg-blue-600, bold white text, solid filled red SVG shield. Pipeline Portfolio Summary → bg-blue-600 with bold white text.
- **Grounds Not Showing FIX**: After auto-identify, the grounds list now ALWAYS refreshes regardless of identified_count. Empty state hidden during scan.
- **Delete Case Button**: Text made bigger (text-base) and bolder (font-extrabold), icon enlarged.
- **Auto-detect DO NOT UNDO guards**: Added to models/__init__.py, routers/documents.py, Dashboard.jsx, and DO_NOT_UNDO.md.

### Session 5 — 30 Mar 2026 (Pipeline + Auto-Detect Fix)
- 5-Stage Pipeline with Argue + Submit extensions
- Pipeline Dashboard, Staleness Engine, One-Click Orchestration
- Pipeline Guards for high-value reports
- Case Creation Auto-Detect Fix (P0 BUG FIX) — 12/12 tests passing

### Previous Sessions
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe preview
- Barrister View with teal UI + Issue Matrix
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth, Email via Resend
- Case sharing, collaboration, messages, notes, notifications (ALL DONE)
- Landing page, stats page, How It Works page

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## DO NOT UNDO (Critical)
See /app/DO_NOT_UNDO.md for full list. Key items:
- CaseCreate state/offence_category/offence_type/sentence defaults MUST remain None
- _background_auto_detect_metadata MUST NOT be removed
- Frontend MUST strip empty strings before sending case creation payload

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: Verified Case Law Database integration
- P3: Database normalisation for legacy records
- P3: Backend refactoring (decompose server.py)
