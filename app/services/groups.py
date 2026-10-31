"""Groups master (product / ledger / godown kinds)."""

from __future__ import annotations

from app.db.connection import get_connection


def _parent_label(parent_id, parents: dict) -> str:
    if not parent_id:
        return "Primary / Top-Level [Root]"
    p = parents.get(parent_id)
    return p["name"] if p else "Primary / Top-Level [Root]"


def _item_count(conn, kind: str, group_id: int) -> int:
    if kind == "product":
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM product WHERE group_id = ?", (group_id,)
            ).fetchone()[0]
        )
    if kind == "ledger":
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM ledger WHERE group_id = ?", (group_id,)
            ).fetchone()[0]
        )
    if kind == "godown":
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM godown WHERE group_id = ?", (group_id,)
            ).fetchone()[0]
        )
    return 0


def list_groups(kind: str | None = None) -> list[dict]:
    with get_connection() as conn:
        if kind:
            rows = conn.execute(
                "SELECT * FROM groups WHERE kind = ? ORDER BY id", (kind,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM groups ORDER BY id").fetchall()
        by_id = {r["id"]: r for r in rows}
        # also need all for parent names
        all_rows = conn.execute("SELECT id, name FROM groups").fetchall()
        parents = {r["id"]: r for r in all_rows}
        out = []
        for r in rows:
            out.append(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "gst": float(r["gst_pct"] or 0),
                    "parent": _parent_label(r["parent_id"], parents),
                    "parent_id": r["parent_id"],
                    "kind": r["kind"],
                    "active": bool(r["is_active"]),
                    "notes": r["notes"] or "",
                    "item_count": _item_count(conn, r["kind"], r["id"]),
                }
            )
        return out


def list_names(kind: str) -> list[str]:
    return [g["name"] for g in list_groups(kind)]


def ensure_group(name: str, kind: str, gst: float = 0) -> int:
    """Return group id, creating if missing."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM groups WHERE kind = ? AND lower(name) = lower(?)",
            (kind, name.strip()),
        ).fetchone()
        if row:
            return int(row["id"])
        cur = conn.execute(
            "INSERT INTO groups (kind, name, gst_pct, is_active) VALUES (?, ?, ?, 1)",
            (kind, name.strip(), gst),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_id_by_name(name: str, kind: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM groups WHERE kind = ? AND lower(name) = lower(?)",
            (kind, name.strip()),
        ).fetchone()
    return int(row["id"]) if row else None


def create_group(data: dict) -> dict:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO groups (kind, name, parent_id, gst_pct, notes, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("kind") or "product",
                data["name"].strip(),
                data.get("parent_id"),
                float(data.get("gst") or data.get("gst_pct") or 0),
                data.get("notes") or None,
                1 if data.get("active", True) else 0,
            ),
        )
        conn.commit()
        gid = cur.lastrowid
    return next(g for g in list_groups() if g["id"] == gid)


def update_group(group_id: int, data: dict) -> dict:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE groups SET name = ?, parent_id = ?, gst_pct = ?, notes = ?, is_active = ?
            WHERE id = ?
            """,
            (
                data["name"].strip(),
                data.get("parent_id"),
                float(data.get("gst") or data.get("gst_pct") or 0),
                data.get("notes") or None,
                1 if data.get("active", True) else 0,
                group_id,
            ),
        )
        conn.commit()
    return next(g for g in list_groups() if g["id"] == group_id)


def delete_group(group_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
