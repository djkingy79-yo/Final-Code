# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** "Created and Designed by Deb King" only at BOTTOM of prints/exports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown. Report colours: Emerald (Quick Summary), Blue (Full Detailed), Purple (Extensive Log), TEAL (Barrister View).
- **Language:** Australian English throughout (analyse, organise, defence, offence).

## Architecture
```
/app/
├── backend/
│   ├── server.py              # App factory + Report/AI/Export engine
│   ├── config.py              # Centralised environment variables
│   ├── routers/               # 20+ modular routers
│   ├── services/              # LLM, offence, email, document, notes helpers
│   └── tests/
└── frontend/
    └── src/
        ├── components/        # ReportsSection, GroundsOfMerit, TimelineEnhanced, LegalFrameworkViewer, NotesSection
        ├── pages/             # BarristerView, ReportView, CaseDetail, DocumentPreviewPage, HowItWorksPage
        ├── utils/             # exportHtml.js
        └── App.js
```

## What's Been Implemented
- Full authentication (email/password + Google OAuth via Emergent)
- Case CRUD with document management + AI-powered report generation (4 tiers)
- Barrister View with Issue Matrix attachment
- Document text extraction, Timeline, Grounds of merit
- PayID/PayPal/Stripe payment integration
- PDF/DOCX export for all reports
- Case sharing and collaboration + Real-time WebSocket chat
- How It Works (9 steps incl. Chat & Collaboration)
- server.py refactoring (7533 → 3848 lines)
- **Barrister View UI overhaul (29 Mar 2026):**
  - Lighter teal (bg-teal-500) coloured header matching landing page
  - Removed invisible white badge from header
  - Barrister report listed as 4th card in Reports tab (teal)
  - Print/PDF preview with coloured .report-header (teal)
- **Print/Export bug fixes (29 Mar 2026):**
  - Fixed localStorage vs sessionStorage mismatch — DocumentPreviewPage was reading stale content
  - Removed "Created and Designed by Deb King" from TOP of Timeline + Grounds prints (kept at bottom only)
  - Fixed Word export MIME type for iOS (application/msword with Word XML envelope + BOM)
  - All export functions now consistently use localStorage

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: "How It Works" page images — user verification pending
- P3: Further collaboration/chat enhancements
- P3: Case sharing improvements
