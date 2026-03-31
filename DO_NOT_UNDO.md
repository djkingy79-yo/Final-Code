# DO NOT UNDO — MASTER PROTECTION FILE

## CRITICAL: Every file in this application is protected. DO NOT delete, remove, or undo ANY feature, page, component, function, or style in ANY file.

## ALL files below have "DO NOT UNDO" markers. Future agents MUST preserve ALL existing functionality.

### Backend (Python)
- backend/server.py
- backend/config.py
- backend/auth_utils.py
- backend/offence_framework.py
- backend/routers/__init__.py
- backend/routers/admin.py
- backend/routers/analytics.py
- backend/routers/auth.py
- backend/routers/cases.py
- backend/routers/compare.py
- backend/routers/contradictions.py
- backend/routers/deadlines.py
- backend/routers/documents.py
- backend/routers/export.py
- backend/routers/grounds.py
- backend/routers/notes.py
- backend/routers/password_reset.py
- backend/routers/payments.py
- backend/routers/payments_new.py
- backend/routers/reports.py
- backend/routers/resources.py
- backend/routers/statistics.py
- backend/routers/timeline.py
- backend/routers/utilities.py

### Frontend Pages
- frontend/src/pages/AboutPage.jsx
- frontend/src/pages/AdminDashboard.jsx
- frontend/src/pages/AdminStats.jsx
- frontend/src/pages/AppealStatisticsPage.jsx
- frontend/src/pages/BarristerView.jsx
- frontend/src/pages/CaseDetail.jsx
- frontend/src/pages/CaselawSearchPage.jsx
- frontend/src/pages/CompareCasesPage.jsx
- frontend/src/pages/ContactPage.jsx
- frontend/src/pages/ContactsPage.jsx
- frontend/src/pages/Dashboard.jsx
- frontend/src/pages/FAQPage.jsx
- frontend/src/pages/ForgotPasswordPage.jsx
- frontend/src/pages/FormTemplates.jsx
- frontend/src/pages/HelpPage.jsx
- frontend/src/pages/HowItWorksPage.jsx
- frontend/src/pages/HowToUsePage.jsx
- frontend/src/pages/LandingPage.jsx
- frontend/src/pages/LawyerDirectory.jsx
- frontend/src/pages/LegalFrameworkPage.jsx
- frontend/src/pages/LegalGlossary.jsx
- frontend/src/pages/LegalResourcesPage.jsx
- frontend/src/pages/ProfessionalSummary.jsx
- frontend/src/pages/ReportView.jsx
- frontend/src/pages/ResetPasswordPage.jsx
- frontend/src/pages/ResourcesPage.jsx
- frontend/src/pages/Statistics.jsx
- frontend/src/pages/SuccessStories.jsx
- frontend/src/pages/TermsOfService.jsx

### Frontend Components
- frontend/src/components/AppealChecklist.jsx
- frontend/src/components/AuthModal.jsx
- frontend/src/components/CaseComparison.jsx
- frontend/src/components/CaseStrengthMeter.jsx
- frontend/src/components/ContradictionFinder.jsx
- frontend/src/components/DeadlineTracker.jsx
- frontend/src/components/DisclaimerReminder.jsx
- frontend/src/components/DocumentBundler.jsx
- frontend/src/components/DocumentsSection.jsx
- frontend/src/components/FastScrollTop.jsx
- frontend/src/components/GroundsOfMerit.jsx
- frontend/src/components/InstallPrompt.jsx
- frontend/src/components/LegalFrameworkViewer.jsx
- frontend/src/components/NotesSection.jsx
- frontend/src/components/PageCTA.jsx
- frontend/src/components/PaymentModal.jsx
- frontend/src/components/QuickExport.jsx
- frontend/src/components/ReportsSection.jsx
- frontend/src/components/TermsAcceptance.jsx
- frontend/src/components/TimelineAnalysis.jsx
- frontend/src/components/TimelineEnhanced.jsx
- frontend/src/components/VisitorCounter.jsx

