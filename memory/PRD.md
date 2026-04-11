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
- Payments: Stripe (sk_test_emergent for preview)
- Emails: Resend
- Exports: reportlab (PDF), python-docx (DOCX)

## Architecture
```
/app/backend/
├── server.py              # Thin app factory (~170 lines)
├── config.py              # Centralised env variables
├── auth_utils.py          # Auth middleware
├── routers/               # All API routes
│   ├── __init__.py        # Router registration
│   ├── auth.py, cases.py, pipeline.py, export.py
│   ├── stripe_payments.py, translate.py, barrister_pack.py
│   ├── collaboration.py, contradictions.py, legislation.py
│   └── analysis.py, admin.py, analytics.py, utilities.py
├── services/
│   ├── startup_tasks.py   # DB indexes, cleanup
│   └── export_footer.py   # Shared footer logic

/app/frontend/src/
├── App.js                 # Route definitions
├── components/            # Reusable components
│   ├── AppFooter.jsx, AuthModal.jsx, PaymentModal.jsx
│   ├── FastScrollTop.jsx  # Floating action buttons (mobile-responsive)
│   └── ShareCaseModal.jsx
├── pages/                 # Page components
│   ├── Dashboard.jsx, CaseDetail.jsx, LandingPage.jsx
│   ├── ReportView.jsx, BarristerView.jsx
│   ├── HowItWorksPage.jsx, HowToUsePage.jsx
│   └── FAQPage.jsx, AppealStatisticsPage.jsx, etc.
└── utils/
    ├── auSpelling.js, exportHtml.js, downloadToken.js
```

## Key DB Collections
- `cases`, `documents`, `timeline_events`, `grounds`, `notes`, `reports`
- `sessions`, `users`, `payments`, `download_tokens`
- `notifications`, `share_links`, `case_shares`, `messages`

## Completed Features (All Sessions)
- Full authentication (Google OAuth + email/password + password reset)
- Case CRUD with document upload, OCR, text extraction
- AI-powered timeline generation and analysis
- Grounds of merit identification and investigation
- 4-tier report generation (Free, Full Detailed, Extensive Log, Barrister View)
- Barrister Issue Matrix attachment
- PDF/DOCX export with exact footer formatting
- Print All with Table of Contents and markdown rendering
- Stripe payment integration
- PayID/PayPal payment flows
- Case law search with AI-suggested cases
- Legal framework with jurisdiction-specific legislation links
- Collaboration/chat with WebSocket support
- Case sharing with share links
- Translation to 41 languages
- Acceptance package generation
- Contradiction scanning
- Download token security for exports
- How It Works / How To Use tutorial pages with screenshots
- FAQ (42 answers across 8 categories)
- Appeal Statistics page
- Success Stories page
- Notification system
- Admin dashboard
- Mobile-responsive FABs
- Service worker with network-first caching
- Capacitor v7 configured for native mobile

## Session 3 Completed (Apr 2026)
- Fixed Stripe checkout 404 (was test script using wrong URL; updated to valid sk_test_emergent key)
- Fixed broken /contact route (added redirect to /legal-resources)
- Fixed mobile FAB overlap (reduced button sizes on mobile: h-8 w-8)
- Comprehensive API health audit (all endpoints verified healthy)
- Full mobile responsiveness audit (all key pages verified at 375px)
- Navigation link audit (all footer and internal links verified working)

## Backlog
- P2: Build native mobile app (Capacitor build/test)
- P2: Counsel conference prep attachment for Barrister View
- P2: Success Stories page content compliance verification
- P2: Real-time collaboration/chat enhancements
- P2: Case sharing enhancements
