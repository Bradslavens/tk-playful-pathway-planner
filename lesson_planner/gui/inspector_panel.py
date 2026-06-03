"""Right panel — shows details of the selected/last activity."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

from lesson_planner.models.activity import Activity
from lesson_planner.gui.colors import bg_for_domain, border_for_domain


class InspectorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(190)
        self.setMaximumWidth(240)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header = QLabel("ℹ️  Activity Info")
        header.setStyleSheet(
            "font-size: 13pt; font-weight: bold; color: #2c3e50; padding: 4px 0;"
        )
        layout.addWidget(header)

        self._card = QFrame()
        self._card.setFrameShape(QFrame.StyledPanel)
        self._card.setStyleSheet("background: #f9f9f9; border-radius: 8px; border: 1px solid #ddd;")
        self._card_layout = QVBoxLayout(self._card)
        self._card_layout.setContentsMargins(10, 10, 10, 10)
        self._card_layout.setSpacing(6)
        layout.addWidget(self._card)

        self._placeholder = QLabel("Click an activity\nfor details.")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: #bbb; font-style: italic; font-size: 10pt;")
        self._card_layout.addWidget(self._placeholder)

        layout.addStretch()

    def show_activity(self, activity: Activity):
        while self._card_layout.count():
            item = self._card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        bg = bg_for_domain(activity.domain)
        border = border_for_domain(activity.domain)
        self._card.setStyleSheet(
            f"background: {bg}; border-radius: 8px; border: 2px solid {border};"
        )

        icon_title = QLabel(f"{activity.icon}  {activity.title}" if activity.icon else activity.title)
        icon_title.setWordWrap(True)
        icon_title.setStyleSheet("font-size: 11pt; font-weight: bold; background: transparent;")
        self._card_layout.addWidget(icon_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {border};")
        self._card_layout.addWidget(sep)

        for label, value in [
            ("Domain", activity.domain),
            ("Suggested time", f"{activity.suggested_minutes} min"),
            ("Energy", activity.energy_level.capitalize()),
        ]:
            row = QLabel(f"<b>{label}:</b> {value}")
            row.setWordWrap(True)
            row.setStyleSheet("font-size: 9pt; background: transparent; color: #222;")
            self._card_layout.addWidget(row)

        if activity.description:
            desc = QLabel(activity.description)
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 9pt; color: #444; font-style: italic; background: transparent;")
            self._card_layout.addWidget(desc)

        if activity.materials:
            mat_lbl = QLabel("<b>Materials:</b>")
            mat_lbl.setStyleSheet("font-size: 9pt; background: transparent;")
            self._card_layout.addWidget(mat_lbl)
            mats = QLabel("• " + "\n• ".join(activity.materials))
            mats.setWordWrap(True)
            mats.setStyleSheet("font-size: 9pt; color: #333; background: transparent;")
            self._card_layout.addWidget(mats)

        if activity.adaptations:
            ada_lbl = QLabel("<b>Adaptations:</b>")
            ada_lbl.setStyleSheet("font-size: 9pt; background: transparent;")
            self._card_layout.addWidget(ada_lbl)
            adas = QLabel("• " + "\n• ".join(activity.adaptations))
            adas.setWordWrap(True)
            adas.setStyleSheet("font-size: 9pt; color: #333; background: transparent;")
            self._card_layout.addWidget(adas)

        self._card_layout.addStretch()
