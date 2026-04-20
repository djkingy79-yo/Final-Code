# Appeal Case Manager

### Criminal Law Appeal Case Management System — Australian Jurisdictions

**criminallawappealmanagement.com.au** — self-hosted, owned end-to-end by Debra King.

---

## About This Project

**Appeal Case Manager** is a comprehensive, AI-powered web and mobile application purpose-built for the Australian criminal justice system. It was conceived, designed, and directed by **Debra King** — a passionate advocate who identified a critical gap in the legal landscape: the overwhelming majority of convicted Australians who may have legitimate grounds for appeal never exercise that right, largely due to systemic barriers including cost, complexity, lack of legal knowledge, and inadequate prior representation.

This platform exists as an **educational research tool** — not legal advice — to empower individuals, families, and legal professionals to organise, analyse, and understand criminal appeal cases across **all eight Australian states and territories** (NSW, VIC, QLD, SA, WA, TAS, NT, ACT) and the Federal jurisdiction.

> **"Only 1 in 80 convicted Australians ever lodge an appeal. This tool was built to change that."**
> — Debra King, Founder

---

## Why It Was Built

The Australian appeals process is notoriously difficult to navigate without specialised legal counsel. Many individuals:

- Cannot afford private barristers or solicitors experienced in appellate law
- Received inadequate representation at trial and are unaware errors occurred
- Do not understand the legal grounds upon which an appeal can succeed
- Face strict filing deadlines (often 28 days) with no guidance on how to prepare
- Are discouraged by the system itself from exercising their lawful right to appeal

Appeal Case Manager was designed to democratise access to appeal preparation by providing structured case management, automated document analysis, AI-driven identification of potential grounds of appeal, and tiered professional-grade reporting — all within a secure, user-friendly platform accessible from any device, including native iOS and Android apps.

---

## Core Features

### 1. Secure Case Management
- Create, organise, and manage multiple criminal appeal cases simultaneously
- Store all case metadata: defendant name, court, jurisdiction, offence category, sentence details, case numbers
- Full case lifecycle tracking from initial assessment through to appeal preparation
- Case sharing and real-time collaboration between registered users (family members, support persons, legal professionals)

### 2. Intelligent Document Management
- Upload and store case-related documents (PDF, DOCX, images, text files)
- **Automated text extraction** using PyPDF, python-docx, and Pillow
- **Optical Character Recognition (OCR)** via Tesseract for scanned documents and images
- AI-powered document analysis that automatically detects case-relevant information including charges, sentences, judicial reasoning, and procedural history
- **Background polling architecture** — bulk text extraction for 16+ documents runs as an asyncio background task with live progress polling (`Extracting text (3/12)...`), fully bypassing Cloudflare/axios 30–100 second timeouts

### 3. AI-Powered Timeline Generation
- Automatic construction of chronological case timelines from uploaded documents
- Manual timeline entry and editing
- Timeline analysis identifying gaps, inconsistencies, and critical procedural dates
- Export timelines to PDF with professional formatting

### 4. Grounds of Merit Identification & Appellate Intelligence
- **AI-driven automatic identification** of potential grounds of appeal from case documents
- **Intelligent ground merging** — related factual issues are automatically clustered under a single ground with sub-particulars (e.g. judge-alone refusal, jury reduction, and juror conduct are merged under "Procedural Unfairness (Jury Integrity)"). This follows the CCA-preferred approach: **"one ground, multiple particulars"**
- **12-topic fuzzy deduplication** with startup and post-sync safety nets (visible "Dedup Active" badge in the UI)
- **Forensic appellate language** throughout — all conclusions framed as arguable, contended, or tenable, not bare declarations. The Court makes findings; the brief identifies where findings are open.
- **Intelligent ground framing by type:**
  - Psychiatric/mental state evidence — framed as **conviction safety attack on mens rea** determination (not merely evidentiary criticism)
  - Jury/procedural issues — clustered as **Procedural Unfairness** with sub-particulars
  - Sentencing errors — tied to **proportionality and moral culpability**
  - Ineffective counsel — marked as **CONTINGENT** — requiring evidentiary support (affidavit, transcript confirmation) before advancement
- **Ground Priority Reorder** — drag-and-drop or arrow-button reordering of grounds by priority, saved to the database
- Each ground is individually investigated with supporting legal analysis
- Covers all recognised appeal grounds under Australian law:
  - Miscarriage of justice (including mens rea determination failures)
  - Errors of law by the trial judge
  - Verdict unreasonable or unsupported by evidence
  - Fresh or newly discovered evidence
  - Sentencing errors (manifestly excessive/inadequate)
  - Procedural irregularities
  - Prosecutorial misconduct
  - Jury irregularities
  - Inadequate legal representation (contingent)
- Grounds are cross-referenced across documents and timeline events

### 5. Three-Axis Appellate Viability Scoring (Legitimacy Engine)
A custom-built scoring engine replaces traditional percentage-based success rates with a counsel-grade three-axis viability assessment:

| Axis | Measures | Levels |
|------|----------|--------|
| **Outcome Impact** | How significantly this ground could affect the appeal result | Determinative / Influential / Minor |
| **Legal Alignment** | How directly existing legal authority supports this ground | Direct authority / Analogous / Weak |
| **Evidence Support** | How strongly the available case materials support this ground | Strong / Partial / Limited |

