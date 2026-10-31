"""Cash flow register."""

from __future__ import annotations

from datetime import date

from app.db.connection import get_connection
from app.services import years as years_svc


def list_entries() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.*, l.name AS ledger_name
            FROM cash_entry c
            LEFT JOIN ledger l ON l.id = c.ledger_id
            ORDER BY c.entry_date DESC, c.id DESC
            """
        ).fetchall()
    return [
        {
            "id": r["id"],
            "date": r["entry_date"],
            "time": r["entry_time"] or "",
            "kind": r["kind"],
            "mode": r["mode"] or "Cash",
            "ref": r["ref_no"],
            "party": r["party_name"] or r["ledger_name"] or "",
            "purpose": r["purpose"] or "",
            "amount": float(r["amount"] or 0),
            "ledger_id": r["ledger_id"],
            "voucher_id": r["voucher_id"],
        }
        for r in rows
    ]


def kpi() -> dict:
    entries = list_entries()
    cash_in = sum(e["amount"] for e in entries if e["kind"] == "In")
    cash_out = sum(e["amount"] for e in entries if e["kind"] == "Out")
    return {
        "opening": 0.0,
        "cash_in": cash_in,
        "cash_out": cash_out,
        "remaining": cash_in - cash_out,
    }


def next_ref(kind: str) -> str:
    prefix = "CSH-IN-" if kind == "In" else "CSH-OUT-"
    with get_connection() as conn:
        n = int(
            conn.execute(
                "SELECT COUNT(*) FROM cash_entry WHERE kind = ?", (kind,)
            ).fetchone()[0]
        )
    return f"{prefix}{n + 1:03d}"


def create_entry(data: dict, created_by: int | None = None) -> dict:
    year_id = years_svc.get_current_year_id()
    if year_id is None:
        today = date.today()
        start_year = today.year if today.month >= 4 else today.year - 1
        years_svc.ensure_current_year(
            f"FY {start_year}–{str(start_year + 1)[-2:]}",
            f"{start_year}-04-01",
            f"{start_year + 1}-03-31",
        )
        year_id = years_svc.get_current_year_id()

    kind = data.get("kind") or "In"
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO cash_entry (
              ac_year_id, entry_date, entry_time, kind, mode, ref_no,
              ledger_id, party_name, purpose, amount, voucher_id, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                year_id,
                data.get("date") or date.today().isoformat(),
                data.get("time"),
                kind,
                data.get("mode") or "Cash",
                data.get("ref") or next_ref(kind),
                data.get("ledger_id"),
                data.get("party") or data.get("party_name"),
                data.get("purpose"),
                float(data["amount"]),
                data.get("voucher_id"),
                created_by,
            ),
        )
        conn.commit()
        eid = cur.lastrowid
    return next(e for e in list_entries() if e["id"] == eid)
