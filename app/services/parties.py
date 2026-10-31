"""Ledger / party master."""

from __future__ import annotations

from app.db.connection import get_connection
from app.services import groups as groups_svc


def _row_to_ui(row, group_name: str) -> dict:
    bal = float(row["opening_balance"] or 0)
    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "short_name": row["short_name"] or row["name"],
        "type": row["party_type"],
        "group": group_name,
        "group_id": row["group_id"],
        "contact_person": row["contact_person"] or "",
        "gstin": row["gstin"] or "",
        "state_code": row["state_code"] or "",
        "phone": row["phone"] or "",
        "address": row["address"] or "",
        "city": row["city"] or "",
        "balance": bal,
        "balance_type": row["opening_type"] or "Dr",
        "opening_balance": bal,
        "credit_limit": float(row["credit_limit"] or 0),
        "credit_days": int(row["credit_days"] or 0),
        "active": bool(row["is_active"]),
        "whatsapp": bool(row["whatsapp"]),
    }


def list_parties() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT l.*, g.name AS group_name
            FROM ledger l
            JOIN groups g ON g.id = l.group_id
            ORDER BY l.id
            """
        ).fetchall()
    return [_row_to_ui(r, r["group_name"]) for r in rows]


def get_party(party_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT l.*, g.name AS group_name
            FROM ledger l
            JOIN groups g ON g.id = l.group_id
            WHERE l.id = ?
            """,
            (party_id,),
        ).fetchone()
    return _row_to_ui(row, row["group_name"]) if row else None


def _next_code(conn) -> str:
    n = int(conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]) + 1
    return f"SLE-PTY-{n:04d}"


def create_party(data: dict) -> dict:
    group_name = data.get("group") or (
        "Sundry Debtor" if data.get("type") == "Customer" else "Sundry Creditor"
    )
    kind = "ledger"
    # map UI names
    if "debtor" in group_name.lower():
        group_name = "Sundry Debtors" if "Sundry" in group_name or True else group_name
    # Prefer exact name from data
    group_name = data.get("group") or group_name
    if group_name == "Sundry Debtor":
        group_name = "Sundry Debtors"
    if group_name == "Sundry Creditor":
        group_name = "Sundry Creditors"
    gid = groups_svc.ensure_group(group_name, kind)

    with get_connection() as conn:
        code = data.get("code") or _next_code(conn)
        cur = conn.execute(
            """
            INSERT INTO ledger (
              code, name, short_name, party_type, group_id, contact_person, gstin,
              state_code, phone, whatsapp, address, city, opening_balance, opening_type,
              credit_limit, credit_days, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                data["name"].strip(),
                data.get("short_name") or data["name"].strip(),
                data.get("type") or "Customer",
                gid,
                data.get("contact_person") or None,
                data.get("gstin") or None,
                data.get("state_code") or None,
                data.get("phone") or None,
                1 if data.get("whatsapp") else 0,
                data.get("address") or None,
                data.get("city") or None,
                float(data.get("opening_balance") or data.get("balance") or 0),
                data.get("balance_type") or data.get("opening_type") or "Dr",
                float(data.get("credit_limit") or 0),
                int(data.get("credit_days") or 0),
                1 if data.get("active", True) else 0,
            ),
        )
        conn.commit()
        pid = cur.lastrowid
    return get_party(pid)


def update_party(party_id: int, data: dict) -> dict:
    group_name = data.get("group") or "Sundry Debtors"
    if group_name == "Sundry Debtor":
        group_name = "Sundry Debtors"
    if group_name == "Sundry Creditor":
        group_name = "Sundry Creditors"
    gid = groups_svc.ensure_group(group_name, "ledger")
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE ledger SET
              name = ?, short_name = ?, party_type = ?, group_id = ?,
              contact_person = ?, gstin = ?, state_code = ?, phone = ?, whatsapp = ?,
              address = ?, city = ?, opening_balance = ?, opening_type = ?,
              credit_limit = ?, credit_days = ?, is_active = ?,
              updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                data["name"].strip(),
                data.get("short_name") or data["name"].strip(),
                data.get("type") or "Customer",
                gid,
                data.get("contact_person") or None,
                data.get("gstin") or None,
                data.get("state_code") or None,
                data.get("phone") or None,
                1 if data.get("whatsapp") else 0,
                data.get("address") or None,
                data.get("city") or None,
                float(data.get("opening_balance") or data.get("balance") or 0),
                data.get("balance_type") or data.get("opening_type") or "Dr",
                float(data.get("credit_limit") or 0),
                int(data.get("credit_days") or 0),
                1 if data.get("active", True) else 0,
                party_id,
            ),
        )
        conn.commit()
    return get_party(party_id)


def delete_party(party_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM ledger WHERE id = ?", (party_id,))
        conn.commit()


def party_vouchers(party_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT doc_date, voucher_type, doc_no, net_amount, balance_amount, status
            FROM voucher WHERE ledger_id = ? ORDER BY doc_date DESC, id DESC
            """,
            (party_id,),
        ).fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "date": r["doc_date"],
                "voucher_type": r["voucher_type"],
                "voucher_no": r["doc_no"],
                "voucher": f"{r['voucher_type']} #{r['doc_no']}",
                "amount": float(r["net_amount"] or 0),
                "balance": float(r["balance_amount"] or 0),
                "status": r["status"] or "",
            }
        )
    return out
