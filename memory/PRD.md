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
- Landing, report, and barrister-content polish updates (AU spelling pass, dropdown/footer-link alignment, upgraded barrister showcase messaging, and extensive-report barrister dossier requirements) are logged in `CHANGELOG.md` (latest session).
- Verification status: `iteration_36.json` (feature/content pass) + backend regression iteration 39 (ready).
- AU-English enforcement pass completed across key user-facing strings; endpoint contracts retained where API naming uses legacy `/analyze` path segments.
- Added cross-page AU-English proofreading sweep (FAQ, Statistics, Compare Cases, Case Detail labels, Form Templates, Landing glossary copy) with regression checks passing.
- Performance hotfix shipped for lag during grounds investigation/report generation: bounded AI context budgets + faster grounds models + clearer long-run UX feedback.
- Legal directory and appeal statistics readability overhaul delivered: merged legal resources/contacts flow, state-ordered filtering, clearer advice-help descriptions, and reorganised statistics hierarchy with prominent appeal-rate spotlight.
- Legal directory further simplified into state-focused default mode with national support included, reducing first-load clutter while retaining all listings.
- Added dedicated `/how-it-works` page with process flow, report pricing, and a direct Start Case CTA while preserving all existing tutorial content on `/how-to-use`.
- Tightened overall presentation: success stories moved to compact 3-column card layout with heading-above-comment format, and landing navigation/footer/resource sections updated to reflect merged pages and new flow.
- Continued polish: glossary now supports compact/expanded reading density (compact default) and landing now includes section-level back-to-top controls for long-scroll usability.
- Visibility pass completed: landing nav uses direct links (no desktop dropdown dependency), stats critical content is always visible, and headings on stats/how-it-works are centred for clearer flow.
- Report generation reliability hotfix completed: adaptive model fallback, normalised admin unlock checks, and guaranteed aggressive options section appended at report bottom when enabled.
- Added historical report embedding on Report View via new `/api/reports/embedded-legacy` endpoint so strongest prior reports are visible in-app and not lost.

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

## Technical Debt (Current)
- `server.py` remains monolithic and should be modularized into focused routers/services.