**Overall Viability Rating** (scored out of 9):
- **Arguable — Strong:** Ground has strong prospects on appeal and warrants prioritisation
- **Arguable — Moderate:** Ground is viable but requires further development
- **Requires Development:** Ground needs significant additional material before advancement

Each ground includes a built-in **glossary** explaining all viability terms in plain English. Ineffective counsel grounds are automatically capped at "moderate" and flagged as contingent unless strong evidentiary support exists.

### 6. Tiered AI Report Generation System
The platform produces four tiers of progressively detailed analytical reports, each generated through multi-pass AI processing using **forensic appellate language**:

| Tier | Report | Price | Purpose |
|------|--------|-------|---------|
| 1 | **Quick Summary** | FREE | Issue identification — identifies and lists potential grounds of appeal with appellate pathways |
| 2 | **Full Detailed Report** | $150 AUD | Appellate pathway analysis — 8-pass generation, 15 sections, comprehensive ground-by-ground assessment with legal reasoning, forensic framing, and precedent references |
| 3 | **Extensive Log Report** | $200 AUD | Operations engine — 10-pass generation, 24 sections, exhaustive deep-dive with checklists, evidence deployment strategy, Crown response anticipation, and defence rebuttals |
| 4 | **Appellate Research Brief** | Unlocked after Tiers 1-3 | Pure counsel-ready synthesis — no repetition from lower tiers. Includes Counsel Synthesis header, Priority Order, Issue Matrix, and Counsel Conference Prep (Attachment B) |

**Report Generation Architecture:**
- Each report is generated through multiple sequential AI passes to ensure depth and accuracy
- **Live pass-by-pass progress** — the UI surfaces the current pass label and section title in real time (`PASS 3/8 — Grounds of Merit — Part 1`) with a pill per pass (completed / active-pulsing / pending) and a real progress bar driven by `current_pass / total_passes`
- The Appellate Research Brief specifically retrieves and synthesises the content of all three lower-tier reports
- **Condensed prompt approach** for 8-pass and 10-pass engines — after Pass 1, subsequent passes receive ~20k tokens instead of 134k to fit within context limits and reduce 502 proxy errors
- **Pass-level retry with exponential backoff** for transient 502 proxy timeouts
- All reports use **strict forensic appellate language** — "It is arguable that...", "It is contended that...", "There is a tenable argument that..." — never bare declarations or weak hedging
- All reports are written in **strict third-person educational language** — no first or second person pronouns
- Reports include jurisdiction-specific legal frameworks, sentencing guidelines, and relevant precedent
- Every report includes the mandatory **"NOT LEGAL ADVICE"** disclaimer
- Australian English spelling enforced throughout (analyse, organise, defence, offence, behaviour)
- **Export footer version badge** on every PDF/Word/Print: *"Legal Framework v2026.02 · 79 Australian Acts manually verified · criminallawappealmanagement.com.au"* — a visible currency stamp for anyone reviewing an exported brief.

### 7. Appellate Research Brief — Counsel-Ready Synthesis
The Appellate Research Brief is designed to tell a barrister "where do I attack?" in minutes, not hours:

**Counsel Synthesis (header):**
- **Primary Issue:** The single most important attack vector for the appeal
- **Secondary Issue:** The second strongest line of attack
- **Tertiary Issue:** The third line of attack
- **Priority Order:** All grounds numbered by priority with one-line assessments
- **Overall Appellate Position:** Calibrated assessment using viability language

**Issue Matrix (attachment):**
- Tabulated issue matrix cross-referencing each ground to supporting documents, witnesses, and legal authorities

**Counsel Conference Prep — Attachment B** (full section):
- **B.1 Key Questions** — questions counsel should put to the client in conference
- **B.2 Weak Points** — markdown table identifying vulnerabilities in each ground
- **B.3 Likely Prosecution Responses** — anticipated Crown rebuttals
- **B.4 Document References** — checklist table of supporting evidence
- **B.5 Suggested Conference Agenda** — structured meeting plan

Tables are parsed by `parseBarristerSections` in `BarristerView.jsx` and rendered via ReactMarkdown + remark-gfm for clean on-screen display.

### 8. Multi-Language Report Translation
Reports can be translated into **41 languages** using AI-powered translation that preserves legal terminology, case citations, and document formatting:
- Chinese (Simplified & Traditional), Hindi, Arabic, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Vietnamese, Thai, Filipino/Tagalog, Greek, Turkish, Russian, Polish, Dutch, Swedish, Indonesian, Malay, Persian/Farsi, Urdu, Bengali, Tamil, Telugu, Nepali, Sinhala, Burmese, Khmer, Lao, Amharic, Swahili, Somali, Tigrinya, Tongan, Samoan, Maori, Punjabi
- Full-report translations are **chunked and run with 3-way concurrency** via `asyncio.Semaphore(3)` — a ten-chunk brief completes in roughly one-third the sequential wall time without tripping OpenAI rate limits.
- **Restart-safe** — task state is mirrored to the `translation_tasks` Mongo collection so an in-flight translation survives a backend restart; the status endpoint falls back to the persisted snapshot and returns `recovered: true`.
- **Per-section translation** — every report section (split on H2 headings) has its own "Translate section" dropdown (20 languages). The section-only endpoint is synchronous, cached per `(report_id, language, section_slug)` in `report_section_translations`, and short-circuits when the target language is English. Ideal for sharing a single Grounds section with a non-English-speaking client.
- Translations are cached for instant subsequent access
- Translated reports can be exported as **professionally formatted PDFs** with cover pages, legal disclaimers, and page numbers
- Accessible via a "Translate" button on any report view or a "Translate section" button next to each section heading

