"""
main.py — Application Entry Point
CS3510 Compiler Construction — Semester Project

Run with:
    python main.py
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui import MainWindow


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("MiniLang Analyzer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CS3510 — Compiler Construction")

    # Set a clean default font
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
