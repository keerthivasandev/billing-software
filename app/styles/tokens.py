"""Stitch Design System Implementation — dense ERP tokens for shop PCs."""

import sys

# Sidebar (Stitch refined)
NAV_BG = "#0F172A"
NAV_HOVER = "#1E293B"
NAV_ACTIVE = "#1E293B"
NAV_ACTIVE_INDICATOR = "#3B82F6"
NAV_TEXT = "#94a3b8"
NAV_TEXT_ACTIVE = "#ffffff"
NAV_GROUP_TEXT = "#64748b"

# Accents
ACCENT = "#1D4ED8"
ACCENT_HOVER = "#1E40AF"
ACCENT_SOFT = "#eff6ff"
PRIMARY_CONTAINER = "#2563eb"
FOCUS_BORDER = "#2563eb"
GRAND_TOTAL_BG = "#0F172A"

# Canvas & surfaces (Stitch)
BG_CANVAS = "#F8FAFC"
SURFACE = "#ffffff"
BORDER = "#E2E8F0"
BORDER_STRONG = "#CBD5E1"
HEADER_BAND = "#F1F5F9"
ALT_ROW = "#f8fafc"
READONLY_CELL = "#F1F5F9"
NAV_ACTIVE_BG = "#1E293B"

# Typography colors
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
TEXT_MUTED = "#475569"

# Status
SUCCESS = "#10b981"
SUCCESS_BG = "#ecfdf5"
WARNING = "#f59e0b"
WARNING_BG = "#fffbeb"
DANGER = "#ef4444"
DANGER_BG = "#fef2f2"
DOC_PILL_BG = "#e0e7ff"
DOC_PILL_FG = "#3730a3"

# Sizing — match Stitch dense desktop
INPUT_H = 28
BUTTON_H = 30
GRID_ROW_H = 32
NAV_COLLAPSED = 72
NAV_EXPANDED = 256
LIST_PANEL_W = 260
HEADER_ZONE_H = 44   # Stitch h-11
BREADCRUMB_H = 24    # Stitch h-6
FAST_STRIP_H = 56
FOOTER_ZONE_H = 210
RADIUS = 4
EMPTY_GRID_ROWS = 12
CARD_RADIUS = 8

# Typography (pt) — Inter/Segoe dense
FONT_SIZE_UI = 9
FONT_SIZE_LABEL = 8
FONT_SIZE_GRID = 9
FONT_SIZE_NAV = 9
FONT_SIZE_TITLE = 11
FONT_SIZE_GRAND = 14
FONT_SIZE_SHORTCUT = 8
FONT_SIZE_MICRO = 7

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
