# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth).
- **Barrister View:** Locked until all 3 standard reports are generated/paid. Acts as a capstone synthesis.
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your". Paragraphs, not bullet points.
- **Branding & Disclaimers:** All reports/exports must feature "NOT LEGAL ADVICE" disclaimers.
- **UI/UX:** Forced light mode globally. High contrast. Blue/slate/navy palette. Bright blue action buttons with white text. No amber/brown.
- **Paywalls:** Grounds of Merit shows only count until $99 paid. Admin bypasses all paywalls.
- **Australian English:** All UI text, code, and AI outputs use Australian spelling (analyse, organise, barrister, defence, offence).

## User Personas
- **Admin (Deb King):** djkingy79@gmail.com — bypasses all paywalls, free reports.
- **Regular Users:** Pay for Grounds unlock ($99), reports ($150/$200), Barrister View.

## Tech Stack
- React frontend + FastAPI backend + MongoDB
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Auth (Google social login)
- Resend (emails), PayPal/PayID/Stripe (payments)

## What's Been Implemented
- User auth (JWT + Google social login)
- Case CRUD with AI auto-detection of metadata (State, Crime, Sentence, Court)
- Document upload with text extraction
- Background auto-generation of timeline events on document upload
- Grounds of Merit identification (AI + manual) with strict $99 paywall
- Deep investigation analysis per ground
- 4-tier report system (Free, $150, $200, Barrister View)
- Document export (Print/PDF/Word) across all features
- Timeline with analysis
- Legal Framework viewer
- Notes section
- Collaboration/sharing
- Stats page, How It Works, How To Use pages
- NOT LEGAL ADVICE disclaimers on all printed/exported views
- Condensed case info on Grounds tab (summary hidden, Deb King branding footer added)

## Prioritised Backlog
- **P1:** Build Native Mobile App (Capacitor configured)
- **P2:** Counsel conference prep attachment for Barrister View
- **P3:** Break up server.py monolith (>7300 lines)

## Architecture
```
/app/
├── backend/
│   ├── server.py           # Core logic, LLM generation engine
│   ├── routers/            # Extracted API routes
│   ├── models/
│   └── .env
└── frontend/
    └── src/
        ├── components/     # GroundsOfMerit, Timeline, Documents, etc.
        ├── pages/          # CaseDetail, Reports, Barrister, Stats, etc.
        └── App.js
```
