"""Center panel — the daily timeline where activities are scheduled."""
from datetime import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy, QTimeEdit, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QMimeData, QTime
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from lesson_planner.models.daily_schedule import DailySchedule
from lesson_planner.models.activity import Activity
from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.gui.widgets.library_card import MIME_TYPE
from lesson_planner.gui.widgets.timeline_card import TimelineCard, MIME_TYPE_TIMELINE


def _fmt_time(t: time) -> str:
    hour = t.hour % 12 or 12
    suffix = "AM" if t.hour < 12 else "PM"
    return f"{hour}:{t.minute:02d}{suffix}"


class DropZone(QFrame):
    """Thin horizontal bar that appears between cards as a drop target."""
    dropped_from_library = Signal(str, int)    # activity_id, insert_index
    dropped_from_timeline = Signal(int, int)   # from_index, to_index

    def __init__(self, insert_index: int, parent=None):
        super().__init__(parent)
        self.insert_index = insert_index
        self.setFixedHeight(12)
        self.setAcceptDrops(True)
        self._idle_style()

    def _idle_style(self):
        self.setStyleSheet("background: transparent; border: none;")

    def _hover_style(self):
        self.setStyleSheet(
            "background: #A8D8EA; border: 2px dashed #5AA0C0; border-radius: 4px;"
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(MIME_TYPE) or event.mimeData().hasFormat(MIME_TYPE_TIMELINE):
            self._hover_style()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._idle_style()

    def dropEvent(self, event: QDropEvent):
        self._idle_style()
        mime = event.mimeData()
        if mime.hasFormat(MIME_TYPE):
            activity_id = mime.data(MIME_TYPE).data().decode()
            self.dropped_from_library.emit(activity_id, self.insert_index)
        elif mime.hasFormat(MIME_TYPE_TIMELINE):
            from_index = int(mime.data(MIME_TYPE_TIMELINE).data().decode())
            self.dropped_from_timeline.emit(from_index, self.insert_index)
        event.acceptProposedAction()


class TimelinePanel(QWidget):
    schedule_changed = Signal()

    def __init__(self, schedule: DailySchedule, library: ActivityLibrary, parent=None):
        super().__init__(parent)
        self._schedule = schedule
        self._library = library
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Header row
        header_row = QHBoxLayout()
        header = QLabel("🕒  Daily Schedule")
        header.setStyleSheet(
            "font-size: 13pt; font-weight: bold; color: #2c3e50; padding: 4px 0;"
        )
        header_row.addWidget(header)
        header_row.addStretch()

        # Start time picker
        start_lbl = QLabel("Starts:")
        start_lbl.setStyleSheet("font-size: 9pt; color: #555;")
        header_row.addWidget(start_lbl)

        self._start_edit = QTimeEdit()
        self._start_edit.setDisplayFormat("h:mm AP")
        t = self._schedule.start_time
        self._start_edit.setTime(QTime(t.hour, t.minute))
        self._start_edit.timeChanged.connect(self._on_start_time_changed)
        header_row.addWidget(self._start_edit)

        layout.addLayout(header_row)

        # Total time bar
        self._total_label = QLabel()
        self._total_label.setStyleSheet(
            "font-size: 9pt; color: #555; padding: 2px 0;"
        )
        layout.addWidget(self._total_label)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setSpacing(0)
        self._content_layout.setContentsMargins(0, 0, 4, 0)

        scroll.setWidget(self._content)
        layout.addWidget(scroll, stretch=1)

    def _on_start_time_changed(self, qt: QTime):
        self._schedule.start_time = time(qt.hour(), qt.minute())
        self._refresh()

    # ── Public refresh ───────────────────────────────────────────────────────
    def _refresh(self):
        # takeAt only removes from the layout; setParent(None) removes from the
        # widget tree so orphaned children don't remain visible on top of new ones.
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        blocks = self._schedule.blocks

        if not blocks:
            empty = QLabel("Drag activities here to build your day →")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                "color: #aaa; font-size: 11pt; font-style: italic; padding: 40px;"
            )
            self._content_layout.addWidget(empty)
            self._content_layout.addStretch()
            self._total_label.setText("No activities yet — drag some in!")
            return

        # Interleave DropZones and TimelineCards
        for i, block in enumerate(blocks):
            drop_zone = DropZone(insert_index=i)
            drop_zone.dropped_from_library.connect(self._on_library_drop)
            drop_zone.dropped_from_timeline.connect(self._on_timeline_reorder)
            self._content_layout.addWidget(drop_zone)

            start_t = self._schedule.block_start_time(i)
            card = TimelineCard(block, index=i, start_label=_fmt_time(start_t))
            card.remove_requested.connect(self._on_remove)
            card.move_requested.connect(self._on_timeline_reorder)
            self._content_layout.addWidget(card)

        # Final drop zone after the last card
        last_zone = DropZone(insert_index=len(blocks))
        last_zone.dropped_from_library.connect(self._on_library_drop)
        last_zone.dropped_from_timeline.connect(self._on_timeline_reorder)
        self._content_layout.addWidget(last_zone)

        self._content_layout.addStretch()

        total = self._schedule.total_minutes
        hours, mins = divmod(total, 60)
        if hours:
            self._total_label.setText(f"Total: {hours}h {mins}min  ({len(blocks)} activities)")
        else:
            self._total_label.setText(f"Total: {total} min  ({len(blocks)} activities)")

        self.schedule_changed.emit()

    # ── Slot handlers ────────────────────────────────────────────────────────
    def _on_library_drop(self, activity_id: str, insert_index: int):
        activity = self._library.by_id(activity_id)
        if activity:
            self._schedule.add_activity(activity, at_index=insert_index)
            self._refresh()

    def _on_remove(self, index: int):
        self._schedule.remove_block(index)
        self._refresh()

    def _on_timeline_reorder(self, from_index: int, to_index: int):
        # Clamp to_index: after removing from_index, valid range shrinks by one
        max_to = len(self._schedule.blocks) - 1
        clamped = min(to_index, max_to)
        if from_index != clamped:
            self._schedule.move_block(from_index, clamped)
        self._refresh()
