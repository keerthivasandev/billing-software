"""Accounting year partitions."""

from __future__ import annotations

from datetime import datetime

from app.db.connection import get_connection


def _fmt_period(start: str, end: str) -> str:
    def _d(s: str) -> str:
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            return s

    return f"{_d(start)} to {_d(end)}"


def _fmt_period_dash(start: str, end: str) -> str:
    return _fmt_period(start, end).replace(" to ", " – ")


def voucher_count(conn, year_id: int) -> int:
    return int(
        conn.execute(
            "SELECT COUNT(*) FROM voucher WHERE ac_year_id = ?", (year_id,)
        ).fetchone()[0]
    )


def list_years() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM accounting_year ORDER BY period_start DESC"
        ).fetchall()
        out = []
        for r in rows:
            status = r["status"] or "archived"
            locked = bool(r["is_locked"]) or status != "current"
            is_current = status == "current"
            out.append(
                {
                    "id": r["id"],
                    "code": r["code"],
                    "status": "Current" if is_current else "Archived",
                    "partition": r["partition"] or "",
                    "period": _fmt_period_dash(r["period_start"], r["period_end"]),
                    "period_start": r["period_start"],
                    "period_end": r["period_end"],
                    "vouchers": voucher_count(conn, r["id"]),
                    "access": "Unlocked (Active)" if not locked else "Locked (Audit)",
                    "locked": locked,
                }
            )
        return out


def active_year() -> dict | None:
    years = list_years()
    for y in years:
        if y["status"] == "Current":
            return {
                "id": y["id"],
                "code": y["code"],
                "period": y["period"].replace(" – ", " to "),
                "partition": y["partition"],
                "vouchers": y["vouchers"],
                "schema": y["code"],
                "terminal": "Terminal-01 (Main Counter)",
            }
    return None


def ensure_current_year(
    code: str,
    period_start: str,
    period_end: str,
    partition: str | None = None,
) -> dict:
    with get_connection() as conn:
        conn.execute(
            "UPDATE accounting_year SET status = 'archived', is_locked = 1 WHERE status = 'current'"
        )
        cur = conn.execute(
            """
            INSERT INTO accounting_year (code, period_start, period_end, partition, status, is_locked)
            VALUES (?, ?, ?, ?, 'current', 0)
            """,
            (code, period_start, period_end, partition),
        )
        conn.commit()
        yid = cur.lastrowid
    years = list_years()
    return next(y for y in years if y["id"] == yid)


def get_current_year_id() -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM accounting_year WHERE status = 'current' LIMIT 1"
        ).fetchone()
    return int(row["id"]) if row else None
