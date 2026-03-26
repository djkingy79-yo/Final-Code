# Appeal Case Manager — PRD

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free, Paid), Barrister View, and PayID integration. Core requirement: hyper-detailed, case-specific legal reports.

## User Persona
- Debra King (founder) — non-lawyer building a legal tech tool for self-represented appellants in Australia
- Strict aesthetic requirement: professional law app, NO dark mode, white backgrounds, black body text, coloured headings, large readable fonts

## Core Requirements
- **Report Tiers:** Free (shows number of grounds), $99 AUD (shows titles), Quick Summary, Full Detailed ($150), Extensive Log ($200)
- **Barrister View:** Capstone report synthesising 3 standard reports
- **UI/UX Rule:** Forced light mode globally. High contrast only. No dark mode toggle. No grey/muted text. Australian spelling throughout.
- **Aggressive Mode:** DELETED by user request

## Tech Stack
- Frontend: React + Tailwind + Shadcn UI
- Backend: FastAPI + MongoDB
- LLM: OpenAI GPT-4o / GPT-4o-mini via Emergent LLM Key
- Auth: Emergent-managed Google Auth

## Key DB Schema
- `reports`: {report_id, case_id, user_id, report_type, status, content}
- `cases`: {case_id, user_id, title, defendant_name, case_number, court, sentence, state}

## Key API Endpoints
- `POST /api/cases/{id}/reports/generate`
- `GET /api/cases/{id}/reports/{id}/export-pdf`

## What's Been Implemented
- Full CRUD for cases, documents, reports
- AI-powered grounds identification (Free + $99 tier)
- 3 report tiers: Quick Summary, Full Detailed, Extensive Log
- Barrister View (unlocks after 3 reports)
- Timeline analysis, document OCR, progress tracking
- 20+ informational pages (Legal Framework, Glossary, Forms, Resources, etc.)
- Force-light CSS enforcement across entire app
- Dark mode toggle removed from ALL pages (26 Mar 2026)
- Report Snapshot cards deleted from Landing Page (26 Mar 2026)
- How It Works page fixed: white step headers, live screenshots, smaller captions, preview cards removed (26 Mar 2026)
- LawyerDirectory: theme toggle removed, "Prepare Before You Meet a Lawyer" CTA deleted (26 Mar 2026)
- SuccessStories: footer CTA text fixed for visibility (26 Mar 2026)
- PageCTA inline variant: fixed for light mode visibility (26 Mar 2026)
- CaseDetail: gradient button replaced with solid blue (26 Mar 2026)

## Prioritised Backlog
### P1
- Backend refactoring (decompose server.py — >5000 lines)
- Native mobile app build (Capacitor configured)

### P2
- Real-time collaboration/chat
- Case sharing between registered users

### P3
- Ongoing UI/UX high-contrast audit (recurring)
