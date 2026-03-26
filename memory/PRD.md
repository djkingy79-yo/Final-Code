# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth, 10-15k words) → $200 (3x depth, 25-35k words)
- **Barrister View:** Locked until all 3 standard reports are generated/paid. Synthesis of all reports — ONE section per topic, NO duplicates.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your"
- **Branding:** "Created and Designed by Deb King" header + bold disclaimer on all reports/exports
- **UI/UX:** Forced light mode. High contrast. Australian spelling mandatory.

## Tech Stack
- React frontend + FastAPI backend + MongoDB
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Auth (Google social login)

## What's Been Implemented
- Full case CRUD with document upload (OCR), timeline, grounds, notes
- AI-powered grounds identification ($99 unlock)
- Multi-pass report generation (1/5/7 passes) with partial DB saving
- PDF and DOCX exports with Grounds count and Sentence in header
- **Barrister View** — category-based merge with 15 categories, ONLY single best entry per category (no supplement/append), expanded patterns to catch all title variants
- Aggressive "you/your" and "we/us/our" language stripping (backend + frontend, 70+ patterns)
- **FAQ page** — clear text headings with icons between question groups (not colored bars)
- **Tables mobile-readable** — word-break instead of fixed minWidth
- All pages: Landing, FAQ, How It Works, Legal Resources, About, Contact
- Footer: EXPLORE and LEGAL columns

## Pending/Backlog
- P1: Backend refactoring (decompose server.py monolith ~5800 lines)
- P1: Native mobile app build (Capacitor configured)
- P2: Real-time collaboration/chat in Notes
- P2: Case sharing between users

## Architecture
```
/app/backend/server.py — Core API, AI prompts, exports (5800+ lines)
/app/frontend/src/pages/ — CaseDetail, ReportView, BarristerView, HowItWorksPage, LandingPage, FAQPage
/app/frontend/src/components/ — ReportsSection, NotesSection, DocumentsSection
```
