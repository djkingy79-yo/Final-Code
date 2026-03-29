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
├── .github/workflows/ci.yml  # CI pipeline (Node 22, Python 3.11)
├── backend/
│   ├── server.py, config.py, auth_utils.py
│   ├── routers/ (20+ modular routers)
│   ├── services/ (LLM, offence, email, document, notes)
│   └── tests/
└── frontend/
    └── src/
        ├── components/ (ReportsSection, GroundsOfMerit, TimelineEnhanced, LegalFrameworkViewer, NotesSection)
        ├── pages/ (BarristerView, ReportView, CaseDetail, DocumentPreviewPage, HowItWorksPage, AppealStatisticsPage, LandingPage)
        ├── utils/ (exportHtml.js)
        └── App.js
```

## What's Been Implemented
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe localStorage-based preview
- Barrister View with teal UI, "Attachment A — Barrister Issue Matrix"
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth
- Email notifications via Resend
- Landing page, stats page, How It Works page
- GitHub Actions CI (Node 22, Python 3.11, actions v5/v4)
- Professional README.md

## Recent Fix (Feb 2026)
- CI workflow: Updated node-version 20 -> 22 to eliminate GitHub Actions deprecation warnings
- package.json engines updated to >=18.0.0
- yarn.lock verified in sync

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
