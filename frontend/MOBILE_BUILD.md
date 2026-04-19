# Appeal Case Manager — Native Mobile Build Guide

Last synced: 19 Apr 2026 — Capacitor v7.6.2 — 12 plugins

The web app is already wrapped for iOS + Android via Capacitor. The React build
is bundled into both native projects with every `npx cap sync` run. You complete
the native build on a Mac (iOS) and any machine with Android Studio (Android).

## Current State

- **Capacitor config**: `frontend/capacitor.config.json`
  - `appId`: `com.debking.criminalappeals`
  - `appName`: Appeal Case Manager
  - `allowNavigation`: `*.emergentagent.com`, `criminallawappealmanagement.com.au`, `*.criminallawappealmanagement.com.au`
- **iOS project**: `frontend/ios/App/App.xcodeproj`
- **Android project**: `frontend/android/`
- **Web build**: `frontend/build/` (also copied to `ios/App/App/public/` and `android/app/src/main/assets/public/`)

## One-Time Setup (already done, re-run whenever web code changes)

```bash
cd /app/frontend
REACT_APP_BACKEND_URL=https://criminal-appeals-au-2.preview.emergentagent.com yarn build
npx cap sync
```

## iOS Build (requires macOS + Xcode 15+)

1. Copy or clone the `frontend/` folder to a Mac.
2. Install CocoaPods if missing: `sudo gem install cocoapods`
3. Open the project: `npx cap open ios`
4. In Xcode:
   - Select signing team (Deb King Apple Developer account).
   - Choose the `App` scheme + a physical device or simulator.
   - Product → Run (⌘R) to test.
5. Archive for App Store:
   - Product → Archive
   - Distribute App → App Store Connect → Upload
6. In App Store Connect:
   - Create a new app with bundle ID `com.debking.criminalappeals`.
   - Attach the uploaded build, complete metadata/screenshots, submit.

## Android Build (any OS with JDK 17 + Android Studio)

1. Install Android Studio Hedgehog or newer; open Android Studio once to let
   it install the SDK + emulator images.
2. Open the project: `npx cap open android` (from `frontend/`)
3. In Android Studio:
   - Let Gradle sync finish.
   - Run on emulator/device (green ▶ button) to test.
4. Release build:
   - Build → Generate Signed Bundle / APK
   - Keystore: `release.keystore` (path configured in `capacitor.config.json`).
     Create if missing with:
     ```bash
     keytool -genkey -v -keystore release.keystore -alias appealcasemanager \
       -keyalg RSA -keysize 2048 -validity 10000
     ```
   - Select **AAB** (Android App Bundle) for Google Play Store upload.
5. Upload the generated `.aab` to Google Play Console under the
   `com.debking.criminalappeals` app.

## Re-Syncing After Web Code Changes

Any time the React code is updated you must re-run:
```bash
cd /app/frontend
yarn build
npx cap sync
```
Then rebuild in Xcode / Android Studio.

## Plugin Inventory (both platforms)
@capacitor/app, camera, device, filesystem, haptics, local-notifications,
network, preferences, push-notifications, share, splash-screen, status-bar.

## Known Gotchas

- **CORS / backend URL**: The app calls `REACT_APP_BACKEND_URL` bundled at
  build time. Must rebuild + sync if you change that env var.
- **Cloudflare cookies**: Session token is stored in `Capacitor Preferences`
  (persistent across app launches) — no cookie issues on native.
- **iOS signing**: Requires an Apple Developer account ($99/yr).
- **Android permissions**: Camera + notifications are requested at runtime
  via Capacitor prompts. No further config needed.
