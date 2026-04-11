# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals case management platform for Australian jurisdictions. Features secure document management, AI-powered case analysis, tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View), and jurisdiction-specific legal frameworks.

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth). Barrister View is capstone synthesis.
- **Report Language:** Strict third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation.
- **Print Formatting:** Exact footer: "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] [Date] Page X of Y" (Times New Roman, italic, 10pt).
- **Australian English:** analyse, organise, judgement, offence, defence throughout.

## Tech Stack
- Frontend: React (CRA) + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o (Emergent LLM Key)
- Auth: Emergent-managed Google OAuth + Email/Password
- Payments: PayID only (Stripe removed)
- Emails: Resend
- Exports: reportlab (PDF), python-docx (DOCX)

## Architecture
```
/app/backend/
├── server.py              # Thin app factory
├── config.py              # Centralised env variables
├── auth_utils.py          # Auth middleware
├── routers/               # All API routes
│   ├── __init__.py        # Router registration
│   ├── payments.py        # PayID payment flow
│   ├── payment_history.py # Payment history & receipts
│   ├── translate.py, barrister_pack.py, export.py
│   ├── pipeline.py, collaboration.py, contradictions.py
│   └── legislation.py, analysis.py, admin.py, etc.
├── services/
│   ├── startup_tasks.py   # DB indexes, cleanup
│   └── export_footer.py   # Shared footer logic

/app/frontend/src/
├── App.js                 # Route definitions
├── components/
│   ├── PaymentModal.jsx   # PayID-only payment
│   ├── AppFooter.jsx, AuthModal.jsx
│   ├── FastScrollTop.jsx  # Mobile-responsive FABs
│   └── ShareCaseModal.jsx
├── pages/
│   ├── Dashboard.jsx, CaseDetail.jsx, LandingPage.jsx
│   ├── ReportView.jsx, BarristerView.jsx
│   ├── PaymentHistoryPage.jsx (PayID only)
│   └── HowItWorksPage.jsx, FAQPage.jsx, etc.
└── utils/
    ├── auSpelling.js, exportHtml.js, downloadToken.js
```

## Completed Features (All Sessions)
- Full authentication (Google OAuth + email/password + password reset)
- Case CRUD with document upload, OCR, text extraction
- AI-powered timeline generation and analysis
- Grounds of merit identification and investigation
- 4-tier report generation (Free, Full Detailed, Extensive Log, Barrister View)
- Barrister Issue Matrix attachment
- PDF/DOCX export with exact footer formatting
- Print All with Table of Contents
- PayID payment integration
- Case law search with AI-suggested cases
- Legal framework with jurisdiction-specific legislation
- Collaboration/chat with WebSocket support
- Case sharing with share links
- Translation to 41 languages
- Acceptance package generation
- Contradiction scanning
- Download token security for exports
- Tutorial pages (How It Works, How To Use) with screenshots
- FAQ (42 answers across 8 categories)
- Appeal Statistics, Success Stories, About pages
- Notification system, Admin dashboard
- Mobile-responsive FABs
- Service worker (network-first caching)
- Capacitor v7 configured for native mobile

## Session 4 Completed (Apr 2026)
- Stripe completely removed (router, package, env key, frontend, config validation)
- PaymentModal simplified to PayID-only flow
- Image optimisation: 1.7MB total savings across 31 images
- "Made with Emergent" badge hidden via CSS (#emergent-badge)
- .gitignore cleaned (removed 12 redundant .pack file entries)
- Fixed /contact broken route (redirect to /legal-resources)
- Fixed mobile FAB overlap (smaller buttons on mobile)
- Comprehensive API health audit (all endpoints verified)
- Full mobile responsiveness audit (all pages at 375px)
- Fixed config.py _REVENUE_ENV undefined variable bug
- Success Stories content compliance: removed all "you/your" from UI text, added legal disclaimer, cleaned pricing reference

## Backlog
- P2: Build native mobile app (Capacitor build/test)
- P2: Counsel conference prep attachment for Barrister View
