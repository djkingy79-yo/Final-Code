# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free -> $150 (2x) -> $200 (3x). Barrister View locked until all 3 are generated/paid.
- **Report Language:** STRICT third-person educational tool. Forensic appellate language. Australian English only.
- **UI:** Forced light mode. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation with correct section numbers. NO NSW defaults.
- **Anti-Hallucination:** Every LLM-calling file must have: anti-hallucination controls, no-NSW-default guard, forensic language rules, Australian English mandate.

## Architecture
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails
- Payment methods: Stripe (card/Apple Pay/Google Pay) + PayID (bank transfer)
- Capacitor v7 configured for native mobile

## What's Been Implemented

### Jurisdiction Flow Hardening (Apr 2026)
- **Federal jurisdiction support:** Added `federal`/`CTH` to `APPELLATE_PATHWAYS`, `AUSTRALIAN_STATES`, and `STATE_FRAMEWORKS` — federal cases no longer silently fall back to NSW
- **Federal appellate pathway:** `s 35A Judiciary Act 1903 (Cth)` / `Federal Court of Australia Act 1976 (Cth)` with dual-jurisdiction notes about state trial courts
- **UI jurisdiction warnings:** Case detail page now shows amber "Action Required" banner when state, offence_category, or offence_type are missing — previously these warnings were only in server logs
- **Backend:** `GET /api/cases/{case_id}` now returns `metadata_warnings` and `jurisdiction_warnings` arrays
- **Federal framework context:** `_build_state_framework_context()` now returns federal-specific dual-jurisdiction guidance instead of duplicating the federal framework block

### Stripe Payment Integration (Apr 2026)
- Backend: `/api/payments/stripe/create-checkout`, `/api/payments/stripe/status/{session_id}`, `/api/webhook/stripe`
- Frontend: `PaymentModal.jsx` with Card (Stripe) and PayID (bank transfer) options
- Apple Pay/Google Pay available automatically through Stripe Checkout

### Payment History & Receipts (Apr 2026)
- Backend: `/api/payments/history`, `/api/payments/history/summary`, `/api/payments/receipt/{payment_id}/pdf`
- Frontend: `PaymentHistoryPage.jsx` with summary dashboard, filter tabs, receipt download
- Dashboard sidebar "Payment History" link

### Security Hardening (Apr 2026)
- `hmac.compare_digest` for timing-safe password comparison
- `slowapi` rate limiting on login (5/min) and register (3/min)
- Shared limiter instance via config.py

### Global Anti-Hallucination Layer (Feb 2026)
- 17 LLM-calling files audited with 4 guardrail categories

### Legislation Framework (Feb 2026)
- offence_framework.py: 15 offence categories, all 9 jurisdictions + federal

### Test Suite
- 21 framework integrity tests
- 22 Stripe integration tests
- 10 payment history tests
- 13 jurisdiction flow tests

## Backlog
- P0: Session token exposure in URLs — replace with short-lived signed download tokens
- P1: `server.py` monolith refactor — extract routes/services systematically
- P1: Clean up test/debug files from root directory
- P1: Verify "How It Works" page screenshots (IMG_4323-4327)
- P1: Caselaw search feature improvement
- P2: Verify "Success Stories" page ethical compliance
- P2: Build Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
