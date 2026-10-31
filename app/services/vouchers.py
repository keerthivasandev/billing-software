"""Sales / purchase / estimate vouchers."""

from __future__ import annotations

from datetime import date

from app.db.connection import get_connection
from app.services import years as years_svc

# DB CHECK: sale|purchase|estimate|sales_return|purchase_return
_UI_TO_DB = {
    "Sale": "sale",
    "Tax Invoice": "sale",
    "sale": "sale",
    "Purchase": "purchase",
    "purchase": "purchase",
    "Estimate": "estimate",
    "estimate": "estimate",
    "Sales Return": "sales_return",
    "sales_return": "sales_return",
    "Purchase Return": "purchase_return",
    "purchase_return": "purchase_return",
}

_DB_TO_UI = {
    "sale": "Sale",
    "purchase": "Purchase",
    "estimate": "Estimate",
    "sales_return": "Sales Return",
    "purchase_return": "Purchase Return",
}


def normalize_type(voucher_type: str) -> str:
    return _UI_TO_DB.get(voucher_type, voucher_type.lower().replace(" ", "_"))


def display_type(voucher_type: str) -> str:
    return _DB_TO_UI.get(voucher_type, voucher_type)


def _history_row(r, party_name: str) -> dict:
    vt = display_type(r["voucher_type"])
    return {
        "date": r["doc_date"],
        "doc": r["doc_no"],
        "party": party_name,
        "amount": float(r["net_amount"] or 0),
        "status": r["status"] or "",
        "type": vt,
        "balance": float(r["balance_amount"] or 0),
        "paid": float(r["paid_amount"] or 0),
        "id": r["id"],
    }


def list_by_type(voucher_type: str) -> list[dict]:
    db_type = normalize_type(voucher_type)
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT v.*, l.name AS party_name
            FROM voucher v
            JOIN ledger l ON l.id = v.ledger_id
            WHERE v.voucher_type = ?
            ORDER BY v.doc_date DESC, v.id DESC
            """,
            (db_type,),
        ).fetchall()
    return [_history_row(r, r["party_name"]) for r in rows]


def sales_history() -> list[dict]:
    return list_by_type("sale")


def purchase_history() -> list[dict]:
    return list_by_type("purchase")


def estimates() -> list[dict]:
    return list_by_type("estimate")


def recent_txns(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT v.doc_date, v.voucher_type, v.doc_no, v.net_amount, l.name AS party_name
            FROM voucher v
            JOIN ledger l ON l.id = v.ledger_id
            ORDER BY v.doc_date DESC, v.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "date": r["doc_date"],
            "type": display_type(r["voucher_type"]),
            "doc": r["doc_no"],
            "party": r["party_name"],
            "amount": float(r["net_amount"] or 0),
        }
        for r in rows
    ]


def next_doc_no(voucher_type: str, prefix: str | None = None) -> str:
    db_type = normalize_type(voucher_type)
    prefix = prefix or {
        "sale": "SLE/",
        "purchase": "PUR/",
        "estimate": "EST/",
        "sales_return": "SR/",
        "purchase_return": "PR/",
    }.get(db_type, "DOC/")
    with get_connection() as conn:
        n = int(
            conn.execute(
                "SELECT COUNT(*) FROM voucher WHERE voucher_type = ?",
                (db_type,),
            ).fetchone()[0]
        )
    return f"{prefix}{n + 1:04d}"


def create_voucher(
    *,
    voucher_type: str,
    ledger_id: int,
    lines: list[dict],
    doc_date: str | None = None,
    godown_id: int | None = None,
    pay_mode: str | None = None,
    party_inv_no: str | None = None,
    notes: str | None = None,
    created_by: int | None = None,
    paid_amount: float = 0,
    doc_no: str | None = None,
) -> dict:
    db_type = normalize_type(voucher_type)
    year_id = years_svc.get_current_year_id()
    if year_id is None:
        today = date.today()
        start_year = today.year if today.month >= 4 else today.year - 1
        code = f"FY {start_year}–{str(start_year + 1)[-2:]}"
        years_svc.ensure_current_year(
            code,
            f"{start_year}-04-01",
            f"{start_year + 1}-03-31",
            partition=f"DATA_{start_year}",
        )
        year_id = years_svc.get_current_year_id()

    taxable = 0.0
    tax = 0.0
    for ln in lines:
        amt = float(ln.get("line_amount") or (float(ln["qty"]) * float(ln["rate"])))
        gst = float(ln.get("gst_pct") or ln.get("gst") or 0)
        taxable += amt
        tax += amt * gst / 100.0
    net = taxable + tax
    paid = float(paid_amount or 0)
    balance = max(0.0, net - paid)
    cgst = sgst = tax / 2.0
    doc_no = doc_no or next_doc_no(db_type)
    doc_date = doc_date or date.today().isoformat()

    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO voucher (
              ac_year_id, voucher_type, doc_no, doc_date, ledger_id, godown_id,
              party_inv_no, pay_mode, notes, taxable_amount, cgst_amount, sgst_amount,
              igst_amount, discount_amount, net_amount, paid_amount, balance_amount,
              status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, 'posted', ?)
            """,
            (
                year_id, db_type, doc_no, doc_date, ledger_id, godown_id,
                party_inv_no, pay_mode, notes, taxable, cgst, sgst, net, paid, balance,
                created_by,
            ),
        )
        vid = cur.lastrowid
        for i, ln in enumerate(lines, start=1):
            qty = float(ln["qty"])
            rate = float(ln["rate"])
            gst = float(ln.get("gst_pct") or ln.get("gst") or 0)
            disc = float(ln.get("discount_pct") or 0)
            line_amt = float(ln.get("line_amount") or qty * rate * (1 - disc / 100))
            conn.execute(
                """
                INSERT INTO voucher_line (
                  voucher_id, line_no, product_id, qty, unit, rate, discount_pct, gst_pct, line_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vid, i, int(ln["product_id"]), qty,
                    ln.get("unit") or "Pcs", rate, disc, gst, line_amt,
                ),
            )
            if godown_id and ln.get("product_id"):
                qty_in = qty if db_type in ("purchase", "sales_return") else 0
                qty_out = qty if db_type in ("sale", "purchase_return") else 0
                if qty_in or qty_out:
                    conn.execute(
                        """
                        INSERT INTO stock_movement (
                          ac_year_id, move_date, product_id, godown_id, qty_in, qty_out, ref_type, ref_id
                        ) VALUES (?, ?, ?, ?, ?, ?, 'voucher', ?)
                        """,
                        (year_id, doc_date, int(ln["product_id"]), godown_id, qty_in, qty_out, vid),
                    )
                    delta = qty_in - qty_out
                    conn.execute(
                        """
                        INSERT INTO godown_stock (godown_id, product_id, qty)
                        VALUES (?, ?, ?)
                        ON CONFLICT(godown_id, product_id) DO UPDATE
                        SET qty = qty + excluded.qty
                        """,
                        (godown_id, int(ln["product_id"]), delta),
                    )
        conn.commit()
    return {"id": vid, "doc_no": doc_no, "net_amount": net, "balance_amount": balance}
