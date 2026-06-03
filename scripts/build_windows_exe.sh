#!/usr/bin/env bash
# Build a Windows .exe for Playful Pathway Planner using Windows Python inside Wine.
#
# Prerequisites (already set up on this machine):
#   - Wine installed  (wine --version)
#   - WINEPREFIX=$HOME/wineprefixes/winpython contains:
#       C:/Program Files/Python311/python.exe  (Python 3.11.9)
#       PySide6 6.11.1, PyInstaller 6.20.0    (pip install'd)
#
# Usage:
#   cd ~/tk-playful-pathway-planner
#   bash scripts/build_windows_exe.sh
#
# Output:
#   dist_windows/Playful Pathway Planner.exe

set -euo pipefail

WINEPREFIX="${WINEPREFIX:-$HOME/wineprefixes/winpython}"
WIN_PYTHON="C:/Program Files/Python311/python.exe"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WINE_APP_DIR="C:/app_src"
WINE_APP_PATH="$WINEPREFIX/drive_c/app_src"
DIST_DIR="$PROJECT_ROOT/dist_windows"

export WINEPREFIX
export WINEDEBUG="-all"   # suppress Wine debug noise

echo "=== Playful Pathway Planner — Windows build ==="
echo "Project root : $PROJECT_ROOT"
echo "Wine prefix  : $WINEPREFIX"
echo ""

# ── Step 1: Copy source into Wine filesystem ──────────────────────────────────
echo "[1/4] Copying source into Wine prefix..."
rm -rf "$WINE_APP_PATH"
mkdir -p "$WINE_APP_PATH"

rsync -a --exclude='.venv*' \
         --exclude='__pycache__' \
         --exclude='*.pyc' \
         --exclude='.git' \
         --exclude='dist' \
         --exclude='dist_windows' \
         --exclude='build' \
         --exclude='spikes' \
         --exclude='tests' \
         --exclude='scripts' \
         "$PROJECT_ROOT/" "$WINE_APP_PATH/"

echo "    Done."

# ── Step 2: Run PyInstaller inside Wine ───────────────────────────────────────
echo "[2/4] Running PyInstaller inside Wine (this takes a few minutes)..."
wine "$WIN_PYTHON" -m PyInstaller \
    --distpath "$WINE_APP_DIR/dist" \
    --workpath "$WINE_APP_DIR/build" \
    --noconfirm \
    "$WINE_APP_DIR/Playful_Pathway_Planner.spec"

echo "    PyInstaller finished."

# ── Step 3: Copy .exe to project dist_windows/ ───────────────────────────────
echo "[3/4] Copying .exe to $DIST_DIR ..."
mkdir -p "$DIST_DIR"
cp "$WINE_APP_PATH/dist/Playful Pathway Planner.exe" "$DIST_DIR/"

# ── Step 4: Report ───────────────────────────────────────────────────────────
EXE_PATH="$DIST_DIR/Playful Pathway Planner.exe"
EXE_MB=$(du -m "$EXE_PATH" | cut -f1)
echo "[4/4] Build complete!"
echo ""
echo "    Output : $EXE_PATH"
echo "    Size   : ${EXE_MB} MB"
echo ""
echo "To test under Wine:"
echo "    WINEPREFIX=$WINEPREFIX wine \"$EXE_PATH\""
