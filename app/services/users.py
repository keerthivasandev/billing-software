"""User CRUD + auth against the `user` table."""

from __future__ import annotations

from app.db.connection import get_connection
from app.security.passwords import hash_password, verify_password

_ROLE_PRIVILEGES = {
    "Admin": ["sales", "purchase", "cash", "master", "fy", "delete"],
    "Billing Clerk": ["sales", "purchase", "cash"],
    "Inventory Manager": ["purchase"],
    "Inventory Mgr": ["purchase"],
}


def _initials(name: str) -> str:
    parts = [p for p in (name or "").split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return (name or "??")[:2].upper()


def _role_meta(role: str) -> tuple[str, str, str]:
    role = (role or "Billing Clerk").strip()
    if role.lower().startswith("admin"):
        return "Admin", "Admin", "Admin (Full System Access)"
    if "inventory" in role.lower():
        return "Inventory Manager", "Inventory Mgr", "Inventory Manager (Godown Inward/Stock)"
    if "clerk" in role.lower() or "billing" in role.lower():
        return "Billing Clerk", "Billing Clerk", "Billing Clerk (POS Counter & Invoicing)"
    return role, role, role


def _terminal_meta(terminal: str | None) -> tuple[str, str, str]:
    t = terminal or "Terminal-01 (Main Counter)"
    short = (
        t.replace(" (Main Counter)", "")
        .replace(" (Back Office)", "")
        .replace(" (Stationary)", "")
    )
    icon = "warehouse" if "godown" in t.lower() else (
        "laptop_mac" if "back" in t.lower() else "desktop_windows"
    )
    return t, short, icon


def _row_to_ui(row) -> dict:
    role, role_label, role_full = _role_meta(row["role"])
    terminal, terminal_short, terminal_icon = _terminal_meta(row["terminal"])
    privs = list(_ROLE_PRIVILEGES.get(role, ["sales"]))
    if role == "Admin":
        privs = list(_ROLE_PRIVILEGES["Admin"])
    return {
        "id": row["id"],
        "initials": _initials(row["full_name"]),
        "username": row["username"],
        "name": row["full_name"],
        "role": role,
        "role_label": role_label,
        "role_full": role_full,
        "terminal": terminal,
        "terminal_short": terminal_short,
        "terminal_icon": terminal_icon,
        "mobile": row["mobile"] or "",
        "email": row["email"] or "",
        "last_login": "Login: —",
        "active": bool(row["is_active"]),
        "privileges": privs,
    }


def count_users() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM user").fetchone()[0])


def list_users() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM user ORDER BY id"
        ).fetchall()
    return [_row_to_ui(r) for r in rows]


def get_by_username(username: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user WHERE lower(username) = lower(?)",
            (username.strip(),),
        ).fetchone()
    return _row_to_ui(row) if row else None


def authenticate(username: str, password: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user WHERE lower(username) = lower(?)",
            (username.strip(),),
        ).fetchone()
    if row is None:
        return None
    if not row["is_active"]:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return _row_to_ui(row)


def create_admin(
    *,
    full_name: str,
    username: str,
    password: str,
    mobile: str = "",
    email: str = "",
    terminal: str = "Terminal-01 (Main Counter)",
) -> dict:
    if count_users() > 0:
        raise RuntimeError("Admin already exists")
    ph = hash_password(password)
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO user (username, full_name, password_hash, role, mobile, email, terminal, is_active)
            VALUES (?, ?, ?, 'Admin', ?, ?, ?, 1)
            """,
            (username.strip().lower(), full_name.strip(), ph, mobile or None, email or None, terminal),
        )
        conn.commit()
        uid = cur.lastrowid
        row = conn.execute("SELECT * FROM user WHERE id = ?", (uid,)).fetchone()
    return _row_to_ui(row)


def create_user(data: dict, password: str = "ChangeMe1!") -> dict:
    role = data.get("role") or "Billing Clerk"
    if "Admin" in (data.get("role_full") or ""):
        role = "Admin"
    ph = hash_password(password)
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO user (username, full_name, password_hash, role, mobile, email, terminal, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["username"].strip().lower(),
                data.get("name") or data.get("full_name") or data["username"],
                ph,
                role,
                data.get("mobile") or None,
                data.get("email") or None,
                data.get("terminal") or "Terminal-01 (Main Counter)",
                1 if data.get("active", True) else 0,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM user WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _row_to_ui(row)


def update_user(user_id: int, data: dict) -> dict:
    role = data.get("role") or "Billing Clerk"
    if "Admin" in (data.get("role_full") or ""):
        role = "Admin"
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE user SET
              full_name = ?, role = ?, mobile = ?, email = ?, terminal = ?, is_active = ?
            WHERE id = ?
            """,
            (
                data.get("name") or data.get("full_name"),
                role,
                data.get("mobile") or None,
                data.get("email") or None,
                data.get("terminal") or None,
                1 if data.get("active", True) else 0,
                user_id,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    return _row_to_ui(row)


def set_password(user_id: int, password: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE user SET password_hash = ? WHERE id = ?",
            (hash_password(password), user_id),
        )
        conn.commit()


def set_active(user_id: int, active: bool) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE user SET is_active = ? WHERE id = ?",
            (1 if active else 0, user_id),
        )
        conn.commit()


def delete_user(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()


def sync_users(users: list[dict]) -> None:
    """Persist directory edits: update existing, create missing, delete removed."""
    existing = {u["id"]: u for u in list_users()}
    keep_ids = set()
    for u in users:
        uid = u.get("id")
        if uid and uid in existing:
            update_user(uid, u)
            keep_ids.add(uid)
        else:
            created = create_user(u)
            keep_ids.add(created["id"])
            u["id"] = created["id"]
    for uid in existing:
        if uid not in keep_ids:
            delete_user(uid)
