# Appeal Case Manager — PRD

## Original Problem Statement
Criminal Appeal Case Manager for Australian jurisdictions. Features secure document management, AI-powered case analysis via a 5-Stage Data Pipeline (Extract → Classify → Verify → Project → Draft), and a tiered reporting system. Built with React + FastAPI + MongoDB.

## Core Requirements
- **Report Language:** Strict third-person educational tool. No "we/us/our/you/your".
- **Branding & UI:** Forced light mode. High contrast. No amber/brown. Bright blue action buttons.
- **Australian English:** analyse, organise, barrister, defence, offence, colour.
- **Issue Spotter:** NOT a legal predictor. Uses "Appeal Preparation Readiness".
- **DO_NOT_UNDO Guards:** Critical functions protected (case auto-detect, models).

## Architecture
```
/app/
├── backend/
│   ├── models/           # Pydantic models (DO NOT UNDO guards)
│   ├── routers/          # auth, cases, grounds, payments, caselaw, pipeline
│   ├── services/pipeline # AI pipeline stages
│   └── server.py         # Core logic
├── frontend/src/
│   ├── components/       # GroundsOfMerit, CaseLawPanel, ReportsSection, etc.
│   ├── pages/            # Dashboard, CaseDetail, ReportView, BarristerView, etc.
│   └── App.js            # Routing and Auth
```

## Integrations
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Google Auth (social login)
- Resend (emails)
- PayPal / Stripe (payments)

## What's Been Implemented
- Full authentication (Google OAuth + email/password)
- Document upload & management (22 docs)
- AI pipeline: Extract → Classify → Verify → Project → Argue
- Grounds of merit identification and investigation (5 grounds)
- Tiered report generation (Free, $150, $200, Barrister)
- PDF/DOCX export with branded footers
- Timeline generation and analysis
- Case Law search integration (AustLII, NSW Caselaw, etc.)
- Print All / PDF All / Word All export (enhanced with full content)
- Case sharing & collaboration
- Admin dashboard & stats
- Pipeline Verification (Verify Top 3/6 Issues)
- DO_NOT_UNDO permanent guards
- iOS-compatible document preview (direct render)

## Key DB Collections
- `users`, `user_sessions`, `cases`, `documents`
- `grounds_of_merit`, `reports`, `notes`, `timeline_events`
- `payments`, `case_shares`, `issue_classifications`, `issue_verifications`

## P0/P1/P2 Remaining
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Database normalisation script for legacy entries