### 9. Case Export Pack
A single, professionally formatted PDF containing ALL generated reports for a case:
- Professional cover page with case metadata (defendant, court, jurisdiction, sentence, offence)
- Table of contents
- Grounds of Merit section with full analysis for each ground
- Case Timeline table
- Every paid/generated report's full analysis content
- Legal Framework Reference
- Page numbers, footers, and legal disclaimers throughout
- Only includes reports the user has actually generated and paid for

### 10. Legal Framework Viewer & Forensic Pipeline
- Jurisdiction-specific legislation covering criminal law, evidence acts, appeal legislation, and human rights across all **9 Australian jurisdictions**
- Displays elements of the offence, maximum penalties, sentencing ranges, and relevant legislation
- Complete appeal acts for NSW, VIC, QLD, SA, WA, TAS, NT, ACT, and Federal (Cth)
- Integrated directly into the case workflow for contextual reference
- **13-stage forensic procedural pipeline** injected into every LLM prompt: Incident → Arrest → Charge → Bail → First Mention → Committal → Indictment → Trial Prep → Trial → Verdict → Sentencing → Intermediate Appellate Court → High Court s.35A special leave. Hybrid and Summary variants cover non-indictable pathways.
- **Mens rea framework** — intention, knowledge, recklessness, negligence, strict liability, absolute liability — each with authorities (He Kaw Teh, Crabbe, Aubrey, Nydam, Lavender) and application guidance. Every one of the 18 offence categories references the fault elements it engages.
- **27 recently commenced Acts (2022–2026)** injected into AI context, including NSW Coercive Control (s 54D), QLD Coercive Control (s 334C), Jury Amendment Act 2024, Knife Crime Act 2024, Racial and Religious Hatred Act 2025, Non-Fatal Strangulation Act, Federal Hate Crimes Act 2025, and Wage Theft Act 2024
- **Anti-hallucination guardrails** at every prompt boundary — AI must cite full Act name + year, preserve jurisdiction references, flag uncertainty, and never default to NSW references when the case is in another state

### 11. Legislation Currency Dashboard (Admin)
Keeps the legal framework anchored to current law:
- **Registry of 79 Australian Acts** across all 9 jurisdictions (NSW 13, VIC 10, QLD 9, SA 9, WA 9, TAS 8, NT 8, ACT 8, Cth 5). Each entry includes a direct **AustLII** URL and a search-fallback URL.
- **Colour-coded age bucketing** — 🟢 Current (<90 days), 🟡 Review soon (90–180 days), 🔴 Overdue (>180 days) based on each Act's `last_verified` date.
- **Manual verification tick** — one-click "Mark verified" per Act writes an entry to the `framework_audit_log` collection with the admin's forensic note (e.g. "confirmed ss.18, 33 still current 14 Feb 2026"). This is the ONLY way an Act's verified date advances — by design.
- **AI cross-check button** — optional GPT-4o prompt for manual review. The AI cannot certify an Act as verified. See the anti-hallucination section below for the strict guardrails that apply to every AI currency check.
- Available to admins at `/admin/legislation-currency`.

### 12. Progress Analysis
- AI-generated assessment of overall case strength and appeal readiness
- Identifies areas requiring further evidence or documentation
- Tracks completion status across all case preparation phases
- Exportable to PDF, Word, and print formats

### 13. Real-Time Collaboration & Chat
- Share cases with other registered users via email invitation
- WebSocket-powered real-time messaging within shared cases
- Notification system for new messages and case updates
- Collaborative notes with pinning, commenting, and version tracking
- Permission controls for view/edit access

### 14. Document Export System
- **PDF Export:** Professional-formatted documents with branded cover pages, coloured report headers, legal disclaimers, and page-numbered footers
- **Word Export (.docx):** iOS-compatible Word documents with proper XML envelope and BOM encoding
- **Print Preview:** Dedicated `/document-preview` route with automatic print dialogue and clean A4-optimised layout
- **Bulk Export with section picker:** "Print All", "PDF All", and "Word All" open an Export Options Modal that lets the user include or exclude individual sections (Cover Page, Notes, Grounds, Timeline, Reports, etc.) per export.
- **Case Export Pack:** Single formatted PDF with all paid reports, grounds, timeline, and legal framework
- **Parity across on-screen, print, PDF and DOCX:** Body 11pt, H1 16pt, H2 15pt, H3 13pt, tables 9pt, cover meta 10pt, cover disclaimer 9pt, body disclaimer 8pt — identical across every format
- Exact footer on every exported page: *Criminal Law Appeal Management / {Document Name} — {Defendant} — {Date} — Page X of Y* (Times Italic, 7pt)
- **Framework version badge** on every export: *"Legal Framework v2026.02 · 79 Australian Acts manually verified · criminallawappealmanagement.com.au"*
- All exports include the **"NOT LEGAL ADVICE"** legal disclaimers

