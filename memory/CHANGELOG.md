# Changelog

## 31 March 2026
### Bug Fixes (5 Critical Bugs Resolved)
1. **Google Auth Redirect Loop (P0)** — Changed redirect URL from `/auth/callback` to `/dashboard` per Emergent playbook. AuthCallback now uses SPA `navigate()` instead of `window.location.replace()`, passing user data via route state to avoid full page reload.
2. **"Not Authenticated" Errors (P0)** — Tied to Bug 1. Also fixed logout endpoint to check Bearer header (not just cookies) for session cleanup in deployed environment.
3. **Print All Only 2 Sheets (P1)** — Enhanced `buildPrintAllHtml` to include full content: document list, ground details (supporting evidence, law sections, similar cases, deep analysis), full timeline descriptions, notes, and progress analysis. Added `@page` CSS rule for proper A4 pagination.
4. **iOS PDF "Cannot be previewed" (P1)** — DocumentPreviewPage now renders HTML directly via `dangerouslySetInnerHTML` for iOS devices instead of using iframe `srcDoc`. Non-iOS still uses iframe for print isolation.
5. **Similar Cases "UNVERIFIED" (P2)** — Changed badge from "UNVERIFIED" (amber) to "AI-SUGGESTED" (blue) since case references are LLM-generated and cannot be machine-verified.

### Files Modified
- `/app/frontend/src/components/AuthModal.jsx` — redirect URL
- `/app/frontend/src/App.js` — AuthCallback SPA navigation
- `/app/backend/routers/auth.py` — logout Bearer token support
- `/app/frontend/src/pages/CaseDetail.jsx` — buildPrintAllHtml enhancement
- `/app/frontend/src/pages/DocumentPreviewPage.jsx` — iOS direct render
- `/app/frontend/src/components/GroundsOfMerit.jsx` — AI-SUGGESTED badge
- `/app/frontend/src/utils/exportHtml.js` — @page CSS rule

## 30 March 2026
- Auto-Detect Permanent Guards with DO_NOT_UNDO
- UI Bug Fixes (React child error, legitimacy panel, Dashboard privacy notice)
- Verified Case Law Database Integration (Law tab)
- Grounds Over-Generation Fix (capped to 8-10)
- Investigate Duplicate Bug Fix
- Grounds Scoring Fix (stricter legitimacy)
- Deployment Health Check passed
