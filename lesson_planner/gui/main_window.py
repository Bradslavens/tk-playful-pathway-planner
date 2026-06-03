"""Main application window — three-panel layout."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar
)
from PySide6.QtCore import Qt

from lesson_planner.models.daily_schedule import DailySchedule
from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.gui.activity_library_panel import ActivityLibraryPanel
from lesson_planner.gui.timeline_panel import TimelinePanel
from lesson_planner.gui.inspector_panel import InspectorPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._library = ActivityLibrary()
        self._schedule = DailySchedule(name="My Day")
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Playful Pathway Planner")
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

        # Left — activity library
        self._library_panel = ActivityLibraryPanel(self._library)
        splitter.addWidget(self._library_panel)

        # Center — timeline
        self._timeline_panel = TimelinePanel(self._schedule, self._library)
        self._timeline_panel.schedule_changed.connect(self._on_schedule_changed)
        splitter.addWidget(self._timeline_panel)

        # Right — inspector
        self._inspector_panel = InspectorPanel()
        splitter.addWidget(self._inspector_panel)

        splitter.setStretchFactor(0, 0)   # library: fixed
        splitter.setStretchFactor(1, 1)   # timeline: expands
        splitter.setStretchFactor(2, 0)   # inspector: fixed
        splitter.setSizes([260, 600, 220])

        root.addWidget(splitter)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Welcome! Drag activities from the library into your schedule.")

    def _on_schedule_changed(self):
        count = len(self._schedule.blocks)
        total = self._schedule.total_minutes
        h, m = divmod(total, 60)
        if count == 0:
            self._status.showMessage("Schedule is empty. Drag activities from the left to get started.")
        elif h:
            self._status.showMessage(f"{count} activities scheduled  •  {h}h {m}min total")
        else:
            self._status.showMessage(f"{count} activities scheduled  •  {total} min total")
