# Appeal Case Manager - Changelog

## 30 March 2026 — Frontend Hardening Patch (Forensic Barrister Review)

### Summary
Implemented comprehensive frontend hardening patch in 3 phases. Created 6 reusable shared components and patched 9 existing files to display legitimacy scores, verification badges, evidence summaries, assessment notes, and report metadata.

### Components Created
1. **StrengthBadge.jsx**: STRONG/MODERATE/WEAK coloured badge
2. **VerificationBadge.jsx**: Draft/Unverified/Reviewed/Verified status
3. **LegitimacyPanel.jsx**: Legal basis, Evidence support, Appellate viability scores (X/3)
4. **EvidenceSummary.jsx**: Supporting evidence with filename + quote preview
5. **AssessmentNote.jsx**: Reusable disclaimer/assessment note block
6. **ReportMetadataPanel.jsx**: Model, fallback, documents analysed, verification status

### Phase 1 (Highest Credibility Impact)
- **GroundsOfMerit.jsx**: StrengthBadge, VerificationBadge, LegitimacyPanel, EvidenceSummary per ground card + detail dialog
- **CaseStrengthMeter.jsx**: Safe rendering (readinessLevel/readinessScore/assessmentNote), Appeal Preparation Readiness block
- **ReportsSection.jsx**: ReportMetadataPanel + AI-analysis warning per report

### Phase 2 (Misleading Analytics Removal)
- **CaseComparison.jsx**: AssessmentNote at top, insufficient data handling
- **DeadlineTracker.jsx**: Explanatory note, per-deadline jurisdiction/verification/source metadata

### Phase 3 (Professional Defensibility)
- **BarristerView.jsx**: BarristerGroundBlock (per-ground: StrengthBadge, VerificationBadge, LegitimacyPanel, EvidenceSummary, similar_cases), ReportMetadataPanel, AI-analysis footer
- **ReportView.jsx**: VerificationBadge, ReportMetadataPanel, AI-analysis warning
- **CaseDetail.jsx**: Review Status widget (unverified grounds, AI timeline events, draft reports), CaseStrengthMeter on Progress tab
- **CompareCasesPage.jsx**: AssessmentNote, insufficient data handling, 'Platform Pattern Indicators' label

### Text Replacements
- 'Case Strength' → 'Appeal Preparation Readiness'
- 'Success Factors' → 'Platform Pattern Indicators'
- 'Strong Grounds' → 'Higher Preparation Grounds'

### Testing
- Backend: 13/13 tests passed (100%)
- Frontend: 12/12 features verified (100%)
- Iterations: 126 (backend), 127 (frontend)

## 30 March 2026 — Backend Schema Hardening (Forensic Barrister Additive Patches)

### Summary
Completed 7/7 additive backend patches from the forensic barrister review. All patches harden data models, LLM services, and routers with strict provenance tracking, JSON-safe AI calls, and backward-compatible structured data models.

### Changes Applied
1. **models/__init__.py**: Typed submodels (EvidenceItem, LawSection, SimilarCase, LegitimacyScores, ReportMetadata) with ConfigDict(extra='ignore'). Fixed _NormaliserMixin with check_fields=False.
2. **llm_service.py**: call_llm_for_json (strict JSON parsing + retry), call_llm_for_report, call_llm_structured (provider/model fallback with metadata return).
3. **grounds.py**: Compatibility wrappers (_wrap_evidence_items) bridging legacy List[str] to EvidenceItem objects. Legitimacy scores returned per-ground.
4. **deadlines.py**: Ownership hardening (user_id checks), "Case Readiness" framing with assessment_note and assessment_type fields.
5. **compare.py**: Platform pattern framing, disclaimers and assessment_note on all endpoints. Removed pseudo-success language.
6. **timeline.py**: JSON-safe extraction via call_llm_for_json, provenance fields (source_mode, verification_status) on events.
7. **server.py**: Metadata detection via call_llm_for_json, report generation via call_llm_structured, ReportMetadata provenance on all generated reports (models_used, fallback_used, documents_analyzed, verification_status).

### Testing
- Backend: 13/13 tests passed (100%)
- Frontend: Homepage, login, dashboard all verified working
- Backward compatibility: All existing frontend data contracts maintained

## 21 March 2026 - Report Content Quality Overhaul (P0 Final Fix)

### Root Cause
The AI was writing ABOUT the analysis instead of DOING the analysis. Generic consultant-speak like "Delve into aggravating factors" and filler sections like "URGENCY PRIORITY: HELPFUL" were filling up word counts without providing any actual legal analysis.

### Fixes Applied
1. **Added hard anti-pattern guardrails** to the AI system prompt:
   - Explicit examples of WRONG vs RIGHT content (e.g., "Delve into..." vs actually applying s.21A to Homann's specific facts)
   - Banned filler section titles (URGENCY PRIORITY, RELEVANCE, KEY TAKEAWAY)
   - Required every paragraph to reference specific names, dates, section numbers, case citations, or document names
   - Required legislation sections to APPLY provisions to THIS case, not just describe what the Act covers
2. **Removed hardcoded boilerplate** — generic "RELIEF OPTIONS / PIVOT STRATEGY" text removed
3. **Fixed frontend parsers** — ReportView and BarristerView now only split on `## N.` main sections (20 sections, not 55+)
4. **Strengthened per-pass instructions** — each multi-pass chunk demands CASE-SPECIFIC analysis

### Content Quality Verification
- Zero garbage patterns found in new reports ("Delve into", "Leverage legal databases", "URGENCY PRIORITY", "RELEVANCE", "empirical trends", "Collate case law data", "KEY TAKEAWAY" — all CLEAN)
- Section 10 (Statutory Framework) now APPLIES s.18 and s.19A to Homann specifically
- Section 9 (Precedent Matrix) has 15+ real cases with full citations and specific factual parallels
- Section 8 (Evidence Gaps) has specific remediation steps referencing Dr Allnutt

### All 6 Reports Regenerated
| Report | Mode | Words | Sections |
|---|---|---|---|
| Quick Summary | Standard | 1,547 | 7 |
| Quick Summary | Aggressive | 1,386 | 7 |
| Full Detailed | Standard | 5,037 | 15 |
| Full Detailed | Aggressive | 6,028 | 15 |
| Extensive Log | Standard | 8,315 | 20 |
| Extensive Log | Aggressive | 8,271 | 20 |
