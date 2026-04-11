# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free → $150 (2x) → $200 (3x). Barrister View locked until all 3 are generated/paid.
- **Report Language:** STRICT third-person educational tool. Forensic appellate language. Australian English only.
- **UI:** Forced light mode. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation with correct section numbers. NO NSW defaults.

## Architecture
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails, PayID payments
- Capacitor v7 configured for native mobile

## What's Been Implemented

### Anti-Hallucination & Jurisdiction Fidelity (Feb 2026)
- **ai_service.py**: Removed hardcoded NSW default in `extract_law_sections()` — now uses jurisdiction detection markers. Added `evidentiary_error`, `prosecution_misconduct`, `jury_irregularity`, `constitutional_violation` to GROUND_TYPES
- **extract.py**: Added anti-hallucination controls (no invented facts/dates), jurisdiction caveat (no NSW assumption), Australian English mandate
- **classify.py**: Replaced NSW-specific Act examples with jurisdiction-aware examples. Added "Do NOT default to NSW Acts for non-NSW cases"
- **verify.py**: Replaced NSW-specific Act examples with jurisdiction-aware examples. Updated JSON template Act placeholder
- **argue.py**: Added jurisdiction caveat, anti-hallucination block, anti-fabrication rules for case citations
- **draft.py**: Added jurisdiction caveat (dynamic per case), anti-hallucination block, forensic language rules, retrospective application instruction
- **submit.py**: Added jurisdiction caveat, anti-hallucination block, forensic language rules
- **report_generator.py**: Made content quality examples jurisdiction-aware (removed Homann NSW-specific examples). Updated legislation accuracy rules with jurisdiction fidelity
- **barrister_generator.py**: Added JURISDICTION FIDELITY section and ANTI-HALLUCINATION section
- **analysis.py**: Added anti-hallucination controls to contradiction analysis prompt

### Legislation Framework (Feb 2026)
- **offence_framework.py** (3639 lines): Complete Australian criminal legislation database
  - 15 offence categories with per-state legislation (8 states + CTH)
  - VIC Crimes Act 1958 sections corrected to post-2014 numbering
  - WA drugs split s.6(1)(a)/s.6(1)(b), added s.6A
  - WA road traffic updated to 2008 Acts
  - NT Part IIAA clarified to "Part III Division AA"
  - 7 new offence categories: arson, cybercrime, perjury, extortion, organised crime, child exploitation, corruption
  - SENTENCING_FRAMEWORK, EVIDENCE_FRAMEWORK, MENTAL_IMPAIRMENT_FRAMEWORK (all 9 jurisdictions)
  - PROCEEDS_OF_CRIME_FRAMEWORK, FEDERAL_FAULT_ELEMENTS, LANDMARK_CASES (16 authorities)
  - APPEAL_GROUNDS_ACCESSIBILITY (plain-language, who_can_use, leave_required)
  - HUMAN_RIGHTS_FRAMEWORK (CAT, CROC, anti-discrimination Acts, charter notes)
  - LEGISLATION_CURRENCY tracking with last_verified dates

### Legitimacy Engine (Feb 2026)
- **legitimacy_engine.py** (272 lines): Four-axis viability scoring with procedural compliance, sentencing-specific scoring

### Offence Helpers (Feb 2026)
- **offence_helpers.py** (698 lines): validate_jurisdiction_completeness(), get_sentencing_context(), get_evidence_context(), get_landmark_cases_context(), retrospective application + appeal time limits injected into prompts

### Legislation Currency Checker (Feb 2026)
- **legislation_checker.py**: AustLII/legislation.gov.au runtime section verification service
- **routers/legislation.py**: POST /api/legislation/check-currency, POST /api/legislation/batch-check

### Test Suite (Feb 2026)
- **test_offence_framework_integrity.py**: 21 passing tests covering section validation, duplicates, framework coverage, legitimacy engine

### Previously Completed
- Barrister View prompt rewrite, sentence extraction, PDF exports, Google Auth, Safari fix, CI/CD fixes, forensic language enforcer, pipeline_models.py, Stats page UI

## Backlog
- P1: Verify "How It Works" page screenshots
- P1: Build Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat
- P2: Case sharing
