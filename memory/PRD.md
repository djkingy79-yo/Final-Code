# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, a 5-Stage Data Pipeline (Extract → Classify → Verify → Project → Draft), and a tiered reporting system.

## Core Requirements
- **Report Tiers:** Free (Quick Summary) → $150 (Full Detailed) → $200 (Extensive Log) → Barrister View (locked until all 3 paid)
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your"
- **Branding & UI:** Forced light mode. High contrast. No amber/brown. Blue/slate/navy only. Action buttons = bright blue
- **Report Colours:** Green (Quick), Blue (Full Detailed), Purple (Extensive), Teal (Barrister)
- **Australian English:** "analyse", "organise", "barrister", "defence", "offence", "colour"

## Architecture
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent Google Auth + JWT
- Payments: PayPal/PayID/Stripe
- Email: Resend

## What's Been Implemented
- Full case management (CRUD, documents, timeline, grounds, notes)
- 5-Stage Data Pipeline with fuzzy deduplication (fuzzywuzzy + bidirectional overlap)
- 4-tier report generation with multi-pass engine (8 passes for Full Detailed)
- PDF/DOCX export with preview mode
- Case Identity Card (blue, prominent, on all views)
- Chat collaboration (WebSocket)
- Case sharing
- Pipeline verification (Verify Top 3/6 Issues)
- Admin dashboard, statistics, legal resources
- Mobile-responsive UI with lazy section loading for large reports

## Report Generation Engine (PROTECTED — DO NOT UNDO)
- Full Detailed: 8 passes, ~13,000+ words
- Extensive Log: 8 passes, ~15,000+ words
- Barrister View: Multi-group synthesis + ground expansion, ~12,000+ words
- Dedup: 0.97 threshold for multi-pass, 0.90 for single-pass
- Section expansion for thin sections
- No "cautious language" guardrail on reports

## Grounds Deduplication (PROTECTED — DO NOT UNDO)
- fuzzywuzzy token_set_ratio >= 65
- Bidirectional word overlap > 0.45
- Applied in: pipeline.py, grounds.py, pipeline_staged.py

## Upcoming Tasks
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Database normalisation script
