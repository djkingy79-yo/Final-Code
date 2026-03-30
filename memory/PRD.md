# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** "Created and Designed by Deb King" only at BOTTOM of prints/exports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown. Report colours: Emerald (Quick Summary), Blue (Full Detailed), Purple (Extensive Log), Teal (Barrister).
- **Language:** Australian English throughout.

## Architecture
```
/app/
├── .github/workflows/ci.yml  # CI pipeline (Node 22, Python 3.11, FORCE_JAVASCRIPT_ACTIONS_TO_NODE24)
├── backend/
│   ├── server.py, config.py, auth_utils.py
│   ├── routers/ (20+ modular routers)
│   ├── services/ (LLM, offence, email, document, notes)
│   └── tests/
└── frontend/
    └── src/
        ├── components/ (ReportsSection, GroundsOfMerit, TimelineEnhanced, LegalFrameworkViewer, NotesSection, InstallPrompt)
        ├── pages/ (BarristerView, ReportView, CaseDetail, DocumentPreviewPage, HowItWorksPage, AppealStatisticsPage, LandingPage, FormTemplates)
        ├── utils/ (exportHtml.js, isIOS.js)
        └── App.js
```

## What's Been Implemented

### Session - 30 Mar 2026
- **CI/CD Pipeline Fix:** Updated node-version 20->22, added FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true, excluded tests/ from ruff lint, auto-fixed 53 backend lint issues
- **iOS Detection Fix (CRITICAL):** Created shared `isIOSDevice()` utility at `/app/frontend/src/utils/isIOS.js` that properly detects iPadOS (desktop user agent: Macintosh + maxTouchPoints > 1). Replaced all 8 inline iOS checks across 7 files. This fixes "Failed to export PDF", "Preview unavailable", and blob download failures on iPadOS.
- **Document Preview Fix:** Removed stale sessionStorage fallback from DocumentPreviewPage — now reads only from localStorage.
- **PDF Print Fix:** Added `-webkit-print-color-adjust: exact !important` to report header and case-info-grid for better iOS PDF rendering.

### Previous Sessions
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe localStorage-based preview
- Barrister View with teal UI, "Attachment A — Barrister Issue Matrix"
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth
- Email notifications via Resend
- Landing page, stats page, How It Works page
- Professional README.md

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: "How It Works" page images verification
- P3: Collaboration/chat enhancements
- P3: Case sharing improvements
