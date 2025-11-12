#!/usr/bin/env bash
set -euo pipefail

# Simple macOS build script for PhotoMetadataManipulator
# - Checks Xcode license
# - Ensures icon exists
# - Runs PyInstaller

APP_NAME="PhotoMetadataManipulator"
ICON_FILE="logo.icns"
ENTRYPOINT="src/main.py"

# Resolve project root from this script's location and run from there
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==> Checking Xcode license (required for lipo)..."
if ! /usr/bin/xcrun --version >/dev/null 2>&1; then
  echo "xcrun not found. Please install Command Line Tools: xcode-select --install" >&2
  exit 1
fi

# xcodebuild -checkFirstLaunchStatus exits 69 before license acceptance on some systems; fallback to message
if ! /usr/bin/xcodebuild -checkFirstLaunchStatus >/dev/null 2>&1; then
  echo "Xcode license not accepted. Attempting non-interactive accept..."
  if sudo /usr/bin/xcodebuild -license accept; then
    echo "Xcode license accepted."
  else
    echo "Please run: sudo xcodebuild -license accept" >&2
    exit 1
  fi
fi

echo "==> Ensuring icon exists..."
if [[ ! -f "$ICON_FILE" ]]; then
  echo "Icon $ICON_FILE not found. If you have an icon.png, generate one via README instructions. Continuing without custom icon."
  ICON_ARG=()
else
  ICON_ARG=(--icon "$ICON_FILE")
fi

echo "==> Running PyInstaller..."
if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller not found. Install it with: pip3 install pyinstaller" >&2
  exit 1
fi

if [[ ! -f "$ENTRYPOINT" ]]; then
  echo "Entrypoint $ENTRYPOINT not found. Are you in the project root? (Current: $PWD)" >&2
  exit 1
fi

echo "==> Using debug mode? (set DEBUG_BUILD=1 to show console)"
if [[ "${DEBUG_BUILD:-0}" == "1" ]]; then
  WINDOW_FLAG="--console"
  echo "Debug build: console enabled."
else
  WINDOW_FLAG="--windowed"
fi

# Hidden imports sometimes required for PyInstaller to include dynamic modules.
HIDDEN_IMPORTS=(libxmp piexif)
HIDDEN_ARGS=()
for mod in "${HIDDEN_IMPORTS[@]}"; do
  HIDDEN_ARGS+=(--hidden-import "$mod")
done

# Optional verbose logging (avoid unbound array under set -u)
: "${VERBOSE:=0}"
LOG_LEVEL=()
if [[ "$VERBOSE" == "1" ]]; then
  LOG_LEVEL=(--log-level DEBUG)
fi

pyinstaller \
  --noconfirm \
  --clean \
  --distpath "dist" \
  --workpath "build" \
  --name "$APP_NAME" \
  $WINDOW_FLAG \
  "${ICON_ARG[@]}" \
  "${HIDDEN_ARGS[@]}" \
  ${LOG_LEVEL:+"${LOG_LEVEL[@]}"} \
  --add-data "src:src" \
  "$ENTRYPOINT"

echo "==> Build complete. Inspect dist/ and build/ folders"
if [[ -d "dist/${APP_NAME}.app" ]]; then
  echo "App bundle: dist/${APP_NAME}.app"
elif [[ -f "dist/${APP_NAME}" ]]; then
  echo "Console binary: dist/${APP_NAME}"
else
  echo "No app or binary found in dist/. Enable VERBOSE=1 to see detailed logs."
fi
echo "Run binary directly for logs: dist/${APP_NAME}.app/Contents/MacOS/${APP_NAME}"
echo "Or rerun with DEBUG_BUILD=1 to keep console open."
