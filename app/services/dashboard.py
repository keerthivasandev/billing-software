"""Dashboard aggregates from live tables."""

from __future__ import annotations

from datetime import date

from app.db.connection import get_connection
from app.services import vouchers as vouchers_svc
from app.services import products as products_svc
from app.services import settlements as settlements_svc


def kpi() -> dict:
    today = date.today().isoformat()
    with get_connection() as conn:
        sales = conn.execute(
            """
            SELECT COALESCE(SUM(net_amount), 0) FROM voucher
            WHERE voucher_type = 'sale' AND doc_date = ?
            """,
            (today,),
        ).fetchone()[0]
        purchases = conn.execute(
            """
            SELECT COALESCE(SUM(net_amount), 0) FROM voucher
            WHERE voucher_type = 'purchase' AND doc_date = ?
            """,
            (today,),
        ).fetchone()[0]
        receipts = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) FROM cash_entry
            WHERE kind = 'In' AND entry_date = ?
            """,
            (today,),
        ).fetchone()[0]
        outstanding = conn.execute(
            "SELECT COALESCE(SUM(balance_amount), 0) FROM voucher WHERE balance_amount > 0"
        ).fetchone()[0]
        inv_count = conn.execute(
            """
            SELECT COUNT(*) FROM voucher
            WHERE voucher_type = 'sale' AND doc_date = ?
            """,
            (today,),
        ).fetchone()[0]
    return {
        "todays_sales": float(sales or 0),
        "todays_purchases": float(purchases or 0),
        "todays_receipts": float(receipts or 0),
        "outstanding": float(outstanding or 0),
        "invoice_count": int(inv_count or 0),
    }


def todays_invoices() -> list[dict]:
    today = date.today().isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT v.doc_no, v.net_amount, l.name AS party_name
            FROM voucher v
            JOIN ledger l ON l.id = v.ledger_id
            WHERE v.voucher_type = 'sale' AND v.doc_date = ?
            ORDER BY v.id DESC LIMIT 10
            """,
            (today,),
        ).fetchall()
    return [
        {"doc": r["doc_no"], "party": r["party_name"], "amount": float(r["net_amount"] or 0)}
        for r in rows
    ]


def low_stock_alerts() -> list[dict]:
    alerts = []
    for p in products_svc.list_products():
        if p["stock"] <= p["min_stock"] and p["min_stock"] > 0:
            alerts.append(
                {
                    "name": p["name"],
                    "note": f"Godown: {p['warehouse'] or '—'} · Reorder trigger hit",
                    "stock": f"{p['stock']:g} {p['unit']} (Min: {p['min_stock']:g})",
                }
            )
    return alerts


def pending_overdue() -> list[dict]:
    out = []
    for r in settlements_svc.outstanding("receivable"):
        if r["overdue"]:
            out.append(
                {
                    "party": r["party"],
                    "note": f"{r['days']} Days Overdue · {r['bill']}",
                    "amount": r["balance"],
                    "actions": ["Call", "WA"],
                }
            )
    return out


def build_snapshot() -> dict:
    k = kpi()
    alerts = low_stock_alerts()
    overdue = pending_overdue()
    return {
        "DASHBOARD_KPI": k,
        "TODAYS_INVOICES": todays_invoices(),
        "LOW_STOCK_ALERTS": alerts,
        "LOW_STOCK_ITEMS": [{"name": a["name"], "left": 0, "out": False} for a in alerts],
        "PENDING_OVERDUE": overdue,
        "PENDING_COLLECTIONS": [
            {"party": p["party"], "note": p["note"], "amount": p["amount"]} for p in overdue
        ],
        "RECENT_TXNS": vouchers_svc.recent_txns(),
        "FAST_LOOKUP_ITEMS": [],
        "TOP_SELLING": [],
        "TOP_STOCKED_QTY": [],
        "TOP_STOCKED_VALUE": [],
        "SALES_BY_CHANNEL": {"counter_cash": 0, "credit": 0},
        "PENDING_ACTIONS": {
            "sales": [],
            "purchases": [],
            "inventory": [("Below Reorder Level", len(alerts))] if alerts else [],
        },
        "COUNTER_SUMMARY": [
            ("Today's Sales", k["todays_sales"]),
            ("Invoices", float(k["invoice_count"])),
            ("Outstanding", k["outstanding"]),
        ],
    }
