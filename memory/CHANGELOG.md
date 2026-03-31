# Changelog

## 31 March 2026 (Session 2 — Final)
### Fixes From User Screenshots
1. **Pipeline Verification RESTORED** — Verify Top 3/6 buttons are back on Reports tab.
2. **Duplicate Grounds Cleaned** — Removed 7 duplicate grounds (13 → 6 unique). Added fuzzy keyword matching to prevent future duplicates (>50% word overlap = duplicate).
3. **Offence Capitalised** — "murder" → "Murder" in Report View header. Strips "The" prefix.
4. **Barrister View → Teal** — Header background changed from blue to teal. Action buttons stay blue.
5. **Word Export → Preview** — Word All, Export Word buttons now open in document-preview page instead of downloading .doc files.
6. **ReportView.jsx cleaned** — Removed duplicate DraftSourceBadge, Pipeline Draft Summary, Pre-Draft Pipeline Activity. "Generated" badge everywhere.
7. **Footer text shrunk** — "Created and Designed by Deb King" made smaller.
8. **Report title font reduced** — text-3xl → text-xl on mobile.

### Deep Analysis Integration
- Investigate endpoint generates 500-800 word deep analysis via LLM after structured verification
- Stored in `deep_analysis.full_analysis` AND `analysis` fields
- Shows in grounds export/print view

### "Case name" Placeholder Prevention
- Fixed verify.py LLM prompt template (example was "Case name" → now "R v [Surname] [Year]")
- Frontend filters strip placeholders in GroundsOfMerit.jsx
- All DB placeholders cleaned

### Case Identity Card (DO_NOT_UNDO Protected)
- Prominent blue card on CaseDetail showing Defendant, Offence, State, Sentence
- Same card in GroundsOfMerit export/print view

### Database Cleanup
- Reports: all 52 set to verification_status "generated", draft_source "pipeline"
- Grounds: 7 duplicates deleted, 4 placeholder similar cases removed

## 30 March 2026
- Auto-Detect Permanent Guards with DO_NOT_UNDO
- Verified Case Law Database Integration (Law tab)
- Grounds Over-Generation Fix (capped to 8-10)
- Investigate Duplicate Bug Fix
- Grounds Scoring Fix (stricter legitimacy)
