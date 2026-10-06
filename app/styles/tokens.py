"""Stitch Design System Implementation — extracted from Stitch MCP screen HTML."""

import sys

# ── Sidebar (Stitch ERP chrome override) ─────────────────────
NAV_BG = "#0F172A"
NAV_HOVER = "#1E293B"
NAV_ACTIVE = "#1E293B"
NAV_ACTIVE_INDICATOR = "#3B82F6"
NAV_TEXT = "#94a3b8"
NAV_TEXT_ACTIVE = "#ffffff"
NAV_GROUP_TEXT = "#64748b"
NAV_ACTIVE_BG = "#1E293B"

# ── Primary / accent (Stitch: button.bg-primary-container + MD3 primary) ──
# Screen CSS override uses #1D4ED8 for primary buttons; MD3 theme primary is #004ac6.
ACCENT = "#1D4ED8"
ACCENT_HOVER = "#1E40AF"
PRIMARY = "#1D4ED8"
PRIMARY_DEEP = "#004ac6"          # MD3 text-primary / icon accent
PRIMARY_CONTAINER = "#1D4ED8"
PRIMARY_FIXED = "#dbeafe"         # soft blue chip / save fill
ACCENT_SOFT = "#dbeafe"
FOCUS_BORDER = "#1D4ED8"
GRAND_TOTAL_BG = "#0F172A"

# ── Canvas & surfaces (Stitch MD3 + ERP override) ─────────────
BG_CANVAS = "#F8FAFC"             # --canvas-bg override
SURFACE = "#ffffff"               # surface-container-lowest
SURFACE_CONTAINER = "#edeef0"     # surface-container
SURFACE_CONTAINER_LOW = "#f3f4f6" # surface-container-low (inputs / bands)
SURFACE_CONTAINER_HIGH = "#e7e8ea"
SURFACE_BRIGHT = "#f8f9fb"
BORDER = "#E2E8F0"                # --card-border
BORDER_STRONG = "#CBD5E1"
HEADER_BAND = "#F1F5F9"
ALT_ROW = "#f8fafc"
READONLY_CELL = "#F1F5F9"
INPUT_BG = "#f3f4f6"

# ── Typography colors (Stitch MD3) ───────────────────────────
TEXT_PRIMARY = "#191c1e"          # on-surface
TEXT_SECONDARY = "#575e70"        # secondary
TEXT_MUTED = "#475569"

# ── Status ───────────────────────────────────────────────────
SUCCESS = "#10b981"
SUCCESS_BG = "#ecfdf5"
SUCCESS_FG = "#047857"
WARNING = "#f59e0b"
WARNING_BG = "#fffbeb"
DANGER = "#ba1a1a"                # Stitch error
DANGER_BG = "#fef2f2"
DANGER_FG = "#b91c1c"
DOC_PILL_BG = "#e0e7ff"
DOC_PILL_FG = "#3730a3"

# ── Sizing — Stitch dense desktop (0.25rem = 4px square fields) ──
INPUT_H = 32
BUTTON_H = 32
GRID_ROW_H = 38          # table body row height (even vertical rhythm)
TABLE_HEADER_H = 36      # table header row height
TABLE_PAD_X = 16         # horizontal cell padding (Stitch px-4)
TABLE_PAD_Y = 8          # vertical cell padding (px)
TABLE_HEADER_PAD_X = 16
TABLE_HEADER_PAD_Y = 8
NAV_COLLAPSED = 72
NAV_EXPANDED = 256
LIST_PANEL_W = 300
HEADER_ZONE_H = 44
BREADCRUMB_H = 24
FAST_STRIP_H = 56
FOOTER_ZONE_H = 210
# Stitch forces border-radius: 0.25rem (4px) on controls; cards use rounded-lg (8px)
RADIUS = 4
CARD_RADIUS = 8
EMPTY_GRID_ROWS = 12

# ── Typography — Stitch loads Inter ──────────────────────────
FONT_SIZE_UI = 9
FONT_SIZE_LABEL = 8
FONT_SIZE_GRID = 9
FONT_SIZE_NAV = 9
FONT_SIZE_TITLE = 11
FONT_SIZE_GRAND = 14
FONT_SIZE_SHORTCUT = 8
FONT_SIZE_MICRO = 7

FONT_UI = "Inter"
FONT_UI_FALLBACK = "Segoe UI"
FONT_MONO = "JetBrains Mono"
FONT_MONO_FALLBACK = "Consolas"

FONT_UI_RESOLVED = FONT_UI
FONT_MONO_RESOLVED = FONT_MONO


def _pick_font(*candidates):
    from PySide6.QtGui import QFontDatabase
    families = set(QFontDatabase.families())
    for name in candidates:
        if name and name in families:
            return name
    if sys.platform == "darwin":
        return "Helvetica Neue"
    return candidates[-1] if candidates else "Arial"


def resolve_fonts():
    """Call after QApplication exists. Prefer bundled Inter (Stitch), then system."""
    global FONT_UI_RESOLVED, FONT_MONO_RESOLVED
    from pathlib import Path
    from PySide6.QtGui import QFontDatabase

    fonts_dir = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    for ttf in fonts_dir.glob("Inter*.ttf"):
        QFontDatabase.addApplicationFont(str(ttf))
    for ttf in fonts_dir.glob("JetBrains*.ttf"):
        QFontDatabase.addApplicationFont(str(ttf))

    # Bundled variable font registers as "Inter Variable" / "Inter Variable Text"
    FONT_UI_RESOLVED = _pick_font(
        "Inter", "Inter Variable", "Inter Variable Text", "Segoe UI", "Arial"
    )
    FONT_MONO_RESOLVED = _pick_font(
        "JetBrains Mono", "Consolas", "Courier New"
    )
    return FONT_UI_RESOLVED, FONT_MONO_RESOLVED
