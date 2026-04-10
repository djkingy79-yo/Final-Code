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
- Comprehensive Legal Framework Update (Apr 2026): Deep forensic audit of all criminal law legislation across all Australian jurisdictions (NSW, VIC, QLD, SA, WA, TAS, NT, ACT + Commonwealth). 174 legislation entries across 9 jurisdictions. Added complete criminal frameworks for ALL states/territories (Primary Acts, Key Regulations, Specialised Legislation) plus FEDERAL_CRIMINAL_FRAMEWORK. 27 recent legislation updates (2022-2026). All 11 primary Criminal Codes/Acts verified.
- Complete NSW/Homicide Fallback Eradication (Apr 2026): Forensic sweep of ALL backend and frontend code. Removed every code-level default to NSW or homicide across: server.py (system prompts, Barrister Brief PDF, PDF/DOCX exports), offence_helpers.py (context builder, system prompt builder, export refs), pipeline.py (case metadata), statistics.py (case stats), documents.py (auto-detect), utilities.py (framework API), classify.py (grounds classification), LegalFrameworkViewer.jsx (component default). Created get_export_legal_refs() helper for dynamic state-specific legislation in PDF/DOCX exports. All `state` parameters now pass through from the case object with no silent NSW substitution. All `offence_category` defaults changed from "homicide" to "other". 93 regression tests passing (12 new anti-fallback tests). Testing agent verified: WA/QLD/empty-state API calls return correct legislation, frontend Legal tab shows correct state, zero NSW contamination.
- Production Readiness Review (Apr 2026): Full sweep — 31/31 backend API tests (auth, CRUD, legal framework, health), mobile responsiveness verified (375px viewport), all env vars set, DB indexes confirmed, no MongoDB _id leaks.
- Minor Fixes (Apr 2026): WebSocket chat accept-first pattern (fixes 409 on proxied environments), DialogContent accessibility (VisuallyHidden Description suppresses Radix warnings), mobile dashboard header responsive sizing.
- Attachment B — Counsel Conference Preparation (Apr 2026): New attachment appended to Barrister View after Attachment A. Generates: key questions for conference (factual, strategic, evidentiary, procedural), identified weak points table, likely prosecution responses per ground, document references checklist, suggested conference agenda. Added to H2 whitelist. Loading message updated.
- Substantive Law Section Fix (Apr 2026): Grounds were generically citing "Criminal Appeal Act 1912 s 6(1)" (the procedural appeal act) for every ground instead of the substantive legislation each ground actually relates to. Fixed classify.py and verify.py to distinguish between appellate pathway (procedural act) and law_sections (substantive legislation — Crimes Act, Evidence Act, Sentencing Act, etc.). Injected state-specific legislative framework into verify.py. Added cleaning to strip placeholder entries ("Relevant Act", "section specific to") and appellate act duplicates. Added "Refresh Legal Refs" button on Grounds tab (calls POST /cases/{case_id}/grounds/refresh-legal-refs) to re-verify all existing grounds. Also fixed verify.py NSW fallback (state defaulted to 'nsw'). 
- Forensic Language Enforcement (Apr 2026): Added post-processing filter (`enforce_forensic_language`) applied to ALL generated content (all 4 report types, Barrister View, grounds verification, arguments). Catches over-assertive declarative phrases ("The trial judge erred", "The conviction is unsafe", "was denied a fair trial", etc.) and rewrites them to forensic appellate language ("It is arguable that...", "arguably...", "There is a tenable argument that..."). Sentence-boundary-aware — preserves precedent citations and already-forensic text. Updated argue.py with explicit forensic language rules. Also eliminated final 5 NSW fallbacks in submit.py, extract.py, timeline.py, pipeline.py, compare.py. 104 regression tests passing (11 new forensic language tests). All 8 states/territories verified clean.

- Deep Legislative Framework Audit (Apr 2026): Forensic verification of ALL criminal legislation across all 9 jurisdictions. Key fixes: (1) Removed fabricated "Criminal Appeal Act 1912 (Qld)" — QLD appeals are via Criminal Code Act 1899 Schedule 1 Chapter LXVIII, not a standalone act; (2) Replaced superseded "Criminal Appeal Act 1914 (Vic)" — VIC appeals governed by Criminal Procedure Act 2009 Part 6.3, updated by Justice Legislation Amendment (Criminal Appeals) Act 2019; (3) Added 3 NT recent legislation entries (Criminal Code Amendment Act 2024, Youth Justice Legislation Amendment Act 2025, Bail and Youth Justice Legislation Amendment Act 2025) — was empty; (4) Added 3 ACT recent legislation entries (MACR reform to age 14 from 1 July 2025, Crimes Legislation Amendment Act 2024, Crimes (Disclosure) Legislation Amendment Act 2024) — was empty; (5) Updated SA appeal court to "Court of Appeal" (established 1 Jan 2021); (6) Corrected SA appeal time limit from "10 business days" to "21 days". Total RECENT_LEGISLATION_UPDATES now 28+ across all jurisdictions. 121 regression tests passing (17 new audit tests). Testing agent verified: 100% pass rate, all 19 verification items confirmed.

