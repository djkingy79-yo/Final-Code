# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** "Created and Designed by Deb King" only at BOTTOM of prints/exports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown. Report colours: Emerald (Quick Summary), Blue (Full Detailed), Purple (Extensive Log), Teal (Barrister).
- **Language:** Australian English throughout.

## Architecture
```
/app/
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

## What's Been Implemented (this session — 29 Mar 2026)
- **Barrister View UI overhaul:** Teal coloured header (bg-teal-500), removed invisible badge, listed as 4th card in Reports tab, print/PDF preview with .report-header
- **Print/Export critical bug fix:** Fixed localStorage vs sessionStorage mismatch — DocumentPreviewPage was reading stale content. All exports now use localStorage consistently.
- **"Created and Designed by Deb King" removed from TOP** of Timeline + Grounds prints (kept at bottom only)
- **Word export iOS fix:** Changed MIME type to application/msword with Word XML envelope + BOM across all HTML-to-Word exports
- **How It Works Step 9:** Added "Chat & Collaboration" step with cyan theme
- **Stats page formatting:** Bigger headings (text-2xl/3xl), compact Data Sources with horizontal bullets, state-coloured tabs (NSW=blue, VIC=purple, QLD=red, WA=emerald, TAS=teal, NT=orange, ACT=indigo), bigger numbered bullet headings with smaller body text
- **Landing page:** "Simple, Affordable Access" heading now text-3xl/4xl

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
