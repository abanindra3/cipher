#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.local.jarvis-cipher.plist"

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.local.jarvis-cipher</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PROJECT_DIR}/.venv/bin/jarvis</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${PROJECT_DIR}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
  <key>StandardOutPath</key>
  <string>${PROJECT_DIR}/logs/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${PROJECT_DIR}/logs/launchd.err.log</string>
</dict>
</plist>
PLIST

mkdir -p "$PROJECT_DIR/logs"
launchctl unload "$PLIST" >/dev/null 2>&1 || true
launchctl load "$PLIST"

echo "JARVIS will start at login. LaunchAgent: $PLIST"