### 15. Payment Integration
- **PayID (Australian bank transfer):** Secure payment via Australian PayID with reference-based tracking, email notifications, and admin verification workflow
- Payment status tracking per report tier per case
- Payment history with downloadable PDF receipts
- Trial pricing available for first-time users

### 16. Admin Dashboard & Analytics
- **PayID verification panel at the top** — pending Australian bank transfers awaiting admin confirmation; one-click "Confirm Payment" unlocks the feature for the user.
- **Live visitor statistics** — real-time visit count, unique IPs, top pages.
- **Signup Source Analytics** (`/admin/analytics`) — per-CTA conversion rates + per-source signup breakdown.
- **OpenAI Cost Tracker** — embedded in `/admin/analytics`. Four stat cards (USD spent this month, projected month-end, tokens processed, success rate), period selector (7-day / this month / all time), daily sparkline, and three breakdown cards (by model / by report type / by task type). Token counts are estimated locally with `tiktoken` (o200k_base) and costs are calculated against OpenAI's Feb 2026 rate card. The "AI Cost Badge" on each case page shows *"Estimated AI cost: $X.XX across N AI calls"* with per-report-type pills.
- **Legislation Currency Dashboard** (`/admin/legislation-currency`) — see Section 11.
- Admin dashboard header carries a subtle self-hosted line: *"Self-hosted · your OpenAI key · your Google OAuth · criminallawappealmanagement.com.au"* — a quiet trust signal when signing in.

### 17. Appeal Statistics Dashboard (Public)
- Comprehensive national and state-by-state criminal appeal statistics
- Data sourced from ABS Criminal Courts Australia, state Supreme Court annual reviews, Judicial Commission of NSW, Victorian Sentencing Advisory Council, and Legal Services Commissioners
- Colour-coded state comparison (NSW, VIC, QLD, SA, WA, TAS, NT, ACT)
- In-depth analysis of why appeal rates are low, systemic barriers, and success factors

### 18. Interactive Tutorial (How It Works)
- Nine-step guided walkthrough covering every feature of the platform
- Each step features a coloured header, description, "What You'll See on Screen" checklist, and pro tips
- Covers: Account Creation, Document Upload, Timeline, Grounds, Notes, Reports, Legal Framework, Deadlines, and Chat & Collaboration

### 19. Native Mobile Apps (iOS & Android)
- **Capacitor 7** configured for native iOS and Android builds from the same React codebase
- 12 Capacitor plugins in sync across both platforms (App, Camera, Device, Filesystem, Haptics, Local Notifications, Network, Preferences, Push Notifications, Share, Splash Screen, Status Bar)
- `allowNavigation` whitelist configured for the production custom domain and its subdomains to prevent mobile CORS failures
- Mobile CTA section on the Help page (App Store + Google Play buttons auto-activate when `REACT_APP_IOS_APP_STORE_URL` / `REACT_APP_GOOGLE_PLAY_URL` are set)
- Step-by-step build instructions in `/app/frontend/MOBILE_BUILD.md` (Xcode + Android Studio)

### 20. Sign-in Diagnostics Panel
- Collapsible "Show sign-in diagnostics" link on the OAuth failure card
- JSON dump of timestamp, hostname, protocol, referrer, `navigator.cookieEnabled`, whether state exists in localStorage, whether state exists in cookie, whether a returned `state`/`code` is in the URL, the error detail, and userAgent
- One-click "Copy diagnostics to clipboard" so users can forward the payload to support without screenshots or guesswork

---

## Anti-Hallucination & Forensic Language Rules

Every AI call in the pipeline is constrained by explicit guardrails. These are not policy aspirations — they are enforced in code at the prompt layer, the response-validation layer, and the UI layer.

- **System prompts** list banned phrases ("The trial judge erred", "I believe", "the court will find") and required phrases ("It is arguable that...", "It is contended that...", "There is a tenable argument that...").
- **Forensic third-person only** — validators reject any LLM output containing the pronouns "I / we / you / us / our".
- **No invented citations** — prompts explicitly forbid fabricated section numbers, case names, or amendment dates. Jurisdiction references MUST be preserved from the case record; the AI is told never to default to NSW when the case is in another state.
- **Strict JSON schemas** for every structured pass — missing keys, invalid enum values, or non-list fields cause the response to be SUPPRESSED and a guardrail message surfaced instead. Hallucinated prose never reaches the UI.
- **Legislation Currency AI check** — see Section 11 — is the most strict: the AI's only valid `status` values are `appears_current | possible_change | cannot_verify | outside_knowledge_cutoff`. The tool refuses to display AI content that triggers the tripwire. The service overwrites any model-supplied `forensic_caveat` with authoritative wording that explicitly states the output is a *prompt for human review, not verification*.
- **Translations** — the translation system prompt preserves all legal terminology, citations, jurisdiction references, and forensic hedging in the target language. Commentary is forbidden.
- **Report generation** — every pass writes to `reports.generation_progress` in Mongo, and every LLM call is recorded by `services.ai_usage_tracker` so the actual cost per report is transparent to the admin.

