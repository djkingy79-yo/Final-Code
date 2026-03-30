# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis via a 5-stage pipeline, and a tiered reporting system.

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown.
- **Language:** Australian English throughout (analyse, organise, defence, offence, colour).
- **Terminology:** "Appeal Preparation Readiness" (not "Case Strength"), "Platform Pattern Indicators" (not "Likelihood of Success").

## Architecture
```
/app/
├── backend/
│   ├── server.py, config.py, auth_utils.py
│   ├── models/__init__.py     # DO NOT UNDO: state/offence = Optional[None]
│   ├── routers/
│   │   ├── caselaw.py         # NEW: Verified case law search
│   │   └── ... (20+ modules)
│   ├── services/
│   │   ├── caselaw_search.py  # NEW: State database configs + URL builders
│   │   └── pipeline/          # extract, classify, verify, draft, argue, submit
│   └── tests/
└── frontend/
    └── src/
        ├── components/
        │   ├── CaseLawPanel.jsx   # NEW: Verified case law database search UI
        │   └── ... (existing components)
        └── pages/
```

## What's Been Implemented

### Session 6 — 30 Mar 2026
**Verified Case Law Database Integration (P2):**
- Backend service `caselaw_search.py` with all 8 Australian jurisdictions configured
- State-specific databases: NSW CaseLaw, QLD Judgments, Supreme Court Library QLD, Courts SA, eCourts WA, Victorian Supreme Court, ACT Courts
- National databases: AustLII (all jurisdictions), High Court of Australia, JADE, Google Scholar
- API endpoints: `/api/cases/{case_id}/caselaw/search`, `/api/cases/{case_id}/caselaw/ground/{ground_id}`, `/api/caselaw/databases`
- Frontend CaseLawPanel component with search bar, state-specific database links, collapsible national databases
- Per-ground quick search links in GroundsOfMerit (AustLII, JADE, NSW CaseLaw, QLD Judgments, Google Scholar)
- All searches open directly in official databases (not AI-generated)

**UI Bug Fixes:**
- Runtime error fix: supporting_evidence objects no longer crash React
- Legitimacy Assessment: no longer overlaps on mobile (grid-cols-1 sm:grid-cols-3)
- Dashboard Privacy notice: bright blue bg, bold white text, solid red shield
- Grounds refresh: auto-identify always refreshes grounds list after completion
- Delete Case button: bigger, bolder white text
- Empty state hidden during AI scan

### Previous Sessions
- 5-Stage Pipeline (Extract → Classify → Verify → Project → Draft) + Argue + Submit
- Pipeline Dashboard, Staleness Engine, One-Click Orchestration
- Case Creation Auto-Detect Fix (state/offence/sentence from documents via LLM)
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe preview
- Barrister View with teal UI + Issue Matrix
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth, Email via Resend
- Case sharing, collaboration, messages, notes, notifications
- Landing page, stats page, How It Works page

## DO NOT UNDO (Critical)
See /app/DO_NOT_UNDO.md for full list.

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Database normalisation for legacy records
- P3: Backend refactoring (decompose server.py)
