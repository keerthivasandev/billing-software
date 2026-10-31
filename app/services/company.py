"""Company master (single-row)."""

from __future__ import annotations

from app.db.connection import get_connection

_EMPTY = {
    "legal_name": "",
    "trade_name": "",
    "entity_type": "",
    "address": "",
    "landmark": "",
    "city": "",
    "district": "",
    "pincode": "",
    "state_code": "",
    "phone": "",
    "mobile": "",
    "landline": "",
    "email": "",
    "contact_person": "",
    "gstin": "",
    "pan": "",
    "business_activity": "",
    "financial_year": "",
    "fy_display": "",
    "assessment_year": "",
    "city_display": "",
    "bank_name": "",
    "beneficiary": "",
    "account_no": "",
    "account_type": "",
    "ifsc": "",
    "branch": "",
    "upi": "",
    "invoice_note": "",
    "valid_from": "",
    "valid_to": "",
    "gst_filing_status": "",
    "einvoice_status": "",
    "terminal_id": "",
    "compliance_version": "",
    "distributor_status": "",
    "compliance_note": "",
    "einvoice_portal": "",
    "hsn_chapters": "",
    "tds_exemption": "",
}


def _enrich(d: dict) -> dict:
    city = d.get("city") or ""
    district = d.get("district") or ""
    if city and district:
        d["city_display"] = f"{city}, {district} District"
    elif city:
        d["city_display"] = city
    else:
        d["city_display"] = ""
    d.setdefault("financial_year", "")
    d.setdefault("fy_display", "")
    d.setdefault("assessment_year", "")
    d.setdefault("valid_from", "")
    d.setdefault("valid_to", "")
    d.setdefault("compliance_version", "")
    d.setdefault("distributor_status", "")
    d.setdefault("compliance_note", "")
    d.setdefault("einvoice_portal", "")
    d.setdefault("hsn_chapters", "")
    d.setdefault("tds_exemption", "")
    return d


def get_company() -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM company ORDER BY id LIMIT 1").fetchone()
    if row is None:
        return dict(_EMPTY)
    d = dict(_EMPTY)
    for k in row.keys():
        if k in d or k in (
            "legal_name", "trade_name", "entity_type", "address", "landmark",
            "city", "district", "pincode", "state_code", "phone", "mobile",
            "landline", "email", "contact_person", "gstin", "pan",
            "business_activity", "bank_name", "beneficiary", "account_no",
            "account_type", "ifsc", "branch", "upi", "invoice_note",
            "gst_filing_status", "einvoice_status", "terminal_id",
        ):
            val = row[k]
            d[k] = "" if val is None else str(val) if not isinstance(val, str) else val
    # keep numeric-ish as string already
    for k in row.keys():
        if k not in ("id", "updated_at") and k not in d:
            d[k] = row[k] if row[k] is not None else ""
    d["id"] = row["id"]
    return _enrich(d)


def display_name() -> str:
    c = get_company()
    return c.get("trade_name") or c.get("legal_name") or "—"


def save_company(data: dict) -> dict:
    fields = [
        "legal_name", "trade_name", "entity_type", "address", "landmark",
        "city", "district", "pincode", "state_code", "phone", "mobile",
        "landline", "email", "contact_person", "gstin", "pan",
        "business_activity", "bank_name", "beneficiary", "account_no",
        "account_type", "ifsc", "branch", "upi", "invoice_note",
        "gst_filing_status", "einvoice_status", "terminal_id",
    ]
    vals = {f: (data.get(f) or None) for f in fields}
    # legal_name is NOT NULL
    if not vals["legal_name"]:
        vals["legal_name"] = data.get("trade_name") or "My Company"

    with get_connection() as conn:
        row = conn.execute("SELECT id FROM company ORDER BY id LIMIT 1").fetchone()
        if row is None:
            cols = ", ".join(fields)
            placeholders = ", ".join("?" for _ in fields)
            conn.execute(
                f"INSERT INTO company ({cols}) VALUES ({placeholders})",
                [vals[f] for f in fields],
            )
        else:
            sets = ", ".join(f"{f} = ?" for f in fields)
            conn.execute(
                f"UPDATE company SET {sets}, updated_at = datetime('now') WHERE id = ?",
                [vals[f] for f in fields] + [row["id"]],
            )
        conn.commit()
    return get_company()
