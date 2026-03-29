# Appeal Case Manager

### Criminal Law Appeal Case Management System — Australian Jurisdictions

---

## About This Project

**Appeal Case Manager** is a comprehensive, AI-powered web application purpose-built for the Australian criminal justice system. It was conceived, designed, and directed by **Debra King** — a passionate advocate who identified a critical gap in the legal landscape: the overwhelming majority of convicted Australians who may have legitimate grounds for appeal never exercise that right, largely due to systemic barriers including cost, complexity, lack of legal knowledge, and inadequate prior representation.

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

Appeal Case Manager was designed to democratise access to appeal preparation by providing structured case management, automated document analysis, AI-driven identification of potential grounds of appeal, and tiered professional-grade reporting — all within a secure, user-friendly platform accessible from any device.

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

### 3. AI-Powered Timeline Generation
- Automatic construction of chronological case timelines from uploaded documents
- Manual timeline entry and editing
- Timeline analysis identifying gaps, inconsistencies, and critical procedural dates
- Export timelines to PDF with professional formatting

### 4. Grounds of Merit Identification
- **AI-driven automatic identification** of potential grounds of appeal from case documents
- Each ground is individually investigated with supporting legal analysis
- Covers all recognised appeal grounds under Australian law:
  - Inadequate legal representation
  - Errors of law by the trial judge
  - Verdict unreasonable or unsupported by evidence
  - Fresh or newly discovered evidence
  - Sentencing errors (manifestly excessive/inadequate)
  - Procedural irregularities
  - Prosecutorial misconduct
  - Jury irregularities
- Grounds are cross-referenced across documents and timeline events

### 5. Tiered AI Report Generation System
The platform produces four tiers of progressively detailed analytical reports, each generated through multi-pass AI processing:

| Tier | Report | Price | Depth |
|------|--------|-------|-------|
| 1 | **Quick Summary** | FREE | Base-level overview of case strengths, weaknesses, and identified grounds |
| 2 | **Full Detailed Report** | $150 AUD | Comprehensive analysis with legal reasoning, precedent references, and detailed ground-by-ground assessment |
| 3 | **Extensive Log Report** | $200 AUD | Exhaustive deep-dive covering every aspect of the case with granular analysis of each piece of evidence |
| 4 | **Barrister Brief** | Unlocked after Tiers 1–3 | Capstone synthesis document combining all three reports into counsel-grade material with an attached **Barrister Issue Matrix** |

**Report Generation Architecture:**
- Each report is generated through multiple sequential AI passes to ensure depth and accuracy
- The Barrister Brief specifically retrieves and synthesises the content of all three lower-tier reports
- All reports are written in **strict third-person educational language** — no first or second person pronouns
- Reports include jurisdiction-specific legal frameworks, sentencing guidelines, and relevant precedent
- Every report includes the mandatory **"NOT LEGAL ADVICE"** disclaimer

### 6. Legal Framework Viewer
- Jurisdiction-specific offence frameworks loaded dynamically based on the case's state and offence category
- Displays elements of the offence, maximum penalties, sentencing ranges, and relevant legislation
- Integrated directly into the case workflow for contextual reference

### 7. Progress Analysis
- AI-generated assessment of overall case strength and appeal readiness
- Identifies areas requiring further evidence or documentation
- Tracks completion status across all case preparation phases
- Exportable to PDF, Word, and print formats

### 8. Real-Time Collaboration & Chat
- Share cases with other registered users via email invitation
- WebSocket-powered real-time messaging within shared cases
- Notification system for new messages and case updates
- Collaborative notes with pinning, commenting, and version tracking
- Permission controls for view/edit access

