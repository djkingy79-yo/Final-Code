#!/bin/bash
# Appeal Case Manager — Mobile App Build Script (iOS + Android via Capacitor)
# Bundle ID: com.debking.criminalappeals
# App Name:  Appeal Case Manager
# ---------------------------------------------------------------------------
# Usage:  ./build-mobile.sh        — run from anywhere (resolves frontend root
#                                    from this script's own location; no
#                                    hardcoded /app paths).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Appeal Case Manager — Mobile Build"
echo "======================================"
echo "Working dir: $SCRIPT_DIR"
echo ""

# Step 1: Build the React app
echo "📦 Step 1: Building React app..."
yarn build

if [ $? -ne 0 ]; then
    echo "❌ React build failed!"
    exit 1
fi
echo "✅ React build complete"

# Step 2: Sync with Capacitor
echo ""
echo "📱 Step 2: Syncing with Capacitor..."
npx cap sync

if [ $? -ne 0 ]; then
    echo "❌ Capacitor sync failed!"
    exit 1
fi
echo "✅ Capacitor sync complete"

# Step 3: Check for platforms
echo ""
echo "📋 Step 3: Checking platforms..."

if [ ! -d "ios" ]; then
    echo "📱 Adding iOS platform..."
    npx cap add ios
fi

if [ ! -d "android" ]; then
    echo "🤖 Adding Android platform..."
    npx cap add android
fi

echo "✅ Platforms ready"

# Step 4: Instructions
echo ""
echo "======================================"
echo "🎉 BUILD PREPARATION COMPLETE!"
echo "======================================"
echo ""
echo "App identity (must match App Store Connect listing):"
echo "  Name:      Appeal Case Manager"
echo "  Bundle ID: com.debking.criminalappeals"
echo ""
echo "Next steps:"
echo ""
echo "FOR iOS (requires Mac with Xcode):"
echo "  1. Copy the 'frontend' folder to your Mac"
echo "  2. Run: npx cap open ios"
echo "  3. In Xcode, select your team for signing"
echo "  4. Build and run on device/simulator"
echo "  5. Archive and upload to App Store Connect"
echo ""
echo "FOR Android:"
echo "  1. Run: npx cap open android"
echo "  2. Android Studio will open"
echo "  3. Build > Generate Signed Bundle/APK"
echo "  4. Upload to Google Play Console"
echo ""
echo "======================================"
