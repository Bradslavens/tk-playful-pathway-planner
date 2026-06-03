"""Main application window — three-panel layout."""
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence

from lesson_planner.models.daily_schedule import DailySchedule
from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.data.schedule_io import save_schedule, load_schedule, FILE_EXTENSION
from lesson_planner.export.pdf_export import export_pdf
from lesson_planner.gui.activity_library_panel import ActivityLibraryPanel
from lesson_planner.gui.timeline_panel import TimelinePanel
from lesson_planner.gui.inspector_panel import InspectorPanel

_FILTER = f"Pathway schedules (*{FILE_EXTENSION});;All files (*)"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._library = ActivityLibrary()
        self._schedule = DailySchedule(name="My Day")
        self._current_path: Optional[Path] = None
        self._dirty = False
        self._build_ui()
        self._build_menu()

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._update_title()
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet("QSplitter::handle { background: #ddd; }")

        self._library_panel = ActivityLibraryPanel(self._library)
        splitter.addWidget(self._library_panel)

        self._timeline_panel = TimelinePanel(self._schedule, self._library)
        self._timeline_panel.schedule_changed.connect(self._on_schedule_changed)
        splitter.addWidget(self._timeline_panel)

        self._inspector_panel = InspectorPanel()
        splitter.addWidget(self._inspector_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([260, 600, 220])

        root.addWidget(splitter)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Welcome! Drag activities from the library into your schedule.")

    def _build_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        new_act = QAction("&New Schedule", self)
        new_act.setShortcut(QKeySequence.New)
        new_act.triggered.connect(self._on_new)
        file_menu.addAction(new_act)

        file_menu.addSeparator()

        open_act = QAction("&Open…", self)
        open_act.setShortcut(QKeySequence.Open)
        open_act.triggered.connect(self._on_open)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        self._save_act = QAction("&Save", self)
        self._save_act.setShortcut(QKeySequence.Save)
        self._save_act.triggered.connect(self._on_save)
        file_menu.addAction(self._save_act)

        save_as_act = QAction("Save &As…", self)
        save_as_act.setShortcut(QKeySequence.SaveAs)
        save_as_act.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_act)

        file_menu.addSeparator()

        export_act = QAction("Export &PDF…", self)
        export_act.setShortcut("Ctrl+P")
        export_act.triggered.connect(self._on_export_pdf)
        file_menu.addAction(export_act)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

    # ── Title bar ────────────────────────────────────────────────────────────

    def _update_title(self):
        name = self._schedule.name if hasattr(self, "_schedule") else "My Day"
        dirty = "● " if self._dirty else ""
        path_part = f" — {self._current_path.name}" if self._current_path else ""
        self.setWindowTitle(f"{dirty}Playful Pathway Planner{path_part} [{name}]")

    # ── File menu actions ────────────────────────────────────────────────────

    def _on_new(self):
        if not self._confirm_discard():
            return
        self._schedule = DailySchedule(name="My Day")
        self._current_path = None
        self._dirty = False
        self._timeline_panel.replace_schedule(self._schedule)
        self._update_title()
        self._status.showMessage("New schedule created.")

    def _on_open(self):
        if not self._confirm_discard():
            return
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Open Schedule", str(Path.home()), _FILTER
        )
        if not path_str:
            return
        path = Path(path_str)
        try:
            self._schedule = load_schedule(path, self._library)
        except Exception as e:
            QMessageBox.critical(self, "Could not open file", str(e))
            return
        self._current_path = path
        self._dirty = False
        self._timeline_panel.replace_schedule(self._schedule)
        self._update_title()
        self._status.showMessage(f"Opened: {path.name}")

    def _on_save(self):
        if self._current_path is None:
            self._on_save_as()
        else:
            self._write(self._current_path)

    def _on_save_as(self):
        default = str(
            (self._current_path or Path.home() / f"{self._schedule.name}{FILE_EXTENSION}")
        )
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Save Schedule As", default, _FILTER
        )
        if not path_str:
            return
        path = Path(path_str)
        if path.suffix != FILE_EXTENSION:
            path = path.with_suffix(FILE_EXTENSION)
        self._write(path)
        self._current_path = path

    def _on_export_pdf(self):
        if self._schedule.is_empty():
            QMessageBox.information(
                self, "Nothing to export",
                "Add some activities to your schedule before exporting."
            )
            return
        default = str(Path.home() / f"{self._schedule.name}.pdf")
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", default, "PDF files (*.pdf)"
        )
        if not path_str:
            return
        path = Path(path_str)
        if path.suffix.lower() != ".pdf":
            path = path.with_suffix(".pdf")
        try:
            export_pdf(self._schedule, path)
        except Exception as e:
            QMessageBox.critical(self, "Export failed", str(e))
            return
        self._status.showMessage(f"PDF exported: {path.name}")

    def _write(self, path: Path):
        try:
            save_schedule(self._schedule, path)
        except Exception as e:
            QMessageBox.critical(self, "Could not save file", str(e))
            return
        self._dirty = False
        self._update_title()
        self._status.showMessage(f"Saved: {path.name}")

    # ── Unsaved-changes guard ────────────────────────────────────────────────

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        reply = QMessageBox.question(
            self,
            "Unsaved changes",
            "You have unsaved changes. Discard them?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )
        if reply == QMessageBox.Save:
            self._on_save()
            return not self._dirty  # if save succeeded, dirty is now False
        return reply == QMessageBox.Discard

    def closeEvent(self, event):
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()

    # ── Schedule change signal ───────────────────────────────────────────────

    def _on_schedule_changed(self):
        self._dirty = True
        self._update_title()

        count = len(self._schedule.blocks)
        total = self._schedule.total_minutes
        h, m = divmod(total, 60)
        if count == 0:
            self._status.showMessage("Schedule is empty. Drag activities from the left to get started.")
        elif h:
            self._status.showMessage(f"{count} activities scheduled  •  {h}h {m}min total")
        else:
            self._status.showMessage(f"{count} activities scheduled  •  {total} min total")
