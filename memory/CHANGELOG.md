# Changelog

## 31 March 2026 (Session 2 — continued)
### Case Identity Card (DO_NOT_UNDO Protected)
- Added prominent blue Case Identity Card to CaseDetail.jsx showing Defendant, Offence, State, Sentence in a 2x2 grid with blue border and labels
- Added same card to GroundsOfMerit.jsx export/print view so all printed outputs include case details
- Updated DO_NOT_UNDO.md with explicit protection for Case Identity Card

### Deep Analysis Generation
- Investigate endpoint now generates a 500-800 word deep analysis via LLM after structured verification
- Deep analysis stored in `deep_analysis.full_analysis` AND `analysis` fields on the ground
- Grounds export/print view already renders this via ReactMarkdown

### "Case name" Placeholder Prevention (Permanent Fix)
- Fixed verify.py LLM prompt template: changed example from `"Case name"` to `"R v [Surname] [Year]"` — the LLM was copying the example literally
- Added frontend filters in GroundsOfMerit.jsx to strip out any similar case with case_name = "Case name" / "R v [Surname] [Year]" / "optional"
- Cleaned ALL placeholder similar cases from database (4 fixed across all grounds)
- Updated DO_NOT_UNDO.md with permanent guard against "Case name" placeholder

### ReportView.jsx Cleanup
- Removed duplicate DraftSourceBadge (showed "Drafted from legacy inputs")
- Removed "Pipeline Draft Summary" section (Pipeline issues/Verified issues/Pre-draft activity)
- VerificationBadge now maps draft/unverified to "Generated" in blue across all views

### Database Cleanup
- Updated ALL 52 reports to verification_status: "generated" and draft_source: "pipeline"
- Removed ALL "Case name" placeholder similar cases from grounds_of_merit

## 31 March 2026 (Session 2)
### UI Cleanup — Removed Confusing Pipeline Internals
1. "Draft" badge → "Generated" in blue
2. "Drafted from legacy inputs" REMOVED (DraftSourceBadge returns null)
3. Report Metadata simplified (no more pipeline_issue_count etc.)
4. Review Status widget REMOVED from case detail
5. Pipeline Verification improved feedback ("All issues verified")
6. Font sizes reduced on mobile
7. "UNVERIFIED" badge → "AI-SUGGESTED" in blue

### Bug Fixes (5 Critical)
1. Google Auth Redirect — redirect to /dashboard, SPA navigate()
2. Not Authenticated — logout checks Bearer header
3. Print All enhanced — full ground details, documents, evidence
4. iOS PDF — direct render instead of iframe srcDoc
5. Similar Cases badge — AI-SUGGESTED

## 30 March 2026
- Auto-Detect Permanent Guards with DO_NOT_UNDO
- UI Bug Fixes (React child error, legitimacy panel)
- Verified Case Law Database Integration (Law tab)
- Grounds Over-Generation Fix (capped to 8-10)
- Investigate Duplicate Bug Fix
- Grounds Scoring Fix (stricter legitimacy)
