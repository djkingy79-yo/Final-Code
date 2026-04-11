# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals case management platform for Australian jurisdictions. Features secure document management, AI-powered case analysis, tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View), and jurisdiction-specific legal frameworks.

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth). Barrister View is capstone synthesis.
- **Report Language:** Strict third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation.
- **Print Formatting:** Exact footer: "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] [Date] Page X of Y" (Times New Roman, italic, 9pt).
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
│   ├── PipelineProgress.jsx # Pipeline stat grid + actions
│   ├── AppFooter.jsx, AuthModal.jsx
│   ├── FastScrollTop.jsx  # Mobile-responsive FABs
│   └── ShareCaseModal.jsx
├── pages/
│   ├── Dashboard.jsx, CaseDetail.jsx, LandingPage.jsx
│   ├── ReportView.jsx, BarristerView.jsx
│   ├── PaymentHistoryPage.jsx (PayID only)
│   ├── DocumentPreviewPage.jsx
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
- Stripe completely removed; PayID-only payment flow
- Image optimisation: 1.7MB total savings
- "Made with Emergent" badge hidden
- Mobile FAB overlap fixed
- Success Stories content compliance
- Legal Framework: added appeal legislation for SA, TAS, NT, ACT, CTH
- Google Login permanent fix (button onClick instead of link)
- Full lint cleanup + dead code removal

## Session 5 Completed (Apr 2026)
- **PDF Print footer overlap FIXED**: @page bottom margin increased from 30mm to 45mm, footer repositioned to bottom:6mm with 9pt font and nowrap to prevent text wrapping/overlap
- **Pipeline Progress empty white boxes FIXED**: Stat grid only renders when `hasAnyPipelineData` is true
- **Native Mobile App Finalised**: React build + Capacitor v7 sync completed. Removed ~1.4MB of stray debug files from public/. 12 plugins registered for both Android & iOS. Ready for Android Studio / Xcode build.
  - App ID: `com.debking.criminalappeals`
  - App Name: `Appeal Case Manager`
  - Web assets: 16MB per platform
- **Print footer floating on iOS FIXED**: `.print-footer` now `display: none` by default, only `display: block` in `@media print` — stops footer from floating over content on screen/iOS views
- **Note cards styling FIXED**: Export note cards changed from blue bg/white text to white bg (#fff) with black text (#0f172a). Dark blue border (#1e3a5f). "Case Notes" header stays bright blue (#2563eb)
- **Word All export FIXED**: Changed from broken HTML preview navigation to direct `.doc` Blob download (application/msword). Works on all devices including iOS. Both "Word All" and Progress "Word" buttons fixed.

## Backlog
- P2: Counsel conference prep attachment for Barrister View