---

## Technical Architecture

### Backend — Python 3.11 / FastAPI 0.135

The backend is built on **FastAPI** (v0.135.2), a high-performance async Python web framework, with **MongoDB** (via Motor 3.7 async driver) as the primary database.

**Application Structure:**
- Thin app factory (`server.py` ~170 lines) — middleware configuration, CORS, security headers, rate limiting, exception handlers
- Multi-pass AI report generation engine with forensic appellate language enforcement
- PDF generation via ReportLab 4.4 with custom `NumberedCanvas` for exact page numbering and branded footers
- DOCX generation via python-docx with styled paragraphs, tables, and section formatting
- Sentence extraction and normalisation using regex-based parsers
- Jurisdiction-specific offence framework context builders
- Database initialisation with indexes for **35+ collections** at startup (`services/startup_tasks.py`)
- **Background task + polling pattern** for heavy LLM operations (document bulk extraction, ground investigation, full-report translation) using `asyncio.create_task` with `task_id`-based status polling to bypass Cloudflare 100s timeouts

**Modular Router Architecture:**
```
/app/backend/routers/
├── __init__.py          # Centralised router registration
├── auth.py              # Session-token auth, registration, direct Google OAuth, password change
├── cases.py             # Case CRUD operations + per-case AI cost endpoint
├── documents.py         # Document upload, OCR, text extraction (background task + polling)
├── timeline.py          # Timeline CRUD, auto-generation, analysis, PDF export
├── grounds.py           # Grounds CRUD, AI investigation, auto-identify, priority reorder
├── notes.py             # Notes CRUD, pinning, comments, WebSocket collaboration
├── reports.py           # Report generation with live pass-by-pass progress
├── report_exports.py    # PDF/DOCX export with branded footers and font-size parity
├── payments.py          # PayID payment processing and verification
├── payment_history.py   # Payment history and PDF receipt generation
├── collaboration.py     # Case sharing, real-time chat, notifications
├── analysis.py          # Contradiction scanning, progress analysis
├── contradictions.py    # AI-powered contradiction detection
├── resources.py         # Resource directory, document templates
├── export.py            # Case Export Pack (PDF)
├── translate.py         # Full-report translation (parallel chunks) + per-section translation
├── barrister_pack.py    # Barrister acceptance package generation
├── pipeline.py          # Background pipeline tasks
├── pipeline_staged.py   # Staged pipeline processing
├── statistics.py        # Public appeal statistics endpoints
├── analytics.py         # Visit tracking, admin dashboard
├── admin.py             # Admin endpoints — signup-source analytics, OpenAI cost tracker,
│                        # legislation currency dashboard, payment verification
├── password_reset.py    # Secure password reset flow via email
├── deadlines.py         # Deadline tracking, checklist, case strength
├── compare.py           # Case comparison and pattern analysis
├── caselaw.py           # Case law search integration
├── legislation.py       # Legislation lookup (legacy — currency dashboard now lives in admin.py)
└── utilities.py         # States, offence frameworks, categories
```

**Service Layer:**
```
/app/backend/services/
├── legitimacy_engine.py      # Three-axis appellate viability scoring engine
├── llm_service.py            # Direct OpenAI GPT-4o integration (self-hosted, owner's key)
├── ai_usage_tracker.py       # tiktoken-based token accounting + USD cost estimation per call
├── legislation_currency.py   # Registry aggregation + mark_verified + anti-hallucination AI check
├── ai_service.py             # AI analysis and extraction services
├── report_generator.py       # Multi-pass report engine with live progress tracking (PASS_TITLES)
├── barrister_generator.py    # Counsel Synthesis + Issue Matrix + Counsel Conference Prep
├── offence_helpers.py        # Jurisdiction-specific offence context builders
│                             # (injects procedural flow + mens rea + 27 recent Acts)
├── email_service.py          # Transactional emails via Resend API (v2.23)
├── document_helpers.py       # Text extraction pipeline (PDF → OCR → DOCX → plaintext)
├── export_footer.py          # Shared PDF/DOCX footer formatting logic (7pt Times-Italic)
├── caselaw_search.py         # Case law search and retrieval
├── ground_dedup.py           # 12-topic fuzzy ground deduplication
├── notes_helpers.py          # WebSocket collaboration helpers
├── startup_tasks.py          # Database index creation and dedup post-sync safety nets
├── pipeline_models.py        # Pydantic models for pipeline data
├── pipeline/
│   ├── classify.py           # Ground classification with intelligent merging
│   ├── extract.py            # Document fact/event/finding extraction
│   ├── verify.py             # Ground verification against extracted record
│   ├── argue.py              # Argumentation strategy generation
│   ├── draft.py              # Draft report composition
│   └── submit.py             # Report submission and finalisation
└── __init__.py
```

