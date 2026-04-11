# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free -> $150 (2x) -> $200 (3x). Barrister View locked until all 3 are generated/paid.
- **Report Language:** STRICT third-person educational tool. Forensic appellate language. Australian English only.
- **UI:** Forced light mode. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation with correct section numbers. NO NSW defaults.
- **Print Format:** All exported/printed documents: h1=18pt, h3=14pt, h4=14pt, body=12pt, Times New Roman. Footer: "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] DD/MM/YYYY Page X of Y" in Times New Roman, italic, 10pt.

## Architecture
```
/app/
├── backend/
│   ├── server.py                 # Thin app factory (170 lines) — middleware, health, router registration
│   ├── config.py                 # Centralised env vars, DB, logger
│   ├── auth_utils.py             # Auth helpers (session + download token validation)
│   ├── routers/
│   │   ├── __init__.py           # Router registry — register_all_routers(app)
│   │   ├── auth.py               # Auth + download token endpoint
│   │   ├── cases.py              # Case CRUD
│   │   ├── reports.py            # Report endpoints + Quick Brief
│   │   ├── report_exports.py     # PDF/DOCX generation
│   │   ├── pipeline.py           # AI pipeline + Acceptance Pack
│   │   ├── caselaw.py            # Case law search + AI-suggested authorities
│   │   ├── export.py             # Export + translate
│   │   ├── timeline.py           # Timeline CRUD + PDF export
│   │   └── ... (28 routers total)
│   └── services/
│       ├── startup_tasks.py      # DB indexes, orphan recovery, dedup (extracted from server.py)
│       ├── export_footer.py      # Shared footer rendering
│       ├── report_generator.py   # Multi-pass AI report generation
│       ├── barrister_generator.py # Barrister View synthesis
│       └── ... (16 services total)
└── frontend/
    └── src/
        ├── utils/
        │   ├── auSpelling.js     # Pure string normaliser (iOS safe)
        │   ├── exportHtml.js     # Shared print HTML builder
        │   └── downloadToken.js  # Secure download token utility
        ├── components/
        │   ├── CaseLawPanel.jsx  # Find Case Law with AI authorities
        │   └── ReportsSection.jsx
        └── pages/
            ├── CaseDetail.jsx    # Main case view with Print All + ToC
            ├── ReportView.jsx    # Report viewer with print footer
            └── BarristerView.jsx # Barrister View with Quick Brief/Acceptance Pack
```

## Tech Stack
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails
- Payment methods: Stripe + PayID
- Capacitor v7 configured for native mobile

## What's Been Implemented

### Session 5 (Apr 2026) — server.py Monolith Refactor
- **server.py** reduced from 432 → 170 lines (61% reduction)
- Extracted startup tasks (DB indexes, orphan recovery, report flagging, dedup) → `services/startup_tasks.py`
- Consolidated 28 router imports → `routers/__init__.py` with `register_all_routers(app)`
- Zero functionality changes — pure architectural cleanup

### Session 4 (Apr 2026) — Print, Security, Acceptance Pack, Case Law
- Print All: Raw `##` markdown → HTML h3/h4, font sizes fixed, Table of Contents, Australian English
- Barrister Quick Brief iOS fix, Acceptance Pack substantially enhanced
- Find Case Law: AI-suggested authorities, legislation refs, copy-to-clipboard
- Download token security, standardised footer across all exports

### Sessions 1-3 (Apr 2026)
- 9-jurisdiction validation, iOS Safari crash fix, translation formatting
- Citation anti-hallucination, metadata warnings, security hardening
- PDF/DOCX export footers, Barrister View deep synthesis

## Test Coverage
- Session 5: Regression — 6/6 key flows pass (health, auth, cases, reports, download tokens, case law)
- Session 4: iteration_187 — 14/14 backend, 100% frontend
- Session 3: iteration_186 — 12/13 backend, 100% frontend

## Backlog
- P1: "How It Works" page screenshots verification
- P2: Verify "Success Stories" page content compliance
- P2: Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
