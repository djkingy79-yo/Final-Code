# Appeal Case Manager — PRD

## Original Problem Statement
Build "Appeal Case Manager" for criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, and a tiered reporting system (Free Quick Summary, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View at $449 total).

## Core Requirements
- Report tiers scale in depth: Free (base) -> $150 (2x) -> $200 (3x) -> Barrister View (capstone synthesis)
- Barrister View: locked until all 3 standard reports generated/paid. Synthesises all 3 reports + adds counsel-grade analysis
- Report language: STRICT third-person educational tool. No "we", "us", "our", "you", "your"
- Branding: forced light mode, high contrast, blue/slate/navy only. Action buttons = bright blue with white text
- Australian English throughout (analyse, organise, barrister, defence, offence)

## Architecture
- Frontend: React + Shadcn/UI
- Backend: FastAPI + MongoDB
- LLM: GPT-4o/Claude via LiteLLM with Emergent LLM Key
- Auth: Emergent Google OAuth + JWT
- Payments: Stripe/PayPal/PayID
- Emails: Resend

## What's Been Implemented
### Reports System (DONE)
- 4-tier report generation with multi-pass LLM engine
- PDF/DOCX export with proper footers, page numbering, legal disclaimers
- iOS-safe PDF preview via /document-preview route
- Report content safely backed up during regeneration (backend backup/restore)

### Barrister View Multi-Pass Architecture (DONE - Updated 2 Apr 2026)
- 8-pass generation: 3 section groups + section expansion + ground expansion + cross-analysis + strategy expansion + comparison tables + issue matrix + final QA
- Section-by-section thin section expansion (catches missing or undersized sections)
- Final QA validation pass (last defence against thin sections)
- Rogue section cleanup (strips hallucinated H2 headings)
- Target output: 120k+ chars / 16k+ words (larger than Extensive Log)
- All critical code protected with DO NOT UNDO markers

### Frontend Report Visibility (DONE - 2 Apr 2026)
- Existing report content visible during regeneration (status banner + content below)
- No more "content loss" perception — backend saves data, frontend shows it

### Ground Deduplication (DONE - Updated 2 Apr 2026)
- Topic-based + fuzzy matching keyword system
- Added coverage for "manifest excess", "inadequate defence", "failure to file" variants
- Prevents grounds multiplying from 6 to 8+

### Backend Performance (DONE)
- Threaded LLM calls via asyncio.to_thread()
- API response time <0.2s during active generation
- 502 retry backoffs optimised (5-14s)
- Frontend polling storm fixed

### Other Features (DONE)
- User authentication (Google OAuth + JWT)
- Document management and upload
- Timeline view
- Notes system
- Appeal statistics page
- How It Works tutorial page

## Upcoming Tasks
- P1: Build Native Mobile App (Capacitor configured)

## Future/Backlog
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat in Notes section
- P2: Case sharing between users
