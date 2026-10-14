#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
THEME="${1:-black}"
OUTPUT="${2:-presentation-${THEME}.pdf}"
URL="http://localhost:${PORT}/?theme=${THEME}&print-pdf"

CHROME_BIN=""
for bin in google-chrome chromium-browser chromium /usr/bin/chromium /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome "/c/Program Files/Google/Chrome/Application/chrome.exe" "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"; do
  if command -v "$bin" &> /dev/null || [[ -x "$bin" ]]; then
    CHROME_BIN="$bin"
    break
  fi
done

if [[ -z "$CHROME_BIN" ]]; then
  echo "Error: Chromium or Google Chrome was not found in PATH." >&2
  exit 1
fi

echo "Starting preview server on port ${PORT}..."
python3 -m http.server "${PORT}" &
SERVER_PID=$!

trap "kill -9 ${SERVER_PID} 2>/dev/null || taskkill //F //PID ${SERVER_PID} 2>/dev/null || true" EXIT
sleep 1

echo "Exporting PDF with theme '${THEME}' to ${OUTPUT}..."
"$CHROME_BIN" --headless --disable-gpu \
  --print-to-pdf="${OUTPUT}" \
  --print-to-pdf-no-header \
  --enable-background-graphics \
  --window-size=1920,1080 \
  "${URL}"

echo "Done: ${OUTPUT}"
