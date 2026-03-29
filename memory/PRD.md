# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** Legal disclaimers on all reports, PDFs, and exports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons.
- **Language:** Australian English throughout (analyse, organise, defence, offence).

## User Personas
- **Deb King (Admin/Creator):** Manages the platform, confirms PayID payments.
- **Self-represented litigants:** Primary users seeking appeal assistance.
- **Legal professionals:** Use Barrister View for case synthesis.

## Architecture (Post-Refactoring)
```
/app/
├── backend/
│   ├── server.py              # App factory + Report/AI/Export engine (3848 lines)
│   ├── config.py              # Centralised environment variables, DB, logger
│   ├── auth_utils.py          # Authentication helpers (get_current_user, verify_case_ownership)
│   ├── models/__init__.py     # All Pydantic models + payment helpers
│   ├── services/
│   │   ├── llm_service.py     # LLM call with model fallback
│   │   ├── offence_helpers.py # Offence framework context builders
│   │   ├── email_service.py   # PayID notification emails via Resend
│   │   ├── document_helpers.py# Text extraction, OCR, document context
│   │   └── notes_helpers.py   # Notes WebSocket collaboration helpers
│   ├── routers/
│   │   ├── cases.py           # Case CRUD
│   │   ├── auth.py            # Authentication (login, register, Google OAuth)
│   │   ├── documents.py       # Document CRUD + OCR + text extraction + auto-detect
│   │   ├── timeline.py        # Timeline CRUD + auto-generate + analyse + PDF export
│   │   ├── deadlines.py       # Deadlines + checklist + case strength
│   │   ├── notes.py           # Notes CRUD + pin + comments + WebSocket
│   │   ├── grounds.py         # Grounds of merit CRUD + investigate + auto-identify
│   │   ├── payments.py        # PayID/PayPal/Stripe payment endpoints
│   │   ├── resources.py       # Resource directory + document templates
│   │   ├── analysis.py        # Contradictions + progress analysis
│   │   ├── messages.py        # Chat messages (unused - handled by collaboration.py)
│   │   ├── collaboration.py   # Case sharing + messages + notifications + chat WS
│   │   ├── export.py          # Appeal package export (ZIP/PDF bundle)
│   │   ├── contradictions.py  # AI contradiction scanning
│   │   ├── compare.py         # Case comparison + patterns
│   │   ├── statistics.py      # Public statistics
│   │   ├── analytics.py       # Visit tracking + admin dashboard
│   │   ├── admin.py           # Admin endpoints (contact, stories)
│   │   ├── password_reset.py  # Password reset flow
│   │   └── utilities.py       # States, offence framework, categories
│   └── tests/                 # 64 pytest files (using localhost:8001)
└── frontend/
    └── src/
        ├── components/
        ├── pages/
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
- How It Works tutorial page
- Security vulnerability patching (14+ CVEs)
- ESLint/production build fixes (204+ errors)
- server.py monolith refactoring (7533 → 3848 lines)
- **Barrister View UI overhaul (29 Mar 2026):**
  - Dark navy blue (bg-blue-900) coloured header matching other 3 reports
  - Removed invisible white badge from header
  - Barrister report now listed as 4th card in Reports tab
  - Print/PDF preview with coloured .report-header
  - Blue-bordered sections with numbered circles
  - Scale icon visibility fix in CaseDetail header

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: "How It Works" page images — user verification pending
- P3: Real-time collaboration/chat enhancements
- P3: Case sharing between registered users