**Frameworks Package** (refactored from the original 3,970-line monolith):
```
/app/backend/frameworks/
├── __init__.py              # Package-level re-exports (27 symbols)
├── jurisdictions.py         # LEGISLATION_CURRENCY, AUSTRALIAN_STATES
├── procedure.py             # INDICTABLE/HYBRID/SUMMARY_PROCEDURE_FLOW, MENS_REA_FRAMEWORK
├── offences.py              # OFFENCE_CATEGORIES (all 18)
├── states.py                # NSW/VIC/QLD/SA/WA/TAS/NT/ACT criminal frameworks
├── federal.py               # Commonwealth criminal framework + fault elements
├── appeal.py                # APPEAL_FRAMEWORK, APPEAL_GROUNDS_ACCESSIBILITY
├── sentencing.py            # SENTENCING_FRAMEWORK
├── evidence.py              # EVIDENCE_FRAMEWORK
├── mental_impairment.py     # MENTAL_IMPAIRMENT_FRAMEWORK
├── landmark_cases.py        # LANDMARK_CASES
├── recent_updates.py        # RECENT_LEGISLATION_UPDATES (27 Acts 2022–2026)
├── common_grounds.py        # COMMON_APPEAL_GROUNDS
├── human_rights.py          # HUMAN_RIGHTS_FRAMEWORK
└── legislation_registry.py  # 79-Act currency registry with AustLII URLs
```
The historical `offence_framework.py` has been reduced to a 10-line back-compat shim; every legacy `from offence_framework import X` continues to work identically.

**Authentication — self-hosted:**
- Session-token management with PBKDF2-HMAC-SHA256 password hashing (100,000 iterations + random 32-byte salt)
- **Direct Google OAuth** (no third-party proxy). `POST /api/auth/google/callback` exchanges the Google `code` directly at `https://oauth2.googleapis.com/token`, verifies the `id_token` with `google.oauth2.id_token.verify_oauth2_token` against `GOOGLE_CLIENT_ID`, upserts the user by verified email, and issues a session token.
- **OAuth CSRF state — belt-and-braces storage:** state is written to BOTH `localStorage` AND a parent-domain-scoped cookie so it survives DNS-level redirects between `www.` and the bare domain (e.g. GoDaddy forwarding). Read falls back between the two sources.
- Role-based access control (admin, user)
- Brute-force protection (10 attempts/minute/IP) and secure password reset via email
- Short-lived, single-use download tokens for secure export URL sharing
- The legacy `/api/auth/session` endpoint (formerly a session-exchange path) now returns **410 Gone** with a clear message, so any bookmarked mid-flow URL fails loudly rather than silently succeeding.

**AI Integration — direct OpenAI, owner's key:**
- **OpenAI GPT-4o** for all AI operations. No proxy, no shared key, no third-party LLM router. Billing goes straight to the owner's OpenAI account via `OPENAI_API_KEY` in `.env`.
- Per-call usage (provider, model, input/output tokens, USD cost, case_id, report_type) recorded fire-and-forget to the `ai_usage` collection by `services.ai_usage_tracker`. The admin dashboard surfaces these aggregates live.
- Multi-pass generation: each report tier uses tailored system prompts with increasing depth requirements
- **Forensic appellate language enforcement:** banned phrases + required phrases + ground-type-specific framing rules (see Anti-Hallucination section above)
- **Full-report translation** runs chunks with `asyncio.Semaphore(3)` and persists task state to Mongo so restarts never orphan jobs.
- **Per-section translation** (`POST /api/cases/{case_id}/translate-section`) is synchronous and cached per `(report_id, language, section_slug)`. English is a no-op short-circuit; sections >30,000 chars reject with 400.
- **Live progress persistence** — each AI pass writes `{current_pass, total_passes, pass_label, pass_title}` to `reports.generation_progress`
- **Condensed prompts** for passes 2+ of the 8-pass and 10-pass engines (134k → ~20k tokens)
- **Pass-level retry with exponential backoff** for transient 502 proxy errors
- Structured output parsing with strict JSON schema validation
- Context window management: documents, timeline events, and existing report content are compiled into optimised prompt payloads
- Offence-specific prompt enrichment: the AI receives jurisdiction-specific sentencing frameworks, elements of the offence, the 13-stage procedural flow, the mens rea framework, 27 recently commenced Acts (2022–2026), and relevant legislative references

### Frontend — React 19 / Tailwind CSS 3 / Shadcn UI

The frontend is a **React** (v19) single-page application styled with **Tailwind CSS** (v3.4) and the **Shadcn/UI** component library built on Radix UI primitives.

**Key Technical Decisions:**
- **Forced light mode globally** — dark backgrounds are overridden via CSS to ensure maximum readability and accessibility for legal documents
- **Crimson Pro serif font** for all headings — professional legal typography
- **Manrope sans-serif** for body text — optimised for screen readability
- **High-contrast colour palette:** Bright blue action buttons (white text), colour-coded report tiers (Emerald, Blue, Purple, Teal), jurisdiction-specific state colours
- **Code splitting with React.lazy** — all admin and feature pages are lazy-loaded to reduce initial bundle size
- **Shared Australian English normaliser** (`utils/auSpelling.js`) — 80+ American-to-Australian spelling replacements applied across all components displaying AI-generated text
- **Optimised images** — all screenshots and stock images compressed and resized for fast loading; all hero images served from local `/public/images/` (no external CDN dependencies)
- **Global Axios 401 interceptor** — graceful session-expiry redirect to the login page; no more confusing "Network Error" states for logged-out users.