### 9. Document Export System
- **PDF Export:** Professional-formatted documents with branded cover pages, coloured report headers, legal disclaimers, and page-numbered footers
- **Word Export (.doc):** iOS-compatible Word documents with proper XML envelope and BOM encoding
- **Print Preview:** Dedicated `/document-preview` route with automatic print dialogue and clean A4-optimised layout
- **Bulk Export:** "Print All", "PDF All", and "Word All" functions export the complete case bundle (summary, timeline, grounds, notes, progress) in a single document
- All exports feature the **"Created and Designed by Deb King"** branding and **"NOT LEGAL ADVICE"** legal disclaimers

### 10. Payment Integration
- **PayID (Australian bank transfer):** Manual confirmation workflow with email notifications
- **PayPal:** Full SDK integration with client-side checkout
- **Stripe:** Secure card payment processing with webhook support
- Payment status tracking per report tier per case

### 11. Appeal Statistics Dashboard
- Comprehensive national and state-by-state criminal appeal statistics
- Data sourced from ABS Criminal Courts Australia, state Supreme Court annual reviews, Judicial Commission of NSW, Victorian Sentencing Advisory Council, and Legal Services Commissioners
- Colour-coded state comparison (NSW, VIC, QLD, SA, WA, TAS, NT, ACT)
- In-depth analysis of why appeal rates are low, systemic barriers, and success factors
- Educational resource for understanding the appeals landscape

### 12. Interactive Tutorial (How It Works)
- Nine-step guided walkthrough covering every feature of the platform
- Each step features a coloured header, description, "What You'll See on Screen" checklist, and pro tips
- Covers: Account Creation, Document Upload, Timeline, Grounds, Notes, Reports, Legal Framework, Deadlines, and Chat & Collaboration

---

## Technical Architecture

### Backend — Python / FastAPI

The backend is built on **FastAPI** (v0.135), a high-performance async Python web framework, with **MongoDB** (via Motor async driver) as the primary database.

**Core Engine (`server.py` — 3,830 lines):**
- Application factory with middleware configuration (CORS, static files, exception handlers)
- Multi-pass AI report generation engine with model fallback logic
- PDF generation via ReportLab with custom page templates, headers, footers, and branded cover pages
- DOCX generation via python-docx with styled paragraphs, tables, and section formatting
- Sentence extraction and normalisation using regex-based parsers
- Offence framework context builders for all Australian jurisdictions

**Modular Router Architecture (23 router files):**
```
/routers/
├── auth.py              # JWT authentication, registration, Google OAuth
├── cases.py             # Case CRUD operations
├── documents.py         # Document upload, OCR, text extraction, auto-detect
├── timeline.py          # Timeline CRUD, auto-generation, analysis, PDF export
├── grounds.py           # Grounds of merit CRUD, AI investigation, auto-identify
├── notes.py             # Notes CRUD, pinning, comments, WebSocket collaboration
├── payments.py          # PayID/PayPal/Stripe payment processing
├── collaboration.py     # Case sharing, real-time chat, notifications
├── analysis.py          # Contradiction scanning, progress analysis
├── resources.py         # Resource directory, document templates
├── export.py            # Appeal package bundling (ZIP/PDF)
├── statistics.py        # Public appeal statistics endpoints
├── analytics.py         # Visit tracking, admin dashboard
├── admin.py             # Admin endpoints (contact, user stories)
├── password_reset.py    # Secure password reset flow via email
├── deadlines.py         # Deadline tracking, checklist, case strength
├── messages.py          # Legacy messaging endpoints
├── contradictions.py    # AI-powered contradiction detection
├── compare.py           # Case comparison and pattern analysis
├── utilities.py         # States, offence frameworks, categories
└── ...
```

**Service Layer (7 service files):**
```
/services/
├── llm_service.py         # OpenAI GPT-4o integration with Emergent LLM Key
├── offence_helpers.py     # Jurisdiction-specific offence context builders
├── email_service.py       # Transactional emails via Resend API
├── document_helpers.py    # Text extraction pipeline (PDF → OCR → DOCX → plaintext)
├── notes_helpers.py       # WebSocket collaboration helpers
└── ...
```

