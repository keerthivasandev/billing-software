"""Design tokens — dense Windows ERP (readable type, compact controls)."""

import sys

# Colors
BG_CANVAS = "#E8EAED"
SURFACE = "#FFFFFF"
BORDER = "#C5CAD3"
BORDER_STRONG = "#9AA3B2"
HEADER_BAND = "#F0F2F5"
NAV_BG = "#1B2A4A"
NAV_TEXT = "#D0D7E2"
NAV_TEXT_ACTIVE = "#FFFFFF"
NAV_HOVER = "#243656"
NAV_ACTIVE = "#2B4A7A"
TEXT_PRIMARY = "#1A1F2C"
TEXT_SECONDARY = "#4B5565"
ACCENT = "#1F6FEB"
ACCENT_HOVER = "#1858C5"
ACCENT_SOFT = "#E8F1FF"
SUCCESS = "#15803D"
WARNING = "#B45309"
DANGER = "#B91C1C"
READONLY_CELL = "#EEF0F3"
ALT_ROW = "#F7F8FA"
NAV_ACTIVE_BG = "#E8F1FF"
FOCUS_BORDER = "#1F6FEB"
GRAND_TOTAL_BG = "#1B2A4A"

# Sizing — matched controls (button ≈ input), denser layout
INPUT_H = 26
BUTTON_H = 26
GRID_ROW_H = 26
NAV_COLLAPSED = 52
NAV_EXPANDED = 210
LIST_PANEL_W = 260
HEADER_ZONE_H = 78
FAST_STRIP_H = 48
FOOTER_ZONE_H = 118
RADIUS = 2
EMPTY_GRID_ROWS = 12

# Typography (pt) — normal desktop ERP scale (Tally/Busy-like)
FONT_SIZE_UI = 9
FONT_SIZE_LABEL = 8
FONT_SIZE_GRID = 9
FONT_SIZE_NAV = 9
FONT_SIZE_TITLE = 11
FONT_SIZE_GRAND = 12
FONT_SIZE_SHORTCUT = 8

FONT_UI = "Segoe UI"
FONT_UI_FALLBACK = "Arial"
FONT_MONO = "Consolas"
FONT_MONO_FALLBACK = "Courier New"


def _pick_font(preferred, fallback):
    from PyQt5.QtGui import QFontDatabase
    families = set(QFontDatabase().families())
    if preferred in families:
        return preferred
    if fallback in families:
        return fallback
    if sys.platform == "darwin":
        return "Helvetica Neue"
    return preferred


FONT_UI_RESOLVED = FONT_UI
FONT_MONO_RESOLVED = FONT_MONO


def resolve_fonts():
    """Call after QApplication exists."""
    global FONT_UI_RESOLVED, FONT_MONO_RESOLVED
    if sys.platform == "darwin":
        # Prefer faces that render clean Latin digits (avoid Arial ₹ fallback junk)
        FONT_UI_RESOLVED = _pick_font("Helvetica Neue", "Arial")
    elif sys.platform == "win32":
        FONT_UI_RESOLVED = _pick_font("Segoe UI", "Arial")
    else:
        FONT_UI_RESOLVED = _pick_font("Ubuntu", "DejaVu Sans")
    FONT_MONO_RESOLVED = FONT_UI_RESOLVED  # amounts use same clean UI face
    return FONT_UI_RESOLVED, FONT_MONO_RESOLVED
