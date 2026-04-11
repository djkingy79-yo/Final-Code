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

### Metadata Quality Enforcement (Apr 2026)
- **Soft pre-generation gates:** All generation endpoints (reports, timeline, grounds) validate case metadata (state, offence_category, offence_type) and log warnings before proceeding
- **Frontend metadata dialog:** ReportsSection shows confirmation dialog listing missing fields before generating — user can proceed or go back to fix
- **Frontend confirm prompts:** Timeline and grounds generation show browser confirm dialogs for missing metadata
- **UI jurisdiction warnings:** Case detail page shows amber "Action Required" banner listing all missing fields
- **Auto-detect enhanced:** Document upload auto-detect now includes federal jurisdiction and 4 new offence categories (cybercrime, arson, perjury, environmental)

### Citation Anti-Hallucination Post-Processing (Apr 2026)
- **`services/case_validation.py`:** New module with citation validation against 40+ known Australian court abbreviations
- **`validate_citation()`:** Checks medium neutral citations ([Year] COURT Number) and law report citations ((Year) Vol Reporter Page) against `_VALID_COURT_ABBREVS` whitelist
- **`strip_hallucinated_citations()`:** Removes text lines containing placeholder patterns ([Surname], [Year], [Full Citation]) or suspicious phrases (citation not available, section unknown)
- **`validate_similar_cases()`:** Filters AI-generated similar cases, removing entries with placeholder/fake citations. Adds `verification_status` to surviving entries
- **`validate_law_sections()`:** Removes law section entries with placeholder section numbers or act names
- **Wired into:** `reports.py` (all report types), `verify.py` (grounds pipeline), runs on every generated output

### Federal Jurisdiction Support (Apr 2026)
- `APPELLATE_PATHWAYS`: `s 35A Judiciary Act 1903 (Cth)` / `Federal Court of Australia Act 1976 (Cth)`
- `AUSTRALIAN_STATES`: `"federal"` entry with CTH abbreviation, HCA/Full Federal Court appeal path
- `STATE_FRAMEWORKS`: Federal framework with dual-jurisdiction guidance
- `_build_state_framework_context()`: Federal-specific notes about Judiciary Act Part X trial jurisdiction

### Stripe Payment Integration (Apr 2026)
- Stripe Checkout for card/Apple Pay/Google Pay
- PaymentModal with Card and PayID options
- Payment success page with status polling

### Payment History & Receipts (Apr 2026)
- Payment history page with summary dashboard, filter tabs, PDF receipt download
- Dashboard sidebar "Payment History" link

### Security Hardening (Apr 2026)
- hmac.compare_digest, slowapi rate limiting, 8-char password minimum

### Previously Completed
- Global Anti-Hallucination Layer (17 LLM files)
- Legislation Framework (15 offence categories, 9 jurisdictions + federal)
- Legitimacy Engine (4-axis scoring)
- Barrister View, PDF exports, Google Auth, CI/CD

## Test Coverage
- 37 citation validation tests (100% pass)
- 22 Stripe payment tests (100% pass)
- 10 payment history tests (100% pass)
- 13 jurisdiction flow tests (100% pass)
- 21 framework integrity tests (100% pass)

## Backlog
- P0: Session token exposure in PDF/DOCX download URLs — replace with short-lived signed tokens
- P1: `server.py` monolith refactor — extract routes/services systematically
- P1: Clean up test/debug files from root directory
- P1: Verify "How It Works" page screenshots (IMG_4323-4327)
- P1: Caselaw search feature improvement
- P2: Verify "Success Stories" page ethical compliance
- P2: Build Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
