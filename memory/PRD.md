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

## Guardrail Coverage (17/17 files — ALL PASS)
Every file that calls the LLM has four mandatory guardrail categories:
1. **Anti-Hallucination (AH):** Do NOT invent/fabricate citations, section numbers, facts, dates
2. **No NSW Default (NSW):** Do NOT default to NSW legislation for non-NSW cases
3. **Forensic Language (FOR):** Use "it is arguable that" framing, NOT declarative assertions
4. **Australian English (AUE):** analyse, defence, offence, behaviour, honour, favour

Files covered: analysis.py, contradictions.py, documents.py, export.py, grounds.py, pipeline.py, timeline.py, barrister_generator.py, llm_service.py (global guardrail layer), argue.py, classify.py, draft.py, extract.py, submit.py, verify.py, report_generator.py, repair_report.py

## What's Been Implemented

### Stripe Payment Integration (Apr 2026)
- **Backend:** `/api/payments/stripe/create-checkout` creates Stripe Checkout sessions
- **Backend:** `/api/payments/stripe/status/{session_id}` polls payment status
- **Backend:** `/api/webhook/stripe` handles Stripe webhook events
- **Frontend:** `PaymentModal.jsx` updated with two payment methods: Card (Stripe) and PayID (bank transfer)
- **Frontend:** `PaymentSuccessPage.jsx` handles Stripe redirect with status polling
- **Frontend:** Fixed AuthCallback conflict with `/payment-success` route (session_id param)
- Apple Pay and Google Pay available automatically through Stripe Checkout

### Security Hardening (Apr 2026)
- `hmac.compare_digest` for timing-safe password comparison in auth.py
- `slowapi` rate limiting on login (5/min) and register (3/min) endpoints
- Shared limiter instance via config.py for consistency
- Password minimum length increased to 8 characters

### Global Anti-Hallucination Layer (Feb 2026)
- **llm_service.py** `_apply_task_guardrails()`: Universal anti-hallucination rules injected into EVERY LLM call
- **17 LLM-calling files** audited and hardened with all 4 guardrail categories

### Legislation Framework (Feb 2026)
- **offence_framework.py** (3639 lines): 15 offence categories, SENTENCING/EVIDENCE/MENTAL_IMPAIRMENT/PROCEEDS_OF_CRIME frameworks, LANDMARK_CASES, APPEAL_GROUNDS_ACCESSIBILITY, FEDERAL_FAULT_ELEMENTS, HUMAN_RIGHTS_FRAMEWORK, LEGISLATION_CURRENCY tracking

### Legitimacy Engine (Feb 2026)
- Four-axis scoring with procedural compliance, sentencing-specific path

### Legislation Currency Checker (Feb 2026)
- AustLII runtime verification: POST /api/legislation/check-currency, POST /api/legislation/batch-check

### Test Suite
- 21 passing framework integrity tests
- Stripe payment integration tests (22 pass)

### Previously Completed
- All prior features (Barrister View, PDF exports, Google Auth, Safari fix, CI/CD, forensic language enforcer, pipeline_models.py, Stats page)

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
