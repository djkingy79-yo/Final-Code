# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free → $150 (2x) → $200 (3x). Barrister View locked until all 3 are generated/paid.
- **Report Language:** STRICT third-person educational tool. Forensic appellate language. Australian English only.
- **UI:** Forced light mode. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation with correct section numbers.

## Architecture
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails, PayID payments
- Capacitor v7 configured for native mobile

## What's Been Implemented

### Legislation Framework (Feb 2026)
- **offence_framework.py** (3639 lines): Complete Australian criminal legislation database
  - 15 offence categories with per-state legislation (8 states + CTH)
  - VIC Crimes Act 1958 sections corrected to post-2014 numbering
  - WA drugs split s.6(1)(a)/s.6(1)(b), added s.6A
  - WA road traffic updated to 2008 Acts
  - NT Part IIAA clarified to "Part III Division AA"
  - Pre-existing duplicate s.4 NSW public order fixed
  - 7 new offence categories: arson, cybercrime, perjury, extortion, organised crime, child exploitation, corruption
  - Mental impairment legislation added to all 8 states
  - SENTENCING_FRAMEWORK: All 9 jurisdictions with key provisions and standard appeal grounds
  - EVIDENCE_FRAMEWORK: Uniform and non-uniform evidence jurisdictions, key provisions, common appeal grounds
  - MENTAL_IMPAIRMENT_FRAMEWORK: All 8 states with NGMI/fitness provisions
  - PROCEEDS_OF_CRIME_FRAMEWORK: All 9 jurisdictions
  - FEDERAL_FAULT_ELEMENTS: Criminal Code Ch 2 (s.4.4 absolute liability, s.9.3 mistake of law)
  - LANDMARK_CASES: 16 settled authorities across 8 ground types
  - APPEAL_GROUNDS_ACCESSIBILITY: Plain-language descriptions, who_can_use, leave_required for all 10 ground types
  - HUMAN_RIGHTS_FRAMEWORK expanded: CAT, CROC, anti-discrimination Acts, SA/WA/TAS/NT charter note
  - Federal Court of Australia Act 1976 (Cth) added to appeal framework
  - LEGISLATION_CURRENCY tracking with last_verified dates

### Legitimacy Engine (Feb 2026)
- **legitimacy_engine.py** (272 lines): Four-axis viability scoring
  - Added new ground types: evidentiary_error, cybercrime_procedural, arson_expert_challenge, perjury_recantation
  - Added Layer 4: Procedural Compliance scoring (within_time/extension/out_of_time)
  - Added sentencing-specific scoring path (manifest_excess vs specific_error)
  - Added out-of-time procedural warning in viability label
  - Full backward compatibility preserved (legacy fields retained)

### Offence Helpers (Feb 2026)
- **offence_helpers.py** (698 lines): Enhanced prompt injection
  - validate_jurisdiction_completeness() — gap warnings for AI prompts
  - get_sentencing_context() — injects sentencing Act and appeal grounds
  - get_evidence_context() — injects evidence Act and uniform/non-uniform provisions
  - get_landmark_cases_context() — injects settled authorities by ground type
  - get_jurisdiction_warnings_prompt() — injects gap warnings
  - Retrospective application instruction added to system prompt
  - Appeal time limits injected into system prompt
  - All context automatically injected via get_offence_context()

### Test Suite (Feb 2026)
- **test_offence_framework_integrity.py** (205 lines): 21 passing tests
  - Section reference validation (no empty keys)
  - Duplicate section detection
  - Appeal framework coverage (all states + federal)
  - Sentencing/Evidence/Mental Impairment framework coverage
  - Human rights framework completeness
  - Legitimacy engine scoring for all ground types
  - Procedural compliance scoring
  - Backward compatibility

### Previously Completed
- Barrister View prompt rewrite with Issue Matrix attachment
- Sentence extraction normalisation
- Document export footer fixes
- PDF preview route for iOS
- Google Auth custom domain bypass
- Safari auSpelling crash fix
- CI/CD deployment fixes (64 Ruff errors, Procfile, CORS)
- Forensic language enforcer expansion
- pipeline_models.py full Pydantic model implementation
- Stats page UI (bright blue background, white text, vibrant red)

## Backlog
- P1: Build Native Mobile App (Capacitor v7 configured)
- P1: Verify "How It Works" page screenshots
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat enhancements
- P2: Case sharing
