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
│   ├── routers/          # auth, cases, grounds, payments, caselaw
│   ├── services/pipeline # AI pipeline stages
│   └── server.py         # Core logic (~7000 lines)
├── frontend/src/
│   ├── components/       # GroundsOfMerit, CaseLawPanel, etc.
│   ├── pages/            # Dashboard, CaseDetail, ReportView, etc.
│   └── App.js            # Routing and Auth (DO NOT UNDO)
```

## Integrations
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Google Auth (social login)
- Resend (emails)
- PayPal / Stripe (payments)

## What's Been Implemented
- Full authentication (Google OAuth + email/password)
- Document upload & management
- AI pipeline: Extract → Classify → Verify → Project → Argue
- Grounds of merit identification and investigation
- Tiered report generation (Free, $150, $200, Barrister)
- PDF/DOCX export with branded footers
- Timeline generation and analysis
- Case Law search integration (AustLII, NSW Caselaw, etc.)
- Print All / PDF All / Word All export
- Case sharing & collaboration
- Admin dashboard & stats
- Verified Case Law Database (Law tab)
- Pipeline Progress tracking
- Deadline Tracker with Google Calendar
- DO_NOT_UNDO permanent guards

## Key DB Collections
- `users`, `user_sessions`, `cases`, `documents`
- `grounds_of_merit`, `reports`, `notes`, `timeline_events`
- `payments`, `case_shares`

## P0/P1/P2 Remaining
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Database normalisation script for legacy entries
