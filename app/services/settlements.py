"""Billwise settlements / outstanding."""

from __future__ import annotations

from datetime import date, datetime

from app.db.connection import get_connection
from app.services import years as years_svc


def _days_since(doc_date: str) -> int:
    try:
        d = datetime.strptime(doc_date[:10], "%Y-%m-%d").date()
        return (date.today() - d).days
    except ValueError:
        return 0


def outstanding(kind: str = "receivable") -> list[dict]:
    """kind: receivable (customer sales) or payable (supplier purchases)."""
    if kind == "receivable":
        types = ("sale",)
        party_type = "Customer"
    else:
        types = ("purchase",)
        party_type = "Supplier"

    placeholders = ",".join("?" for _ in types)
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT v.doc_no, v.doc_date, v.net_amount, v.balance_amount, l.name AS party_name,
                   l.credit_days
            FROM voucher v
            JOIN ledger l ON l.id = v.ledger_id
            WHERE v.voucher_type IN ({placeholders})
              AND v.balance_amount > 0.009
              AND l.party_type = ?
            ORDER BY v.doc_date
            """,
            (*types, party_type),
        ).fetchall()
    out = []
    for r in rows:
        days = _days_since(r["doc_date"])
        credit = int(r["credit_days"] or 0)
        overdue = days > credit if credit else days > 30
        out.append(
            {
                "party": r["party_name"],
                "bill": r["doc_no"],
                "date": r["doc_date"],
                "due": r["doc_date"],
                "amount": float(r["net_amount"] or 0),
                "balance": float(r["balance_amount"] or 0),
                "days": max(0, days - credit) if overdue else max(0, credit - days),
                "overdue": overdue,
            }
        )
    return out


def create_settlement(
    *,
    kind: str,
    ledger_id: int,
    mode: str,
    total_amount: float,
    allocations: list[dict],
    ref_no: str | None = None,
    settle_date: str | None = None,
    created_by: int | None = None,
) -> int:
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

    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO settlement (
              ac_year_id, settle_date, kind, ledger_id, mode, ref_no, total_amount, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                year_id,
                settle_date or date.today().isoformat(),
                kind,
                ledger_id,
                mode,
                ref_no,
                total_amount,
                created_by,
            ),
        )
        sid = cur.lastrowid
        for a in allocations:
            amt = float(a["allocated_amount"])
            vid = int(a["voucher_id"])
            conn.execute(
                """
                INSERT INTO settlement_allocation (settlement_id, voucher_id, allocated_amount)
                VALUES (?, ?, ?)
                """,
                (sid, vid, amt),
            )
            conn.execute(
                """
                UPDATE voucher SET
                  paid_amount = paid_amount + ?,
                  balance_amount = MAX(0, balance_amount - ?)
                WHERE id = ?
                """,
                (amt, amt, vid),
            )
        conn.commit()
    return sid
