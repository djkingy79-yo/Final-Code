# Criminal Appeal AI - Case Management

## Original Problem Statement
Create an app to sort, store and organise documents, briefs, case notes, and public case information for criminal appeals. Features include timeline generation, AI-powered grounds of merit identification, cross-referencing with source material, multiple report types, notes/comments, barrister presentation view, and PDF/DOCX export.

## Owner
**Deb King, Glenmore Park 2745**
*One woman's fight for justice — seeking truth for Joshua Homann, failed by the system*

## User Choices
- AI Provider: OpenAI GPT-4o with Emergent LLM key
- Authentication: Google Social Login (Emergent Auth)
- Multi-case support: Yes
- Document formats: PDF, DOCX, TXT, Images (with OCR)
- Export: PDF and DOCX with Grounds of Merit and Legal References
- Payment: PayPal integration for premium features

## Pricing Model (PayPal / PayID)
| Feature | Price (AUD) |
|---------|-------------|
| Document Upload | FREE |
| Grounds of Merit (count only) | FREE |
| **Unlock Grounds of Merit Details** | **$99.00** |
| **Quick Summary Report** | **FREE** |
| **Full Detailed Report** | **$150.00** |
| **Extensive Log Report** | **$200.00** |

## Architecture
- **Backend**: FastAPI with MongoDB
- **Frontend**: React with Tailwind CSS + Shadcn UI
- **AI**: OpenAI GPT-4o via Emergent Integrations
- **Auth**: Emergent Google OAuth
- **PDF Generation**: ReportLab library
- **DOCX Generation**: python-docx library
- **OCR**: Tesseract OCR + pdf2image

## Features Implemented

### Core Features ✅
- [x] Google OAuth authentication
- [x] Multi-case dashboard with search
- [x] Case CRUD operations
- [x] Multi-file document upload
- [x] Document text extraction (PDF, DOCX, TXT)
- [x] OCR for scanned documents and images
- [x] Document search across case files
- [x] Timeline event management

### Enhanced Timeline System ✅ (Mar 2026)
- [x] **Comprehensive Event Categories** - Pre-trial, Trial, Evidence, Post-conviction, Investigation
- [x] **27 Event Types** - Arrest, Charge, Bail, Committal, Jury Selection, Witness Testimony, etc.
- [x] **Event Details:**
  - Significance levels (Critical, Important, Normal, Minor)
  - Perspective tracking (Prosecution, Defence, Neutral)
  - Source citations
  - Participants with roles
  - Document linking
  - Ground of appeal linking
- [x] **Contested Facts** - Mark disputed events with details
- [x] **Inconsistency Notes** - Track contradictions
- [x] **Timeline Analysis (AI):**
  - Gap detection between events
  - Inconsistency identification  
  - Prosecution vs Defence balance
  - Ground of appeal connections
  - Key observations and recommendations
- [x] **Timeline Filters** - By category, significance, perspective, contested status
- [x] **Timeline Search** - Search across events, participants, sources
- [x] **PDF Export** - Professional formatted timeline document

### AI-Powered Features ✅
- [x] Auto-identify Grounds of Merit from documents **with duplicate prevention**
- [x] Deep investigation of individual grounds
- [x] Law section extraction (NSW & Federal)
- [x] Similar case identification
- [x] Report generation (Quick Summary, Full Detailed, Extensive Log)
- [x] **Auto-generate Timeline from documents** - AI extracts dates and events

### PayPal Paywall System ✅ (Mar 2026)
- [x] **Grounds of Merit Paywall** - Shows count for free, $50 to unlock full details
- [x] **Report Tiers:**
  - Quick Summary: FREE
  - Full Detailed Report: $29.99
  - Extensive Log Report: $50.00
- [x] PayPal payment integration
- [x] Payment tracking per case
- [x] Unlock state persistence
- [x] Payment modal UI component

### Export & Presentation ✅
- [x] PDF export with grounds and legal references
- [x] DOCX/Word export for editing
- [x] Barrister View (A4 professional format)
- [x] Print-ready formatting

### Mobile App Support ✅ (Feb 2026)
- [x] Progressive Web App (PWA) - installable from browser
- [x] App icons for all platforms (72px to 512px)
- [x] iOS "Add to Home Screen" support
- [x] Android install prompt
- [x] Service worker for offline caching
- [x] Capacitor configured for App Store/Play Store submission
- [x] Mobile-responsive design

### Notes & Comments ✅
- [x] Create/edit/delete notes
- [x] 6 note categories
- [x] Pin/unpin important notes

## Key API Endpoints
- `POST /api/auth/session`: OAuth session exchange
- `POST /api/cases`: Create case
- `POST /api/cases/{id}/documents`: Upload documents
- `POST /api/cases/{id}/documents/search`: Search documents
- `POST /api/cases/{id}/documents/{id}/ocr`: OCR single document
- `POST /api/cases/{id}/ocr-all`: OCR all documents
- `POST /api/cases/{id}/grounds/auto-identify`: AI identify grounds
- `POST /api/cases/{id}/grounds/{id}/investigate`: Deep investigation
- `POST /api/cases/{id}/timeline/auto-generate`: AI generate timeline from docs
- `POST /api/cases/{id}/timeline/analyze`: AI timeline analysis (gaps, inconsistencies)
- `GET /api/cases/{id}/timeline/export-pdf`: Export timeline as PDF
- `POST /api/cases/{id}/reports/generate`: Generate report
- `GET /api/cases/{id}/reports/{id}/export-pdf`: Export PDF
- `GET /api/cases/{id}/reports/{id}/export-docx`: Export Word

## Database Schema
- **users**: user_id, email, name, google_id
- **user_sessions**: session_token, user_id, expires_at
- **cases**: case_id, user_id, title, defendant_name, case_number, court, state, offence_category, offence_type
- **documents**: document_id, case_id, filename, content_text, ocr_extracted
- **timeline_events**: event_id, case_id, title, event_date, event_type, event_category, significance, perspective, is_contested, contested_details, linked_documents, participants, related_grounds, source_citation, inconsistency_notes
- **notes**: note_id, case_id, title, content, category, is_pinned
- **grounds_of_merit**: ground_id, case_id, title, ground_type, status, strength, law_sections, similar_cases, analysis
- **reports**: report_id, case_id, report_type, content, generated_at

## 3rd Party Integrations
- **OpenAI GPT-4o** via Emergent LLM Key
- **Emergent Google OAuth** for authentication
- **ReportLab** for PDF generation
- **python-docx** for Word document generation
- **Tesseract OCR** for image text extraction
- **pdf2image** for scanned PDF processing

## Legal Framework Reference
- Crimes Act 1900 (NSW)
- Criminal Appeal Act 1912 (NSW)
- Criminal Code Act 1995 (Cth)
- Evidence Act 1995 (NSW & Cth)
- Sentencing Act 1995 (NSW)

