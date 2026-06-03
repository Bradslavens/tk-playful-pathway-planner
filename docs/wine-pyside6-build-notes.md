# Successful PySide6 Wine Build Notes (for Playful Pathway Planner)

**Date:** 2026-06-01  
**Method that worked:** Build the executable *inside* a dedicated Wine prefix using **Windows Python + PySide6 + PyInstaller**.

This is the recommended path going forward (as per the official `windows-exe-build-wine` skill).

---

## Exact Working Recipe

### 1. Create a dedicated Wine prefix (if you don't have one yet)
```bash
export WINEPREFIX=$HOME/wineprefixes/winpython   # or any name you like
wineboot   # initializes the prefix
```

### 2. Install Windows Python 3.11 inside Wine
```bash
# Full installer (recommended for simplicity)
wine msiexec /i https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe \
    /passive PrependPath=1 Include_test=0
```

Wait for it to finish.

### 3. Install PySide6 + PyInstaller using the Windows Python
```bash
export WINEPREFIX=$HOME/wineprefixes/winpython

wine "C:/Program Files/Python311/python.exe" -m pip install --upgrade pip

wine "C:/Program Files/Python311/python.exe" -m pip install \
    PySide6 pyinstaller --only-binary=:all:
```

### 4. Copy your source code into the prefix
```bash
mkdir -p "$WINEPREFIX/drive_c/app_src"
cp -r path/to/your/project/* "$WINEPREFIX/drive_c/app_src/"
```

### 5. Build from inside Wine (this is the key step)
```bash
cd "$WINEPREFIX/drive_c/app_src"

wine "C:/Program Files/Python311/python.exe" -m PyInstaller \
    --onefile \
    --windowed \
    --name "YourAppName" \
    main.py
```

The resulting `.exe` will be at:
```
$WINEPREFIX/drive_c/app_src/dist/YourAppName.exe
```

### 6. Test it
```bash
export WINEPREFIX=$HOME/wineprefixes/winpython

wine drive_c/app_src/dist/YourAppName.exe
```

---

## Results from the June 1 2026 Spike

- **Linux cross-built PySide6 .exe** (71 MB) → Failed with "xcb plugin" error (expected when running Linux Qt libs under Wine).
- **Wine-internal Windows Python build** → Produced a clean **24 MB** Windows .exe that launched without the xcb/tcl/tk errors.

The internal-Wine build is the one that worked.

---

## Helpful Wine Setup for Qt Apps

```bash
winetricks -q corefonts vcrun2019
```

Optional environment tweaks before running:
```bash
export QT_QPA_PLATFORM=windows
# or for headless CI testing:
# export QT_QPA_PLATFORM=offscreen
```

---

## Production Recommendation for Playful Pathway Planner

For all future releases:
- Do development on Linux (fast iteration with native PySide6).
- For **release builds**, always use the "Windows Python inside dedicated Wine prefix" method above.
- Keep the runnable source in the repo; the `.exe` is generated in CI or manually when shipping.
- Document the recommended `WINEPREFIX` path in README.

---

**Reference:**
This spike (Task 0.2) proved that PySide6 is viable and reliable when built the right way.

See also:
- `docs/02-tech-stack-decision.md`
- `skills/windows-exe-build-wine`

This approach will give us the beautiful Qt drag-and-drop experience + reliable Windows distribution for teachers.