## Backlog
- P0: "How It Works" page screenshots (IMG_4323-4327) — user-uploaded images still need placement
- P1: Native Mobile App build (Capacitor v7)
- P2: Camera/Share native device features
- P2: Backend refactoring — decompose server.py (~6000 lines)

## Document Formatting Overhaul (Apr 2026)
- Unified legal report format across ALL views (screen, print, PDF, DOCX):
  - Body: Times New Roman 12pt throughout
  - Headings (##): Times New Roman Bold 18pt, page break before new sections
  - Subheadings (###): Times New Roman Bold 14pt
  - Sub-subheadings (####): Times New Roman Bold 12pt
  - Bullets: Indented 2.5rem, 12pt
  - Tables: Times New Roman 11pt
  - Footer on ALL pages: 10pt Times New Roman Italic — Document Name | Appellant | Date | Page X
- PDF: reportlab with Times-Roman/Times-Bold fonts, PageBreak before ## sections, A4 margins 20mm/15mm/25mm/15mm
- DOCX: python-docx Heading 1 with page_break_before=True, Times New Roman on all styles, footer via section.footer
- Print/Screen: CSS @page A4, .legal-report h2 page-break-before: always, fixed print footer
- Testing: 100% pass — 11 backend tests (PDF/DOCX exports for all report types), all frontend verified

## Unified Legal Formatting — All Tabs & Print Views (Apr 2026)
- Extended Times New Roman 12pt legal formatting from Reports to ALL case detail tabs and print/word/PDF export views
- Added `.legal-content` CSS class in `index.css`: h1 22pt, h2 18pt, h3 14pt, h4 12pt, body 12pt, lists indented 2.5rem
- Applied `legal-content` class to all 9 TabsContent wrappers in CaseDetail.jsx
- Replaced ALL `Crimson Pro` references with `Times New Roman` across 35+ files
- **Case Identity Card**: On-screen values (Defendant, Offence, State, Sentence) now Times New Roman 14pt bold
- **Print/Word/PDF Views**: Grounds, Timeline, Notes, Legal, Progress export templates all updated to Times New Roman 12pt body, proper heading hierarchy, 10pt italic footer with document name, appellant, date, page numbers
- **Grounds Appellate Pathways & Law Sections**: Backend `refresh-legal-refs` endpoint enhanced to:
  1. Auto-generate missing appellate_pathway via LLM with state framework context
  2. Relaxed verify_issue prompt to always return at least one law_sections entry (allows appellate/procedural acts when no substantive section applies)
  3. Post-processor allows appellate act when no other substantive entries exist
  All 11 cases (NSW x4, VIC, QLD, SA, WA, TAS, NT, ACT) — 94 total grounds — verified COMPLETE: 0 missing appellate pathways, 0 missing law sections
- Testing: 100% pass (iterations 175-176)

## Full Report Regeneration & Verification (Apr 2026)
- **NSW (case_6cc234434cbd)**: All 4 reports + quick brief verified. Quick Summary 15.9K, Full Detailed 113.7K, Extensive Log 147.7K, Barrister View 156K chars. All correct NSW legislation, zero violations.
- **6-State Expansion (VIC, QLD, SA, TAS, NT, ACT)**: Created test cases, generated grounds + 24 reports (6×4 tiers). All 24 verified: zero wrong-state legislation, zero language violations, all Barrister Views have Attachment A + B.
  - VIC: assault, Criminal Procedure Act 2009. QLD: drugs, Criminal Code 1899. SA: fraud, CLCA 1935. TAS: sexual, Criminal Code 1924. NT: DV, Criminal Code 1983. ACT: robbery, Supreme Court Act 1933.
- **LLM Error Fix**: Replaced 5 direct LlmChat calls (documents.py, contradictions.py) with centralized retry/fallback service — root cause of LLM 502/timeout failures.
- **Grounds Investigate Updated**: Now injects offence context + anti-hallucination + forensic language filter (was missing all 3).
- **Progress Analysis Updated**: Now injects offence_context, anti-hallucination, forensic language filter.
- **Timeline Analysis Fixed**: Removed hardcoded "NSW", now uses dynamic state.
- **Legal Framework API Updated**: `/api/offence-framework` now returns `recent_legislation_updates` for all 9 jurisdictions.

## Production Readiness (Apr 2026)
- Full review passed: 31/31 backend tests, all auth flows (login, register, logout, session), CRUD cases, legal framework, health checks, no MongoDB _id leaks
- Mobile responsiveness: Fixed dashboard header overflow at 375px viewport. Landing page, dashboard, and case detail all pass mobile overflow check
- Environment: All required env vars set (MONGO_URL, DB_NAME, FRONTEND_URL, ADMIN_EMAILS, CONTACT_EMAIL, EMERGENT_LLM_KEY). Optional vars (RESEND_API_KEY, CORS_ORIGINS, RESEND_FROM_EMAIL, PAYID_EMAIL) all set
- Database: 31 collections, proper indexes on users/cases/reports/sessions/grounds/documents
- Minor items resolved: WebSocket accept-first, DialogContent accessibility, mobile responsive buttons