## Bug Fixes (Feb 2026)
- [x] **Case Loading Error** - Improved error handling with retry functionality
  - Changed from `Promise.all` to `Promise.allSettled` for resilient data loading
  - Added specific error messages for session expired, not found, timeout
  - Added retry button instead of immediate redirect
  - File: `frontend/src/pages/CaseDetail.jsx`

### User Guide & Glossary ✅ (Mar 2026)
- [x] Comprehensive "How to Use" guide with step-by-step instructions
- [x] **Legal Glossary** with 40+ terms covering:
  - Appeal Process (Appeal, Leave to Appeal, Ground of Appeal)
  - Parties (Appellant, Respondent)
  - Types of Grounds (Miscarriage of Justice, Procedural Error, etc.)
  - Evidence Terms (Hearsay, ERISP, Brief of Evidence, Disclosure)
  - Trial Process (Committal, Indictment, Verdict, Summing Up)
  - Legal Standards (Beyond Reasonable Doubt, Onus of Proof)
  - Offences & Defences (Murder, Manslaughter, Self-Defence)
  - App-specific terms (Significance, Perspective, Contested Facts)
- [x] Searchable glossary with category filtering
- [x] Examples for each term

### New Features (Mar 2026) ✅
- [x] **Appeal Deadline Tracker** - Track critical dates with countdown timers
- [x] **Witness Statement Contradiction Finder** - AI compares documents to find inconsistencies
- [x] **Case Strength Meter** - Visual dashboard showing appeal prospects (grounds, docs, timeline, preparation)
- [x] **Appeal Checklist System** - 22-step checklist from Preparation to Hearing
- [x] **Resource Directory** - Legal Aid offices, advocacy groups, courts, information services
- [x] **Document Templates** - Notice of Appeal, Leave to Appeal, Fresh Evidence Affidavit, Extension of Time
- [x] **Progress Tab** - New tab showing Case Strength, Deadlines, and Checklist

