# Appeal Case Manager — PRD

## Original Problem Statement
Criminal Appeal Case Manager for Australian jurisdictions. Secure document management, AI-powered case analysis via 5-Stage Pipeline (Extract → Classify → Verify → Project → Draft), tiered reporting system. React + FastAPI + MongoDB.

## Core Requirements
- **Report Language:** Strict third-person. No "we/us/our/you/your".
- **UI:** Forced light mode. High contrast. No amber/brown. Bright blue action buttons.
- **Report Colours:** Green (Quick Summary), Blue (Full Detailed), Purple (Extensive Log), Teal (Barrister).
- **Australian English:** analyse, organise, barrister, defence, offence, colour.
- **DO_NOT_UNDO Guards:** Case auto-detect, models, Case Identity Card, "Case name" prevention.

## Architecture
```
/app/
├── backend/
│   ├── models/           # Pydantic models (DO NOT UNDO)
│   ├── routers/          # auth, cases, grounds, payments, caselaw, pipeline
│   ├── services/pipeline # AI pipeline stages (extract, classify, verify, project, argue)
│   └── server.py         # Report generation (~4400 lines)
├── frontend/src/
│   ├── components/       # GroundsOfMerit, CaseLawPanel, ReportsSection, PipelineProgress
│   ├── pages/            # Dashboard, CaseDetail, ReportView, BarristerView
│   └── App.js            # Routing and Auth
```

## Integrations
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Google Auth (social login)
- Resend (emails)
- PayPal / Stripe (payments)

## What's Implemented
- Authentication (Google OAuth + email/password)
- Document upload & auto-detect (state, offence, sentence, timeline)
- AI pipeline: Extract → Classify → Verify → Project → Argue
- Grounds of merit with Investigation (deep analysis)
- Pipeline Verification (Verify Top 3/6 Issues)
- Tiered reports (Free/Quick, $150/Full, $200/Extensive, Barrister)
- PDF/DOCX/Print export via document preview (no downloads)
- Case Law search (AustLII, NSW Caselaw)
- Case Identity Card (defendant, offence, state, sentence)
- Fuzzy deduplication for grounds
- Chat, Collab, Share features

## P0/P1/P2 Remaining
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Database normalisation script
