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

### Download Token Security (Apr 2026, Session 3)
- **Short-lived download tokens** replace session_token exposure in PDF/DOCX download URLs
- `POST /api/auth/download-token` generates 5-minute, single-use tokens stored in MongoDB
- `auth_utils.py` validates download_token query params; legacy session_token kept for WebSocket only
- Frontend updated: `ReportView.jsx`, `BarristerView.jsx`, `ReportsSection.jsx`, `CaseDetail.jsx`
- New utility: `/app/frontend/src/utils/downloadToken.js`

### Standardised Print/Export Footer (Apr 2026, Session 3)
- **Exact footer format:** "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] DD/MM/YYYY Page X of Y"
- Times New Roman, italic, 10pt across ALL export views
- Backend: `export_footer.py` shared by PDF (NumberedCanvas) and DOCX (apply_docx_footer)
- Frontend: `exportHtml.js`, `ReportView.jsx`, `BarristerView.jsx` all use matching CSS footer
- Removed duplicate DOCX footer overwrite in `report_exports.py`
- Fixed timeline PDF filename Unicode encoding error (em-dash in title)

### Bug Fixes — iOS Safari & Pipeline (Apr 2026, Session 2)
- **auSpelling.js COMPLETELY REWRITTEN**: Dictionary-based single-pass approach. Eliminates iOS Safari JIT crash.
- **`'created_at'` KeyError FIXED**: Added `created_at` field to extraction models.
- **Timeline Ordering Improved**: Secondary sort by `created_at` + strict chronological ordering.
- **OAuth Error Handling**: AuthCallback handles "Invalid state parameter" gracefully.

### 9-Jurisdiction End-to-End Validation (Apr 2026, Session 1)
- **All 9 jurisdictions tested and PASS**: NSW, VIC, QLD, SA, WA, TAS, NT, ACT, Federal
- Zero NSW default leaks, zero hallucinated citations

### Previously Completed
- Stripe + PayID payment integration
- Payment History Dashboard with PDF receipts
- Federal jurisdiction routing
- Citation anti-hallucination post-processing
- Metadata soft warnings
- Security hardening (rate limiting, bcrypt)
- Barrister View deep synthesis + Issue Matrix
- PDF/DOCX exports with legal disclaimers
- Translation formatting (ReactMarkdown + remarkGfm for 41 languages)
- Repository cleanup

## Test Coverage
- Download token security: 12/13 PASS (iteration_186)
- 9-jurisdiction matrix: 9/9 PASS
- Previous iterations 180-185: All passing

## Backlog
- P1: "How It Works" page screenshots verification
- P1: `server.py` monolith refactor (user approved multi-session)
- P1: Caselaw search feature upgrade
- P2: Verify "Success Stories" page content compliance
- P2: Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
