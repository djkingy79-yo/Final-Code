# Appeal Case Manager — PRD

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free, Paid), Barrister View, and PayID integration.

## UI/UX Rule
Forced light mode globally. High contrast only. No dark mode toggle. No grey/muted text. Australian spelling. White backgrounds, black body text, coloured headings.

## Tech Stack
React + Tailwind + Shadcn UI / FastAPI + MongoDB / OpenAI GPT-4o via Emergent LLM Key / Emergent Google Auth

## Case Tabs (CORRECT ORDER)
Documents, Timeline, Grounds, Notes, Reports, Legal Framework, Progress — **NO Contradictions tab**

## Report Tiers & Pricing
| Tier | Price | Target Words | Passes |
|---|---|---|---|
| Quick Summary | FREE | 2,000-3,000 | 1 |
| Full Detailed | $150 AUD | 12,000-18,000 | 5 (3 sections/pass, 3000+ words/pass) |
| Extensive Log | $200 AUD | 25,000-35,000 | 7 |
| Barrister View | LOCKED | N/A | Synthesis of all 3 |

Barrister View unlocks only after all 3 standard reports are generated.

## What's Been Implemented (26 Mar 2026)
- Full CRUD for cases, documents, reports
- AI-powered grounds identification (Free + $99 tier)
- 3 report tiers: Quick Summary, Full Detailed, Extensive Log
- Barrister View (unlocks after 3 reports)
- Dark mode toggle removed from ALL 30+ pages
- ALL CSS variables replaced with explicit light-mode colours
- 7 mobile-width (390px) mockup screenshots with real case data for How It Works page
- Mockup tabs corrected: no Contradictions, shows Legal Framework
- Report Snapshot cards deleted from Landing Page
- How It Works FAQ answers reduced to text-xs
- Legal Resources: all text sizes reduced, ResourceCard made compact, intro text deleted, banner removed, Innocence heading made bigger
- LandingPage footer fixed with explicit colours
- PageCTA inline variant fixed for light mode
- SuccessStories footer CTA and Share My Story button fixed
- CaseDetail gradient button replaced with solid blue
- **Report language sanitisation**: "we/us/our" eliminated from AI prompts + post-processing
- **Print/PDF preview rebuilt**: Professional layout matching on-screen view
- **CLIENT PLAIN-ENGLISH BRIEF** prompts updated across all 3 report tiers
- **Extensive Log timeout fix**: Reduced per-pass LLM timeout, partial-save after each pass
- **Progress indicator improved**: Shows contextual messages during generation
- **Report content depth enforced**: Full Detailed target 12k-18k words (increased from 10k-15k), Extensive Log target 25k-35k words
- **ALL grounds enforcement**: Every report prompt now has GROUNDS TO COVER with "MUST INCLUDE ALL"
- **Comparison table**: Added to end of ALL report views and print/PDF
- **Disclaimer with hazard symbol**: Present on all on-screen reports AND print/PDF views
- **Prompt instruction stripping**: Headings cleaned in both backend and frontend
- **Pricing updated**: $150 AUD Full Detailed, $200 AUD Extensive Log
- **BarristerView overhaul**: Header fixed, lock icon, print preview
- **Bold disclaimer on ALL reports**: "NOT LEGAL ADVICE" + "Created and Designed by Deb King"
- **Table overflow fix**: Horizontal scroll on mobile, table-layout:fixed for print only
- **"You/your" language ban**: All pronouns replaced with third-person references

### Implemented This Session (26 Mar 2026 — Session 2)
- **Generate Report Modal Redesign**: Cards now show coloured icons (emerald/blue/purple), feature lists with CheckCircle2, clear pricing badges
- **Barrister View in Modal**: 4th option added to Generate Report dialog, locked with Lock icon until all 3 reports generated, shows Crown icon when unlocked
- **Generating Indicator Redesign**: Blue header bar with progress steps (Reading → Analysing → Writing → Finalising), elapsed timer, progress bar
- **Strength Rating Colour Coding**: "Strong" renders in RED (text-red-600), "Moderate" in BLUE (text-blue-600), "Weak" in orange within ReportView MarkdownBlock
- **Documents Tab Cleanup**: Removed "Extract Text" and "OCR Scan" buttons per user request, only Upload Document remains
- **Progress Analysis Fix**: Backend `strength_rating` → `strength` field name corrected so AI gets actual ground strengths
- **Full Detailed Report Depth**: Increased from 2000→3000 minimum words per pass (5 passes), target range 12k-18k words, stronger differentiation instructions vs free report
- **Consistent Case Law Font Size**: Set `li` font-size to 1.15rem in legal-report CSS

## Prioritised Backlog
### P0
- None

### P1
- Backend refactoring (decompose server.py — >5000 lines)
- Native mobile app build (Capacitor configured)

### P2
- Real-time collaboration/chat
- Case sharing between registered users
