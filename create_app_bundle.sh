#!/bin/bash
# Create a proper macOS app for easy launching
# Usage: bash create_app_bundle.sh

APP_DIR="/Applications/SEO Crawler.app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/analyze2.py"

# Use the same Python you use in terminal (captures conda/pyenv/homebrew)
PYTHON_BIN="$(command -v python || command -v python3)"
if [ -z "$PYTHON_BIN" ]; then
    echo "❌ No python interpreter found. Install Python 3 first."
    exit 1
fi
echo "Using interpreter: $PYTHON_BIN"

echo "🚀 Creating macOS app bundle..."

# Create app structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create launcher script (uses the resolved Python interpreter)
cat > "$APP_DIR/Contents/MacOS/SEO Crawler" << EOF
#!/bin/bash
SCRIPT_DIR="\$(cd "\$(dirname "\$0")" && pwd)"
cd "\$SCRIPT_DIR/../Resources" || exit 1
export PYTHONPATH="\${PYTHONPATH:-}"
exec "$PYTHON_BIN" "\$SCRIPT_DIR/../Resources/analyze2.py" "\$@"
EOF

chmod +x "$APP_DIR/Contents/MacOS/SEO Crawler"

# Copy script
cp "$SCRIPT_PATH" "$APP_DIR/Contents/Resources/"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>SEO Crawler</string>
    <key>CFBundleIdentifier</key>
    <string>com.seo-crawler.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>SEO Crawler Pro</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>SEO Crawler Pro © 2026</string>
    <key>NSMainNibFile</key>
    <string></string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

echo "✅ App created at: $APP_DIR"
echo ""
echo "🎯 You can now:"
echo "  1. Find 'SEO Crawler Pro' in /Applications"
echo "  2. Add it to Dock for quick access"
echo "  3. Spotlight search: Cmd+Space, type 'SEO'"
