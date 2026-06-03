# Playful Pathway Planner

**Status: PAUSED** (as of June 1, 2026)

A Windows desktop GUI tool for transitional kindergarten teachers to visually plan daily schedules using intuitive drag-and-drop for ages 3–5.

## Current State
- ✅ Framework decided: **PySide6 (Qt for Python)**
- ✅ Seed data created (16 TK-appropriate activities)
- ✅ Technology spike complete (Tkinter rejected; PySide6 proved reliable when built with Windows Python inside Wine)
- ⏸️ Phase 0 (Foundation) ~80% complete
- ⏸️ Phase 1 (Core models + TDD) **not started**

## When Resuming
Start here:
1. Main plan: `.hermes/plans/2026-06-01_105141-tk-playful-pathway-planner-implementation.md`
2. Framework decision + build instructions: `docs/02-tech-stack-decision.md`
3. Wine/PySide6 build recipe that worked: `docs/wine-pyside6-build-notes.md`
4. Current project status: `docs/03-project-status.md`

## Development Notes
- Primary dev: Linux + Wine testing
- Packaging: Build .exe inside Wine using Windows Python 3.11 + PyInstaller
- Target: Single-file Windows .exe for teachers

**This project is on hold at the user's request. Do not resume development until explicitly told to continue.**

## Next planned work (when unpaused)
- Finish wireframes (Task 0.4)
- Begin strict TDD on domain models (Phase 1)

---

Maintained by Link (Bradley Slavens)  
Paused: June 1, 2026