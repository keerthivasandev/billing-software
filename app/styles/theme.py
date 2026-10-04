"""Zoho Inventory QSS — flat, lightweight, token-driven."""

from app.styles import tokens as T
from app.widgets.icons import icon_url as _icon_url


def build_qss() -> str:
    ui = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    return f"""
* {{
    font-family: "{ui}", "Inter", "Inter Variable", "Segoe UI", "{T.FONT_UI_FALLBACK}", -apple-system, BlinkMacSystemFont, sans-serif;
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
    border-right: 1px solid #0b1220;
}}

QLabel#navBrand {{
    color: {T.NAV_TEXT_ACTIVE};
    font-size: {T.FONT_SIZE_TITLE}pt;
    font-weight: bold;
    padding: 0;
}}

QLabel#navBrandSub {{
    color: {T.NAV_TEXT};
    font-size: {T.FONT_SIZE_MICRO}pt;
    padding: 0;
}}

QPushButton#navToggle {{
    background-color: transparent;
    color: {T.NAV_TEXT};
    border: 1px solid transparent;
    border-radius: {T.RADIUS}px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 2px;
}}

QPushButton#navToggle:hover {{
    background-color: {T.NAV_HOVER};
    color: {T.NAV_TEXT_ACTIVE};
}}

QFrame#topBar {{
    background-color: {T.SURFACE};
    border-bottom: none;
}}

QFrame#breadcrumbBar {{
    background-color: {T.HEADER_BAND};
    border-top: 1px solid {T.BORDER};
    border-bottom: 1px solid {T.BORDER};
}}

QLabel#companyTitle {{
    font-size: 11pt;
    font-weight: 700;
    color: {T.TEXT_PRIMARY};
}}

QFrame#globalSearchBox {{
    background-color: {T.INPUT_BG};
    border: 1px solid {T.BORDER_STRONG};
    border-radius: {T.RADIUS}px;
}}

QLineEdit#globalSearch {{
    background: transparent;
    border: none;
    padding: 0 4px;
    min-height: 24px;
    max-height: 28px;
    font-size: 9pt;
    color: {T.TEXT_PRIMARY};
}}

QLineEdit#globalSearch:focus {{
    border: none;
    background: transparent;
}}

QFrame#globalSearchBox:focus-within {{
    border: 1px solid {T.FOCUS_BORDER};
    background-color: {T.SURFACE};
}}

QLabel#fyBadge {{
    color: {T.PRIMARY};
    background-color: {T.ACCENT_SOFT};
    border: 1px solid {T.BORDER};
    border-radius: {T.RADIUS}px;
    padding: 2px 6px;
    font-size: 8pt;
    font-weight: 600;
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
    background-color: {T.INPUT_BG};
    border: 1px solid {T.BORDER};
    border-radius: {T.RADIUS}px;
    padding: 1px 6px;
    min-height: {T.INPUT_H}px;
    max-height: {T.INPUT_H}px;
    font-size: {T.FONT_SIZE_UI}pt;
    selection-background-color: {T.PRIMARY};
    selection-color: white;
}}

QTextEdit {{
    max-height: 90px;
    min-height: 60px;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {T.FOCUS_BORDER};
    background-color: #fafcff;
}}

QComboBox QAbstractItemView {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER};
    selection-background-color: {T.ACCENT_SOFT};
    selection-color: {T.TEXT_PRIMARY};
    font-size: {T.FONT_SIZE_UI}pt;
    outline: 0;
}}

QPushButton {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER_STRONG};
    border-radius: {T.RADIUS}px;
    padding: 4px 14px;
    min-height: {T.BUTTON_H}px;
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
    color: #9ca3af;
    background-color: {T.HEADER_BAND};
}}

QToolButton {{
    background-color: {T.ACCENT};
    color: white;
    border: 1px solid {T.ACCENT};
    border-radius: {T.RADIUS}px;
    padding: 4px 16px;
    font-weight: bold;
    font-size: {T.FONT_SIZE_UI}pt;
    min-height: {T.BUTTON_H}px;
    min-width: 148px;
}}

QToolButton:hover {{
    background-color: {T.ACCENT_HOVER};
}}

QToolButton::menu-button {{
    border-left: 1px solid rgba(255,255,255,0.45);
    width: 22px;
}}

QComboBox::drop-down, QDateEdit::drop-down {{
    border: none;
    border-left: 1px solid {T.BORDER};
    width: 22px;
    background: {T.HEADER_BAND};
    subcontrol-origin: padding;
    subcontrol-position: top right;
}}

QDateEdit {{
    padding-right: 4px;
}}

/* Larger, readable spin / date stepper arrows (Ant-style SVG) */
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
    subcontrol-origin: border;
    width: 22px;
    border-left: 1px solid {T.BORDER};
    background: {T.HEADER_BAND};
}}

QAbstractSpinBox::up-button {{
    subcontrol-position: top right;
    border-top-right-radius: {T.RADIUS}px;
}}

QAbstractSpinBox::down-button {{
    subcontrol-position: bottom right;
    border-bottom-right-radius: {T.RADIUS}px;
}}

QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {{
    background: {T.ACCENT_SOFT};
}}

QAbstractSpinBox::up-arrow {{
    image: url({_icon_url("caret-up-dark")});
    width: 12px;
    height: 12px;
}}

QAbstractSpinBox::down-arrow {{
    image: url({_icon_url("caret-down-dark")});
    width: 12px;
    height: 12px;
}}

QTableWidget, QTreeWidget, QListWidget {{
    background-color: {T.SURFACE};
    border: 1px solid {T.BORDER};
    border-radius: {T.RADIUS}px;
    gridline-color: transparent;
    alternate-background-color: {T.ALT_ROW};
    selection-background-color: {T.ACCENT_SOFT};
    selection-color: {T.TEXT_PRIMARY};
    font-size: {T.FONT_SIZE_GRID}pt;
    outline: 0;
}}

QHeaderView {{
    background-color: {T.SURFACE_CONTAINER_LOW};
}}

QHeaderView::section {{
    background-color: {T.SURFACE_CONTAINER_LOW};
    border: none;
    border-right: 1px solid {T.BORDER};
    border-bottom: 1px solid {T.BORDER};
    padding: {T.TABLE_HEADER_PAD_Y}px {T.TABLE_HEADER_PAD_X}px;
    font-size: {T.FONT_SIZE_LABEL}pt;
    font-weight: 700;
    color: {T.TEXT_SECONDARY};
}}

QHeaderView::section:last {{
    border-right: none;
}}

QTableWidget::item {{
    padding: {T.TABLE_PAD_Y}px {T.TABLE_PAD_X}px;
    border-bottom: 1px solid {T.BORDER};
}}

QTableWidget::item:focus {{
    border: 1px solid {T.FOCUS_BORDER};
    background-color: #fafcff;
}}

QTableWidget::item:selected {{
    background-color: {T.ACCENT_SOFT};
    color: {T.TEXT_PRIMARY};
}}

QListWidget::item {{
    padding: {T.TABLE_PAD_Y}px {T.TABLE_PAD_X}px;
    border-bottom: 1px solid {T.BORDER};
    font-size: {T.FONT_SIZE_UI}pt;
    min-height: {T.GRID_ROW_H - 8}px;
}}

QListWidget::item:selected {{
    background-color: {T.ACCENT_SOFT};
    border-left: 3px solid {T.ACCENT};
}}

QTabWidget::pane {{
    border: 1px solid {T.BORDER};
    background: {T.SURFACE};
    border-radius: 0 0 {T.CARD_RADIUS}px {T.CARD_RADIUS}px;
}}

QTabBar::tab {{
    background: {T.HEADER_BAND};
    border: 1px solid {T.BORDER};
    border-bottom: none;
    padding: 6px 14px;
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

QProgressBar {{
    border: none;
    background: {T.HEADER_BAND};
    border-radius: 3px;
    max-height: 8px;
    min-height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {T.ACCENT};
    border-radius: 3px;
}}

QScrollBar:vertical {{
    background: {T.HEADER_BAND};
    width: 10px;
    border-left: 1px solid {T.BORDER};
}}

QScrollBar::handle:vertical {{
    background: {T.BORDER_STRONG};
    min-height: 24px;
    border-radius: 4px;
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
    border-top: 1px solid #0b1220;
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
    padding: 6px 22px 6px 12px;
}}

QMenu::item:selected {{
    background: {T.ACCENT_SOFT};
}}

QFrame#toastBanner {{
    background-color: {T.NAV_BG};
    border-radius: {T.CARD_RADIUS}px;
    border: 1px solid #374151;
}}
"""


def get_qss() -> str:
    return build_qss()


QSS = build_qss()
