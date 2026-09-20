"""Ant Design–style local SVG icons (lightweight, offline, potato-PC safe)."""

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

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
    """file:/// URL for QSS image: url(...)."""
    path = icon_path(name).resolve().as_posix()
    if not path.startswith("/"):
        path = "/" + path
    return f"file://{path}"


def qicon(name: str, size: int = 20, color: str = None) -> QIcon:
    """Load local Ant-style SVG as QIcon (QtSvg plugin)."""
    svg = icon_path(name)
    if not svg.exists():
        return QIcon()
    return QIcon(str(svg))


def nav_icon(key: str, size: int = 20) -> QIcon:
    return qicon(NAV_ICON.get(key, "file-text"), size=size)


def icon_size(px: int = 20) -> QSize:
    return QSize(px, px)
