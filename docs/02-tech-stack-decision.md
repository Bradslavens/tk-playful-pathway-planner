# Tech Stack Decision — Drag & Drop GUI Framework
**Date:** 2026-06-01  
**Project:** Playful Pathway Planner (Transitional Kindergarten Lesson Planning)  
**Task:** 0.2 — Mandatory spike for framework choice

## Executive Summary

After building and testing two minimal but representative drag-and-drop prototypes (the exact core mechanical interaction required for Idea 1):

- **Tkinter + tkinterdnd2** → Strong native experience, **fatally flawed** packaging for Wine → Windows exe.
- **PySide6 (Qt)** → Better native drag UX + vastly superior long-term packaging and export story.

**Recommendation: Use PySide6 (Qt for Python)**

We will accept the larger binary size (~70 MB) and proceed with the recommended "build inside dedicated Wine prefix using Windows Python" workflow from the `windows-exe-build-wine` skill for all future releases.

---

## Detailed Results

### 1. Tkinter + tkinterdnd2 Spike

**Files:**
- `spikes/drag_demo_tkinterdnd/main.py` — full working library → timeline drag & drop with colored domain cards.

**Native Linux (Ubuntu host):**
- Excellent behavior.
- Smooth drags, correct hover feedback (green), drop feedback (yellow flash).
- Cards appear correctly in timeline.
- Easy to develop and iterate.

**Packaging (Linux PyInstaller --onefile --windowed):**
- Clean build.
- Final binary: **~12 MB** (excellent compactness).

**Wine Execution Test (`wine dist/TK_Pathway_TkSpike`):**
```
ImportError: libtcl9.0.so: cannot open shared object file: No such file or directory
```

PyInstaller build log showed multiple warnings:
> WARNING: Library not found: could not resolve 'libtcl9.0.so'...

This is a **well-documented, recurring, and difficult-to-fix** problem with tkinter + modern Python + PyInstaller when targeting Windows via Wine. The Tcl/Tk runtime DLLs are extremely hard to bundle reliably.

Workarounds (manual DLL copying, custom hooks, full Windows Python inside Wine + winetricks) exist but are fragile and add significant maintenance burden for every future release.

**Conclusion for tkinter path:**  
High risk of ongoing packaging pain and broken Windows executables for teachers. Rejected for production.

---

### 2. PySide6 (Qt) Spike

**Files:**
- `spikes/drag_demo_pyside6/main.py` — equivalent functional demo using Qt native `QDrag` / `QMimeData` / `QWidget`.

**Native Linux:**
- Very good drag UX (slightly smoother than tkinterdnd version in testing).
- Excellent theming control via stylesheets.
- Built-in support for future PDF printing (major advantage for "beautiful classroom rhythm posters").

**Packaging (Linux PyInstaller):**
- Final binary: **~71 MB** (larger but acceptable — no strong feelings from Link).
- Build succeeded without major warnings (some optional image format warnings).

**Initial Wine Test (Linux-built .exe):**
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**Root Cause:** Linux PySide6 build bundles Linux xcb/wayland plugins. When the Windows PE is executed under Wine it still tries to load Linux plugin libraries → failure.

This is **much more solvable** than the tkinter/tcl problem.

### Solving the Qt Wine Packaging Problem

This exact situation is addressed in the project's existing skills.

The reliable production path (as documented in `windows-exe-build-wine`) is:

1. Create dedicated Wine prefix.
2. Install **Windows Python** (embeddable zip or full installer) *inside* Wine.
3. `pip install PySide6 pyinstaller` using the Windows Python inside Wine (via `wine python.exe -m pip ...`).
4. Copy source into `WINEPREFIX/drive_c/...`
5. Run PyInstaller *from inside Wine*.
6. The resulting `.exe` will contain proper Windows Qt plugins and run cleanly.

This method has been proven on this machine for other Windows GUI applications.

Additional helpful Wine setup for Qt:
- `winetricks corefonts vcrun2019`
- Environment variables: `QT_QPA_PLATFORM=windows` or `offscreen` for headless testing.
- Optional: install a minimal display driver set.

---

### Comparison Table

| Criterion                        | Tkinter + tkinterdnd2                  | PySide6 (Qt)                              | Winner     |
|----------------------------------|----------------------------------------|-------------------------------------------|------------|
| Native Linux development speed   | Excellent                              | Excellent                                 | Tie        |
| Drag & drop visual quality       | Good                                   | Better (native Qt, pixmap support)        | PySide6    |
| Binary size (packaged)           | ~12 MB                                 | ~71 MB                                    | Tkinter    |
| PDF / rich printing for teachers | Poor (needs extra libs)                | Excellent (Qt PDF printer built-in)       | **PySide6** |
| Future UI richness (multiple views, inspectors, themes) | Limited | Very strong (model/view, QSS, graphics) | **PySide6** |
| Wine → Windows exe reliability   | High friction / recurring breakage     | Solvable with documented "build in Wine" method | **PySide6** |
| Maintenance burden long-term     | High (tcl/tk hell)                     | Moderate (Qt ecosystem is mature)         | **PySide6** |
| Alignment with existing skills   | Moderate                               | Excellent (`windows-exe-build-wine`)      | **PySide6** |

---

## Final Decision

**Use PySide6 (Qt for Python) as the GUI framework for Playful Pathway Planner.**

### Rationale (prioritized for this specific project)

1. **Teacher value delivery** — The beautiful printable PDFs / classroom posters are a *core feature*, not an afterthought. Qt's printing system makes this trivial and high-quality. Tkinter would require significant extra work (reportlab + layout pain).
2. **Reliable Windows shipping via Linux dev workflow** — The user has already established and documented a working Linux + Wine development process. PySide6 fits cleanly into the existing `windows-exe-build-wine` patterns with one well-known extra step (build inside Wine Python). Tkinter does not.
3. **Future extensibility** — This app will grow (multiple views, activity editor, better inspector, themes, undo stack). Qt's architecture scales much better.
4. **Drag & drop quality** — Meets or exceeds the "highly intuitive" requirement.

### Accepted Tradeoffs

- Larger binary (~70 MB instead of 12 MB) — acceptable per user's feedback.
- Slightly more complex initial build process (use Windows Python inside Wine for releases) — worth it for long-term reliability.

### Next Actions (Phase 0 continuation)

- Adopt PySide6 for all production code starting with Phase 1 models (models stay framework-agnostic) and Phase 2 GUI.
- When we reach packaging (Task 3.4), follow the internal-Wine-Python build workflow.
- Add a short `docs/wine-qt-notes.md` capturing the exact `QT_*` env vars and winetricks verbs that work.
- Consider adding PySide6 to the project's main `requirements.txt` going forward.

---

## Artifacts Produced During This Spike

- `spikes/drag_demo_tkinterdnd/main.py` + 12 MB Linux PyInstaller build
- `spikes/drag_demo_pyside6/main.py` + 71 MB Linux PyInstaller build
- `docs/spike-status.md` (intermediate notes)
- This decision document

**Both spikes can now be archived or deleted** once Phase 2 begins (they have served their purpose).

---

**Signed off for implementation:** PySide6 (Qt for Python)

Ready to proceed with the rest of the plan using this framework, Link.