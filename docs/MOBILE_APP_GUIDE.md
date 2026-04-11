# Criminal Appeal AI - Mobile App Build Guide

## Progressive Web App (PWA)
The app is already configured as a PWA. Users can install it from their browser:

### iOS (Safari)
1. Open the app in Safari
2. Tap the Share button at the bottom
3. Scroll down and tap "Add to Home Screen"
4. Tap "Add"

### Android (Chrome)
1. Open the app in Chrome
2. Tap the menu (⋮) in the top right
3. Tap "Add to Home screen" or "Install app"
4. Tap "Add"

---

## App Store Submission with Capacitor

### Prerequisites
- **iOS:** Mac with Xcode 14+, Apple Developer Account ($99/year)
- **Android:** Android Studio, Google Play Developer Account ($25 one-time)

### Step 1: Build the Web App
```bash
cd /app/frontend
yarn build
```

### Step 2: Initialize Capacitor Platforms

#### For iOS:
```bash
npx cap add ios
npx cap sync ios
npx cap open ios
```
This opens Xcode. From there:
1. Select your Team in Signing & Capabilities
2. Update the Bundle Identifier if needed
3. Archive and upload to App Store Connect

#### For Android:
```bash
npx cap add android
npx cap sync android
npx cap open android
```
This opens Android Studio. From there:
1. Build > Generate Signed Bundle / APK
2. Create or use existing keystore
3. Upload AAB file to Google Play Console

### Step 3: App Store Assets Required

#### iOS (App Store Connect)
- Screenshots: 6.5" (1284x2778), 5.5" (1242x2208)
- App Icon: 1024x1024 (already generated)
- Description, keywords, privacy policy URL

#### Android (Google Play Console)
- Screenshots: Phone, 7" tablet, 10" tablet
- Feature graphic: 1024x500
- Hi-res icon: 512x512 (already generated)
- Description, privacy policy URL

### Step 4: Privacy Policy
Create a privacy policy page and host it. Required fields:
- What data you collect (email via Google login)
- How you use the data (case management)
- Third-party services (Google Auth, OpenAI)
- Data retention and deletion policy

### Updating the App
After making changes:
```bash
yarn build
npx cap sync
```
Then rebuild in Xcode/Android Studio and submit update.

---

## App Configuration

### Bundle IDs
- iOS: `com.debking.criminalappealai`
- Android: `com.debking.criminalappealai`

### App Name
"Criminal Appeal AI"

### Version
Update version in:
- `package.json`
- Xcode (iOS)
- `build.gradle` (Android)

---

## Support
For issues with mobile builds, contact Emergent support or refer to:
- Capacitor docs: https://capacitorjs.com/docs
- iOS submission: https://developer.apple.com/app-store/submitting/
- Android submission: https://developer.android.com/distribute/console
