# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth). Barrister View locked until all 3 reports generated/paid.
- **Report Language:** STRICT third-person educational tool. No first/second person pronouns.
- **Branding:** Forced light mode. High contrast. No amber/brown. Action buttons bright blue (bg-blue-600) with white text.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Payments:** PayID only (no Stripe/PayPal).
- **Production Domain:** criminallawappealmanagement.com.au

## Tech Stack
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + Python
- Database: MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Email: Resend
- Payments: PayID only

## Architecture
```
/app/
├── backend/
│   ├── server.py (core logic, LLM engine, security middleware)
│   ├── config.py (env validation, DB setup)
│   ├── auth_utils.py (session management)
│   └── routers/ (auth, cases, payments, timeline, etc.)
├── frontend/
│   └── src/
│       ├── pages/ (all page components)
│       ├── components/ (shared components)
│       └── App.js (routing, global nav)
├── Dockerfile
├── Procfile
├── DEPLOYMENT.md
├── SECURITY.md
├── BACKUP.md
└── PRODUCTION_CHECKLIST.md
```

## What's Been Implemented
- Full authentication (Google + email/password)
- Case CRUD with document management
- 4-tier AI report generation (Free, Detailed, Extensive, Barrister)
- PDF/DOCX export with branding/disclaimers
- PayID payment integration
- Timeline with reorder feature
- All resource pages (Glossary, Forms, Stats, Resources, Lawyers, FAQ, etc.)
- Comprehensive Terms & Conditions + Privacy Policy
- Global floating navigation
- Production security hardening (see below)

## Completed (5 Apr 2026)
- Restyled CaselawSearchPage: AustLII box bright blue, enlarged headings
- Replaced Barrister View screenshot on How To Use page
- Fixed footer mobile layout (3 columns, copyright bar)
- Reorganised all navigation (footer + mobile menu) to user's 15-page order
- Removed criminallawappealmanagement.com.au from footer brand section
- Rewrote Terms & Conditions (29 sections, 3 parts, PayID-only payment terms)
- Full backend security scan: CORS, env validation, session tokens, HTTP status codes
- Full frontend code scan: null checks, dead code, XSS defence, debug logs removed
- Production hardening: Dockerfile, Procfile, .env.example, security headers, rate limiting, readiness/liveness probes, deep health check
- Created DEPLOYMENT.md, SECURITY.md, BACKUP.md, PRODUCTION_CHECKLIST.md
- Password reset and session invalidation
- Test credentials scrubbed from all test files

## Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
