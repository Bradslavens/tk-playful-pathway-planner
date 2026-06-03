"""Activity card as it appears in the timeline — shows start time, has remove button."""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag

from lesson_planner.models.schedule_block import ScheduleBlock
from lesson_planner.gui.colors import bg_for_domain, border_for_domain
from lesson_planner.gui.widgets.library_card import (
    MIME_TYPE as MIME_TYPE_LIBRARY,
    activity_id_from_mime,
)

MIME_TYPE_TIMELINE = "application/x-timeline-index"


class TimelineCard(QFrame):
    remove_requested = Signal(int)
    move_requested = Signal(int, int)        # from_index, to_index
    library_drop_requested = Signal(str, int)  # activity_id, insert_index

    def __init__(self, block: ScheduleBlock, index: int, start_label: str, parent=None):
        super().__init__(parent)
        self.block = block
        self.index = index
        self._start_label = start_label
        self._build_ui()
        self.setAcceptDrops(True)

    def _build_ui(self):
        activity = self.block.activity
        bg = bg_for_domain(activity.domain)
        border = border_for_domain(activity.domain)

        self.setStyleSheet(f"""
            QFrame#TimelineCard {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; color: #111; }}
            QPushButton {{
                background: transparent;
                border: none;
                color: #888;
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: #cc2222; }}
        """)
        self.setObjectName("TimelineCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.OpenHandCursor)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(10, 6, 6, 6)
        outer.setSpacing(8)

        # Time badge
        time_badge = QLabel(self._start_label)
        time_badge.setFixedWidth(44)
        time_badge.setStyleSheet("font-size: 9pt; font-weight: bold; color: #555;")
        time_badge.setAlignment(Qt.AlignTop | Qt.AlignRight)
        outer.addWidget(time_badge)

        # Vertical divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFixedWidth(2)
        divider.setStyleSheet(f"background: {border};")
        outer.addWidget(divider)

        # Title + meta
        content = QVBoxLayout()
        content.setSpacing(2)
        content.setContentsMargins(0, 0, 0, 0)

        icon_text = f"{activity.icon}  {activity.title}" if activity.icon else activity.title
        title_lbl = QLabel(icon_text)
        title_lbl.setStyleSheet("font-size: 11pt; font-weight: bold;")
        title_lbl.setWordWrap(True)
        content.addWidget(title_lbl)

        meta_lbl = QLabel(f"{activity.domain}  •  {self.block.duration} min")
        meta_lbl.setStyleSheet("font-size: 8pt; color: #444;")
        content.addWidget(meta_lbl)

        outer.addLayout(content, stretch=1)

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setToolTip("Remove from schedule")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.index))
        outer.addWidget(remove_btn, alignment=Qt.AlignTop)

    # ── Drag to reorder ──────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(MIME_TYPE_TIMELINE, str(self.index).encode())
        drag.setMimeData(mime)
        drag.setPixmap(self.grab())
        drag.setHotSpot(event.pos())
        drag.exec(Qt.MoveAction)

    # ── Accept drops: reorder from timeline, or insert from library ───────────
    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasFormat(MIME_TYPE_TIMELINE) or mime.hasFormat(MIME_TYPE_LIBRARY):
            event.acceptProposedAction()

    def _drop_after(self, event) -> bool:
        """True if the drop landed on the lower half of the card."""
        return event.position().y() > self.height() / 2

    def dropEvent(self, event):
        mime = event.mimeData()
        activity_id = activity_id_from_mime(mime)
        if activity_id is not None:
            insert_index = self.index + 1 if self._drop_after(event) else self.index
            self.library_drop_requested.emit(activity_id, insert_index)
        elif mime.hasFormat(MIME_TYPE_TIMELINE):
            from_index = int(mime.data(MIME_TYPE_TIMELINE).data().decode())
            to_index = self.index + 1 if self._drop_after(event) else self.index
            if from_index != to_index:
                self.move_requested.emit(from_index, to_index)
        event.acceptProposedAction()
