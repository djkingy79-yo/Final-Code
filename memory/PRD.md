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
- 4-tier report generation with multi-pass engine (8 passes for Full Detailed)
- PDF/DOCX export with preview mode, Case Identity Card
- Chat collaboration (WebSocket), Case sharing
- Pipeline verification, Admin dashboard, statistics, legal resources
- Mobile-responsive with lazy section loading

## Protected Systems (DO NOT UNDO)
- **Report Engine:** 8-pass Full Detailed, dedup thresholds 0.97/0.90, no cautious-language guardrail
- **Ground Dedup:** Topic classification + fuzzywuzzy (≥65) + bidirectional overlap (>0.45). ALL 5 paths use fuzzy dedup.
- **Case Identity Card:** Blue card with inline CSS for print
- **grounds.py:** _classify_pipeline_issues and _sync_pipeline_issues_to_grounds MUST use fuzzy dedup

## Upcoming Tasks
- P1: Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P3: Database normalisation script
