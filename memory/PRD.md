# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis. TEAL colour.
- **Report Language:** STRICT third-person educational tool. NO "we/us/our/you/your". Conditional language only.
- **Branding:** "Created and Designed by Deb King" at BOTTOM of prints/exports. Legal disclaimer on all reports.
- **UI/UX:** Forced light mode. High contrast. Bright blue action buttons. No amber/brown.
- **Language:** Australian English throughout (analyse, organise, defence, offence, colour).

## Architecture
```
/app/
├── .github/workflows/ci.yml     # CI: Node 22, Python 3.11, FORCE_JAVASCRIPT_ACTIONS_TO_NODE24
├── backend/
│   ├── server.py, config.py, auth_utils.py, models.py
│   ├── routers/ (auth, cases, documents, grounds, deadlines, compare, payments, analytics, etc.)
│   ├── services/
│   │   ├── legitimacy_engine.py  # NEW: 3-layer forensic scoring engine
│   │   ├── llm_service.py        # UPGRADED: task types, structured metadata, anti-hallucination
│   │   ├── offence_helpers.py    # UPGRADED: restrained prompts, jurisdiction awareness
│   │   ├── document_helpers.py   # UPGRADED: page provenance, category ranking, OCR preprocessing
│   │   ├── notes_helpers.py
│   │   └── email_service.py
│   └── tests/
└── frontend/
    └── src/
        ├── components/ (GroundsOfMerit [legitimacy display], CaseStrengthMeter [readiness], etc.)
        ├── pages/ (BarristerView, ReportView, CaseDetail, CompareCasesPage, etc.)
        ├── utils/ (exportHtml.js, isIOS.js)
        └── App.js
```

## What's Been Implemented

### Session 3 — 30 Mar 2026 (Forensic Barrister Review Implementation)

**Tier 1 — Critical Security & Legal Safety:**
- **Legitimacy Engine** (`services/legitimacy_engine.py`): 3-layer scoring system for grounds of merit
  - Layer 1: Legal Basis (recognised appellate pathway, 0-3)
  - Layer 2: Evidence Sufficiency (direct quotes vs inference, 0-3)
  - Layer 3: Appellate Viability (Court intervention likelihood, 0-3)
  - Hard safety rule: No STRONG without evidence_score >= 2
  - Existing grounds retroactively scored on first fetch
- **Access Control Fix** (`routers/deadlines.py`): Added `user_id` to ALL mutating endpoints (update_deadline, delete_deadline, update_checklist_item)
- **"Case Readiness" Reframe** (`deadlines.py` + `CaseStrengthMeter.jsx`): "Case Strength" → "Case Readiness Score" with disclaimer: "This score reflects case preparation and documentation completeness. It is not a determination of legal merit."
- **Anti-Hallucination Controls** (`offence_helpers.py`): Removed overconfident "senior barrister" persona. Added mandatory analytical controls: no invented citations, conditional language, distinguish fact from inference, flag missing material.
- **Grounds Validation** (`routers/grounds.py`): Legitimacy engine overrides AI-guessed strength, validates ground_type, marks similar cases as `verified: false`, failover creates `needs_review` not `moderate`

**Tier 2 — Analytics & Language:**
- **Compare Analytics Reframe** (`routers/compare.py`): "Success Factors" → "Case Composition Patterns". All outputs carry provenance disclaimer. Minimum sample threshold (5 cases) to prevent misleading small-cohort analysis.
- **LLM Service Upgrade** (`services/llm_service.py`): Task-type aware model selection, structured metadata return (provider, model, attempt, latency, warnings), anti-hallucination safety suffix auto-appended to legal tasks
- **Unverified Case Badges** (`GroundsOfMerit.jsx`): Similar cases display "UNVERIFIED" badge and "AI-referenced — requires verification" note

**Tier 3 — Document & Extraction:**
- **Document Provenance** (`services/document_helpers.py`): Page-level boundaries in PDF extraction, category-priority document ranking (judgments/transcripts first), OCR preprocessing (grayscale, contrast, sharpen), DOCX table extraction, structured metadata return
- **System Prompt Upgrade**: All legal prompts use jurisdiction-specific legislation, not NSW default. Document coverage notes included. Conditional language enforced.

**Also in this session:**
- CI/CD: Node 22, FORCE_JAVASCRIPT_ACTIONS_TO_NODE24, ruff lint exclusion for tests/
- iOS detection: Shared `isIOSDevice()` utility for iPadOS desktop user agent
- PDF page breaks: cover page, coloured header, disclaimer all prevent page-splitting
- File upload: 10MB max size validation, 120s timeout

### Session 4 — 30 Mar 2026 (server.py Additive Patch Completion)
- Completed 7th and final forensic barrister additive patch to `server.py`
- Metadata detection now uses `call_llm_for_json` (with validation callback)
- Report generation uses `call_llm_structured` with enhanced timeouts (420s for detailed, 300s for standard)
- All generated reports now include `ReportMetadata` (models_used, fallback_used, documents_analyzed, verification_status)
- DB records include `source_mode: "ai_generated"` and `verification_status: "draft"` provenance fields
- Fixed `_NormaliserMixin` Pydantic error (check_fields=False for mixin validators)
- Full regression test: 13/13 backend, 100% frontend — all passing

### Previous Sessions
- Multi-pass AI report generation (4 tiers) with GPT-4o
- Document export (PDF/DOCX) with iOS-safe localStorage-based preview
- Barrister View with teal UI, "Attachment A — Barrister Issue Matrix"
- PayPal/PayID/Stripe payment integration
- Google OAuth via Emergent Auth, Email via Resend
- Landing page, stats page, How It Works page
- Professional README.md

## 3rd Party Integrations
- OpenAI GPT-4o (via Emergent LLM Key)
- Emergent Auth (Google OAuth)
- Resend (email notifications)
- PayPal/PayID/Stripe (payments)

## Prioritised Backlog
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: Further legitimacy engine refinement (verified case law database, jurisdiction-specific appellate tests)
- P3: Central case_analysis_service.py (single structured analysis object)
- P3: Staged LLM pipelines (extract → classify → verify → draft)
- P3: "How It Works" page images verification
- P3: Collaboration/chat enhancements
