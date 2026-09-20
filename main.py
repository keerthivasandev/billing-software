#!/usr/bin/env python3
"""Entry point — Wholesale Billing & Inventory desktop ERP."""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QStyleFactory

from app.main_window import MainWindow
from app.styles import tokens as T


def _apply_windows_like_palette(app: QApplication):
    """Neutral Fusion palette so Mac preview matches Windows .exe look."""
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(T.BG_CANVAS))
    pal.setColor(QPalette.WindowText, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.Base, QColor(T.SURFACE))
    pal.setColor(QPalette.AlternateBase, QColor(T.ALT_ROW))
    pal.setColor(QPalette.Text, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.Button, QColor(T.SURFACE))
    pal.setColor(QPalette.ButtonText, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.Highlight, QColor(T.ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.ToolTipBase, QColor(T.SURFACE))
    pal.setColor(QPalette.ToolTipText, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.Link, QColor(T.ACCENT))
    app.setPalette(pal)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    # Fusion = same widget chrome on Mac and Windows (critical for preview parity)
    app.setStyle(QStyleFactory.create("Fusion"))
    _apply_windows_like_palette(app)

    T.resolve_fonts()
    app.setApplicationName("Wholesale Billing & Inventory")
    app.setOrganizationName("Sri Lakshmi Electricals")
    app.setFont(QFont(T.FONT_UI_RESOLVED, T.FONT_SIZE_UI))

    from app.styles.theme import get_qss
    app.setStyleSheet(get_qss())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
