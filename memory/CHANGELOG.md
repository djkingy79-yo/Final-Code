# Appeal Case Manager - Changelog

## 21 March 2026 - Report Quality Overhaul (P0)

### Fixed (Round 2 - based on user screenshots)
- **Removed hardcoded aggressive boilerplate** — "RELIEF OPTIONS — ORDERS SOUGHT" and "IF THE COURT IS AGAINST YOU — Pivot Strategy" was generic text appended identically to every aggressive report. Now removed entirely.
- **Fixed frontend parser** — ReportView was splitting on every `###` and `**bold**` sub-heading, creating 55+ sections in the TOC. Now only splits on `## N.` main section headings → correct 20 sections.
- **Fixed BarristerView parser** — Same issue: removed catch-all bold/### patterns that created excessive section splits.
- **Improved formatting rules** — AI prompts now enforce flowing paragraphs instead of `**bold**` sub-headings and thin bullet points. Ground analysis must be 300+ words of continuous prose.
- **Content hierarchy enforced** — Full Detailed explicitly builds on Quick Summary. Extensive Log explicitly builds on Full Detailed. No cross-tier repetition.

### All 6 Reports Regenerated
| Report | Mode | Words | Sections | Status |
|---|---|---|---|---|
| Quick Summary | Standard | 1,391 | 7 | CLOSE |
| Quick Summary | Aggressive | 1,779 | 7 | PASS |
| Full Detailed | Standard | 5,638 | 15 | PASS |
| Full Detailed | Aggressive | 6,309 | 15 | PASS |
| Extensive Log | Standard | 9,345 | 20 | PASS |
| Extensive Log | Aggressive | 8,390 | 20 | PASS |

### Testing
- Iteration 74: Multi-pass generation verified
- Iteration 75: All 6 reports content + frontend verified
- Visual verification: TOC shows 20 sections (not 55+), no boilerplate, flowing paragraphs

## Earlier Changes
- Multi-pass architecture: 5-pass (Full Detailed), 7-pass (Extensive Log)
- max_tokens=16384 on report LLM calls
- Australian English audit
- Tier comparison toggle on landing page
- AI sentence extraction regex fix
- cases.py router extraction