**Authentication:**
- JWT token-based session management with bcrypt password hashing
- Google OAuth integration via Emergent-managed social login
- Role-based access control (admin, user)
- Brute-force protection and secure password reset via email

**AI Integration:**
- **OpenAI GPT-4o** via the Emergent Integrations library and Universal LLM Key
- Multi-pass generation: each report tier uses tailored system prompts with increasing depth requirements
- Structured output parsing with fallback error handling
- Context window management: documents, timeline events, and existing report content are compiled into optimised prompt payloads
- Offence-specific prompt enrichment: the AI receives jurisdiction-specific sentencing frameworks, elements of the offence, and relevant legislative references

### Frontend — React / Tailwind CSS / Shadcn UI

The frontend is a **React** (v19) single-page application styled with **Tailwind CSS** (v3) and the **Shadcn/UI** component library built on Radix UI primitives.

**Key Technical Decisions:**
- **Forced light mode globally** — dark backgrounds are overridden via CSS to ensure maximum readability and accessibility for legal documents
- **Crimson Pro serif font** for all headings — professional legal typography
- **Manrope sans-serif** for body text — optimised for screen readability
- **High-contrast colour palette:** Bright blue action buttons, colour-coded report tiers (Emerald, Blue, Purple, Teal), jurisdiction-specific state colours

**Frontend Stack:**
- React 19 with React Router v7 for client-side routing
- Axios for HTTP communication with the FastAPI backend
- Shadcn/UI components (40+ Radix primitives): Accordion, Dialog, Tabs, Select, Toast, Progress, Badge, and more
- Sonner for toast notifications
- Embla Carousel for image carousels
- html2canvas for client-side screenshot generation
- date-fns for date formatting and manipulation
- Capacitor (v7) configured for native iOS and Android builds

**Component Architecture (111 files):**
- Page components: LandingPage, CaseDetail, BarristerView, ReportView, HowItWorksPage, AppealStatisticsPage, DocumentPreviewPage, and more
- Feature components: ReportsSection, GroundsOfMerit, TimelineEnhanced, LegalFrameworkViewer, NotesSection, CollaborationPanel
- Utility modules: exportHtml.js (shared HTML export builder with branded templates)

### Database — MongoDB

- **Motor** async driver for non-blocking database operations
- Collections: `users`, `cases`, `reports`, `documents`, `timeline_events`, `grounds`, `notes`, `payments`, `messages`, `notifications`, `shared_cases`, `analytics`
- All ObjectId fields excluded from API responses to ensure JSON serialisation safety
- UTC timestamps throughout with ISO string storage

### DevOps & Deployment

- **Kubernetes-ready** containerised deployment via Emergent platform
- Supervisor-managed processes (backend on port 8001, frontend on port 3000)
- Ingress routing: `/api/*` → backend, all other routes → frontend
- Environment-driven configuration: zero hardcoded URLs, secrets, or database credentials
- CI/CD via GitHub Actions with Node 24 compatible runners
- Ruff linting for Python (246 errors resolved), ESLint for JavaScript
- 64 pytest test files for backend regression testing

---

## Security & Compliance

- All passwords hashed with bcrypt (12 rounds)
- JWT session tokens with configurable expiry
- CORS configuration for production origin restriction
- No sensitive data stored in localStorage beyond session tokens
- All AI-generated content includes mandatory legal disclaimers
- Payment processing via PCI-compliant third-party providers (Stripe, PayPal)
- OCR processing performed server-side — no document content transmitted to unauthorised third parties
- Google OAuth tokens managed by Emergent's secure authentication proxy

---

## Legal Disclaimer

**This application is an educational research tool only and does NOT constitute legal advice.** It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers **Australian law only**. No solicitor-client relationship is created by using this service.

---

## Credits

**Conceived, Designed, and Directed by Debra King**

Appeal Case Manager — Criminal Appeal Research Tool — Australian Law Only

Founded by Debra King | All Rights Reserved

---
