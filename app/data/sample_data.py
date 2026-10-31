"""Runtime UI data facade — backed by SQLite (`data/data`), not demo fixtures.

Screens keep `from app.data import sample_data as D`. Call `D.reload()` after writes.
"""

from app.data import store as _store

# Re-export everything the UI reads
reload = _store.reload

COMPANY_TAGLINE = _store.COMPANY_TAGLINE
MACHINE_ID = _store.MACHINE_ID
LICENSE_STATUS = _store.LICENSE_STATUS
LICENSE = _store.LICENSE
USER_ROLES = _store.USER_ROLES
USER_TERMINALS = _store.USER_TERMINALS
USER_PRIVILEGES = _store.USER_PRIVILEGES
AC_YEAR_NEW = _store.AC_YEAR_NEW
TERMINAL_NAME = _store.TERMINAL_NAME
SERVER_STATUS = _store.SERVER_STATUS
SYNC_STATUS = _store.SYNC_STATUS
COUNTER_SHIFT_LABEL = _store.COUNTER_SHIFT_LABEL


def __getattr__(name: str):
    """Resolve module attrs from the live store (always current after reload)."""
    if hasattr(_store, name):
        return getattr(_store, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(dir(_store)))


# Initial load
_store.reload()
