"""Flat Windows-ERP QSS — readable fonts, compact equal-height controls."""

from app.styles import tokens as T


def build_qss() -> str:
    ui = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    return f"""
* {{
    font-family: "{ui}", "{T.FONT_UI_FALLBACK}";
    font-size: {T.FONT_SIZE_UI}pt;
    color: {T.TEXT_PRIMARY};
}}

QMainWindow, QDialog {{
    background-color: {T.BG_CANVAS};
}}

QWidget#centralRoot {{
    background-color: {T.BG_CANVAS};
}}

QFrame#navRail {{
    background-color: {T.NAV_BG};
    border-right: 1px solid #122038;
}}

QLabel#navBrand {{
    color: {T.NAV_TEXT_ACTIVE};
    font-size: {T.FONT_SIZE_TITLE}pt;
    font-weight: bold;
    padding: 2px 4px;
}}

QLabel#navBrandSub {{
    color: {T.NAV_TEXT};
    font-size: {T.FONT_SIZE_SHORTCUT}pt;
    padding: 0 4px 6px 4px;
}}

QPushButton#navToggle {{
    background-color: {T.NAV_HOVER};
    color: {T.NAV_TEXT_ACTIVE};
    border: 1px solid #2A3F5F;
    border-radius: {T.RADIUS}px;
    min-width: 26px;
    max-width: 26px;
    min-height: 24px;
    max-height: 24px;
    padding: 0;
}}

QFrame#topBar {{
    background-color: {T.SURFACE};
    border-bottom: 1px solid {T.BORDER};
}}

QFrame#breadcrumbBar {{
    background-color: {T.HEADER_BAND};
    border-bottom: 1px solid {T.BORDER};
}}

QLabel#companyTitle {{
    font-size: {T.FONT_SIZE_TITLE}pt;
    font-weight: bold;
}}

QLabel#fyBadge {{
    color: {T.TEXT_PRIMARY};
    background-color: {T.ACCENT_SOFT};
    border: 1px solid #BFD6F8;
    padding: 2px 8px;
    font-size: {T.FONT_SIZE_LABEL}pt;
    font-weight: bold;
}}

QLabel#userBadge {{
    color: {T.TEXT_SECONDARY};
    background-color: {T.HEADER_BAND};
    border: 1px solid {T.BORDER};
    padding: 2px 8px;
    font-size: {T.FONT_SIZE_LABEL}pt;
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER};
    border-radius: {T.RADIUS}px;
    padding: 1px 6px;
    min-height: {T.INPUT_H}px;
    max-height: {T.INPUT_H}px;
    font-size: {T.FONT_SIZE_UI}pt;
    selection-background-color: {T.ACCENT};
    selection-color: white;
}}

QTextEdit {{
    max-height: 80px;
    min-height: 60px;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {T.FOCUS_BORDER};
    background-color: #FAFCFF;
}}

QComboBox::drop-down {{
    border: none;
    border-left: 1px solid {T.BORDER};
    width: 20px;
    background: {T.HEADER_BAND};
}}

QComboBox QAbstractItemView {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER};
    selection-background-color: {T.ACCENT_SOFT};
    selection-color: {T.TEXT_PRIMARY};
    font-size: {T.FONT_SIZE_UI}pt;
    outline: 0;
}}

/* Compact buttons — same height as inputs */
QPushButton {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER_STRONG};
    border-radius: {T.RADIUS}px;
    padding: 2px 10px;
    min-height: {T.BUTTON_H}px;
    max-height: {T.BUTTON_H}px;
    min-width: 72px;
    font-size: {T.FONT_SIZE_UI}pt;
    color: {T.TEXT_PRIMARY};
}}

QPushButton:hover {{
    background-color: {T.HEADER_BAND};
    border-color: {T.ACCENT};
}}

QPushButton:pressed {{
    background-color: {T.BORDER};
}}

QPushButton:disabled {{
    color: #9AA3B2;
    background-color: {T.HEADER_BAND};
}}

QToolButton {{
    background-color: {T.ACCENT};
    color: white;
    border: 1px solid {T.ACCENT};
    border-radius: {T.RADIUS}px;
    padding: 2px 10px;
    font-weight: bold;
    font-size: {T.FONT_SIZE_UI}pt;
    min-height: {T.BUTTON_H}px;
    max-height: {T.BUTTON_H}px;
}}

QToolButton:hover {{
    background-color: {T.ACCENT_HOVER};
}}

QToolButton::menu-button {{
    border-left: 1px solid rgba(255,255,255,0.45);
    width: 18px;
}}

QTableWidget, QTreeWidget, QListWidget {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER};
    gridline-color: {T.BORDER};
    alternate-background-color: {T.ALT_ROW};
    selection-background-color: {T.ACCENT_SOFT};
    selection-color: {T.TEXT_PRIMARY};
    font-size: {T.FONT_SIZE_GRID}pt;
    outline: 0;
}}

QHeaderView::section {{
    background-color: #E2E6EC;
    border: none;
    border-right: 1px solid {T.BORDER};
    border-bottom: 1px solid {T.BORDER_STRONG};
    padding: 4px 6px;
    font-size: {T.FONT_SIZE_LABEL}pt;
    font-weight: bold;
    color: {T.TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 1px 4px;
}}

QTableWidget::item:focus {{
    border: 1px solid {T.FOCUS_BORDER};
    background-color: #FAFCFF;
}}

QListWidget::item {{
    padding: 6px 8px;
    border-bottom: 1px solid {T.BORDER};
    font-size: {T.FONT_SIZE_UI}pt;
}}

QListWidget::item:selected {{
    background-color: {T.ACCENT_SOFT};
    border-left: 3px solid {T.ACCENT};
}}

QTabWidget::pane {{
    border: 1px solid {T.BORDER};
    background: {T.SURFACE};
}}

QTabBar::tab {{
    background: {T.HEADER_BAND};
    border: 1px solid {T.BORDER};
    border-bottom: none;
    padding: 5px 14px;
    margin-right: 2px;
    font-size: {T.FONT_SIZE_UI}pt;
    color: {T.TEXT_SECONDARY};
}}

QTabBar::tab:selected {{
    background: {T.SURFACE};
    color: {T.ACCENT};
    font-weight: bold;
    border-top: 2px solid {T.ACCENT};
}}

QRadioButton {{
    font-size: {T.FONT_SIZE_UI}pt;
    spacing: 4px;
}}

QScrollBar:vertical {{
    background: {T.HEADER_BAND};
    width: 10px;
    border-left: 1px solid {T.BORDER};
}}

QScrollBar::handle:vertical {{
    background: {T.BORDER_STRONG};
    min-height: 24px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {T.HEADER_BAND};
    height: 10px;
}}

QScrollBar::handle:horizontal {{
    background: {T.BORDER_STRONG};
    min-width: 24px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QStatusBar {{
    background-color: {T.NAV_BG};
    color: {T.NAV_TEXT};
    font-size: {T.FONT_SIZE_LABEL}pt;
    border-top: 1px solid #122038;
}}

QSplitter::handle {{
    background-color: {T.BORDER};
    width: 1px;
}}

QMenu {{
    background: {T.SURFACE};
    border: 1px solid {T.BORDER};
    font-size: {T.FONT_SIZE_UI}pt;
}}

QMenu::item {{
    padding: 5px 20px 5px 10px;
}}

QMenu::item:selected {{
    background: {T.ACCENT_SOFT};
}}
"""


def get_qss() -> str:
    return build_qss()


QSS = build_qss()
