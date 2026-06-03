"""
Minimal Drag-and-Drop Spike for TK Lesson Planner (Idea 1 - Playful Pathway)
Framework: PySide6 (Qt)

Goal: Replicate the core experience with high fidelity for direct comparison
against the tkinterdnd2 version.

Features implemented:
- Colorful ActivityCards (domain-coded)
- Draggable from left library
- Droppable into vertical timeline slots
- Visual feedback on hover / drop
- Drag data carried via MIME
- Clean Qt-native drag & drop (no external dnd libs)
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QMimeData, QSize
from PySide6.QtGui import QDrag, QColor, QPalette

# ---- Domain colors (pastel teacher-friendly) ----
DOMAIN_COLORS = {
    "Social-Emotional": "#FFCCE1",
    "Language": "#CCE5FF",
    "Mathematics": "#CCFFCC",
    "Science": "#FFFFCC",
    "Physical": "#FFCC99",
    "Arts": "#E0CCFF",
    "Approaches": "#CCCCCC",
}

SEED_ACTIVITIES = [
    {"id": "a1", "title": "Morning Greeting Circle", "domain": "Social-Emotional", "minutes": 10},
    {"id": "a2", "title": "Block Building Challenge", "domain": "Mathematics", "minutes": 20},
    {"id": "a3", "title": "Outdoor Running Games", "domain": "Physical", "minutes": 15},
    {"id": "a4", "title": "Story Time with Puppets", "domain": "Language", "minutes": 12},
    {"id": "a5", "title": "Sensory Bin Exploration", "domain": "Science", "minutes": 18},
    {"id": "a6", "title": "Finger Painting at Art Table", "domain": "Arts", "minutes": 15},
    {"id": "a7", "title": "Free Choice Centers", "domain": "Approaches", "minutes": 25},
]


class ActivityCard(QFrame):
    """A draggable colorful activity card."""
    def __init__(self, activity):
        super().__init__()
        self.activity = activity
        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        color = DOMAIN_COLORS.get(activity["domain"], "#EEEEEE")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px solid #333;
                border-radius: 8px;
            }}
            QLabel {{
                background-color: transparent;
                color: #111;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        # Title (big and bold)
        title = QLabel(activity["title"])
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 13pt; font-weight: bold;")
        layout.addWidget(title)

        # Bottom info line
        info = QLabel(f"{activity['domain']}  •  {activity['minutes']} min")
        info.setStyleSheet("font-size: 9pt;")
        layout.addWidget(info)

        self.setAcceptDrops(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            # Carry just the activity ID as plain text (simple and robust)
            mime.setText(self.activity["id"])
            drag.setMimeData(mime)

            # Optional: give a visual drag pixmap (simple rectangle for now)
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            drag.exec(Qt.MoveAction)


class DroppableSlot(QFrame):
    """A timeline slot that accepts drops."""
    def __init__(self, index: int, on_drop_callback):
        super().__init__()
        self.index = index
        self.on_drop_callback = on_drop_callback

        self.setFixedHeight(52)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #F5F5F5; border: 1px dashed #aaa;")

        self.label = QLabel("Drop activity here →")
        self.label.setStyleSheet("color: #888; font-style: italic; font-size: 9pt;")
        self.label.setAlignment(Qt.AlignCenter)

        lay = QVBoxLayout(self)
        lay.addWidget(self.label)
        lay.setContentsMargins(4, 4, 4, 4)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            self.setStyleSheet("background-color: #D0FFD0; border: 2px solid #0A0;")
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("background-color: #F5F5F5; border: 1px dashed #aaa;")

    def dropEvent(self, event):
        activity_id = event.mimeData().text().strip()
        self.setStyleSheet("background-color: #FFFACD; border: 2px solid #CC0;")  # yellow flash
        print(f"[PySide6] Dropped activity_id={activity_id} into slot {self.index}")

        # Call the parent callback so the timeline actually receives the card
        self.on_drop_callback(self.index, activity_id)

        # Reset style after a short delay
        from PySide6.QtCore import QTimer
        QTimer.singleShot(450, self._reset_style)

        event.acceptProposedAction()

    def _reset_style(self):
        self.setStyleSheet("background-color: #F5F5F5; border: 1px dashed #aaa;")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TK Pathway Spike — PySide6 (Qt) Version")
        self.setGeometry(200, 100, 860, 560)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # ===== LEFT: Activity Library =====
        lib_container = QWidget()
        lib_layout = QVBoxLayout(lib_container)
        lib_layout.setSpacing(6)

        lib_title = QLabel("📚 ACTIVITY LIBRARY")
        lib_title.setStyleSheet("font-weight: bold; font-size: 12pt; color: #2c3e50;")
        lib_layout.addWidget(lib_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        lib_inner = QWidget()
        lib_vbox = QVBoxLayout(lib_inner)
        lib_vbox.setSpacing(5)
        lib_vbox.setContentsMargins(4, 4, 4, 4)

        for act in SEED_ACTIVITIES:
            card = ActivityCard(act)
            lib_vbox.addWidget(card)

        lib_vbox.addStretch()
        scroll.setWidget(lib_inner)
        lib_layout.addWidget(scroll, 1)

        main_layout.addWidget(lib_container, 0)

        # ===== CENTER: Timeline =====
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setSpacing(4)

        timeline_title = QLabel("🕒 DAILY TIMELINE  (drag cards from left)")
        timeline_title.setStyleSheet("font-weight: bold; font-size: 12pt; color: #2c3e50;")
        timeline_layout.addWidget(timeline_title)

        self.timeline_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_widget)
        self.timeline_layout.setSpacing(3)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)

        self.slots = []
        for i in range(8):
            slot = DroppableSlot(i, self.on_activity_dropped)
            self.timeline_layout.addWidget(slot)
            self.slots.append(slot)

        timeline_layout.addWidget(self.timeline_widget, 1)

        main_layout.addWidget(timeline_container, 1)

        # ===== RIGHT: Instructions =====
        side = QWidget()
        side.setFixedWidth(210)
        side_layout = QVBoxLayout(side)

        instructions_title = QLabel("HOW TO TEST THIS SPIKE")
        instructions_title.setStyleSheet("font-weight: bold; font-size: 10pt;")
        side_layout.addWidget(instructions_title)

        instructions = (
            "1. Click and drag any ActivityCard\n"
            "   from the left library.\n\n"
            "2. Drag over a timeline slot.\n"
            "   • Green highlight = ready to drop\n\n"
            "3. Release the mouse.\n\n"
            "4. Watch terminal + yellow flash\n"
            "   on successful drop.\n\n"
            "5. Drop multiple cards to see\n"
            "   how they stack visually.\n\n"
            "This is a focused comparison spike.\n"
            "Full reorder logic in real app."
        )

        instr_label = QLabel(instructions)
        instr_label.setWordWrap(True)
        instr_label.setStyleSheet("font-size: 9pt; line-height: 1.25;")
        side_layout.addWidget(instr_label)
        side_layout.addStretch()

        main_layout.addWidget(side, 0)

        # Bottom note
        self.status = QLabel("PySide6 drag & drop spike ready. Try dragging!")
        self.status.setStyleSheet("color: #555; font-size: 8pt; font-style: italic;")
        timeline_layout.addWidget(self.status)

    def on_activity_dropped(self, slot_index: int, activity_id: str):
        """Callback from a DroppableSlot when something is dropped."""
        act = next((a for a in SEED_ACTIVITIES if a["id"] == activity_id), None)
        if not act:
            return

        # Create a new visual card and insert it right after the slot
        new_card = ActivityCard(act)

        # Simple placement: insert after the slot
        slot = self.slots[slot_index]
        idx_in_layout = self.timeline_layout.indexOf(slot)
        self.timeline_layout.insertWidget(idx_in_layout + 1, new_card)

        self.status.setText(f"✓ Dropped '{act['title']}' into position {slot_index + 1}")
        self.status.setStyleSheet("color: #006400; font-weight: bold; font-size: 9pt;")

        # Clear status after a few seconds
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2800, lambda: self.status.setText("Ready for more drags...") or
                                       self.status.setStyleSheet("color: #555; font-size: 8pt; font-style: italic;"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")   # Clean look on all platforms including Wine

    win = MainWindow()
    win.show()

    print("=== pySide6 Drag & Drop SPIKE ===")
    print("Drag cards from left → drop into timeline slots.")
    print("Watch green hover highlight and console output.")
    sys.exit(app.exec())