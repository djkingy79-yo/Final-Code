# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions.

## Core Requirements
- **Report Tiers:** Free (Quick Summary) → $150 (Full Detailed) → $200 (Extensive Log) → Barrister View (locked until all 3 paid)
- **Report Language:** STRICT third-person. No "we", "us", "our", "you", "your"
- **UI:** Forced light mode. High contrast. Blue/slate/navy. Bright blue action buttons.
- **Australian English:** "analyse", "organise", "barrister", "defence", "offence"

## Architecture
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent Google Auth + JWT | Payments: PayPal/PayID/Stripe | Email: Resend

## What's Implemented
- Full case management, documents, timeline, grounds, notes
- 5-Stage Data Pipeline with topic-based deduplication (ground_dedup.py)
- 4-tier report generation with multi-pass engine (8 passes for Full Detailed, 7-8 for Extensive Log)
- PDF/DOCX export with preview mode, Case Identity Card
- Chat collaboration (WebSocket), Case sharing
- Pipeline verification, Admin dashboard, statistics, legal resources
- Mobile-responsive with lazy section loading
- **Bulletproof ground deduplication** (12 legal topics, 3-layer matching, startup+post-sync safety nets)
- **Condensed prompts** for multi-pass generation (prevents 502 proxy errors)
- **Pass-level retry** with exponential backoff for 502/503 errors
- **LLM Thread Pool** — all LLM calls run in ThreadPoolExecutor to prevent event loop blocking
- **Optimised 502 backoffs** — 5-14s per model (was 15-45s), 10-20s per pass (was 30-60s)
- **Database normalisation** script (normalise_db.py) on startup

## Protected Systems (DO NOT UNDO)
- **Report Engine:** 8-pass Full Detailed, 7-8 pass Extensive Log, dedup thresholds 0.97/0.90
- **Condensed Prompt:** Passes 2+ use ~20k char prompt instead of 134k, no output reduction
- **LLM Thread Pool:** 4-worker ThreadPoolExecutor prevents sync litellm.completion() from blocking event loop
- **502 Backoff Timing:** 5-14s per model, 10-20s per pass. Model order: gpt-4o → claude → gpt-4o-mini → gpt-4o
- **Ground Dedup:** Topic classification (12 categories) + fuzzywuzzy (≥65) + bidirectional overlap (>0.45)
- **Case Identity Card:** Blue card with inline CSS for print
- **Auth Retry:** 3x retry on /auth/me and /auth/session before logout

## Upcoming Tasks
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Report Health Dashboard (live pass-by-pass progress with ETA)
