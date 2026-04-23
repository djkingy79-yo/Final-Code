#!/bin/bash
# Criminal Law Appeal Management - Mobile App Build Script
# Run this script to build iOS and Android apps

echo "🚀 Criminal Law Appeal Management - Mobile Build"
echo "======================================"

# Step 1: Build the React app
echo ""
echo "📦 Step 1: Building React app..."
cd /app/frontend
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
