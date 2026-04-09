# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free Quick Summary, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Quick Summary -> Full Detailed -> Extensive Log -> Barrister View (counsel synthesis).
- **Report Language:** STRICT third-person educational tool. Forensic appellate language ("It is arguable", "There is a tenable argument"). Never definitive conclusions.
- **Appellate Credibility:** Grounds linked to Appellate Pathways. 3-axis viability scoring (legitimacy_engine.py). Psychiatric evidence framed as Mens Rea attack.
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue/slate/navy palette. Action buttons: bright blue + white text.
- **Language:** Australian English throughout (analyse, organise, defence, offence, behaviour).

## Tech Stack
- Frontend: React + Shadcn/UI + Tailwind
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent Google Auth + JWT
- Payments: Stripe + PayPal + PayID
- Email: Resend
- Native: Capacitor v7 (configured, not yet built)

## Key Features Implemented
- Multi-pass AI report generation (Quick Summary, Full Detailed, Extensive Log, Barrister View)
- Staged pipeline: Document extraction -> Classification -> Verification -> Ground projection
- Barrister Quick Brief (2-page PDF via ReportLab, content-truncated to enforce page contract)
- Ground of Merit: CRUD, auto-identification, deep investigation, drag-and-drop priority reorder
- Legitimacy Engine (3-axis scoring: Outcome Impact, Legal Alignment, Evidence Support)
- PDF/DOCX/Word export with iOS-safe fallbacks
- Australian English normaliser (auSpelling.js) — protects markdown links/URLs
- Ground deduplication (fuzzy matching) with error_identified/materiality preservation
- Acceptance Pack PDF
- Statistics page
- How It Works tutorial page
- Admin cross-user case/report access

## What's Complete (as of Feb 2026)
- All 4 report types functional with correct forensic language
- Barrister View with Counsel Synthesis + Attachment A Issue Matrix
- Ground merging with sub-particulars (psychiatric_mens_rea, jury_integrity, sentencing clusters)
- iOS PDF export working (document-preview route + direct URL for Quick Brief)
- Deployment health checks passing
- 8-point code review fixes (iteration 161): credential redaction, auSpelling markdown safety, iOS Quick Brief fix, reorder atomic validation, merged grounds field preservation, UI jump fix, Pytest guards
- 12-point code review fixes (iteration 162): evidence scoring single-quote Partial fix, viability_score legacy semantics restored, state key normalisation for APPELLATE_PATHWAYS, Quick Brief 2-page enforcement, clustering test assertions enforced, Pytest portable paths + BASE_URL guards, auSpelling analysis capitalisation fix, blank appellate_pathway fallback, admin export owner_user_id propagation, README fenced block annotation
- Critical fixes (iteration 163): Counsel Synthesis added to H2 whitelist/thin_section_targets/final_min_chars (was being stripped), XSS fix for jurisdiction in law_sections export HTML (GroundsOfMerit.jsx + CaseDetail.jsx)
- P0 Google Auth Fix (Apr 2026): Removed orphaned `setAuthError(null)` call in AuthCallback (App.js) that caused a ReferenceError crashing the entire Google OAuth callback flow. All auth flows verified passing.
- Case Export Pack (Apr 2026): New formatted PDF export at GET /api/cases/{case_id}/export/case-pack. Generates a single professional PDF containing ALL generated reports with proper legal layout (cover page, table of contents, grounds of merit, timeline table, each report's full analysis, legal framework reference, page numbers, disclaimers). Only includes reports actually generated/paid for. Frontend updated with prominent "Download Case Export Pack (PDF)" button in QuickExport dialog.
- Multi-Language Translation (Apr 2026): 41 languages supported. GET /api/languages for language list. POST /api/cases/{case_id}/translate with {language, report_id} to translate any report. Uses LLM with caching in report_translations collection. Translate button added to both ReportView and BarristerView header toolbars. Searchable language picker dialog. Translated reports exportable as formatted PDFs via GET /api/cases/{case_id}/translate/{report_id}/pdf?lang={code} with cover page, legal layout, page numbers, and disclaimers.
- Barrister View Refactor (Apr 2026): Barrister Brief no longer auto-generates when navigating to the page. User must explicitly select "Barrister View" in the Generate Report dialog and click "Generate Report". Once generated, the Barrister Brief appears in the reports list alongside the other 3 reports as a proper report card with "CAPSTONE" badge. Duplicate old barrister reports cleaned up. Backend returns 404 when no report exists (instead of auto-generating). BarristerView page shows "Not Yet Generated" message instead of auto-retrying.
- Comprehensive Legal Framework Update (Apr 2026): Deep forensic audit of all criminal law legislation across all Australian jurisdictions (NSW, VIC, QLD, SA, WA, TAS, NT, ACT + Commonwealth). 174 legislation entries across 9 jurisdictions. Added complete criminal frameworks for ALL states/territories (Primary Acts, Key Regulations, Specialised Legislation) plus FEDERAL_CRIMINAL_FRAMEWORK. 27 recent legislation updates (2022-2026). All 11 primary Criminal Codes/Acts verified. Removed all hardcoded NSW/homicide fallbacks — auto-detect now correctly identifies jurisdiction and offence from case material. Added strict JURISDICTION FIDELITY rules, STRICT NO-HALLUCINATION CONTROLS, and LEGISLATION ACCURACY guardrails to all LLM prompts. Fresh reports verified: WA DV case correctly uses WA legislation (zero NSW bleed), NSW homicide correctly uses NSW legislation (zero pronoun/declarative hallucination). 81 regression tests passing.

## Backlog
- P1: Native Mobile App build (Capacitor v7)
- P2: Camera/Share native device features
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat
- P2: Case sharing between users
- P2: Backend refactoring — decompose server.py (~5900 lines)
