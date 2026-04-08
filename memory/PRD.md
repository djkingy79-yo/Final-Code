# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free Quick Summary, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Quick Summary → Full Detailed → Extensive Log → Barrister View (counsel synthesis).
- **Report Language:** STRICT third-person educational tool. Forensic appellate language ("It is arguable", "There is a tenable argument"). Never definitive conclusions.
- **Appellate Credibility:** Grounds linked to Appellate Pathways. 3-axis viability scoring (legitimacy_engine.py). Psychiatric evidence framed as Mens Rea attack.
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue/slate/navy palette. Action buttons: bright blue + white text.
- **Language:** Australian English throughout (analyse, organise, defence, offence, behaviour).

## Tech Stack
- Frontend: React + Shadcn/UI + Tailwind
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent Google Auth + JWT
- Payments: Stripe + PayPal + PayID
- Email: Resend
- Native: Capacitor v7 (configured, not yet built)

## Key Features Implemented
- Multi-pass AI report generation (Quick Summary, Full Detailed, Extensive Log, Barrister View)
- Staged pipeline: Document extraction → Classification → Verification → Ground projection
- Barrister Quick Brief (2-page PDF via ReportLab)
- Ground of Merit: CRUD, auto-identification, deep investigation, drag-and-drop priority reorder
- Legitimacy Engine (3-axis scoring)
- PDF/DOCX/Word export with iOS-safe fallbacks
- Australian English normaliser (auSpelling.js) — protects markdown links
- Ground deduplication (fuzzy matching)
- Acceptance Pack PDF
- Statistics page
- How It Works tutorial page

## What's Complete (as of Feb 2026)
- All 4 report types functional with correct forensic language
- Barrister View with Counsel Synthesis + Attachment A Issue Matrix
- Ground merging with sub-particulars (psychiatric_mens_rea, jury_integrity, sentencing clusters)
- iOS PDF export working (document-preview route)
- Deployment health checks passing
- 8-point code review fixes (iteration 161): credential redaction, auSpelling markdown safety, iOS Quick Brief fix, reorder atomic validation, merged grounds field preservation, UI jump fix, Pytest guards

## Backlog
- P1: Native Mobile App build (Capacitor v7)
- P2: Camera/Share native device features
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat
- P2: Case sharing between users
