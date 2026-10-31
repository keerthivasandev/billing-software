"""In-process session after login (current user + chrome labels)."""

from __future__ import annotations

_current_user: dict | None = None


def set_user(user: dict | None) -> None:
    global _current_user
    _current_user = dict(user) if user else None


def current_user() -> dict | None:
    return dict(_current_user) if _current_user else None


def clear() -> None:
    set_user(None)
