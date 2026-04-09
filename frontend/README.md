# Appeal Case Manager — Frontend

React 19 single-page application for the Appeal Case Manager platform.

## Stack

- **React 19** with React Router v7
- **Tailwind CSS 3.4** for styling
- **Shadcn/UI** (40+ Radix UI primitives) in `/src/components/ui/`
- **Sonner** for toast notifications
- **Axios** for API communication
- **Capacitor v7** for native iOS/Android builds
- **React.lazy** code splitting — 26 pages lazy-loaded for faster initial load

## Setup

```bash
# Install dependencies (use yarn, not npm)
yarn install

# Copy and configure environment
cp .env.example .env
# Set REACT_APP_BACKEND_URL to your backend URL

# Start development server (hot reload on port 3000)
yarn start

# Production build
yarn build
```

## Project Structure

```
src/
├── App.js                    # Root — routing, auth state, lazy imports
├── components/
│   ├── ui/                   # Shadcn component library (40+ components)
│   ├── AuthModal.jsx         # Login/register + Google Auth
│   ├── QuickExport.jsx       # Case Export Pack (PDF) + ZIP export
│   ├── ReportTranslator.jsx  # Multi-language translation UI
│   ├── ReportsSection.jsx    # Report tier cards and generation
│   ├── GroundsOfMerit.jsx    # Grounds management and display
│   ├── TimelineEnhanced.jsx  # Case timeline component
│   ├── NotesSection.jsx      # Collaborative notes
│   └── ...
├── pages/
│   ├── LandingPage.jsx       # Public landing (eagerly loaded)
│   ├── Dashboard.jsx         # User dashboard (eagerly loaded)
│   ├── CaseDetail.jsx        # Case view (eagerly loaded)
│   ├── ReportView.jsx        # Report display (lazy)
│   ├── BarristerView.jsx     # Barrister Brief (lazy)
│   └── ... (20+ more pages, all lazy-loaded)
├── contexts/
│   └── ThemeContext.js        # Forced light mode provider
├── utils/
│   ├── auSpelling.js         # Australian English normaliser (80+ replacements)
│   └── exportHtml.js         # Shared HTML export builder
├── native/
│   └── appLifecycle.js       # Capacitor native app lifecycle
└── index.css                 # Global styles, forced light mode overrides
```

## Design Rules

- **Forced light mode** — no dark backgrounds anywhere
- **Colour palette:** Blue/slate/navy only. No amber or brown.
- **Action buttons:** Bright blue (`bg-blue-700`) with white text
- **Fonts:** Crimson Pro (headings), Manrope (body)
- **Australian English** throughout all UI text

## Key Commands

```bash
yarn start          # Dev server (port 3000, hot reload)
yarn build          # Production build
yarn test           # Run tests
npx eslint src/     # Lint all source files
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `REACT_APP_BACKEND_URL` | Backend API URL (e.g. `https://yourdomain.com.au`) |
| `WDS_SOCKET_PORT` | WebSocket port for dev server (default: 443) |

---

**Created and Designed by Debra King** | Appeal Case Manager | Australian Law Only
