# Changelog

## 31 March 2026 (Session 2)
### UI Cleanup — Removed Confusing Pipeline Internals
1. **"Case name" placeholder REMOVED** — Cleaned junk LLM-generated placeholder from MongoDB grounds_of_merit for "Refusal of Judge-Alone Trial" ground.
2. **"Draft" badge → "Generated"** — VerificationBadge now maps draft/unverified to "Generated" in blue. No more yellow "Draft" badges.
3. **"Drafted from legacy inputs" REMOVED** — DraftSourceBadge returns null. No more confusing pipeline source labels.
4. **Report Metadata simplified** — Removed "Pipeline issues considered: 0", "Verified issues considered: 0", "Fallback used: No". Status always shows "Generated" instead of "draft".
5. **Review Status widget REMOVED** — No more "Unverified grounds: 4" confusion on case detail page.
6. **Pipeline Verification improved** — Cleaner text, shows "All issues verified. Ready to generate report." when no unverified issues.
7. **Font sizes reduced on mobile** — Case title text-xl, ground titles text-sm, Barrister section headings text-lg.
8. **"UNVERIFIED" badge → "AI-SUGGESTED"** — Similar cases badge changed from amber to blue with clearer label.

### Bug Fixes (5 Critical from User Screenshots)
1. **Google Auth Redirect (P0)** — Changed redirect URL to `/dashboard`, uses SPA `navigate()` instead of `window.location.replace()`.
2. **"Not Authenticated" (P0)** — Fixed logout to check Bearer header.
3. **Print All (P1)** — Enhanced buildPrintAllHtml with full ground details, documents, evidence.
4. **iOS PDF (P1)** — Direct HTML render for iOS instead of iframe srcDoc.
5. **Similar Cases "UNVERIFIED" (P2)** — Badge text changed.

### Files Modified
- `/app/frontend/src/components/VerificationBadge.jsx`
- `/app/frontend/src/components/ReportsSection.jsx`
- `/app/frontend/src/components/ReportMetadataPanel.jsx`
- `/app/frontend/src/components/GroundsOfMerit.jsx`
- `/app/frontend/src/components/AuthModal.jsx`
- `/app/frontend/src/pages/CaseDetail.jsx`
- `/app/frontend/src/pages/DocumentPreviewPage.jsx`
- `/app/frontend/src/pages/BarristerView.jsx`
- `/app/frontend/src/App.js`
- `/app/frontend/src/utils/exportHtml.js`
- `/app/backend/routers/auth.py`

## 30 March 2026
- Auto-Detect Permanent Guards with DO_NOT_UNDO
- UI Bug Fixes (React child error, legitimacy panel, Dashboard privacy notice)
- Verified Case Law Database Integration (Law tab)
- Grounds Over-Generation Fix (capped to 8-10)
- Investigate Duplicate Bug Fix
- Grounds Scoring Fix (stricter legitimacy)
- Deployment Health Check passed