**Frontend Stack:**
- React 19 with React Router v7 for client-side routing
- Axios for HTTP communication with the FastAPI backend (60s default timeout, 90s for main case GET)
- Shadcn/UI components (40+ Radix primitives): Accordion, Dialog, Tabs, Select, Toast, Progress, Badge, and more
- Sonner for toast notifications
- Embla Carousel for image carousels
- html2canvas for client-side screenshot generation
- date-fns for date formatting and manipulation
- ReactMarkdown + remark-gfm for rendering Appellate Research Brief markdown tables and per-section translations
- Capacitor 7 for native iOS and Android builds (12 plugins)

**Key Component Additions:**
- `OpenAICostsPanel.jsx` — live admin cost tracker (stat cards, sparkline, breakdowns).
- `AiCostBadge.jsx` — per-case "Estimated AI cost: $X.XX across N calls" badge on the Reports tab.
- `SectionTranslatableReport.jsx` — splits markdown on H2 and adds a "Translate section" dropdown per heading.
- `ExportOptionsModal.jsx` — section picker for bulk PDF / Word / Print exports.
- `LegislationCurrency.jsx` — admin currency dashboard with AustLII links, manual tick, and anti-hallucination-guarded AI check dialog.

### Database — MongoDB

- **Motor 3.7** async driver for non-blocking database operations
- **35+ indexed collections** initialised at startup, including: `users`, `user_sessions`, `cases`, `reports`, `report_translations`, `report_section_translations`, `translation_tasks`, `documents`, `document_extracts`, `case_extracts`, `grounds_of_merit`, `timeline_events`, `notes`, `payments`, `pipeline_tasks`, `notifications`, `case_shares`, `share_links`, `case_messages`, `issue_classifications`, `issue_verifications`, `issue_arguments`, `activities`, `deadlines`, `checklist_items`, `submissions_drafts`, `contradiction_scans`, `contact_messages`, `visits`, `visit_stats`, `counters`, `password_reset_tokens`, `download_tokens`, `ai_usage`, `framework_audit_log`
- **Unique compound indexes** on `report_translations` (report_id + language) and `report_section_translations` (report_id + language + section_slug)
- **TTL indexes** for automatic session, password reset token, and download token expiry
- All ObjectId fields excluded from API responses to ensure JSON serialisation safety
- UTC timestamps throughout with ISO string storage

### DevOps & Deployment

- Currently containerised (Kubernetes preview + custom-domain frontend); self-hosting migration guide at `/app/memory/SELF_HOSTING_GUIDE.md` walks through moving the backend to Railway / Render / Fly.io under `api.criminallawappealmanagement.com.au`.
- Multi-stage Dockerfile (Node 22 Alpine for frontend build, Python 3.11 for backend)
- Supervisor-managed processes (backend on port 8001, frontend on port 3000)
- Ingress routing: `/api/*` → backend, all other routes → frontend
- Environment-driven configuration: zero hardcoded URLs, secrets, or database credentials
- **CORS restricted** to explicit production domains (no wildcards)
- Hot reload enabled for both frontend and backend in development
- Ruff linting for Python, ESLint for JavaScript

**CI/CD Pipeline (GitHub Actions — 5 strict gates):**
1. **Python lint** — `ruff check backend/` must pass (test-scaffolding excluded via `backend/pyproject.toml`)
2. **JavaScript lint** — `eslint frontend/src/` must pass
3. **Backend tests** — `pytest backend/tests/` runs against a live MongoDB 7 service container (476+ offline tests covering offence / state / legal / dedup / legislation frameworks, AI usage tracker, translation concurrency + recovery, section translation, legislation currency registry + guardrails, frameworks refactor parity)
4. **Frontend build** — `yarn build` with `--frozen-lockfile` enforcement and lockfile drift detection
5. **Security scan** — no hardcoded secrets (sk-/AKIA/AIza/ghp_), no `os.system`, no `subprocess(shell=True)`, no `eval/exec`, no bare `except:` in production code, no raw `innerHTML` (only `dangerouslySetInnerHTML` via `DOMPurify.sanitize`), all API keys read from `os.environ`
- Nightly cron schedule + commit SHA logging on every run
- Test credentials read from GitHub Secrets (never hardcoded)

---

## Security & Compliance

### Authentication & Access Control
- All passwords hashed with **PBKDF2-HMAC-SHA256** (100,000 iterations + random 32-byte salt).
- Session tokens (UUID4) with configurable expiry and TTL-indexed database storage.
- **Short-lived, single-use download tokens** for secure document export — prevents URL sharing of sensitive exports.
- **Direct Google OAuth** with `id_token` signature verification (no third-party auth proxy in the trust chain). The owner runs their own Google Cloud Console OAuth client for `criminallawappealmanagement.com.au`.
- **OAuth CSRF protection** via cryptographically random `state` parameter, stored with belt-and-braces resilience (localStorage + domain-scoped cookie) and rotated on every login attempt.
- **Role-based access control** — every admin endpoint checks the session against `ADMIN_EMAILS`.
- **Case ownership verification** on every data-access endpoint. Users can only see cases they own or have been explicitly shared.
- **Brute-force protection** — 10 requests/minute/IP on authentication endpoints via `slowapi`.
- **Global Axios 401 interceptor** on the frontend — silent redirect to login on session expiry; no stale data is left on screen.

