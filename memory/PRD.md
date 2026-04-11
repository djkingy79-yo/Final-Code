# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free -> $150 (2x) -> $200 (3x). Barrister View locked until all 3 are generated/paid.
- **Report Language:** STRICT third-person educational tool. Forensic appellate language. Australian English only.
- **UI:** Forced light mode. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation with correct section numbers. NO NSW defaults.
- **Anti-Hallucination:** Every LLM-calling file must have: anti-hallucination controls, no-NSW-default guard, forensic language rules, Australian English mandate.
- **Citation Integrity:** Post-processing validates all citations against known Australian court abbreviations. Placeholder and suspicious citations are stripped automatically.

## Architecture
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails
- Payment methods: Stripe (card/Apple Pay/Google Pay) + PayID (bank transfer)
- Capacitor v7 configured for native mobile

## What's Been Implemented

### 9-Jurisdiction End-to-End Validation (Apr 2026)
- **All 9 jurisdictions tested and PASS**: NSW, VIC, QLD, SA, WA, TAS, NT, ACT, Federal
- Each tested with a different crime type (homicide, sexual offences, drug trafficking, assault, robbery, fraud, DV, driving, drug importation)
- **Zero NSW default leaks** — every jurisdiction cites its own correct legislation
- **Zero hallucinated citations** — no [Surname], [Year], [Full Citation] placeholders in any output
- **Deep validation**: NSW tested with all 3 report tiers (quick_summary, full_detailed, extensive_log) — all PASS
- Test script at `/app/backend/tests/test_9_jurisdiction_quick.py`

### Bug Fixes (Apr 2026)
- **iOS Safari auSpelling crash FIXED**: Removed `const` regex with `g` flag + `lastIndex = 0` pattern that crashed iOS Safari. Now creates fresh regex instances per call.
- **OAuth "Invalid state parameter" FIXED**: AuthCallback now detects OAuth error parameters, auto-retries with fresh redirect (up to 3 attempts), and shows friendly error UI instead of raw JSON.

### Repository Cleanup (Apr 2026)
- Moved 6 test/debug Python scripts from root to `/app/backend/tests/legacy/`
- Moved 4 temp export files to `/app/test_reports/`
- Moved 3 audit documents to `/app/docs/audit/`
- Moved 9 documentation files to `/app/docs/`
- Updated `.gitignore` for legacy test files and audit docs

### Metadata Quality Enforcement (Apr 2026)
- Soft pre-generation gates, frontend metadata dialog, UI jurisdiction warnings
- Auto-detect enhanced with federal jurisdiction and 4 new offence categories

### Citation Anti-Hallucination Post-Processing (Apr 2026)
- `services/case_validation.py` with citation validation, placeholder stripping, similar case filtering

### Federal Jurisdiction Support (Apr 2026)
- APPELLATE_PATHWAYS, AUSTRALIAN_STATES, STATE_FRAMEWORKS all support "federal" with CTH abbreviation

### Stripe Payment Integration (Apr 2026)
- Stripe Checkout, PaymentModal, Payment success page

### Payment History & Receipts (Apr 2026)
- Payment history page with dashboard, filter tabs, PDF receipt download

### Security Hardening (Apr 2026)
- hmac.compare_digest, slowapi rate limiting, 8-char password minimum

### Previously Completed
- Global Anti-Hallucination Layer (17 LLM files)
- Legislation Framework (15 offence categories, 9 jurisdictions + federal)
- Legitimacy Engine (4-axis scoring)
- Barrister View, PDF exports, Google Auth, CI/CD

## Test Coverage
- 9-jurisdiction matrix: 9/9 PASS (quick_summary for all, deep validation for NSW)
- 37 citation validation tests (100% pass)
- 22 Stripe payment tests (100% pass)
- 10 payment history tests (100% pass)
- 13 jurisdiction flow tests (100% pass)
- 21 framework integrity tests (100% pass)
- Frontend bug fix verification: 100% pass (iteration 184)

## Backlog
- P0: Session token exposure in PDF/DOCX download URLs — replace with short-lived signed tokens
- P1: `server.py` monolith refactor — extract routes/services systematically (user approved multi-session)
- P1: Verify "How It Works" page screenshots (IMG_4323-4327)
- P1: Caselaw search feature improvement
- P2: Verify "Success Stories" page ethical compliance
- P2: Build Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
