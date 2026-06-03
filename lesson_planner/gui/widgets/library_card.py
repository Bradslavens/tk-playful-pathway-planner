"""Draggable activity card shown in the left library panel."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

from lesson_planner.models.activity import Activity
from lesson_planner.gui.colors import bg_for_domain, border_for_domain

MIME_TYPE = "application/x-activity-id"


def make_activity_mime(activity_id: str) -> QMimeData:
    """Build the drag payload carried from a library card to the timeline.

    Extracted so the drag/drop contract can be unit-tested without a real
    mouse-driven QDrag.exec() loop.
    """
    mime = QMimeData()
    mime.setData(MIME_TYPE, activity_id.encode())
    return mime


def activity_id_from_mime(mime: QMimeData) -> str | None:
    """Inverse of make_activity_mime; None if the payload isn't a library drag."""
    if not mime.hasFormat(MIME_TYPE):
        return None
    return bytes(mime.data(MIME_TYPE).data()).decode()


class LibraryCard(QFrame):
    def __init__(self, activity: Activity, parent=None):
        super().__init__(parent)
        self.activity = activity
        self._build_ui()

    def _build_ui(self):
        bg = bg_for_domain(self.activity.domain)
        border = border_for_domain(self.activity.domain)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; color: #111; }}
        """)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setCursor(Qt.OpenHandCursor)
        self.setToolTip(self.activity.description or self.activity.title)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(2)

        icon_title = QLabel(f"{self.activity.icon}  {self.activity.title}" if self.activity.icon else self.activity.title)
        icon_title.setWordWrap(True)
        icon_title.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout.addWidget(icon_title)

        meta = QLabel(f"{self.activity.domain}  •  {self.activity.suggested_minutes} min  •  {self.activity.energy_level} energy")
        meta.setStyleSheet("font-size: 8pt; color: #444;")
        layout.addWidget(meta)

    _drag_start = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.position().toPoint()
            # Accept (don't call super, which would ignore() the press) so this
            # card becomes the mouse grabber and receives the move events that
            # start the drag.
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self._drag_start is None:
            return
        # Wait until the pointer has moved past the platform drag threshold so a
        # plain click doesn't kick off a drag.
        moved = (event.position().toPoint() - self._drag_start).manhattanLength()
        if moved < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        drag.setMimeData(make_activity_mime(self.activity.id))
        drag.setPixmap(self.grab())
        drag.setHotSpot(event.position().toPoint())
        self.setCursor(Qt.ClosedHandCursor)
        drag.exec(Qt.CopyAction)
        self.setCursor(Qt.OpenHandCursor)
        self._drag_start = None
