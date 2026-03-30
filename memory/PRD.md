# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your".
- **Branding:** "Created and Designed by Deb King" only at BOTTOM of prints/exports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown.
- **Language:** Australian English throughout.

## Architecture
```
/app/
├── .github/workflows/ci.yml  # CI: Node 22, Python 3.11, FORCE_JAVASCRIPT_ACTIONS_TO_NODE24
├── backend/
│   ├── server.py, config.py, auth_utils.py
│   ├── routers/ (documents, auth, cases, payments, analytics, etc.)
│   ├── services/ (LLM, offence, email, document, notes)
│   └── tests/
└── frontend/
    └── src/
        ├── components/ (ReportsSection, DocumentsSection, InstallPrompt, etc.)
        ├── pages/ (BarristerView, ReportView, CaseDetail, DocumentPreviewPage, etc.)
        ├── utils/ (exportHtml.js, isIOS.js)
        └── App.js
```

## What's Been Implemented

### Session 3 — 30 Mar 2026
- **CI/CD Pipeline Fix:** node-version 20→22, FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true, excluded tests/ from ruff lint, auto-fixed 53 backend lint issues
- **iOS/iPadOS Detection Fix (CRITICAL):** Created shared `isIOSDevice()` utility (`/app/frontend/src/utils/isIOS.js`) that detects iPadOS desktop user agent (Macintosh + maxTouchPoints > 1). Replaced all 8+ inline `/iPad|iPhone|iPod/` checks across 7 files. Fixes: "Failed to export PDF", "Preview unavailable", blob download failures, and auto-print blocking on iPadOS.
- **Document Preview Fix:** Removed stale sessionStorage fallback from DocumentPreviewPage — now reads only from localStorage.
- **PDF Page Break Fixes:** Added comprehensive page-break CSS rules across ReportView, BarristerView, CaseDetail, and exportHtml.js:
  - Cover page gets its own page (page-break-after: always)
  - Coloured report header starts on new page (page-break-before: always, page-break-inside: avoid)
  - Disclaimer never splits across pages (page-break-inside: avoid)
  - Branding stays with disclaimer (page-break-before: avoid)
- **Print Colour Fix:** Added universal `* { -webkit-print-color-adjust: exact !important }` in @media print across all export HTML generators. Forces iOS Safari to render coloured backgrounds in PDF output.
- **File Upload Fix:** Added 10MB max file size validation and 120s timeout to document upload in DocumentsSection.jsx. Better error messages.

### Previous Sessions
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe localStorage-based preview
- Barrister View with teal UI, "Attachment A — Barrister Issue Matrix"
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth, Email via Resend
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
