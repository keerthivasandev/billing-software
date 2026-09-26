"""Shared UI helpers — Zoho-style compact controls + lightweight toast."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from app.styles import tokens as T


def ui_font(size_pt=None, bold=False):
    face = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    f = QFont(face, size_pt or T.FONT_SIZE_UI)
    f.setBold(bold)
    return f


def amount_font(size_pt=None, bold=False):
    face = getattr(T, "FONT_UI_RESOLVED", T.FONT_UI)
    f = QFont(face, size_pt or T.FONT_SIZE_GRID)
    f.setBold(bold)
    f.setStyleHint(QFont.StyleHint.SansSerif)
    f.setFixedPitch(False)
    f.setKerning(True)
    return f


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
        f"color: {T.TEXT_SECONDARY}; font-family: '{face}'; "
        f"font-size: {T.FONT_SIZE_SHORTCUT}pt;"
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
    # Qt treats single "&" as mnemonic (underline) — "Save & Print" becomes Save_Print.
    safe = text.replace("&", "&&")
    label = f"{safe}  {shortcut}" if shortcut else safe
    btn = QPushButton(label)
    btn.setAutoDefault(False)
    btn.setDefault(False)
    base = (
        f"min-height: {T.BUTTON_H}px; "
        f"padding: 4px 14px; border-radius: {T.RADIUS}px; "
        f"font-size: {T.FONT_SIZE_UI}pt;"
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
            f"QPushButton:hover {{ background-color: {T.DANGER_BG}; }}"
        )
    elif kind == "ghost":
        btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid transparent; "
            f"color: {T.TEXT_SECONDARY}; {base} }}"
            f"QPushButton:hover {{ color: {T.TEXT_PRIMARY}; "
            f"background-color: {T.HEADER_BAND}; border-color: {T.BORDER}; }}"
        )
    else:
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {T.SURFACE}; color: {T.TEXT_PRIMARY}; "
            f"border: 1px solid {T.BORDER_STRONG}; {base} }}"
            f"QPushButton:hover {{ background-color: {T.HEADER_BAND}; "
            f"border-color: {T.ACCENT}; }}"
        )
    btn.setMinimumHeight(T.BUTTON_H)
    return btn


def balance_label(amount: float) -> QLabel:
    if amount > 0:
        text = f"Rs. {amount:,.2f} DUE"
        bg, fg, border = T.DANGER_BG, T.DANGER, T.DANGER
    elif amount < 0:
        text = f"Rs. {abs(amount):,.2f} CREDIT"
        bg, fg, border = T.SUCCESS_BG, T.SUCCESS, T.SUCCESS
    else:
        text = "Rs. 0.00"
        bg, fg, border = T.HEADER_BAND, T.TEXT_SECONDARY, T.BORDER
    lbl = QLabel(text)
    lbl.setFont(amount_font(T.FONT_SIZE_UI, bold=True))
    lbl.setStyleSheet(
        f"color: {fg}; background: {bg}; border: 1px solid {border}; "
        f"padding: 3px 10px; font-weight: bold; border-radius: {T.RADIUS}px;"
    )
    return lbl


def format_inr(amount: float) -> str:
    return f"Rs. {amount:,.2f}"


def format_inr_indian(amount: float, with_symbol: bool = True) -> str:
    """Indian grouping: ₹ 1,84,650.00 (matches Stitch mockups)."""
    neg = amount < 0
    amount = abs(float(amount))
    whole, frac = f"{amount:.2f}".split(".")
    if len(whole) <= 3:
        grouped = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        chunks = []
        while rest:
            chunks.append(rest[-2:])
            rest = rest[:-2]
        grouped = ",".join(reversed(chunks)) + "," + last3
    sign = "-" if neg else ""
    if with_symbol:
        return f"{sign}₹ {grouped}.{frac}"
    return f"{sign}{grouped}.{frac}"


def readonly_brush():
    return QColor(T.READONLY_CELL)


def type_badge(text: str) -> QLabel:
    """Document / txn type pill (Sale, Purchase, SI, etc.)."""
    mapping = {
        "Sale": (T.SUCCESS_BG, T.SUCCESS),
        "Purchase": (T.WARNING_BG, T.WARNING),
        "Receipt": (T.ACCENT_SOFT, T.ACCENT),
        "Payment": (T.DANGER_BG, T.DANGER),
        "SI": (T.DOC_PILL_BG, T.DOC_PILL_FG),
        "PI": (T.DOC_PILL_BG, T.DOC_PILL_FG),
        "RC": (T.DOC_PILL_BG, T.DOC_PILL_FG),
        "PY": (T.DOC_PILL_BG, T.DOC_PILL_FG),
        "QT": (T.DOC_PILL_BG, T.DOC_PILL_FG),
    }
    bg, fg = mapping.get(text, (T.HEADER_BAND, T.TEXT_SECONDARY))
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 8px; "
        f"padding: 2px 8px; font-size: {T.FONT_SIZE_SHORTCUT}pt; font-weight: bold;"
    )
    return lbl


def growth_pill(pct: float) -> QLabel:
    positive = pct >= 0
    bg = T.SUCCESS_BG if positive else T.DANGER_BG
    fg = T.SUCCESS if positive else T.DANGER
    sign = "+" if positive else ""
    lbl = QLabel(f"{sign}{pct:.1f}%")
    lbl.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 8px; "
        f"padding: 1px 6px; font-size: {T.FONT_SIZE_SHORTCUT}pt; font-weight: bold;"
    )
    return lbl


def card_frame() -> QFrame:
    box = QFrame()
    box.setStyleSheet(
        f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
        f"border-radius: {T.CARD_RADIUS}px; }}"
    )
    return box


def section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {T.FONT_SIZE_UI}pt; font-weight: bold; color: {T.TEXT_PRIMARY}; "
        f"border: none; background: transparent;"
    )
    return lbl


def page_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {T.FONT_SIZE_TITLE}pt; font-weight: bold; color: {T.TEXT_PRIMARY};"
    )
    return lbl


class ToastHost(QWidget):
    """Non-blocking toast overlay — no QMessageBox / alert()."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.hide()
        self._banner = QFrame(self)
        self._banner.setObjectName("toastBanner")
        lay = QHBoxLayout(self._banner)
        lay.setContentsMargins(14, 8, 14, 8)
        self._label = QLabel("")
        self._label.setStyleSheet(
            f"color: {T.NAV_TEXT_ACTIVE}; font-size: {T.FONT_SIZE_UI}pt; border: none;"
        )
        lay.addWidget(self._label)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_toast(self, message: str, ms: int = 2200):
        parent = self.parentWidget() or self.window()
        if parent is None:
            return
        self.setParent(parent)
        self._label.setText(message)
        self._banner.adjustSize()
        w = max(280, self._banner.sizeHint().width() + 8)
        h = self._banner.sizeHint().height() + 8
        self.resize(w, h)
        self._banner.setGeometry(0, 0, w, h)
        pw = parent.width()
        self.move(max(12, (pw - w) // 2), 56)
        self.raise_()
        self.show()
        self._timer.start(ms)


_TOAST_HOST = None


def toast(widget: QWidget, message: str, ms: int = 2200):
    """Show lightweight non-blocking toast from any widget."""
    global _TOAST_HOST
    win = widget.window() if widget else None
    if win is None:
        return
    if _TOAST_HOST is None or _TOAST_HOST.parent() is not win:
        _TOAST_HOST = ToastHost(win)
    _TOAST_HOST.show_toast(message, ms)