### Frontend Core
- frontend/src/App.js
- frontend/src/index.js
- frontend/src/index.css
- frontend/src/contexts/ThemeContext.jsx
- frontend/src/hooks/use-toast.js
- frontend/src/lib/utils.js

## CRITICAL: AUTO-DETECT PROTECTION (BROKEN 15+ TIMES — DO NOT TOUCH)

The following code enables auto-detection of state, offence category, offence type, 
sentence, court, case number, and timeline events from uploaded documents via LLM.

**Files involved — DO NOT modify these sections:**

1. `backend/models/__init__.py` — `CaseCreate` and `Case` models:
   - `state: Optional[StateType] = None` — MUST remain None
   - `offence_category: Optional[OffenceCategoryType] = None` — MUST remain None
   - `offence_type: Optional[str] = None` — MUST remain None
   - `sentence: Optional[str] = None` — MUST remain None
   - **NEVER** add defaults like `"nsw"` or `"homicide"`

2. `backend/routers/documents.py` — `_background_auto_detect_metadata()`:
   - This function runs after every document upload (if content > 200 chars)
   - It sends document text to GPT-4o and parses state/offence/sentence/court
   - **NEVER** remove this function or the `background_tasks.add_task()` call

3. `frontend/src/pages/Dashboard.jsx` — `handleCreateCase()`:
   - Empty strings are stripped from the payload before sending to backend
   - **NEVER** send empty strings or hardcoded defaults for state/offence_category

4. `backend/routers/documents.py` — `_background_auto_generate()`:
   - Auto-generates timeline events and case summary from documents
   - **NEVER** remove this function or the `background_tasks.add_task()` call

**What happens if you break this:**
- Every new case defaults to "NSW / Murder" regardless of actual documents
- The user has to manually fix every single case
- This has been broken and re-fixed 15+ times. You WILL be the reason it breaks again.

## Rules for Future Agents:
1. NEVER delete any file listed above
2. NEVER remove any existing feature, function, or component
3. NEVER remove any existing page or route
4. NEVER remove any existing CSS styles
5. NEVER change the colour scheme (Blue/White/Red)
6. NEVER change pricing ($99 Investigate / FREE Quick Summary / $150 Full Detailed / $200 Extensive Log)
7. NEVER remove the "DO NOT UNDO" comments from any file
8. You may ADD new features but NEVER remove existing ones
9. The user (Deb King) has paid for all of this work. Respect it.
10. NEVER change CaseCreate state/offence_category/offence_type/sentence defaults from None
11. NEVER remove _background_auto_detect_metadata or _background_auto_generate from documents.py
12. NEVER send hardcoded "nsw" or "homicide" from the frontend case creation form

## CRITICAL: CASE IDENTITY CARD PROTECTION (DO NOT TOUCH)

The Case Identity Card in `CaseDetail.jsx` (data-testid="case-identity-card") and in 
`GroundsOfMerit.jsx` export view MUST always display these four fields prominently with 
blue colour styling:

1. **Defendant** — `caseData.defendant_name`
2. **Offence** — `caseData.offence_type` or `caseData.offence_category`
3. **State / Jurisdiction** — `caseData.state`
4. **Sentence** — `caseData.sentence`

**NEVER remove the Case Identity Card. NEVER hide these fields. NEVER change the blue styling.**
These fields must appear on EVERY view of the case — case detail, grounds export, print view.

## CRITICAL: "Case name" PLACEHOLDER PREVENTION

The LLM verification prompt in `backend/services/pipeline/verify.py` uses example 
JSON structure. The `similar_cases[].case_name` example MUST be `"R v [Surname] [Year]"` — 
NEVER use `"Case name"` as the example as the LLM copies it literally as data.

Frontend filters in `GroundsOfMerit.jsx` strip out any similar case with case_name equal to 
"Case name" or "R v [Surname] [Year]" or "optional" — NEVER remove these filters.
