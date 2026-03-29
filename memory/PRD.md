# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** Legal disclaimers on all reports, PDFs, and exports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown. Report colours: Emerald (Quick Summary), Blue (Full Detailed), Purple (Extensive Log), TEAL (Barrister View).
- **Language:** Australian English throughout (analyse, organise, defence, offence).

## User Personas
- **Deb King (Admin/Creator):** Manages the platform, confirms PayID payments.
- **Self-represented litigants:** Primary users seeking appeal assistance.
- **Legal professionals:** Use Barrister View for case synthesis.

## Architecture (Post-Refactoring)
```
/app/
├── backend/
│   ├── server.py              # App factory + Report/AI/Export engine
│   ├── config.py              # Centralised environment variables, DB, logger
│   ├── auth_utils.py          # Authentication helpers
│   ├── models/__init__.py     # All Pydantic models + payment helpers
│   ├── services/              # LLM, offence, email, document, notes helpers
│   ├── routers/               # 20+ modular routers
│   └── tests/
└── frontend/
    └── src/
        ├── components/        # ReportsSection.jsx, etc.
        ├── pages/             # BarristerView.jsx, ReportView.jsx, HowItWorksPage.jsx, etc.
        ├── utils/
        └── App.js
```

## What's Been Implemented
- Full authentication (email/password + Google OAuth via Emergent)
- Case CRUD with document management
- AI-powered report generation (4 tiers)
- Barrister View with Issue Matrix attachment
- Document text extraction (PDF, DOCX, images via OCR)
- Timeline management with auto-generation
- Grounds of merit with AI investigation
- PayID/PayPal/Stripe payment integration
- PDF/DOCX export for all reports
- Case sharing and collaboration
- Real-time WebSocket chat and notes collaboration
- Appeal statistics page
- How It Works tutorial page (9 steps)
- server.py monolith refactoring (7533 → 3848 lines)
- **Barrister View UI overhaul (29 Mar 2026):**
  - TEAL coloured header (bg-teal-700) matching landing page
  - Removed invisible white badge from header
  - Barrister report listed as 4th card in Reports tab (teal)
  - Print/PDF preview with coloured .report-header (teal)
  - Teal-bordered sections with numbered circles
  - Scale icon visibility fix in CaseDetail header
- **How It Works Step 9 (29 Mar 2026):**
  - Added "Chat & Collaboration" as Step 9 with cyan theme
  - Updated hero from "8 steps" to "9 steps"

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
