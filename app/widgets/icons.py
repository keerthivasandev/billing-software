"""Ant Design–style local SVG icons (lightweight, offline, potato-PC safe)."""

import re
from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, QSize
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"

# Map nav keys → icon stem (Ant-like outline set)
NAV_ICON = {
    "dashboard": "home",
    "company": "file-text",
    "parties": "team",
    "groups": "appstore",
    "products": "inbox",
    "godowns": "folder",
    "purchase": "shopping",
    "sales": "file-text",
    "cash_flow": "wallet",
    "billwise": "book",
    "estimate": "file-text",
    "ledger_stmt": "book",
    "registers": "history",
    "reports_ar_ap": "history",
    "export_tools": "folder",
    "audit_trail": "history",
    "users": "team",
    "change_fy": "calendar",
    "rollover": "calendar",
    "license": "safety",
}


def icon_path(name: str) -> Path:
    return ICONS_DIR / f"{name}.svg"


def icon_url(name: str) -> str:
    """Absolute path for QSS ``image: url(...)``.

    On Windows, Qt stylesheets paint reliably with a bare forward-slash path
    (``D:/app/assets/icons/x.png``). The ``file:///`` form silently fails and
    leaves combo/date arrows blank — that was the global missing-arrow bug.
    Prefers PNG when present (SVG can also fail to paint via QSS).
    """
    png = ICONS_DIR / f"{name}.png"
    path = (png if png.exists() else icon_path(name)).resolve().as_posix()
    return path


def combo_dropdown_qss(
    *,
    width: int = 24,
    background: str = "transparent",
    border_left: str = "none",
) -> str:
    """Shared QComboBox / QDateEdit drop-down + filled down-arrow caret.

    Uses a bare ``D:/...png`` path (quoted). ``file:///`` URLs do not paint on
    Windows/Qt stylesheets and were the cause of blank global dropdown arrows.
    """
    arrow = icon_url("caret-down-dark")
    return f"""
    QComboBox::drop-down, QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: {width}px;
        border: none;
        border-left: {border_left};
        background: {background};
    }}
    QComboBox::down-arrow, QDateEdit::down-arrow {{
        image: url("{arrow}");
        width: 12px;
        height: 12px;
    }}
    QComboBox::down-arrow:on, QDateEdit::down-arrow:on {{
        image: url("{arrow}");
    }}
    QComboBox, QDateEdit {{
        padding-right: {width + 6}px;
    }}
    """


def apply_combo_arrow(widget) -> None:
    """Ensure a combo/date edit keeps a visible dropdown caret (merge into stylesheet)."""
    if widget.property("_caretOk"):
        return
    existing = widget.styleSheet() or ""
    # Already has a working (non file://) caret rule
    if "caret-down-dark" in existing and "file:" not in existing and "down-arrow" in existing:
        widget.setProperty("_caretOk", True)
        return
    widget.setStyleSheet(existing + "\n" + combo_dropdown_qss())
    widget.setProperty("_caretOk", True)


def install_global_combo_arrows(app) -> None:
    """Force a visible caret on every QComboBox / QDateEdit (app-wide)."""
    from PySide6.QtCore import QEvent, QObject
    from PySide6.QtWidgets import QComboBox, QDateEdit

    class _ComboArrowPolish(QObject):
        def eventFilter(self, obj, event):
            if event.type() not in (QEvent.Type.Polish, QEvent.Type.Show):
                return False
            if isinstance(obj, (QComboBox, QDateEdit)):
                apply_combo_arrow(obj)
            return False

    filt = _ComboArrowPolish(app)
    app.installEventFilter(filt)
    app.setProperty("_comboArrowPolish", filt)  # keep alive


def _device_pixel_ratio() -> float:
    app = QGuiApplication.instance()
    if app is None:
        return 1.0
    screen = app.primaryScreen()
    if screen is None:
        return 1.0
    return max(1.0, float(screen.devicePixelRatio()))


def _tint_svg(xml: str, color: str, thicken: bool = True) -> str:
    """Retint stroke/fill hex colors for light canvases (keep fill=none)."""
    if not color:
        return xml

    def _stroke(_m):
        return f'stroke="{color}"'

    def _fill(m):
        val = m.group(1)
        if val.lower() in ("none", "transparent"):
            return m.group(0)
        return f'fill="{color}"'

    xml = re.sub(r'stroke="#[0-9A-Fa-f]{3,8}"', _stroke, xml)
    xml = re.sub(r'fill="([^"]+)"', _fill, xml)
    # Material Symbols filled paths often omit fill= — inject tint color.
    if 'fill="' not in xml or re.search(r"<path(?![^>]*fill=)", xml):
        xml = re.sub(r"<path(?![^>]*\bfill=)", f'<path fill="{color}"', xml)
    if thicken:
        # Thin 1.8 strokes look soft at ~20px; bump for field icons on light UI.
        def _width(m):
            try:
                w = float(m.group(1))
            except ValueError:
                return m.group(0)
            return f'stroke-width="{max(w, 2.15):.2f}"'

        xml = re.sub(r'stroke-width="([\d.]+)"', _width, xml)
    return xml


def icon_pixmap(name: str, size: int = 20, color: str = None) -> QPixmap:
    """
    Crisp SVG pixmap at logical `size` (HiDPI-aware via devicePixelRatio).
    Prefer this for QLabel.setPixmap — avoids soft upscaling on 125%/150% displays.
    """
    svg = icon_path(name)
    empty = QPixmap(size, size)
    empty.fill(QColor(0, 0, 0, 0))
    if not svg.exists():
        return empty

    dpr = _device_pixel_ratio()
    pixel = max(1, int(round(size * dpr)))
    try:
        xml = svg.read_text(encoding="utf-8")
        if color:
            xml = _tint_svg(xml, color, thicken=True)
        renderer = QSvgRenderer(QByteArray(xml.encode("utf-8")))
        if not renderer.isValid():
            return empty
        pm = QPixmap(pixel, pixel)
        pm.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        # Slight inset so thick strokes aren't clipped at edges.
        pad = max(1.0, pixel * 0.06)
        renderer.render(painter, QRectF(pad, pad, pixel - 2 * pad, pixel - 2 * pad))
        painter.end()
        pm.setDevicePixelRatio(dpr)
        return pm
    except Exception:
        return empty


def qicon(name: str, size: int = 20, color: str = None) -> QIcon:
    """Load local Ant-style SVG as QIcon (QtSvg plugin). Optional color tint."""
    svg = icon_path(name)
    if not svg.exists():
        return QIcon()
    if not color:
        return QIcon(str(svg))
    try:
        return QIcon(icon_pixmap(name, size=size, color=color))
    except Exception:
        return QIcon(str(svg))


def nav_icon(key: str, size: int = 20) -> QIcon:
    return qicon(NAV_ICON.get(key, "file-text"), size=size)


def icon_size(px: int = 20) -> QSize:
    return QSize(px, px)
