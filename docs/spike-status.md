# Drag & Drop Framework Spike — Live Status (2026-06-01)

## Tkinter + tkinterdnd2 Side (STRIKE AGAINST)

**Linux Native Behavior (Code Review + Timeout Test):**
- Code starts cleanly.
- Full ActivityCard + droppable TimelineSlot implementation complete.
- Proper domain-colored cards, drag data passing, visual hover feedback (green on enter, yellow on drop).
- Timeline accepts drops and displays cards.

**Packaging Result:**
- PyInstaller --onefile --windowed succeeded → 12 MB single binary.
- `dist/TK_Pathway_TkSpike` produced.

**Wine Test (Critical Failure):**
```bash
wine dist/TK_Pathway_TkSpike
```
Result:
```
ImportError: libtcl9.0.so: cannot open shared object file: No such file or directory
```

This was predicted by PyInstaller build-time warnings:
> WARNING: Library not found: could not resolve 'libtcl9.0.so'

This is a **well-known and recurring pain point** with tkinter + PyInstaller on Wine/Linux cross-compilation. Common workarounds are heavy (winetricks, manual DLL copying, custom hooks, or switching to a full Windows Python inside Wine prefix). They add significant friction and fragility for a teacher-facing tool that must "just work" on school Windows machines.

**Conclusion for this framework (at this stage):**
Strong native Linux experience.
**Unacceptable Wine packaging experience** for our primary target deployment method (Linux development → Wine validation → Windows .exe for schools).

---

## Next: PySide6 Side

Proceeding immediately with PySide6 equivalent demo for direct comparison. Expected advantages:
- Qt has excellent, well-maintained PyInstaller hooks.
- Much better cross-platform binary story (especially under Wine).
- Native `QDrag` / `QMimeData` / `QWidget` drag-and-drop is generally smoother and more customizable than tkinterdnd2.
- Native PDF printing (important for the "beautiful classroom poster" feature).

Will report results in next update.