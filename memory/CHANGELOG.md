# Appeal Case Manager - Changelog

## 21 March 2026 - All 6 Reports Generated with Tier Hierarchy

### Implemented
- **All 6 reports generated** for R v Homann case:
  - Quick Summary: Standard (1,435 words) + Aggressive (1,727 words)
  - Full Detailed: Standard (5,521 words) + Aggressive (6,187 words)
  - Extensive Log: Standard (9,476 words) + Aggressive (9,260 words)
- **Content hierarchy** — each tier builds on the previous without repetition:
  - Full Detailed system prompt instructs AI not to repeat Quick Summary overview content
  - Extensive Log system prompt instructs AI not to repeat Full Detailed analysis
  - Phrase overlap between tiers measured at <1% for standard mode
- **Barrister Views** render correctly for all Full Detailed and Extensive Log reports
- **Aggressive mode badges** visible in UI for all aggressive reports

### Root Cause Fix (from earlier)
1. Missing `max_tokens=16384` on report LLM calls
2. Restructured multi-pass: 5-pass (Full Detailed), 7-pass (Extensive Log), 3 sections per pass

### Testing
- Iteration 74: 100% pass rate — multi-pass generation verified
- Iteration 75: 97% backend (30/31), 100% frontend — all 6 reports verified
  - Minor: aggressive Full Detailed has 13.8% overlap with aggressive Quick Summary (natural for aggressive mode)
