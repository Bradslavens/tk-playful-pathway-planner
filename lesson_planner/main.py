import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from lesson_planner.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Playful Pathway Planner")

    font = app.font()
    font.setFamily("Segoe UI, Arial, sans-serif")
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