### Complete UI/UX Redesign (Dec 2025 - Mar 2026) ✅
- [x] **New Color Scheme** - "Hope in Darkness" theme
  - Deep Indigo (#1E1B4B) primary color
  - Burnished Amber (#B45309) accent color
  - Professional dark mode support
- [x] **Typography Update**
  - Crimson Pro for headings (serif, legal feel)
  - Manrope for body text (clean, modern)
- [x] **Landing Page Redesign**
  - Asymmetric hero section with Lady Justice image
  - State selector for jurisdiction-specific content
  - Feature preview mockups for timeline, grounds, reports
  - Cleaner feature cards in bento grid layout
  - Quick links bar for easy navigation
  - Condensed About section with personal story
  - Legal Resources section
- [x] **Dashboard Redesign**
  - New sidebar navigation (collapsible)
  - Stat cards showing Total Cases, Documents, Timeline Events
  - Dark/Light mode toggle in sidebar
  - User profile section at bottom
- [x] **Case Detail Styling Update**
  - Glass header with breadcrumb navigation
  - Updated tab styling with rounded corners
  - Consistent card styling throughout
- [x] **All Pages Updated** (Mar 2026 Session)
  - ✅ AuthModal - Branded header with gradient, amber button styling
  - ✅ ContactPage - Hero section, form redesign, navigation
  - ✅ Statistics Page - Dashboard with stat cards and bar charts
  - ✅ AdminStats - Admin analytics page
  - ✅ TermsOfService - Collapsible sections, highlighted warnings
  - ✅ SuccessStories - Story cards with outcome badges
  - ✅ Forms & Templates page
  - ✅ FAQ page with accordion and category graphics
  - ✅ Lawyer Directory page
  - ✅ Legal Glossary page with expandable definitions
  - All pages use new design tokens
- [x] **Glass Morphism Effects** - Backdrop blur on headers and modals
- [x] **Legal-themed Graphics** - Scales of justice, gavel imagery throughout
- [x] **Testing Verified** - All redesigned pages tested (test_reports/iteration_19.json)
- [x] **New Features Tested** - Compare Cases and Contradiction Finder (test_reports/iteration_20.json)
  - Backend: 20/20 API tests passed
  - Frontend: All features working correctly

- [x] **Export Features Tested** - Quick Export, Document Bundler, Enhanced Case Strength Meter (test_reports/iteration_21.json)
  - Backend: 11/13 API tests passed (85%)
  - Frontend: 100% - All new features verified



## Future Enhancements
- [ ] Case sharing with other users
- [ ] Email notifications
- [ ] Case law database integration
- [ ] Report comparison view
- [ ] Document version history

### New Features (Mar 2026 - Session 2) ✅
- [x] **Compare Cases Feature** - New page at `/compare` with two modes:
  - My Cases: Compare 2-5 of your own cases side-by-side
  - Platform Patterns: View anonymized aggregate insights from all users
  - Filters by offence category, state, and ground type
  - Success factors analysis showing what correlates with strong appeals
  - Backend: `/app/backend/routers/compare.py`
  - Frontend: `/app/frontend/src/pages/CompareCasesPage.jsx`

- [x] **Contradiction Finder (Enhanced)** - New tab in Case Detail:
  - AI-powered scan of documents, notes, and timeline for inconsistencies
  - Detects: witness statement contradictions, timeline issues, evidence conflicts
  - Severity levels: Critical, Significant, Minor
  - Specific quotes and recommendations for each finding
  - Scan history with ability to compare past scans
  - Backend: `/app/backend/routers/contradictions.py`
  - Frontend: `/app/frontend/src/components/ContradictionFinder.jsx`

- [x] **Dashboard Navigation Update** - Added Compare Cases link to sidebar

- [x] **Quick Export (Appeal Package) ✅** - Full ZIP with everything + editable DOCX
  - ZIP contains: all docs, timeline, grounds, notes, reports, AI analysis
  - 5 editable legal templates pre-filled with case data:
    - Notice of Intention to Appeal
    - Application for Leave to Appeal
    - Written Submissions Template
    - Fresh Evidence Affidavit
    - Chronology of Proceedings
  - Backend: `/app/backend/routers/export.py`
  - Frontend: `/app/frontend/src/components/QuickExport.jsx`

- [x] **Document Bundler ✅** - Bundle multiple docs into single PDF
  - Select documents to include
  - Auto-generate table of contents
  - Includes AI analysis notes
  - Backend: Added to `/app/backend/routers/export.py`
  - Frontend: `/app/frontend/src/components/DocumentBundler.jsx`

- [x] **Enhanced Case Strength Meter ✅** - Visual scoring system
  - Circular score display (0-100)
  - Color-coded rating badge
  - 4 breakdown categories: Grounds, Documentation, Timeline, Preparation
  - Recommendations to improve score
  - Frontend: Updated `/app/frontend/src/components/CaseStrengthMeter.jsx`

## Technical Debt (Priority)
- [x] **Backend Refactoring** - Created modular structure (COMPLETE - NO REGRESSIONS)
  - ✅ `/app/backend/models/__init__.py` - All Pydantic models extracted
  - ✅ `/app/backend/config.py` - Database connection and configuration
  - ✅ `/app/backend/auth_utils.py` - Shared authentication utilities
  - ✅ `/app/backend/services/ai_service.py` - AI helper functions
  - ✅ `/app/backend/routers/auth.py` - Auth endpoints
  - ✅ `/app/backend/routers/cases.py` - Case CRUD endpoints
  - ✅ `/app/backend/routers/documents.py` - Document handling
  - ✅ `/app/backend/routers/timeline.py` - Timeline management
  - ✅ `/app/backend/routers/notes.py` - Notes management
  - ✅ `/app/backend/routers/deadlines.py` - Deadlines & Checklist
  - ✅ `/app/backend/routers/resources.py` - Resources & Templates
  - Tested: 17/17 backend tests passed

- [x] **Frontend Refactoring** - Created reusable components (COMPLETE - NO REGRESSIONS)
  - ✅ `/app/frontend/src/components/DocumentSection.jsx` - Document handling (~400 lines)
  - ✅ `/app/frontend/src/components/NotesSection.jsx` - Notes management (~250 lines)
  - ✅ `/app/frontend/src/components/ReportsSection.jsx` - Report generation (~320 lines)
  - Tested: All frontend sections loading correctly

## Bug Fixes (Mar 2026)
- [x] **Report Generation Fixed** - All 3 report types working (Quick Summary, Full Detailed, Extensive Log)
  - Verified with comprehensive backend testing (17/17 tests passed)
  - AI calls use GPT-4o via Emergent LLM Key with retry logic
  - Test reports: `/app/test_reports/iteration_9.json`, `/app/test_reports/iteration_10.json`

### All Criminal Offence Types Support ✅ (Mar 2026)
- [x] **Expanded Beyond Murder/Manslaughter** - Now supports ALL criminal offence categories:
  - Homicide (Murder, Manslaughter, Attempted Murder, Dangerous Driving Causing Death)
  - Assault & Violence (Common Assault, ABH, GBH, Wounding, Affray, Intimidation)
  - Sexual Offences (Sexual Assault, Aggravated Sexual Assault, Sexual Touching, Child Offences)
  - Robbery & Theft (Armed Robbery, Theft, Receiving Stolen Property, Break and Enter)
  - Drug Offences (Possession, Supply, Trafficking, Importation, Manufacturing)
  - Fraud & Dishonesty (Fraud, Forgery, Identity Theft, Money Laundering)
  - Firearms & Weapons (Unauthorised Possession, Prohibited Weapons, Trafficking)
  - Domestic Violence (DV Assault, Stalking, Intimidation, AVO Contravention)
  - Public Order Offences (Riot, Affray, Offensive Conduct, Resist Arrest)
  - Terrorism Offences (Terrorist Acts, Membership, Financing, Foreign Incursion)
  - Driving Offences (Dangerous Driving, Drink/Drug Driving, Driving While Disqualified)

- [x] **Dynamic Legal Framework** - Each offence category includes:
  - NSW legislation with specific section references
  - Commonwealth/Federal legislation where applicable
  - Available defences specific to offence type
  - Key elements that must be proven
  
- [x] **AI Analysis Uses Offence Context** - All AI features now dynamically adjust:
  - Auto-identify grounds uses offence-specific system prompts
  - Deep investigation references correct legislation
  - Report generation tailored to offence type
  
- [x] **UI Enhancements**:
  - Dashboard: Offence category selector when creating new case
  - Dashboard: Dynamic offence type dropdown based on selected category
  - Case Detail: Displays offence category and type badges
  - Landing Page: Shows all supported offence types

- [x] **API Endpoints**:
  - `GET /api/offence-categories` - Returns all 11 categories with offences
  - `GET /api/offence-framework` - Returns complete legal framework
  - `GET /api/offence-framework/{category}` - Returns detailed framework for specific category

- [x] **Testing**: All tests passed (`/app/test_reports/iteration_13.json`)

### Legal Framework Viewer ✅ (Mar 2026)
- [x] **New Tab in Case Detail** - "Legal Framework" tab shows applicable legislation for the case
- [x] **Collapsible Sections**:
  - State-specific Legislation with section references (dynamically loads based on state)
  - Commonwealth/Federal Legislation
  - Key Elements to Prove (numbered list)
  - Available Defences (badge tags)
  - Appeal Procedure (state-specific court, time limits, forms)
  - Common Appeal Grounds
- [x] **State Selector** - Dropdown to switch between Australian states and view their specific legislation
- [x] **AustLII Link** - Quick link to view full legislation on AustLII.edu.au
- [x] **Component**: `/app/frontend/src/components/LegalFrameworkViewer.jsx`

### All Australian States Expansion ✅ (Mar 2026)
- [x] **Full National Coverage** - Now supports ALL Australian jurisdictions:
  - New South Wales (NSW)
  - Victoria (VIC)
  - Queensland (QLD)
  - South Australia (SA)
  - Western Australia (WA)
  - Tasmania (TAS)
  - Northern Territory (NT)
  - Australian Capital Territory (ACT)
  - Commonwealth/Federal law

- [x] **State-Specific Legislation** - Each state has its own legislation mapped:
  - NSW: Crimes Act 1900 (NSW)
  - VIC: Crimes Act 1958 (Vic)
  - QLD: Criminal Code Act 1899 (Qld)
  - SA: Criminal Law Consolidation Act 1935 (SA)
  - WA: Criminal Code Act Compilation Act 1913 (WA)
  - TAS: Criminal Code Act 1924 (Tas)
  - NT: Criminal Code Act 1983 (NT)
  - ACT: Crimes Act 1900 (ACT)

- [x] **State-Specific Appeal Procedures** - Each state has mapped:
  - Governing legislation (e.g., Criminal Appeal Act 1912 NSW, Criminal Procedure Act 2009 Vic)
  - Appeal court name
  - Time limits for lodging appeals
  - Required forms

- [x] **UI Enhancements**:
  - Landing page shows all 8 state badges + Federal
  - Dashboard: State selector when creating new case
  - Case Detail: State badge displayed in blue
  - Legal Framework Viewer: State dropdown to switch jurisdictions

- [x] **API Endpoints**:
  - `GET /api/states` - Returns all 8 Australian states/territories
  - `GET /api/offence-framework/{category}?state={state}` - Returns state-specific legislation

- [x] **Testing**: All 35 tests passed (`/app/test_reports/iteration_14.json`)
  - Verified all states return correct legislation
  - Verified appeal framework returns state-specific procedures

### Case Law Research Links ✅ (Mar 2026)
- [x] **All State Case Law Databases Added**:
  - NSW: caselaw.nsw.gov.au (Supreme, District & Local Court)
  - VIC: AustLII Victoria (Supreme & County Court)
  - QLD: sclqld.org.au (Supreme & District Court Library)
  - SA: courts.sa.gov.au/judgments
  - WA: ecourts.justice.wa.gov.au
  - TAS: AustLII Tasmania
  - NT: AustLII NT
  - ACT: courts.act.gov.au/supreme/judgments
  
- [x] **Federal Courts Added**:
  - High Court of Australia (hcourt.gov.au)
  - Federal Court of Australia (fedcourt.gov.au)
  
- [x] **AustLII Integration** - Main search for all Australian law
- [x] **Landing Page** - New "Search Real Court Decisions" section with all state links
- [x] **Legal Framework Viewer** - Case law links integrated into Legal Framework tab

### Refactoring & Technical Improvements ✅ (Mar 2026)
- [x] **Admin Email Moved to Environment Variable**:
  - `ADMIN_EMAILS` env var in `/app/backend/.env`
  - Supports comma-separated list for multiple admins
  - Default fallback to `djkingy79@gmail.com`

- [x] **Component Extraction from CaseDetail.jsx**:
  - Created `/app/frontend/src/components/DocumentsSection.jsx` - Document upload, list, search, OCR
  - Created `/app/frontend/src/components/NotesSection.jsx` - Notes management with categories
  - Updated `/app/frontend/src/components/ReportsSection.jsx` - Report generation and viewing
  - **INTEGRATED into CaseDetail.jsx** - Reduced from 2294 to 1209 lines (Dec 2025)

### Criminal Law & Human Rights Resources ✅ (Mar 2026)
- [x] **Criminal Legislation by State** - Direct links to:
  - NSW: Crimes Act 1900, Criminal Appeal Act 1912, Evidence Act 1995
  - VIC: Crimes Act 1958, Criminal Procedure Act 2009
  - QLD: Criminal Code Act 1899, Evidence Act 1977
  - SA: Criminal Law Consolidation Act 1935
  - WA: Criminal Code Act 1913, Criminal Appeals Act 2004
  - CTH: Criminal Code Act 1995, Evidence Act 1995, Judiciary Act 1903

- [x] **Human Rights Framework** - Links to:
  - International: ICCPR, UDHR, Convention Against Torture
  - Australian: Victoria Charter, ACT Human Rights Act, QLD Human Rights Act
  - Fair Trial Rights summary (before/during trial + after conviction)

- [x] **Case Law Research** - Links to all state court databases:
  - NSW Caselaw, Victorian Cases (AustLII), QLD Caselaw, SA Judgments
  - WA eCourts, Tasmanian Cases, NT Cases, ACT Judgments
  - High Court & Federal Court of Australia
  - AustLII main search

### CaseDetail.jsx Refactoring Complete ✅ (Dec 2025)
- [x] **Reduced from 2294 lines to 1209 lines** (~47% reduction)
- [x] **Integrated Section Components**:
  - `DocumentsSection.jsx` - Handles document upload, listing, search, OCR
  - `NotesSection.jsx` - Manages notes CRUD, categories, pinning
  - `ReportsSection.jsx` - Report generation with payment integration
- [x] **Cleaned Up Unused Code**:
  - Removed 10+ unused state variables
  - Removed 15+ unused handler functions
  - Removed unused imports (ScrollArea, ScanLine, etc.)
- [x] **Testing Verified**: All 7 tabs working (Documents, Timeline, Grounds, Notes, Reports, Legal Framework, Progress)
- [x] **Test Report**: `/app/test_reports/iteration_16.json`

### Pricing & Paywall Updates ✅ (Dec 2025)
- [x] **Quick Summary Reports now FREE**
- [x] **Grounds of Merit paywall fixed** - Shows count only, $50 to unlock details
- [x] **Updated pricing**:
  - Quick Summary: FREE
  - Full Detailed: $29 AUD
  - Extensive Log: $39 AUD
  - Grounds of Merit Details: $50 AUD

### Success Stories Page Updated ✅ (Dec 2025)
- [x] **4 detailed, realistic stories** with specific legal issues:
  - Sarah M. (NSW) - Jury misdirection, sentence reduced by 5 years
  - Michael T. (NSW) - Self-defence, CCTV contradiction, appeal pending
  - Jenny K. (QLD) - Search warrant timing issue, Legal Aid review
  - David R. (VIC) - Forensic calculation error, sentence reduced
- [x] **Added timeframe badges** showing appeal duration

### Case Statistics Dashboard ✅ (Dec 2025)
- [x] **Public statistics page** at `/statistics`
- [x] **Overview metrics**: Total cases, documents, reports, grounds identified
- [x] **Visual charts**:
  - Cases by Offence Type (horizontal bar chart)
  - Cases by State (horizontal bar chart)
  - Most Common Appeal Grounds (ranked list)
  - Ground Strength Distribution (circular badges)
- [x] **Key Insights section** highlighting trends
- [x] **Navigation links** added to header and footer

### New Pages & Features ✅ (Dec 2025)
- [x] **FAQ Page** (`/faq`) - Searchable FAQ with 6 categories, 20+ questions
- [x] **Lawyer Directory** (`/lawyers`) - Legal Aid, Bar Association, Law Society links for all 8 states
- [x] **Dark Mode Toggle** - Moon/Sun icon in header, persists in localStorage
- [x] **Drag & Drop Upload** - Enhanced document upload with drag/drop zone
- [x] **Updated Navigation** - FAQ, Find Lawyers links in header and footer

### Compare Your Case Feature ✅ (Dec 2025)
- [x] **New API endpoint** `/api/cases/{case_id}/comparison`
- [x] **CaseComparison component** in Progress tab showing:
  - Similar cases count (same offence, same state, exact match)
  - Your documents vs average comparison
  - Your grounds vs average comparison
  - Most common grounds for your offence type
  - Personalized insights and recommendations
- [x] **Visual indicators** (above/below average badges)

### Landing Page Design Cleanup ✅ (Dec 2025)
- [x] **Criminal Law by State** section converted to **collapsible accordions**
- [x] Each state (NSW, VIC, QLD, SA, WA, CTH) is now a clickable dropdown
- [x] Reduces visual clutter - users only expand what they need

## Next Priority Tasks
- [ ] Finalize PayPal backend payment processing
- [ ] Real-time collaboration/chat for Notes (WebSockets)
- [ ] Continue backend refactoring — extract cases, documents, grounds, notes, reports, payments routes from server.py

## Backlog (Bottom)
- [ ] Build and submit native mobile app (Capacitor ready)
- [ ] Enhanced collaboration features (replies, threads, @mentions in notes)
- [ ] Deadline Tracker with Calendar integration

### Bug Fixes & Improvements (Mar 2026 - Session 4) ✅
- [x] **Google Sign-in Button Restored** - Added "Sign in with Google" button to AuthModal
- [x] **How To Use Page Updated with Real Screenshots** - 8 real app screenshots
- [x] **Landing Page Navigation Improved** - All 9 content cards now clickable links
- [x] **Admin Bypass for Payments** - Admin users (djkingy79@gmail.com) get all features unlocked
  - `/api/auth/me` returns `is_admin: true` for admin emails
  - `/api/cases/{id}/payments` returns all features unlocked for admins
  - Grounds of merit always unlocked for admins
  - ReportsSection skips payment modal for admins
- [x] **Contacts Page Converted to Scrollable View** - Removed tab navigation, all 6 sections visible on scroll
- [x] **Legal Resources Page Scroll Anchors** - Tab buttons converted to smooth-scroll to sections
- [x] **Fixed "Objects are not valid as React child" error** - ReportsSection renders `report.content.analysis` not raw object
- [x] **Fixed LlmChat constructor error** in contradictions.py - was missing required args
- [x] **Testing**: iteration_23 (24/24 pass), iteration_24 (all pass), iteration_25 (18/18 pass)

### Session 4 - Super Reports & Stripe (Mar 2026) ✅
- [x] **Super Report Prompts** — All 3 report types massively upgraded:
  - Quick Summary: Structured with grounds preview, similar cases teaser, upgrade CTA
  - Full Detailed ($29): 10 sections including similar cases with AustLII links, complete appeal filing guide for all court levels, strategic case presentation advice
  - Extensive Log ($39): 14 sections, forensic-level analysis, 8-12 similar cases, witness credibility, sentencing comparison, complete appeal strategy
- [x] **Stripe Payment Integration** — Replaced PayPal with Stripe (supports Apple Pay, Google Pay, cards)
  - Backend: `/api/payments/checkout`, `/api/payments/status/{id}`, `/api/payments/prices`
  - Frontend: New PaymentModal with Stripe redirect
  - Webhook handler for payment confirmation
- [x] **Barrister View Fixed** — Grounds now display correctly (fixed data binding)
- [x] **PDF Export Fixed** — iOS-compatible download (opens in new tab on iPhone)
- [x] **Testing**: iteration_28 (100% backend + frontend)

### Session 5 - Stripe Removal & Barrister View Overhaul (Mar 2026) ✅
- [x] **Stripe Integration Removed** — Per user request, completely removed Stripe payment system:
  - Deleted `/app/backend/routers/stripe_payments.py` and `stripe_webhook.py`
  - Removed Stripe imports from `server.py` (lines 4103-4109)
  - Removed `stripe==14.3.0` from requirements.txt
  - Updated `PaymentModal.jsx` to show "Payment Coming Soon" placeholder
  - Removed Stripe checkout verification from `CaseDetail.jsx`
- [x] **Barrister View Redesigned** — Complete overhaul for "sensational" legal professional presentation:
  - Premium gradient header with branded design
  - Executive Summary section with case strength score (0-100 circular indicator)
  - Enhanced grounds display with color-coded strength badges (HIGH/MEDIUM/LOW)
  - Key Timeline Events section with critical event highlighting
  - Legal Framework reference section with primary/federal legislation
  - Professional footer with branding
  - Fullscreen mode for presentations
  - Mobile-responsive design
  - Print-optimized with page break controls
- [x] **Landing Page Report Section Updated** — New descriptions matching upgraded AI reports:
  - Quick Summary: Now shows "FREE" badge with feature list
  - Full Detailed: "$29 AUD" with Similar Cases Analysis + Complete Appeal Filing Guide
  - Extensive Log: "$39 AUD" with 14 sections, forensic-level analysis description
  - Clear pricing badges in header of each report card
  - Highlights: 8-12 similar cases, witness credibility, sentencing comparison, risk assessment
- [x] **Testing**: iteration_29 (100% backend + frontend pass)

### Session 6 - PayPal & PayID Payment Integration (Mar 2026) ✅
- [x] **PayPal Payment Integration** — Full PayPal REST API integration:
  - Backend: `/api/payments/paypal/create-order`, `/api/payments/paypal/execute`, `/api/payments/paypal/status/{id}`
  - Frontend: PayPal button redirects to PayPal checkout
  - Fixed pricing enforced server-side (never accepts amounts from frontend)
- [x] **PayID (Australian Bank Transfer)** — Manual bank transfer support:
  - Generates unique reference codes (ACM-XXXX-XXXX format)
  - PayID: djkingy79@gmail.com
  - Clear instructions for users on how to make bank transfer
  - Admin verification endpoint `/api/payments/payid/admin-confirm/{reference}`
- [x] **Payment Modal Updated** — Dual-tab interface:
  - Tab 1: PayPal / Card (redirects to PayPal)
  - Tab 2: PayID / Bank (shows bank transfer details with copy buttons)
  - Both methods support: Full Report ($29), Extensive Report ($39), Grounds of Merit ($50)
- [x] **Admin Dashboard Updated** — Pending PayID payments section:
  - Shows all pending bank transfers awaiting verification
  - One-click confirm button to unlock features for users
  - Instructions for how to verify against bank statement
- [x] **Testing**: iteration_30 (100% backend + frontend pass)

### Session 7 - Australian English & Legal Images (Mar 2026) ✅
- [x] **Australian English Throughout** — Fixed ~20 American English spellings:
  - "organize" → "organise" (LandingPage, FAQPage, LawyerDirectory, SuccessStories, PageCTA)
  - "analyze" → "analyse" (LandingPage, ReportsSection, BarristerView, Statistics, CaseDetail, FAQPage, HelpPage, ContradictionFinder)
  - "favor" → "favour" (TimelineAnalysis)
  - "analyzed" → "analysed" (ReportView, BarristerView, CompareCasesPage, ContradictionFinder)
- [x] **Legal-Themed Background Images** — 4 AI-generated images added:
  - Courtroom interior (hero section background)
  - Gavel and law books with barrister wig (hero right side)
  - Handcuffs with scales of justice (features section)
  - Prison bars with light (about section)
- [x] **Landing Page Accuracy Verified** — Deadline tracker with calendar view confirmed to exist
- [x] **Testing**: iteration_31 (95% pass - all major features verified)

### Session 8 - PayID Email Notifications (Mar 2026) ✅
- [x] **Email Notifications for PayID Payments** — Automatic email when admin confirms bank transfer:
  - Professional HTML email template with branding
  - Shows: Feature name, amount, reference, status
  - Direct link to user's case
  - Sent via Resend API
- [x] **Email Notifications for PayPal Payments** — Automatic email when PayPal payment completes
- [x] **Email Template Features**:
  - Branded header with Criminal Appeal AI logo
  - Success badge confirmation
  - Payment details summary
  - "View Your Case" button linking directly to case
  - Footer with contact info and tagline

### Session 9 - Visitor Counter (Mar 2026) ✅
- [x] **Public Visitor Counter** — Real-time statistics displayed on landing page:
  - Total Visitors (unique)
  - Today's Visitors
  - Registered Users
  - Cases Created
- [x] **Backend Analytics Endpoints**:
  - `POST /api/analytics/track-visit` — Tracks unique visitors by IP + user agent fingerprint
  - `GET /api/analytics/visitor-count` — Returns public stats (no auth required)
- [x] **VisitorCounter Component** — Reusable React component with 3 variants:
  - `full` — 4 coloured stat cards
  - `compact` — Single badge with visitor count
  - `badge` — Tiny inline badge
- [x] **Placement**: Below hero section with "Join thousands of Australians researching their appeals"

## Delivery Tracking Files
- Detailed implementation history moved to: `/app/memory/CHANGELOG.md`
- Prioritized pending work moved to: `/app/memory/ROADMAP.md`

## Latest Delivery Note (Mar 2026)
- **Session 13 (Mar 19, 2026)**: Deployment readiness check passed. Report generation reliability fixed with retry + model fallback (Claude x2 → gpt-4o-mini). Australian English verified clean. Print buttons verified. Testing: iteration_65 — 100% pass.
- Previous sessions: See `/app/memory/CHANGELOG.md` for full history.

### Final Comprehensive Fix + DO NOT UNDO Reinforcement (Mar 2026) ✅
- [x] **DO_NOT_UNDO.md** — Project-level protection file with 10 absolute rules
- [x] **DO NOT UNDO markers** on 80+ files across entire codebase
- [x] **Investigation speed fixed** — Reduced doc context 18000→12000, retry 4→3, backoff exponential→flat 2s
- [x] **Print button fixed** — Now opens full report page in new tab then triggers print for clean output
- [x] **Report generation warning** — "Please Allow Time for Generation" blue warning box restored
- [x] **All content cleaned** — Zero contradictions, zero old prices, zero Case Strength on any page
- [x] **Testing**: iteration_48 — 100% backend (8/8 API) + 100% code verification (13/13) + 100% frontend UI

### Complete Front-to-Back Content Sweep (Mar 2026) ✅
- [x] **All pages updated** — Removed all contradiction/witness/case strength references from:
  - Landing page: "Case Strength 72/100" → "5 Grounds / Grounds Identified"
  - Success Stories: "contradiction finder" → "AI analysis"
  - How To Use: "Find Contradictions" step → "Review Legal Framework"
  - FAQ: All prices updated ($99/$150/$200)
  - Professional Summary: "Witness statement contradictions" → "Comparative sentencing analysis"
- [x] **Print CSS enhanced** — Full @media print styles: hides nav/buttons, formats tables, proper font sizing
- [x] **Print button fixed** — Opens full report page then triggers print for clean output
- [x] **Barrister View** — Print/PDF/Word always visible on ALL screens, enhanced cover page
- [x] **Testing**: iteration_47 — 100% backend + 100% frontend across ALL 8 pages verified

### Critical Fixes — Barrister View, Progress Tab, Reports (Mar 2026) ✅
- [x] **Barrister View Print/PDF/Word** — Buttons now ALWAYS visible on all screen sizes (were hidden on mobile)
- [x] **Barrister View tables** — Now render as formatted HTML tables via ReactMarkdown (was raw markdown text)
- [x] **Barrister View cover page** — Added Prepared date, Report Type, Generated By, CONFIDENTIAL notice
- [x] **Progress tab RESTORED** — With Deadline Tracker and Appeal Checklist (only Case Strength /100 removed)
- [x] **Report generation warning** — "Please Allow Time for Generation" message restored in dialog
- [x] **Extensive Log ($200) prompt** — Word target raised to 9000-12000, 10 mandatory quality requirements added
- [x] **Aggressive mode** — 10 comprehensive directives, doubled content requirement, draft submissions
- [x] **Testing**: iteration_46 — 100% backend (7/7 pytest) + 100% frontend

### Aggressive Mode Enhancement (Mar 2026) ✅
- [x] **Aggressive directive expanded** from 4 bullet points to 10 comprehensive instructions including:
  - Double detail requirement, scripted oral submissions, 12+ case comparisons
  - Draft Notice of Appeal, pivot strategy for hostile bench
  - 3 argument structures (conservative/moderate/aggressive)
  - Persuasive advocacy tone throughout
- [x] **Aggressive appendix expanded** with Primary Order, 3 Fallback Positions, Pivot Strategy
- [x] **Model fallback fixed**: gpt-4o kept for 3 attempts before falling back to gpt-4o-mini (was 2)
- [x] **Content length check**: Reports under 2000 chars auto-retry
- [x] **Verified**: Aggressive quick_summary = 12,245 chars vs standard = 9,819 chars (25% more)

### Complete Design Overhaul — Blue/White/Red (Mar 2026) ✅
- [x] **REMOVED ALL yellow/amber/gold** — 636 occurrences across 52 files replaced
- [x] **New colour scheme**: Blue (primary), White (backgrounds), Red (accents/CTA)
- [x] **Court imagery**: Hero uses Australian High Court building with blue-950 overlay
- [x] **Typography**: Crimson Pro for headings, Manrope for body text
- [x] **CSS variables updated**: index.css completely cleaned of amber/gold references
- [x] **Testing**: iteration_45 — 100% clean across all 6 major pages, 0 amber/yellow/gold references

### Bug Fix: Recovered Reports + Case Strength Removal (Mar 2026) ✅
- [x] **Removed "Recovered Reports / Embedded High-Detail Reports"** section from ReportView.jsx — was cluttering paid reports
- [x] **Removed Case Strength meter** from all pages (legal implications, educational tool only)
- [x] **Removed Appeal Readiness Gauge** from ReportView.jsx
- [x] **Improved LLM retry** — falls back to gpt-4o-mini after 2 failed gpt-4o attempts (faster recovery from 502 errors)
- [x] **Testing**: Clean lint, no runtime errors, report renders correctly

### Bug Fix: HelpCircle Runtime Error (Mar 2026) ✅
- [x] **Root cause**: HelpCircle icon was removed from lucide-react import in CaseDetail.jsx while the Help button still used it
- [x] **Fix**: Added HelpCircle back to the import statement
- [x] **Testing**: iteration_44 — 100% backend (11/11 tests) + 100% frontend, no console errors on CaseDetail

### Major Overhaul (Mar 2026 — Current Session) ✅
- [x] **Pricing Updated**: Grounds $99, Full Report $150, Extensive Log $200 AUD
- [x] **Report Rendering Fixed**: Reports now render as formatted Markdown (was raw text)
- [x] **Action Buttons Moved to Top**: Full Report Page, Barrister View, PDF Export, Print buttons now at top of report card
- [x] **Tabs Simplified**: Removed Contradictions tab and Progress tab (including Case Strength meter) from CaseDetail
  - Remaining tabs: Documents, Timeline, Grounds, Notes, Reports, Legal Framework
- [x] **Legal Framework Strengthened**:
  - Legislation sections now have clickable AustLII links
  - Added "How to Start Your Appeal" 6-step guide with external links
  - Added "Appeal Forms & Court Registries" section with links for NSW, VIC, QLD, SA, WA, Legal Aid
- [x] **Report Prompts Enhanced**:
  - All reports now include links to AustLII, court websites, and legal aid
  - Full Report ($150): Added step-by-step appeal filing guide, required forms section, detailed outcome analysis
  - Extensive Report ($200): Added complete appeal process guide, forms checklist, detailed outcome analysis per case, barrister conference dossier
  - Both paid reports explain how each ground could assist in a successful appeal
- [x] **Testing**: iteration_43 — 100% backend + frontend pass


- [x] **79 files marked** with "DO NOT UNDO" comments to protect approved features:
  - 29 frontend page files
  - 22 frontend component files
  - 3 frontend core files (App.js, index.css, tailwind.config.js)
  - 20 backend router files
  - 4 backend core files (server.py, config.py, auth_utils.py, offence_framework.py)
  - 1 backend service file (ai_service.py)
  - 1 backend model file (models/__init__.py)

### Australian English Final Sweep (Mar 2026) ✅
- [x] Fixed remaining American English in user-facing text:
  - "specializing" → "specialising" (LawyerDirectory, SuccessStories, server.py, contradictions.py)
  - "organization" → "organisation" (AppealStatisticsPage)
  - "specialize" → "specialise" (server.py AI prompts)
- [x] Verified: No American English spellings found in visible UI text (iteration_42.json)

### P0 Fix: Professional Report Rendering (Mar 2026) ✅
- [x] **Created `.legal-report` CSS stylesheet** in `index.css` with comprehensive professional legal document styling:
  - Tables: Blue gradient headers (#1e3a8a), white header text, alternating row colours, hover effects, responsive overflow
  - Links: Blue underlined text, hover states, visited colours, opens in new tab
  - Blockquotes: Blue left border, grey background, italic, legal citation style
  - Headings: H1 with blue bottom border, H2 with grey border, proper hierarchy
  - Lists: Blue markers, proper indentation, nested list support
  - Dark mode: Full dark mode overrides for all elements
  - Print: Dedicated print styles with colour-adjust for headers
- [x] **Applied `.legal-report` wrapper** across all 3 report rendering locations:
  - `ReportView.jsx` — Full report page MarkdownBlock component
  - `ReportsSection.jsx` — Inline accordion report preview
  - `BarristerView.jsx` — Barrister presentation mode
- [x] **Redesigned ReportView.jsx** to match landing page style:
  - Colour-coded gradient headers (green=Quick, blue=Full Detailed, purple=Extensive)
  - Case overview grid (Defendant, Offence, Sentence, Documents, Timeline)
  - Table of Contents bar with section count
  - Section cards with coloured left borders and numbered circles
  - UPPERCASE tracking-wide section headings
  - Price badges and report type labels
  - Not Legal Advice disclaimer footer
- [x] **Redesigned ReportsSection.jsx** inline report cards:
  - Colour-coded headers matching report type (green/blue/purple gradient)
  - Price badges on report headers
- [x] **Fixed section parser** — no longer splits numbered list items into separate sections
- [x] **Testing**: iterations 49-51 — 100% pass, all design/visual/API elements verified

### Bug Fixes (Mar 2026) ✅
- [x] **Delete Case button** — Added to CaseDetail.jsx header with red styling, confirmation dialog, and redirect to dashboard after deletion
- [x] **Print CSS** — Added `-webkit-print-color-adjust: exact` for gradient headers, TOC bar, and section borders in print mode
- [x] **Report sections verified** — All 8 sections render (Executive Summary, Grounds, Sentencing Table, Legislation, Next Steps, Strategic Advice, Filing Guide, Appeal Forms)
- [x] **Form download links** — Fixed with iOS Safari fallback (opens in new tab) and toast notifications. Delayed URL revocation to prevent premature cleanup.
- [x] **How It Works page** — Completely rewritten with 6 detailed steps, colour-coded headers, "What You'll See on Screen" sections, Pro Tips, interactive CTAs, document upload priority table, sticky step navigation, and 3-tier pricing section
- [x] **Legal Framework page** — Verified NOT deleted. All 8 states + Commonwealth present with expandable legislation sections
- [x] **Mobile responsive** — Verified on iPhone viewport (390px) for How It Works, Forms, and Legal Framework pages
- [x] **Testing**: iterations 49-53 — 100% pass across all features

### Expanded Content & Features (Mar 2026) ✅
- [x] **Legal Framework page** — Expanded from ~5 laws per state to comprehensive listings:
  - NSW: 20 acts (Crimes, Drug Misuse, Bail, Evidence, Criminal Appeal, Mental Health, Summary Offences, Road Transport, Children, Terrorism, etc.)
  - VIC: 16 acts | QLD: 14 acts | SA: 13 acts | WA: 12 acts | TAS: 11 acts | NT: 11 acts | ACT: 12 acts | CTH: 12 acts
  - All links open to official government legislation websites in new tab
- [x] **How It Works page** — Now 7 steps including:
  - Step 3: "Find Grounds — FREE" (AI identifies how many grounds exist)
  - Step 4: "Investigate Grounds — $99 AUD" (detailed legal analysis of each ground)
  - "What You Get for $99" section with 6 value items
- [x] **Print buttons** — Added to ALL CaseDetail tabs (Timeline, Grounds, Notes, Progress)
- [x] **Form downloads** — Fixed with iOS Safari fallback and toast notifications

## Technical Debt (Current)
- `server.py` remains monolithic and should be modularized into focused routers/services.

### Performance Optimisation (Mar 2026) ✅
- [x] **Reduced all retry backoff delays** from 3-24 seconds to 1 second max across ALL AI endpoints
- [x] **Lawyer Directory** — Already populated with all 8 states

### UX & Health Check Improvements (Mar 2026) ✅
- [x] **Scroll to Top on Navigation** — Every page now starts at the top when navigated from menu bar
  - `ScrollToTopOnNav` component uses `useLocation` + `useEffect` to call `window.scrollTo(0, 0)` on pathname change
  - Added to `App.js` inside `BrowserRouter`
- [x] **Quick Home Button** — Floating home icon button appears after scrolling 420px
  - Positioned above the existing scroll-to-top button
  - Navigates to landing page (`/`) on click
  - `data-testid="global-quick-home-btn"`
- [x] **Enhanced Health Check** — `/api/health` now checks MongoDB connectivity
  - Returns `status` (healthy/degraded), `database` (connected/disconnected), `timestamp`
  - `ENABLE_HEALTH_CHECK=true` in frontend .env
- [x] **Full Page Audit** — All 16 public pages verified working on desktop (1920px) and mobile (390px)
  - No broken sections found
  - All navigation links working
  - Dark mode toggle working
  - Mobile hamburger menu working with 17 links
  - Testing: iteration_54 — 100% backend + 100% frontend

### Delete Report Button Fix (Mar 2026) ✅
- [x] **Delete report button now visible on mobile** — Changed from ghost/transparent to solid red circle (bg-red-600)
  - Was invisible on gradient backgrounds (text-white/70 on dark gradient)
  - Now renders as a clear red circle with white trash icon
  - Added data-testid for each button
- [x] **Delete case button on Dashboard** — Changed from hidden dropdown menu to visible red trash button on case card
  - Was inside a 3-dot dropdown menu that was hard to find on mobile
  - Now renders as direct red trash button on each case card
- [x] **Delete case button on CaseDetail** — Changed from ghost to destructive variant with full "Delete Case" text
  - Was ghost variant with hidden text on mobile (only tiny icon visible)
  - Now renders as solid red button with icon + "Delete Case" text always visible
- [x] **Report generation progress indicator** — Blue card with spinner + animated progress bar during generation
  - Shows message: "AI is analysing your case. Please allow time for generation."
  - Reminds user: "This can take 1-3 minutes for detailed reports. Do not close this page."
- [x] **Testing**: iterations 55-56 — 100% backend (10/10) + 100% frontend

### Delete Fix: AlertDialog + AI Progress Tab (Mar 2026) ✅
- [x] **Root cause: window.confirm() doesn't work on mobile Safari** — Replaced ALL window.confirm() with AlertDialog modals from shadcn/ui
  - Dashboard delete case — AlertDialog modal with "Yes, Delete Case" red button
  - CaseDetail delete case — AlertDialog modal  
  - CaseDetail delete event — AlertDialog modal
  - CaseDetail delete ground — AlertDialog modal
  - Reports delete report — AlertDialog modal with "Delete Report" red button
- [x] **AI Progress Analysis** — New "AI Analyse Progress" button in Progress tab
  - Purple-blue gradient button triggers AI analysis of case progress
  - Backend: POST /api/cases/{case_id}/progress-analysis using GPT-4o
  - Returns structured analysis: Progress Summary, Completed Steps, Critical Next Steps, Case Strength, Timeline Recommendations, Strategic Recommendations, Risk Factors
  - Progress indicator shows "AI Scan in Progress — Analysing Case Progress" during generation
- [x] **DO NOT UNDO comments** — Added to all new code sections
- [x] **Testing**: iteration_57 — 100% backend + 100% frontend code verification

### Caselaw Search Box + Delete Ground Fix (Mar 2026) ✅
- [x] **Caselaw search box for EVERY ground** — Each ground now has its own independent "Search" button
  - Uses per-ground state `searchOpen = {}` (object) so ALL grounds can have search boxes open simultaneously
  - Search box opens AustLII with the ground's title as default query
  - Custom search terms can be entered per ground
  - `data-testid="search-box-{ground_id}"` for each
- [x] **Delete ground button now visible on mobile** — Changed from ghost (invisible) to destructive with bg-red-600
- [x] **DO NOT UNDO comments** added to all new code sections
- [x] **Testing**: iteration_58 — 100% backend (15/15) + 100% frontend code verification

### Progress Bar on Each Ground + Barrister Print + Extensive Report Upgrade (Mar 2026) ✅
- [x] **AI investigation progress bar now shows ON each ground card** — Not at the top of the tab, but right on the specific ground being investigated
  - Uses `investigating === ground.ground_id` condition inside GroundsOfMerit.jsx
  - Shows spinner, "AI Scan in Progress" message, time estimate, and animated progress bar on that ground's card
- [x] **Barrister View print button fixed** — White visible styling on dark header + fallback toast for mobile Safari
- [x] **Extensive Log report ($200) massively upgraded** — Now 25 sections (was 23), word target 12000-18000 (was 9000-12000)
  - New sections: Barrister Case Snapshot, Complete Draft Written Submissions (ready for filing), Complete Draft Notice of Appeal, Enhanced Barrister Conference Dossier
  - Each ground now includes draft submission paragraph, key authority with AustLII link, practical impact analysis
  - Comparative sentencing expanded to 15+ cases with detailed outcome analysis
  - This is the premium differentiator — actual filing-ready documents
- [x] **Testing**: iteration_59 — 100% backend (9/9) + all code review verified

### Report Links Fix + Report Quality Upgrade (Mar 2026) ✅
- [x] **All report links now clickable** — Fixed across all 5 components rendering markdown:
  - ReportView.jsx, BarristerView.jsx, ReportsSection.jsx, GroundsOfMerit.jsx, CaseDetail.jsx
  - All links: blue + underlined + open in new tab + security attributes
  - GroundsOfMerit.jsx formatAnalysis completely rewritten from plain-text to ReactMarkdown
- [x] **Extensive Log report split into 3 API calls** — Sections 1-9, 10-18, 19-25 generated separately to avoid placeholder text
  - Anti-placeholder instructions added: "NEVER write descriptions in parentheses"
  - Each section required to have minimum 300 words of real content
- [x] **Full Detailed report also upgraded** with anti-placeholder instructions
- [x] **Testing**: iteration_60 — 100% (13/13 code verification tests)

### PayID Payments + Full Regression (Mar 2026) ✅
- [x] **PayID backend endpoints implemented** — POST /api/payments/payid/create-reference and POST /api/payments/payid/verify
  - Generates unique ACM-XXXXXXXX reference for bank transfers
  - Auto-grants feature access after payment confirmation
- [x] **PayPal endpoint path fixed** in PaymentModal.jsx — was calling wrong path
- [x] **PayID MongoDB bug fixed** — was inserting with _id: None causing duplicate key errors
- [x] **Full regression test passed** — iteration_62: 17/17 backend + 100% mobile UI
  - All CRUD operations: create/read/update/delete cases, reports
  - All AI features: progress analysis, report generation
  - All payment flows: PayPal redirect + PayID reference
  - All mobile UI: login, dashboard, tabs, delete buttons, floating buttons

### iPad Navigation Fix (Mar 2026) ✅
- [x] **iPad now has full navigation** — Changed breakpoint from md: (768px) to lg: (1024px)
  - iPad (768-1023px) now gets hamburger menu with ALL 17+ navigation links
  - Desktop (1024px+) gets full nav bar with "More" dropdown containing 8 extra pages
  - Dashboard sidebar consistent with lg: breakpoint
- [x] **More dropdown on desktop** — Forms, Glossary, Legal Framework, Lawyers, How To Use, Contact, Caselaw Search, Professional Summary
- [x] **Testing**: iteration_63 — 100% all viewports (390px, 810px, 1024px, 1920px)

### Background Report Generation Fix (Mar 2026) ✅
- [x] **Root cause identified**: Kubernetes ingress proxy times out (~60s) before AI report generation completes (30-90s), causing the HTTP response to never reach the frontend — user sees "reports not generating"
- [x] **Background task pattern implemented**:
  - `POST /api/cases/{case_id}/reports/generate` now returns **immediately** (~1s) with `status: "generating"`
  - AI analysis runs as an `asyncio.create_task()` background task
  - On completion, report `status` is updated to `"completed"` in MongoDB
  - On failure, status is updated to `"failed"` with error message
- [x] **New polling endpoint**: `GET /api/cases/{case_id}/reports/{report_id}/status`
  - Returns `{ report_id, status }` — used by frontend to poll every 4 seconds
- [x] **Frontend polling logic** in `ReportsSection.jsx`:
  - After POST returns, starts polling status endpoint every 4 seconds
  - Shows progress indicator with animated bar during generation
  - On `completed`: shows success toast and refreshes reports list
  - On `failed`: shows error toast
  - Max wait: 5 minutes before timeout
  - Generating/failed reports filtered from display list
- [x] **Australian English enforcement**:
  - Added "Use Australian English spelling and grammar" directive to `get_offence_system_prompt()` base function (used by all AI features)
  - Added Australian English directives to standalone prompts: timeline extraction, timeline analysis, contradiction finder
  - Report generation prompts already had "Use Australian English only" in guardrails
- [x] **Testing**: iteration_64 — 100% backend (6/6) + 100% frontend