# Appeal Case Manager — PRD

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free, Paid), Barrister View, and PayID integration.

## UI/UX Rules
- Forced light mode globally. High contrast only. No dark mode.
- Australian spelling (analyse, organise, barrister, defence)
- White backgrounds, black body text, coloured headings
- All reports: third-person only. No "we/us/our/you/your".
- All reports: "Created and Designed by Deb King" header + bold legal disclaimer footer
- Tables: scrollable on mobile, white text on dark headers

## Tech Stack
React + Tailwind + Shadcn UI / FastAPI + MongoDB / OpenAI GPT-4o via Emergent LLM Key / Emergent Google Auth

## Report Tiers & Pricing
| Tier | Price | Sections | Target Words | Passes | Words/Ground |
|---|---|---|---|---|---|
| Quick Summary | FREE | 7 | 2,000-3,000 | 1 | Preview only |
| Full Detailed | $150 AUD | 15 | 15,000-20,000 | 5 | 800+ |
| Extensive Log | $200 AUD | 20 | 25,000-35,000 | 7 | 1,200+ |
| Barrister View | LOCKED | Synthesis | N/A | N/A | N/A |

Barrister View unlocks only after all 3 standard reports are generated.

## What's Been Implemented

### Session 1 (Prior)
- Full CRUD for cases, documents, reports
- AI-powered grounds identification
- 3 report tiers + Barrister View
- Dark mode fully removed from 30+ pages
- Mobile table scrolling, print/PDF styling
- Report language sanitisation, branding, disclaimers

### Session 2 (26 Mar 2026)
- Generate Report Modal redesigned with coloured icons, feature lists, Barrister View option (locked)
- Generating indicator redesigned with progress steps
- Strength Rating colours: Strong=RED, Moderate=BLUE
- Documents Tab: Extract Text and OCR Scan buttons removed
- Progress Analysis: backend field name fixed (strength_rating → strength)

### Session 3 (26 Mar 2026 — Current)
- **Full Detailed report prompts completely rewritten**: 5 passes, each with section-specific word minimums (4000-6000 words/pass), explicit ground coverage requirements, anti-laziness rules
- **Extensive Log report prompts completely rewritten**: 7 passes, each with section-specific word minimums, 1200+ words per ground, 9 content requirements per ground
- **PDF export fixed**: Table rendering crash fixed, error handling added, numbered lists handled, markdown links converted
- **Partial saving**: Each LLM pass saves to DB immediately, server restart recovers content
- **Expansion step removed** for full_detailed/extensive_log (multi-pass already produces enough)
- **"we/us/our" catch-all**: 30+ additional patterns added to strip function
- **Broken markdown links**: `<Search NSW Court...>` pattern stripped
- **Barrister View button removed** from all 3 report views
- **Case info moved INTO coloured header box** for all reports + print preview
- **Table header text forced WHITE** with inline styles on th elements
- **Sentence truncation fixed**: Life sentence detection, 120-char limit
- **FAQ category headers**: Replaced broken Unsplash images with clean coloured backgrounds
- **FAQ "Still have questions?"**: Blue themed buttons, flex-wrap on mobile
- **Landing page pricing**: Barrister View added, word counts updated to match actual targets
- **Top Appeal Grounds numbering**: All 6 items have unique coloured circles
- **Footer links**: Explicit visited:text-slate-700 to prevent blue visited links
- **How It Works page**: Fake mockup images removed, Barrister View added to pricing, descriptions updated
- **"we/our" language purged** from FAQ, Statistics, Lawyer Directory, Appeal Statistics, How It Works pages
- **Legal Resources**: Profession Bodies text size reduced
- **Comparison table word counts updated**: Full Detailed 15k-20k, Extensive Log 25k-35k, Grounds 800+/1200+

## Prioritised Backlog

### P0
- None currently

### P1
- Backend refactoring (decompose server.py — >5000 lines)
- Native mobile app build (Capacitor configured)

### P2
- Real-time collaboration/chat
- Case sharing between registered users
- Replace How It Works mockup images with actual app screenshots (when real case data available)
