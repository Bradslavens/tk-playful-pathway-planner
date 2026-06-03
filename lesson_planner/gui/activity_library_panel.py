"""Left panel — scrollable activity library with domain filter and search."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QScrollArea, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal

from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.models.activity import Activity
from lesson_planner.gui.widgets.library_card import LibraryCard


class ActivityLibraryPanel(QWidget):
    """Emits activity_selected when a card is clicked (for inspector use)."""
    activity_selected = Signal(object)  # Activity

    def __init__(self, library: ActivityLibrary, parent=None):
        super().__init__(parent)
        self._library = library
        self._cards: list[LibraryCard] = []
        self._build_ui()
        self._populate("", "All Domains")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Header
        header = QLabel("📚  Activity Library")
        header.setStyleSheet(
            "font-size: 13pt; font-weight: bold; color: #2c3e50; padding: 4px 0;"
        )
        layout.addWidget(header)

        # Search bar
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search activities…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self._search)

        # Domain filter
        self._domain_combo = QComboBox()
        self._domain_combo.addItem("All Domains")
        for domain in self._library.domains:
            self._domain_combo.addItem(domain)
        self._domain_combo.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self._domain_combo)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setSpacing(5)
        self._cards_layout.setContentsMargins(2, 2, 2, 2)
        self._cards_layout.addStretch()

        scroll.setWidget(self._cards_container)
        layout.addWidget(scroll, stretch=1)

        self.setMinimumWidth(230)
        self.setMaximumWidth(290)

    def _on_filter_changed(self):
        query = self._search.text()
        domain = self._domain_combo.currentText()
        self._populate(query, domain)

    def _populate(self, query: str, domain: str):
        # Remove existing cards (but keep the trailing stretch)
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()

        activities = self._library.search(query)
        if domain != "All Domains":
            activities = [a for a in activities if a.domain == domain]

        for act in activities:
            card = LibraryCard(act, parent=self._cards_container)
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)
            self._cards.append(card)
