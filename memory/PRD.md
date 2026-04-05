# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth). Barrister View locked until all 3 standard reports generated/paid.
- **Report Language:** STRICT third-person educational tool. No first/second person pronouns.
- **Branding:** Forced light mode. High contrast. No amber/brown. Action buttons bright blue (bg-blue-600) with white text.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.

## Tech Stack
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + Python
- Database: MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth
- Email: Resend
- Payments: Stripe

## Architecture
```
/app/
├── backend/
│   ├── server.py (core logic, LLM engine)
│   ├── config.py (env variables)
│   └── routers/ (auth, cases, payments, timeline, etc.)
└── frontend/
    └── src/
        ├── pages/ (all page components)
        ├── components/ (shared components)
        └── App.js (routing, global nav)
```

## What's Been Implemented
- Full authentication (Google social login)
- Case CRUD with document management
- 4-tier AI report generation (Free, Detailed, Extensive, Barrister)
- PDF/DOCX export with proper branding/disclaimers
- PayID/PayPal/Stripe payment integration
- Timeline with reorder feature
- Lawyer Directory (real solicitors per state)
- Legal Glossary, Forms, Statistics, Resources pages
- How It Works / How To Use pages
- Success Stories page
- Live Caselaw Search page (AustLII + all jurisdictions)
- Global floating navigation (Back, Home, Top, Chat)
- Landing page with proper section ordering
- Professional Summary page

## Completed (This Session - 5 Apr 2026)
- Restyled CaselawSearchPage.jsx: AustLII box bright blue with bold white font, enlarged AustLII heading, enlarged Understanding Court Judgments heading

## Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: Case Sharing between users (noted as already done by user)
- P2: Real-time Collaboration/Chat (noted as already done by user)

## Credentials
- Email: djkingy79@gmail.com
- Password: Grubbygrub88
