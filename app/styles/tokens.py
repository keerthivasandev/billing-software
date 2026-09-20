"""Zoho Inventory palette — dense ERP tokens for low-spec PCs."""

import sys

# Sidebar & dark accents
NAV_BG = "#111827"
NAV_HOVER = "#1f2937"
NAV_ACTIVE = "#2563eb"
NAV_TEXT = "#9ca3af"
NAV_TEXT_ACTIVE = "#f9fafb"
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
ACCENT_SOFT = "#eff6ff"
FOCUS_BORDER = "#2563eb"
GRAND_TOTAL_BG = "#111827"

# Canvas & surfaces
BG_CANVAS = "#f3f4f6"
SURFACE = "#ffffff"
BORDER = "#e5e7eb"
BORDER_STRONG = "#d1d5db"
HEADER_BAND = "#f9fafb"
ALT_ROW = "#f9fafb"
READONLY_CELL = "#f3f4f6"
NAV_ACTIVE_BG = "#eff6ff"

# Typography colors
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

# Status
SUCCESS = "#10b981"
SUCCESS_BG = "#ecfdf5"
WARNING = "#f59e0b"
WARNING_BG = "#fffbeb"
DANGER = "#ef4444"
DANGER_BG = "#fef2f2"
DOC_PILL_BG = "#e0e7ff"
DOC_PILL_FG = "#3730a3"

# Sizing — readable controls (avoid clipped footer / buttons)
INPUT_H = 30
BUTTON_H = 30
GRID_ROW_H = 28
NAV_COLLAPSED = 72
NAV_EXPANDED = 248
LIST_PANEL_W = 260
HEADER_ZONE_H = 100
FAST_STRIP_H = 56
FOOTER_ZONE_H = 210
RADIUS = 4
EMPTY_GRID_ROWS = 12
CARD_RADIUS = 6

# Typography (pt)
FONT_SIZE_UI = 9
FONT_SIZE_LABEL = 8
FONT_SIZE_GRID = 9
FONT_SIZE_NAV = 9
FONT_SIZE_TITLE = 11
FONT_SIZE_GRAND = 13
FONT_SIZE_SHORTCUT = 8

# Prefer Segoe UI on Windows for packaging / low-spec PCs (no custom font install).
FONT_UI = "Segoe UI"
FONT_UI_FALLBACK = "Arial"
FONT_MONO = "Consolas"
FONT_MONO_FALLBACK = "Courier New"

FONT_UI_RESOLVED = FONT_UI
FONT_MONO_RESOLVED = FONT_MONO


def _pick_font(preferred, fallback):
    from PySide6.QtGui import QFontDatabase
    families = set(QFontDatabase.families())
    if preferred in families:
        return preferred
    if fallback in families:
        return fallback
    if sys.platform == "darwin":
        return "Helvetica Neue"
    return fallback


def resolve_fonts():
    """Call after QApplication exists. Prefer Segoe UI on Windows."""
    global FONT_UI_RESOLVED, FONT_MONO_RESOLVED
    if sys.platform == "darwin":
        FONT_UI_RESOLVED = _pick_font("Helvetica Neue", "Arial")
    elif sys.platform == "win32":
        FONT_UI_RESOLVED = _pick_font("Segoe UI", "Arial")
    else:
        FONT_UI_RESOLVED = _pick_font("Ubuntu", "DejaVu Sans")
    FONT_MONO_RESOLVED = FONT_UI_RESOLVED
    return FONT_UI_RESOLVED, FONT_MONO_RESOLVED
