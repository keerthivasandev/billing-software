#!/usr/bin/env python3
"""Entry point — Wholesale Billing & Inventory desktop ERP (PySide6)."""

import sys

from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import QApplication, QStyleFactory
# from app.screens.license_dialog import LicenseActivationDialog
from app.main_window import MainWindow
from app.styles import tokens as T


def _apply_windows_like_palette(app: QApplication):
    """Neutral Fusion palette so Mac preview matches Windows .exe look."""
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(T.BG_CANVAS))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.ColorRole.Base, QColor(T.SURFACE))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(T.ALT_ROW))
    pal.setColor(QPalette.ColorRole.Text, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.ColorRole.Button, QColor(T.SURFACE))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(T.ACCENT))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(T.SURFACE))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(T.TEXT_PRIMARY))
    pal.setColor(QPalette.ColorRole.Link, QColor(T.ACCENT))
    app.setPalette(pal)

# This will show the license dialog first time the app is run
# app = QApplication(sys.argv)
# dlg = LicenseActivationDialog()
# dlg.exec()
# sys.exit(app.exec())

def main():
    # Qt6 handles High-DPI scaling natively.
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    _apply_windows_like_palette(app)

    T.resolve_fonts()
    app.setApplicationName("Wholesale Billing & Inventory")
    app.setOrganizationName("Sri Lakshmi Electricals")
    app.setFont(QFont(T.FONT_UI_RESOLVED, T.FONT_SIZE_UI))

    from app.styles.theme import get_qss
    app.setStyleSheet(get_qss())

    from app.widgets.icons import install_global_combo_arrows
    install_global_combo_arrows(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
