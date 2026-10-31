"""Godown master + stock lines."""

from __future__ import annotations

from app.db.connection import get_connection
from app.services import groups as groups_svc


def _row_to_ui(row, item_count: int) -> dict:
    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "ref_id": row["ref_id"] or "",
        "group_id": row["group_id"],
        "incharge": row["incharge"] or "",
        "phone": row["phone"] or "",
        "alt_phone": row["alt_phone"] or "",
        "address": row["address"] or "",
        "location_label": row["location_label"] or "",
        "pin_zone": row["pin_zone"] or "",
        "item_count": item_count,
        "status": row["status"] or ("Primary / Active" if row["is_default"] else "Active"),
        "role_tag": row["role_tag"] or "",
        "active": bool(row["is_active"]),
        "is_default": bool(row["is_default"]),
        "icon": "location_on" if row["is_default"] else "warehouse",
    }


def list_godowns() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM godown ORDER BY id").fetchall()
        out = []
        for r in rows:
            cnt = int(
                conn.execute(
                    "SELECT COUNT(*) FROM godown_stock WHERE godown_id = ? AND qty > 0",
                    (r["id"],),
                ).fetchone()[0]
            )
            out.append(_row_to_ui(r, cnt))
        return out


def get_godown(godown_id: int) -> dict | None:
    for g in list_godowns():
        if g["id"] == godown_id:
            return g
    return None


def stock_for(godown_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT gs.qty, p.sku, p.name, p.unit, p.sale_rate, g.name AS group_name
            FROM godown_stock gs
            JOIN product p ON p.id = gs.product_id
            JOIN groups g ON g.id = p.group_id
            WHERE gs.godown_id = ?
            ORDER BY p.name
            """,
            (godown_id,),
        ).fetchall()
    return [
        {
            "sku": r["sku"],
            "name": r["name"],
            "group": r["group_name"],
            "qty": float(r["qty"] or 0),
            "unit": r["unit"],
            "value": float(r["qty"] or 0) * float(r["sale_rate"] or 0),
        }
        for r in rows
    ]


def create_godown(data: dict) -> dict:
    group_name = data.get("group") or data.get("role_tag") or "Primary"
    gid = groups_svc.ensure_group(group_name, "godown")
    with get_connection() as conn:
        n = int(conn.execute("SELECT COUNT(*) FROM godown").fetchone()[0]) + 1
        code = data.get("code") or f"GDN-{n:02d}"
        is_default = 1 if data.get("is_default") else (1 if n == 1 else 0)
        if is_default:
            conn.execute("UPDATE godown SET is_default = 0")
        cur = conn.execute(
            """
            INSERT INTO godown (
              code, name, ref_id, group_id, incharge, phone, alt_phone, address,
              location_label, pin_zone, role_tag, status, is_default, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                data["name"].strip(),
                data.get("ref_id") or None,
                gid,
                data.get("incharge") or None,
                data.get("phone") or None,
                data.get("alt_phone") or None,
                data.get("address") or None,
                data.get("location_label") or None,
                data.get("pin_zone") or None,
                data.get("role_tag") or None,
                data.get("status") or None,
                is_default,
                1 if data.get("active", True) else 0,
            ),
        )
        conn.commit()
        return get_godown(cur.lastrowid)


def update_godown(godown_id: int, data: dict) -> dict:
    with get_connection() as conn:
        if data.get("is_default"):
            conn.execute("UPDATE godown SET is_default = 0")
        conn.execute(
            """
            UPDATE godown SET
              code = ?, name = ?, ref_id = ?, incharge = ?, phone = ?, alt_phone = ?,
              address = ?, location_label = ?, pin_zone = ?, role_tag = ?, status = ?,
              is_default = ?, is_active = ?
            WHERE id = ?
            """,
            (
                data.get("code"),
                data["name"].strip(),
                data.get("ref_id") or None,
                data.get("incharge") or None,
                data.get("phone") or None,
                data.get("alt_phone") or None,
                data.get("address") or None,
                data.get("location_label") or None,
                data.get("pin_zone") or None,
                data.get("role_tag") or None,
                data.get("status") or None,
                1 if data.get("is_default") else 0,
                1 if data.get("active", True) else 0,
                godown_id,
            ),
        )
        conn.commit()
    return get_godown(godown_id)


def delete_godown(godown_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM godown_stock WHERE godown_id = ?", (godown_id,))
        conn.execute("DELETE FROM godown WHERE id = ?", (godown_id,))
        conn.commit()