### Transport & Headers
- **CORS restricted** to explicit production domains — no wildcards in production.
- **Security headers middleware:** X-Frame-Options DENY, X-Content-Type-Options nosniff, X-XSS-Protection, Cache-Control no-store on sensitive responses.
- HTTPS enforced at the ingress layer; HSTS handled at the reverse proxy.

### Data Handling
- No sensitive data stored in localStorage beyond session tokens and OAuth state.
- Input validation via **Pydantic models** on every API endpoint.
- ObjectId fields excluded from all API responses; Mongo projections consistently use `{"_id": 0}`.
- UTC timestamps throughout; `datetime.now(timezone.utc)` never `datetime.utcnow()`.
- **OCR processing performed server-side** — no document content transmitted to unauthorised third parties.

### AI & Forensic Integrity
- All AI-generated content includes mandatory **"NOT LEGAL ADVICE"** disclaimers.
- **Anti-hallucination guardrails** enforced at the prompt, schema, and UI layers (see dedicated section above). The Legislation Currency AI check is the most strict: AI output can never mark an Act verified; only a human tick can.
- **Forensic third-person language** enforced via banned-phrase lists and first-person-pronoun validators; violations cause the response to be SUPPRESSED rather than surfaced.
- **Per-call AI usage logging** — every LLM call is recorded in the `ai_usage` collection so cost, volume, and provenance are auditable for every case.
- **Framework audit log** — every manual legislation re-verification tick is persisted with `verified_by`, `verified_at`, and the admin's forensic note.

### Payments & Financial Controls
- Payment processing via **PayID (Australian bank transfer)** — no card data or PCI-scope data handled by the application.
- Admin-only PayID verification panel at the top of `/admin/dashboard`.
- Per-report payment state tracked in the `payments` collection with admin confirmation timestamps.

### Self-Hosting Independence
- No third-party LLM proxy; no shared authentication service; no shared environment.
- Runtime dependencies: owner's **OpenAI API key**, owner's **Google OAuth client**, owner's **Resend API key**, owner's **MongoDB Atlas** cluster (once migrated per `SELF_HOSTING_GUIDE.md`), and owner's **domain** (`criminallawappealmanagement.com.au`).
- A grep for "Emergent" across `/app/backend` and `/app/frontend/src` returns zero hits outside the `emergentintegrations` Python library name (just an SDK wrapper around the standard OpenAI client — calls go straight to OpenAI on the owner's billing).
- The admin dashboard carries a quiet footer line: *"Self-hosted · your OpenAI key · your Google OAuth · criminallawappealmanagement.com.au"*.

---

## Environment Setup

### Backend (`/app/backend/.env`)
| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URL` | Yes | MongoDB connection string |
| `DB_NAME` | Yes | Database name |
| `CORS_ORIGINS` | Yes | Comma-separated allowed frontend origins |
| `OPENAI_API_KEY` | Yes | Owner's OpenAI API key for GPT-4o (billing goes to this account) |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth 2.0 client ID (from Google Cloud Console) |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth 2.0 client secret |
| `RESEND_API_KEY` | Yes | Resend.com API key for transactional emails |
| `RESEND_FROM_EMAIL` | Yes | Sender email address |
| `CONTACT_EMAIL` | Yes | Admin contact email |
| `FRONTEND_URL` | Yes | Frontend URL for email links and OAuth callbacks |
| `ADMIN_EMAILS` | Yes | Comma-separated admin email addresses |
| `PAYID_EMAIL` | No | PayID payment notification email |

The app **fails fast at startup** if any Yes-required variable is missing.

### Frontend (`/app/frontend/.env`)
| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_BACKEND_URL` | Yes | Backend API base URL (set to `https://api.criminallawappealmanagement.com.au` after self-hosting migration) |
| `REACT_APP_GOOGLE_CLIENT_ID` | Yes | Google OAuth 2.0 client ID (same value as backend) |
| `REACT_APP_IOS_APP_STORE_URL` | No | iOS App Store URL — activates App Store button on Help page when set |
| `REACT_APP_GOOGLE_PLAY_URL` | No | Google Play Store URL — activates Google Play button on Help page when set |

See `.env.example` files in both directories for annotated templates.

---

## Legal Disclaimer

**This application is an educational research tool only and does NOT constitute legal advice.** It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers **Australian law only**. No solicitor-client relationship is created by using this service.

No document, report, or output generated by this application should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body without independent verification by a qualified Australian legal professional.

---

## Credits

**Conceived, Designed, and Directed by Debra King**

Appeal Case Manager — Criminal Appeal Research Tool — Australian Law Only

Self-hosted on **criminallawappealmanagement.com.au**. Founded by Debra King. All Rights Reserved.

---
