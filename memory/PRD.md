# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth).
- **Barrister View:** Locked until all 3 standard reports are generated/paid. Acts as a capstone synthesis.
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your". Paragraphs, not bullet points.
- **Branding & Disclaimers:** All reports/exports must feature "NOT LEGAL ADVICE" disclaimers + branding footer (scales icon + Appeal Case Manager + Founded by Debra King).
- **UI/UX:** Forced light mode globally. High contrast. Blue/slate/navy palette. Bright blue action buttons with white text. No amber/brown.
- **Paywalls:** Grounds of Merit shows only count until $99 paid. Admin bypasses all paywalls.
- **Australian English:** All UI text, code, and AI outputs use Australian spelling.

## What's Been Implemented
- User auth (JWT + Google social login)
- Case CRUD with AI auto-detection of metadata (State, Crime, Sentence, Court)
- Document upload with text extraction + background auto-timeline generation
- Grounds of Merit identification with strict $99 paywall
- Deep investigation analysis per ground
- 4-tier report system (Free, $150, $200, Barrister View)
- Document export (Print/PDF/Word) across all features with page+date footers
- Branding footer on all report views and exports
- Report Tier Comparison table (Landing Page only, removed from exports)
- Timeline, Legal Framework, Notes, Stats pages
- Chat button (bottom-left), Home+ScrollTop (bottom-right) — properly separated
- PDF preview auto-sizes to content height
- Condensed case info on Grounds tab (summary hidden, Deb King branding footer)

## Prioritised Backlog
- **P1:** Build Native Mobile App (Capacitor configured)
- **P2:** Counsel conference prep attachment for Barrister View
- **P3:** Break up server.py monolith (>7300 lines)

## Architecture
```
/app/
├── backend/
│   ├── server.py           # Core logic, LLM generation engine
│   ├── routers/            # Extracted API routes
│   └── .env
└── frontend/
    └── src/
        ├── components/     # GroundsOfMerit, Timeline, CaseChat, Documents, etc.
        ├── pages/          # CaseDetail, ReportView, BarristerView, DocumentPreviewPage, etc.
        └── App.js
```
