# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth). Barrister View locked until all 3 standard reports generated/paid.
- **Report Language:** STRICT third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue action buttons.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Payment:** PayID only (djkingy79@gmail.com, NAB). Stripe/PayPal permanently removed.

## Tech Stack
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key (LiteLLM)
- Auth: Emergent Google Auth + JWT
- Email: Resend
- Exports: reportlab (PDF), python-docx (DOCX)
- Mobile: Capacitor 7 (iOS + Android)

## What's Been Implemented

### Core Features
- Full report generation pipeline (4 tiers)
- Document upload & management
- Timeline analysis
- Grounds of merit tracking
- PDF/DOCX export with cover pages, disclaimers, footers
- Barrister View with Issue Matrix attachment
- Google Auth + email/password auth
- PayID payment flow
- DOMPurify XSS sanitisation (with style tag preservation)
- Lawyer Directory with verified links
- Appeal Statistics page
- How It Works tutorial page
- Sentence extraction normalisation across all reports
- Security audit (18-point checklist)
- Export Appeal Package (ZIP with all case materials and templates)
- Pipeline Portfolio Summary on Dashboard

### Native Mobile App (Capacitor) — Feb 2026
- **Camera Document Scanning:** Native camera integration for scanning legal documents, with preview and retake. Gallery picker. Converts to File for upload.
- **Offline Access:** Enhanced service worker with API response caching, static asset caching, offline fallback. Capacitor Preferences for offline data storage (cases, reports, pending notes).
- **Push & Local Notifications:** Schedule deadline reminders, receive push notifications. Falls back to web Notification API.
- **Haptic Feedback:** Tactile feedback on actions (success, error, warning). Light/medium/heavy impact.
- **Share:** Native share sheet for case summaries and exported documents. Falls back to navigator.share or clipboard on web.
- **Biometric Auth:** Face ID (iOS) and fingerprint (Android) permission setup. Info.plist and AndroidManifest configured.
- **App Lifecycle:** Status bar styling, splash screen, Android back button, deep links, app state change handling.
- **Offline Banner:** Shows when device loses connectivity with retry button.
- **iOS & Android Projects Generated:** Both native projects exist at `/app/frontend/ios` and `/app/frontend/android`. Permissions configured for camera, photo library, Face ID, biometrics, notifications, storage.
- **Service Worker v2:** Cache-first for static assets, network-first with cache fallback for API requests, background sync for pending notes, push notification handling.

### Bug Fixes — Feb 2026
- Font size standardisation across all reports, prints, and exports
- PayID email typo fix (gmsil.com → gmail.com)
- Export Appeal Package crash fix (supporting_evidence dict handling)
- Terms of Service font reduction
- Dashboard overview cards enlarged
- Case page heading enlarged

## Building Native Apps

### iOS
1. Open `/app/frontend/ios/App/App.xcworkspace` in Xcode
2. Select your development team in Signing & Capabilities
3. Run on simulator or device

### Android
1. Open `/app/frontend/android` in Android Studio
2. Let Gradle sync
3. Run on emulator or device

### Updating Web Content
```bash
cd /app/frontend
yarn build
npx cap sync
```

## Backlog
- P1: Deploy fixes to production (user must click "Deploy" in Emergent chat)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes section
- P2: Case sharing between registered users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- DOMPurify must use `{ WHOLE_DOCUMENT: true, ADD_TAGS: ['style'] }`
- PDF export blob fallback for iOS must not be modified
- Grounds of merit hard cap: max 2 new per sync
- PayID email must remain djkingy79@gmail.com
- All native calls must be wrapped in isNativePlatform() checks
