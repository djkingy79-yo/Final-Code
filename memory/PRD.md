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
- **Database normalisation** script (normalise_db.py) on startup

## Protected Systems (DO NOT UNDO)
- **Report Engine:** 8-pass Full Detailed, 7-8 pass Extensive Log, dedup thresholds 0.97/0.90
- **Condensed Prompt:** Passes 2+ use ~20k char prompt instead of 134k, no output reduction
- **Ground Dedup:** Topic classification (12 categories) + fuzzywuzzy (≥65) + bidirectional overlap (>0.45)
- **Case Identity Card:** Blue card with inline CSS for print
- **Auth Retry:** 3x retry on /auth/me and /auth/session before logout

## Verified Report Stats (1 Apr 2026)
- Quick Summary: ~1,662 words, 12,677 chars
- Full Detailed: ~12,915 words, 93,005 chars
- Extensive Log: ~15,710 words, 117,184 chars, 25 sections
- Barrister View: ~12,585 words

## Upcoming Tasks
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
