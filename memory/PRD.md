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
- **Auto-Extraction:** Document upload automatically triggers text extraction, timeline generation, and facts/events/findings identification.

## Architecture
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails
- Payment methods: Stripe (card/Apple Pay/Google Pay) + PayID (bank transfer)
- Capacitor v7 configured for native mobile

## What's Been Implemented

### Bug Fixes — iOS Safari & Pipeline (Apr 2026, Session 2)
- **auSpelling.js COMPLETELY REWRITTEN**: Replaced 100+ chained `.replace()` calls with dictionary-based single-pass approach (SPELLING_MAP + single regex). Added try-catch safety net. Eliminates "Attempted to assign to readonly property" crash on iOS Safari JIT.
- **`'created_at'` KeyError FIXED**: Added `created_at` field to `DocumentExtract`, `IssueClassification`, `IssueVerification` Pydantic models. Added `_safe_isoformat()` helper to `grounds.py` and `pipeline_staged.py`.
- **Timeline Ordering Improved**: Added secondary sort by `created_at` + enhanced AI prompt for strict chronological ordering with exact date extraction.
- **OAuth Error Handling**: AuthCallback handles "Invalid state parameter" gracefully with auto-retry.

### 9-Jurisdiction End-to-End Validation (Apr 2026, Session 1)
- **All 9 jurisdictions tested and PASS**: NSW, VIC, QLD, SA, WA, TAS, NT, ACT, Federal
- Zero NSW default leaks, zero hallucinated citations
- Test script at `/app/backend/tests/test_9_jurisdiction_quick.py`

### Repository Cleanup (Apr 2026, Session 1)
- Moved test/debug scripts, temp exports, audit docs, documentation to proper directories

### Previously Completed
- Stripe + PayID payment integration
- Payment History Dashboard with PDF receipts
- Federal jurisdiction routing
- Citation anti-hallucination post-processing
- Metadata soft warnings
- Security hardening (rate limiting, bcrypt)
- Barrister View deep synthesis + Issue Matrix
- PDF/DOCX exports with legal disclaimers

## Test Coverage
- 9-jurisdiction matrix: 9/9 PASS
- Bug fix verification: 100% (iteration 185 — 12 backend, all frontend tests)
- Previous iterations 180-184: All passing

## Backlog
- P0: Session token exposure in PDF/DOCX download URLs — replace with short-lived signed tokens
- P1: `server.py` monolith refactor (user approved multi-session)
- P1: "How It Works" page screenshots verification
- P1: Caselaw search feature upgrade
- P2: Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
