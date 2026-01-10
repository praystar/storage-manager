#!/bin/bash
# Native Messaging Host Installer (Chrome / Brave / Chromium / Edge)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST_NAME="com.storage_checker"

PY_HOST="$SCRIPT_DIR/native_host.py"
WRAPPER="$SCRIPT_DIR/native_host.sh"

# ---- sanity checks ----
if [ ! -f "$PY_HOST" ]; then
    echo " native_host.py not found in $SCRIPT_DIR"
    exit 1
fi

# Resolve absolute paths
PY_HOST="$(realpath "$PY_HOST")"
WRAPPER="$(realpath "$WRAPPER" 2>/dev/null || echo "$WRAPPER")"

# ---- create wrapper script ----
cat > "$WRAPPER" <<EOF
#!/bin/bash
exec /usr/bin/python3 "$PY_HOST"
EOF

chmod +x "$WRAPPER"

# ---- get extension ID ----
EXTENSION_ID="$1"
if [ -z "$EXTENSION_ID" ]; then
    echo "Enter your extension ID (from chrome://extensions):"
    read -r EXTENSION_ID
fi

if [ -z "$EXTENSION_ID" ]; then
    echo " Extension ID required"
    exit 1
fi

# ---- create manifest ----
TEMP_MANIFEST="$(mktemp)"
cat > "$TEMP_MANIFEST" <<EOF
{
  "name": "$HOST_NAME",
  "description": "Disk Space Checker Native Host",
  "path": "$WRAPPER",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://$EXTENSION_ID/"
  ]
}
EOF

# ---- install locations ----
install_manifest() {
    local DIR="$1"
    if [ -d "$(dirname "$DIR")" ]; then
        mkdir -p "$DIR"
        cp "$TEMP_MANIFEST" "$DIR/$HOST_NAME.json"
        echo "✓ Installed: $DIR/$HOST_NAME.json"
    fi
}

# Chrome
install_manifest "$HOME/.config/google-chrome/NativeMessagingHosts"

# Chromium
install_manifest "$HOME/.config/chromium/NativeMessagingHosts"

# Snap Chromium
install_manifest "$HOME/snap/chromium/common/.config/chromium/NativeMessagingHosts"

# Brave
install_manifest "$HOME/.config/BraveSoftware/Brave-Browser/NativeMessagingHosts"

# Edge
install_manifest "$HOME/.config/microsoft-edge/NativeMessagingHosts"

rm "$TEMP_MANIFEST"

echo ""
echo "Native messaging host installed successfully!"
echo ""
echo "IMPORTANT:"
echo "• Extension IDs differ per browser"
echo "• Run this script ONCE per browser"
echo "• Restart the browser after install"
echo ""
echo "Debug paths:"
echo "  Chrome:   chrome://extensions-internals"
echo "  Brave:    brave://extensions-internals"
echo "  Edge:     edge://extensions-internals"
