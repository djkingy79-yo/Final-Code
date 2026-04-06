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

## Completed (5 Apr 2026 — CI Fix)
- Fixed 95 Ruff lint errors across backend/tests/ (F401 unused imports, F541 f-strings, E741 ambiguous vars, E712 False comparison, F841 unused assignment)
- Verified `ruff check backend/` passes with zero errors
- Verified `yarn build` passes cleanly
- Backend health check confirmed healthy

## Completed (6 Apr 2026 — Security & Health Fixes)
- CORS: Removed wildcard `["*"]` fallback, restricted to FRONTEND_URL only
- XSS: Installed DOMPurify, sanitised dangerouslySetInnerHTML in DocumentPreviewPage
- .env.example: Created with all required backend/frontend vars
- CI: Added backend-tests job with pytest execution
- toggleTheme: Clarified as forced light mode (intentional no-op, DO_NOT_UNDO)
- Dead code: Deleted payments_new.py (unmounted duplicate of payments.py)
- Verified existing: security headers, rate limiting (429 after 10 req/min), DB ping, EMERGENT_LLM_KEY validation, console.log removal, PyPI index

## Completed (6 Apr 2026 — Google Auth Fix)
- Fixed Google login redirect to landing page: removed window.history.replaceState before navigate (was desyncing React Router), initialised ProtectedRoute from location.state, fixed cookie samesite mismatch in logout, removed sess_ prefix fallback, removed dead /auth/callback route
- All auth flows verified: 100% pass rate (13/13 backend, all frontend flows)

## Completed (6 Apr 2026 — Broken Links Audit)
- Fixed 7 broken URLs in LawyerDirectory.jsx (VIC: Stary Norton Halphen, Doogue+George; ACT: Andrew Byrnes typo; QLD: Gilshenan & Luton; WA: WA Bar; TAS: Tierney Law; NT: Legal Aid)
- Fixed 7 broken/outdated URLs in ContactsPage.jsx + LegalResourcesPage.jsx (ACLEI→NACC, QPILCH→LawRight, TAS Law Society, Prisoners Aid NSW, WA Justice, NT Legal Aid)
- All external links verified via HTTP requests and web search

## Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
