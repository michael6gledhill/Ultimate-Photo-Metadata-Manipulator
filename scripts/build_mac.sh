#!/usr/bin/env bash
set -euo pipefail

# macOS build script for PhotoMetadataManipulator
# - Supports arch selection: current, x86_64, arm64, universal2 (PyInstaller 5.6+)
# - Checks Xcode CLT and license (needed for lipo and some toolchains)
# - Ensures icon exists
# - Uses .spec when present, otherwise falls back to CLI args

APP_NAME="PhotoMetadataManipulator"
ICON_FILE="logo.icns"
ENTRYPOINT="src/main.py"
SPEC_FILE="PhotoMetadataManipulator.spec"

# Accept TARGET_ARCH via env or -a/--arch flag
TARGET_ARCH="${TARGET_ARCH:-current}"
while [[ ${1-} ]]; do
  case "$1" in
    -a|--arch)
      TARGET_ARCH="${2:-current}"; shift 2 ;;
    -h|--help)
      cat <<EOF
Usage: $(basename "$0") [--arch current|x86_64|arm64|universal2]
Env:   TARGET_ARCH=current|x86_64|arm64|universal2
Other env: DEBUG_BUILD=1, VERBOSE=1, DIST_DIR=dist
EOF
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Resolve project root from this script's location and run from there
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

DIST_DIR="${DIST_DIR:-dist}"

echo "==> Checking Xcode license (required for mac builds)..."
if ! /usr/bin/xcrun --version >/dev/null 2>&1; then
  echo "xcrun not found. Please install Command Line Tools: xcode-select --install" >&2
  exit 1
fi

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

echo "==> Checking PyInstaller..."
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

# Hidden imports: always include local modules, plus optional external ones
HIDDEN_ARGS=(--hidden-import metadata_handler --hidden-import templates)
while read -r mod; do
  [[ -z "$mod" ]] && continue
  HIDDEN_ARGS+=(--hidden-import "$mod")
done < <(python3 - <<'PY'
import importlib.util as u
mods = ['piexif','libxmp']
print('\n'.join([m for m in mods if u.find_spec(m) is not None]))
PY
)

# Add src to module search paths so PyInstaller can find local modules
PATHS_ARGS=(--paths src)

# Optional verbose logging (avoid unbound array under set -u)
: "${VERBOSE:=0}"
LOG_LEVEL=()
if [[ "$VERBOSE" == "1" ]]; then
  LOG_LEVEL=(--log-level DEBUG)
fi

# Target architecture handling (requires PyInstaller supporting --target-arch)
ARCH_ARGS=()
case "$TARGET_ARCH" in
  current) : ;; # no extra args
  x86_64|arm64|universal2)
    ARCH_ARGS=(--target-arch "$TARGET_ARCH") ;;
  *) echo "Unknown TARGET_ARCH: $TARGET_ARCH (use current|x86_64|arm64|universal2)" >&2; exit 2 ;;
esac

# ONEFILE support: set ONEFILE=1 env to build a single-file executable inside the .app
ONEFILE_FLAG=()
if [[ "${ONEFILE:-0}" == "1" ]]; then
  ONEFILE_FLAG=(--onefile)
  echo "==> Onefile mode enabled"
fi

# Use spec if available; otherwise fall back to CLI with ENTRYPOINT
mkdir -p "$DIST_DIR"
OUT_DIR="$DIST_DIR/$TARGET_ARCH"
mkdir -p "$OUT_DIR"

echo "==> Building for arch: $TARGET_ARCH -> $OUT_DIR"

# Force CLI build to avoid spec conflicts with arch/onefile and to prevent universal2 issues
# The .spec has target_arch=None which PyInstaller interprets as universal2, but wxPython binaries are single-arch
USE_SPEC=0

if [[ $USE_SPEC -eq 1 ]]; then
  pyinstaller \
    --noconfirm \
    --clean \
    --distpath "$OUT_DIR" \
    --workpath "build-$TARGET_ARCH" \
    ${ARCH_ARGS:+"${ARCH_ARGS[@]}"} \
    ${LOG_LEVEL:+"${LOG_LEVEL[@]}"} \
    "$SPEC_FILE"
else
  pyinstaller \
    --noconfirm \
    --clean \
    --distpath "$OUT_DIR" \
    --workpath "build-$TARGET_ARCH" \
    --name "$APP_NAME" \
    $WINDOW_FLAG \
    "${ICON_ARG[@]}" \
    "${HIDDEN_ARGS[@]}" \
    "${PATHS_ARGS[@]}" \
    ${ARCH_ARGS:+"${ARCH_ARGS[@]}"} \
    ${LOG_LEVEL:+"${LOG_LEVEL[@]}"} \
    ${ONEFILE_FLAG:+"${ONEFILE_FLAG[@]}"} \
    "$ENTRYPOINT"
fi

echo "==> Build complete. Inspect $OUT_DIR and build-$TARGET_ARCH folders"
if [[ -d "$OUT_DIR/${APP_NAME}.app" ]]; then
  echo "App bundle: $OUT_DIR/${APP_NAME}.app"
elif [[ -f "$OUT_DIR/${APP_NAME}" ]]; then
  echo "Console binary: $OUT_DIR/${APP_NAME}"
else
  echo "No app or binary found in $OUT_DIR. Enable VERBOSE=1 to see detailed logs."
fi
echo "Run binary directly for logs: $OUT_DIR/${APP_NAME}.app/Contents/MacOS/${APP_NAME}"
echo "Or rerun with DEBUG_BUILD=1 to keep console open."
