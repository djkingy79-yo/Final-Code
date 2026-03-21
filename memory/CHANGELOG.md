# Appeal Case Manager - Changelog

## 21 March 2026 - Multi-Pass Report Generation Fix (P0)

### Fixed
- **Report word counts now hit targets** - The core issue was reports generating drastically below word count targets
  - Quick Summary: 1,714 words (target 1,500-2,200) - PASS
  - Full Detailed: 5,405 words (target 4,500-6,500) - PASS
  - Extensive Log: 9,684 words (target 7,000-10,000) - PASS

### Root Cause
1. **Missing `max_tokens=16384`** on the report generation LLM calls (`_subprocess_llm`). Only the general `call_llm_with_fallback` had it. The report generator was using default token limits.
2. **Too few passes with too many sections per pass** - Previous 3-pass (Full Detailed) and 4-pass (Extensive Log) approach crammed 5 sections into each pass, resulting in ~1,300 words per pass.

### Changes
- Added `.with_params(max_tokens=16384)` to report generation LLM calls in `_subprocess_llm`
- Restructured Full Detailed from 3-pass to **5-pass** (3 sections per pass)
- Restructured Extensive Log from 4-pass to **7-pass** (3 sections per pass)
- Boosted per-pass minimum word demand to 1,500 words
- Boosted Quick Summary system prompt to demand 1,800+ words
- All 15 sections present in Full Detailed, all 20 sections present in Extensive Log

### Testing
- Test iteration 74: 100% pass rate (19/19 backend tests, frontend verified)
- All three report types verified in ReportView and BarristerView
- No AI placeholder text found in any reports
- Section count verification passed for all tiers
