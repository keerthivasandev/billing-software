"""Shared UI helpers — compact controls, readable labels."""

from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from app.styles import tokens as T


def ui_font(size_pt=None, bold=False):
    face = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    f = QFont(face, size_pt or T.FONT_SIZE_UI)
    f.setBold(bold)
    return f


def amount_font(size_pt=None, bold=False):
    """Clean sans-serif for money/qty — never monospace / typewriter."""
    face = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    f = QFont(face, size_pt or T.FONT_SIZE_GRID)
    f.setBold(bold)
    f.setStyleHint(QFont.SansSerif)
    f.setFixedPitch(False)
    f.setKerning(True)
    return f


# Back-compat alias used across screens
def mono_font(size_pt=None, bold=False):
    return amount_font(size_pt, bold)


def field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_LABEL}pt; font-weight: 600;"
    )
    return lbl


def shortcut_badge(text: str) -> QLabel:
    face = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: #6B7280; font-family: '{face}'; font-size: {T.FONT_SIZE_SHORTCUT}pt;"
    )
    return lbl


def labeled_field(label: str, widget: QWidget, shortcut: str = None) -> QWidget:
    wrap = QWidget()
    lay = QVBoxLayout(wrap)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(2)
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(4)
    row.addWidget(field_label(label))
    if shortcut:
        row.addWidget(shortcut_badge(shortcut))
    row.addStretch()
    lay.addLayout(row)
    lay.addWidget(widget)
    return wrap


def make_button(text: str, kind: str = "secondary", shortcut: str = None) -> QPushButton:
    label = f"{text}  {shortcut}" if shortcut else text
    btn = QPushButton(label)
    # Keep button height locked to INPUT_H / BUTTON_H — no tall padded CTAs
    base = (
        f"min-height: {T.BUTTON_H}px; max-height: {T.BUTTON_H}px; "
        f"padding: 1px 8px; border-radius: {T.RADIUS}px; "
        f"font-size: {T.FONT_SIZE_UI}pt; min-width: 72px;"
    )
    if kind == "primary":
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {T.ACCENT}; color: white; "
            f"border: 1px solid {T.ACCENT}; font-weight: bold; {base} }}"
            f"QPushButton:hover {{ background-color: {T.ACCENT_HOVER}; }}"
        )
    elif kind == "destructive":
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {T.SURFACE}; color: {T.DANGER}; "
            f"border: 1px solid {T.DANGER}; {base} }}"
            f"QPushButton:hover {{ background-color: #FEF2F2; }}"
        )
    elif kind == "ghost":
        btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"color: {T.TEXT_SECONDARY}; {base} min-width: 56px; }}"
            f"QPushButton:hover {{ color: {T.TEXT_PRIMARY}; "
            f"background-color: {T.HEADER_BAND}; }}"
        )
    else:
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {T.SURFACE}; color: {T.TEXT_PRIMARY}; "
            f"border: 1px solid {T.BORDER_STRONG}; {base} }}"
            f"QPushButton:hover {{ background-color: {T.HEADER_BAND}; "
            f"border-color: {T.ACCENT}; }}"
        )
    btn.setFixedHeight(T.BUTTON_H)
    return btn


def balance_label(amount: float) -> QLabel:
    if amount > 0:
        text = f"Rs. {amount:,.2f} DUE"
        bg, fg, border = "#FEE2E2", T.DANGER, T.DANGER
    elif amount < 0:
        text = f"Rs. {abs(amount):,.2f} CREDIT"
        bg, fg, border = "#DCFCE7", T.SUCCESS, T.SUCCESS
    else:
        text = "Rs. 0.00"
        bg, fg, border = T.HEADER_BAND, T.TEXT_SECONDARY, T.BORDER
    lbl = QLabel(text)
    lbl.setFont(amount_font(T.FONT_SIZE_UI, bold=True))
    lbl.setStyleSheet(
        f"color: {fg}; background: {bg}; border: 1px solid {border}; "
        f"padding: 3px 10px; font-weight: bold;"
    )
    return lbl


def format_inr(amount: float) -> str:
    # Use "Rs." (ASCII) so Qt won't fall back to a typewriter font for missing ₹ glyphs
    return f"Rs. {amount:,.2f}"


def readonly_brush():
    return QColor(T.READONLY_CELL)
