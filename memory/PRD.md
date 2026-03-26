# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth, 10-15k words) → $200 (3x depth, 25-35k words)
- **Barrister View:** Locked until all 3 standard reports are generated/paid. Synthesis of all reports.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your"
- **Branding:** "Created and Designed by Deb King" header + bold disclaimer on all reports/exports
- **UI/UX:** Forced light mode. High contrast. Australian spelling mandatory.
- **Export:** PDF and Word (DOCX). Print available on Barrister View.

## Tech Stack
- React frontend + FastAPI backend + MongoDB
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Auth (Google social login)

## What's Been Implemented
- Full case CRUD with document upload (OCR), timeline, grounds, notes
- AI-powered grounds identification ($99 unlock)
- Multi-pass report generation (1/5/7 passes) with partial DB saving
- PDF and DOCX exports with Grounds count and Sentence in header
- **Barrister View complete rewrite** — category-based merge (15 categories) replacing scattered paragraph selection. Sections now properly deduplicated and ordered logically.
- Aggressive "you/your" and "we/us/our" language stripping (backend + frontend, 70+ patterns)
- Anti-placeholder text stripping in reports
- Landing page, FAQ, How It Works, Legal Resources, About, Contact pages
- Footer reorganised into EXPLORE and LEGAL columns
- Mobile-responsive tables in reports
- Strength rating colour coding (Red=Strong, Blue=Moderate)
- LLM prompts enforce paragraphs (not bullet points), ban placeholder text, ban "you/your"

## Pending/Backlog
- P1: Backend refactoring (decompose server.py monolith ~5800 lines)
- P1: Native mobile app build (Capacitor configured)
- P2: Real-time collaboration/chat in Notes
- P2: Case sharing between users
- P2: Monitor 502 timeout resilience on large report generation

## Architecture
```
/app/backend/server.py — Core API, AI prompts, exports (5800+ lines)
/app/frontend/src/pages/ — CaseDetail, ReportView, BarristerView, HowItWorksPage, LandingPage
/app/frontend/src/components/ — ReportsSection, NotesSection, DocumentsSection
```


## Key Changes This Session
1. Barrister View merge logic completely rewritten (category-based, 15 fixed categories)
2. PDF/DOCX exports now include Grounds count and Sentence
3. 70+ "you/your" patterns added to backend and frontend sanitisation
4. LLM prompts updated: no placeholders, paragraphs not bullets, stronger "you/your" ban
5. How It Works page updated (removed "printed directly" references)
6. Footer reorganised into separate EXPLORE and LEGAL columns
7. Sentence display truncated to 80 chars for card layout
8. Section titles in Barrister View fixed (text-slate-100 → text-slate-900)
