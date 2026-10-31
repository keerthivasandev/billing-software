"""Product master."""

from __future__ import annotations

from app.db.connection import get_connection
from app.services import groups as groups_svc


def _stock_qty(conn, product_id: int, opening: float) -> float:
    row = conn.execute(
        "SELECT COALESCE(SUM(qty), 0) AS q FROM godown_stock WHERE product_id = ?",
        (product_id,),
    ).fetchone()
    moved = float(row["q"] or 0)
    if moved:
        return moved
    return float(opening or 0)


def _row_to_ui(row, group_name: str, warehouse: str, stock: float) -> dict:
    sale = float(row["sale_rate"] or 0)
    return {
        "id": row["id"],
        "sku": row["sku"],
        "name": row["name"],
        "group": group_name,
        "group_id": row["group_id"],
        "hsn": row["hsn"] or "",
        "unit": row["unit"],
        "sale_rate": sale,
        "purchase_rate": float(row["purchase_rate"] or 0),
        "gst": float(row["gst_pct"] or 0),
        "stock": stock,
        "warehouse": warehouse or "",
        "min_stock": float(row["min_stock"] or 0),
        "opening_qty": float(row["opening_qty"] or 0),
        "rate": sale,
        "active": bool(row["is_active"]),
        "default_godown_id": row["default_godown_id"],
    }


def list_products() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.*, g.name AS group_name, gd.name AS godown_name
            FROM product p
            JOIN groups g ON g.id = p.group_id
            LEFT JOIN godown gd ON gd.id = p.default_godown_id
            ORDER BY p.id
            """
        ).fetchall()
        out = []
        for r in rows:
            stock = _stock_qty(conn, r["id"], r["opening_qty"])
            out.append(_row_to_ui(r, r["group_name"], r["godown_name"] or "", stock))
        return out


def get_product(product_id: int) -> dict | None:
    for p in list_products():
        if p["id"] == product_id:
            return p
    return None


def create_product(data: dict) -> dict:
    group_name = data.get("group") or "General"
    gid = groups_svc.ensure_group(group_name, "product", float(data.get("gst") or 18))
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO product (
              sku, name, group_id, hsn, unit, sale_rate, purchase_rate, gst_pct,
              min_stock, opening_qty, default_godown_id, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("sku") or f"SKU-{data['name'][:8].upper()}",
                data["name"].strip(),
                gid,
                data.get("hsn") or None,
                data.get("unit") or "Pcs",
                float(data.get("sale_rate") or data.get("rate") or 0),
                float(data.get("purchase_rate") or 0),
                float(data.get("gst") or 18),
                float(data.get("min_stock") or 0),
                float(data.get("opening_qty") or data.get("stock") or 0),
                data.get("default_godown_id"),
                1 if data.get("active", True) else 0,
            ),
        )
        conn.commit()
        pid = cur.lastrowid
        # seed opening into default godown if any
        opening = float(data.get("opening_qty") or data.get("stock") or 0)
        gd = data.get("default_godown_id")
        if gd and opening:
            conn.execute(
                """
                INSERT INTO godown_stock (godown_id, product_id, qty)
                VALUES (?, ?, ?)
                ON CONFLICT(godown_id, product_id) DO UPDATE SET qty = excluded.qty
                """,
                (gd, pid, opening),
            )
            conn.commit()
    return get_product(pid)


def update_product(product_id: int, data: dict) -> dict:
    group_name = data.get("group") or "General"
    gid = groups_svc.ensure_group(group_name, "product", float(data.get("gst") or 18))
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE product SET
              sku = ?, name = ?, group_id = ?, hsn = ?, unit = ?,
              sale_rate = ?, purchase_rate = ?, gst_pct = ?,
              min_stock = ?, opening_qty = ?, default_godown_id = ?, is_active = ?,
              updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                data.get("sku"),
                data["name"].strip(),
                gid,
                data.get("hsn") or None,
                data.get("unit") or "Pcs",
                float(data.get("sale_rate") or data.get("rate") or 0),
                float(data.get("purchase_rate") or 0),
                float(data.get("gst") or 18),
                float(data.get("min_stock") or 0),
                float(data.get("opening_qty") or 0),
                data.get("default_godown_id"),
                1 if data.get("active", True) else 0,
                product_id,
            ),
        )
        conn.commit()
    return get_product(product_id)


def delete_product(product_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM godown_stock WHERE product_id = ?", (product_id,))
        conn.execute("DELETE FROM product WHERE id = ?", (product_id,))
        conn.commit()
