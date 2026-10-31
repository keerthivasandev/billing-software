"""Load UI-facing dicts/lists from SQLite. Call reload() after writes."""

from __future__ import annotations

from app import session
from app.services import (
    cash as cash_svc,
    company as company_svc,
    dashboard as dash_svc,
    godowns as godowns_svc,
    groups as groups_svc,
    parties as parties_svc,
    products as products_svc,
    settlements as settlements_svc,
    users as users_svc,
    vouchers as vouchers_svc,
    years as years_svc,
)

# Static chrome / license placeholders (license gate wired later)
COMPANY_TAGLINE = "Wholesale Billing & ERP"
MACHINE_ID = "HW-LOCAL-NODE"
LICENSE_STATUS = "Pending"
LICENSE = {
    "status": "Not activated",
    "entity": "—",
    "entity_loc": "",
    "edition": "Enterprise Edition",
    "product_key": "—",
    "activated_at": "—",
    "expires_at": "—",
    "grace_days": 0,
    "features": [],
    "hw_signature": MACHINE_ID,
    "hw_matched": False,
    "ip_binding": "Local",
    "last_verified": "—",
    "partner": "—",
    "partner_address": "",
    "helpline": "",
    "hours": "",
    "footer": "Activate license from Settings → License",
}

USER_ROLES = [
    "Billing Clerk (POS Counter & Invoicing)",
    "Admin (Full System Access)",
    "Inventory Manager (Godown Inward/Stock)",
    "Custom Operator",
]
USER_TERMINALS = [
    "Terminal-01 (Main Counter)",
    "Terminal-02 (Back Office)",
    "Godown Desk (Stationary)",
    "Floating / Any Authorized Terminal",
]
USER_PRIVILEGES = [
    ("sales", "Create & Print Sales Invoices (F2)",
     "Counter POS billing and print duplicate receipts", False),
    ("purchase", "Inward Purchase Entry & GRN (F3)",
     "Enter supplier vouchers and godown receipts", False),
    ("cash", "Record Cash Flow & Receipt Slips",
     "Counter cash drawer settlement & voucher logging", False),
    ("master", "Modify Master Company GSTIN / Bank",
     "[Admin Only - Locked]", True),
    ("fy", "Create / Close Accounting Fiscal Year",
     "[Admin Only - Locked]", True),
    ("delete", "Delete Invoices / Adjust Stock Ledgers",
     "[Admin Only - Locked]", True),
]

AC_YEAR_NEW = {
    "code": "",
    "period": "",
    "sales_prefix": "",
    "purchase_prefix": "",
}

TERMINAL_NAME = "Terminal-01 (Main Counter)"
SERVER_STATUS = "Server: Local SQLite"
SYNC_STATUS = "Sync: Local"
COUNTER_SHIFT_LABEL = "Shift: 08:30 AM - Ongoing"


def _dashboard_demo() -> dict:
    """Stitch dashboard fixtures — temporary until live KPI wiring is finished."""
    low_stock = [
        {
            "name": "Philips 20W LED Batten 4ft Cool Day",
            "note": "Godown: Main Shelf B2 · Reorder trigger hit",
            "stock": "8 NOS (Min: 25)",
        },
        {
            "name": "Finolex 1.5 sq mm Blue FR Wire 90M",
            "note": "Godown: Cable Bay C1 · Fast moving",
            "stock": "12 ROL (Min: 30)",
        },
        {
            "name": "Schneider 16A 1-Way Modular Switch",
            "note": "Godown: Box Rack D4 · Regular order",
            "stock": "15 NOS (Min: 50)",
        },
    ]
    overdue = [
        {
            "party": "Balaji Electricals",
            "note": "6 Days Overdue · Inv #791",
            "amount": 13250.00,
            "actions": ["Call", "WA"],
        },
        {
            "party": "Venkateshwara Wires",
            "note": "Due Today · Net 15 terms",
            "amount": 48500.00,
            "actions": ["Reminder"],
        },
        {
            "party": "Polycab Local Agency",
            "note": "3 Days Overdue · Inv #812",
            "amount": 22000.00,
            "actions": ["Reminder"],
        },
    ]
    return {
        "DASHBOARD_WELCOME": "Welcome back",
        "DASHBOARD_SHIFT": (
            "Main Wholesale Counter · Shift active since 08:30 AM · Auto-sync: Active"
        ),
        "COUNTER_SHIFT_LABEL": "Shift: 08:30 AM - Ongoing",
        "DASHBOARD_KPI": {
            "todays_sales": 148250.00,
            "todays_purchases": 86400.00,
            "cash_in_hand": 119450.00,
            "receivables_due": 1428400.00,
            "todays_sales_bills": 18,
            "sales_growth_pct": 14.2,
            "purchase_vouchers": 3,
            "purchase_godown": "Godown: Central Main",
            "drawer_txns": 42,
            "drawer_status": "Tally: Reconciled",
            "active_debtors": 112,
            "overdue_amount_label": "₹ 83.7k overdue",
            "purchases_note": "3 Inward Vouchers",
            "cash_opening": 5000.00,
            "low_stock_count": 3,
            # aliases used by older helpers
            "todays_receipts": 35000.00,
            "outstanding": 1428400.00,
            "invoice_count": 18,
        },
        "COUNTER_SUMMARY": [
            {
                "title": "Cash Sales",
                "amount": 48250.00,
                "meta": "11 Cash Memos",
                "badge": "32.5%",
                "badge_kind": "neutral",
            },
            {
                "title": "Credit Sales",
                "amount": 100000.00,
                "meta": "7 Ledger Parties",
                "badge": "67.5%",
                "badge_kind": "neutral",
            },
            {
                "title": "Collections Recd",
                "amount": 35000.00,
                "meta": "Dr Clearances",
                "badge": "Reconciled",
                "badge_kind": "success",
            },
        ],
        "FAST_LOOKUP_ITEMS": [
            {
                "code": "EL-WIR-104",
                "name": "Finolex 1.5 sq mm Blue FR Wire 90M",
                "category": "Wires & Cables",
                "stock": "32 ROL",
                "low": False,
                "rate": 1450.00,
                "unit": "/coil",
            },
            {
                "code": "EL-LED-202",
                "name": "Philips 20W LED Batten 4ft Cool Day",
                "category": "LED Fixtures",
                "stock": "8 NOS (Low)",
                "low": True,
                "rate": 240.00,
                "unit": "/pc",
            },
            {
                "code": "EL-WIR-205",
                "name": "Polycab 2.5 sq mm Red FR Wire 90M",
                "category": "Wires & Cables",
                "stock": "45 ROL",
                "low": False,
                "rate": 2200.00,
                "unit": "/coil",
            },
            {
                "code": "EL-SWT-312",
                "name": "Schneider 16A 1-Way Modular Switch",
                "category": "Switches",
                "stock": "15 NOS",
                "low": False,
                "rate": 95.00,
                "unit": "/pc",
            },
            {
                "code": "EL-MCB-408",
                "name": "Legrand 32A DP Isolator MCB",
                "category": "Switchgear",
                "stock": "28 NOS",
                "low": False,
                "rate": 420.00,
                "unit": "/pc",
            },
        ],
        "LOW_STOCK_ALERTS": low_stock,
        "LOW_STOCK_ITEMS": [
            {"name": a["name"], "left": 0, "out": False} for a in low_stock
        ],
        "PENDING_OVERDUE": overdue,
        "PENDING_COLLECTIONS": [
            {"party": p["party"], "note": p["note"], "amount": p["amount"]}
            for p in overdue
        ],
        "TODAYS_INVOICES": [
            {"doc": "INV-2026-0842", "party": "Sri Venkateshwara Electricals", "amount": 41400.00},
            {"doc": "INV-2026-0841", "party": "Sai Balaji Electricals", "amount": 12675.00},
            {"doc": "INV-2026-0840", "party": "Maruthi Power Controls", "amount": 9200.00},
        ],
        "RECENT_TXNS": [],
        "TOP_SELLING": [
            {"name": "1.5 sq.mm Copper Wire", "units": 86, "growth": 12.4},
            {"name": "Modular Switch 1-Way", "units": 420, "growth": 8.1},
            {"name": "LED Bulb 9W", "units": 310, "growth": -2.3},
            {"name": "MCB 16A Single Pole", "units": 95, "growth": 18.6},
        ],
        "TOP_STOCKED_QTY": [
            {"name": "PVC Conduit 20mm", "value": 800, "max": 1000},
            {"name": "Modular Switch 1-Way", "value": 500, "max": 1000},
            {"name": "6A Socket Outlet", "value": 320, "max": 1000},
            {"name": "LED Bulb 9W", "value": 210, "max": 1000},
        ],
        "TOP_STOCKED_VALUE": [
            {"name": "2.5 sq.mm Copper Wire", "value": 79800, "max": 120000},
            {"name": "1.5 sq.mm Copper Wire", "value": 77700, "max": 120000},
            {"name": "Ceiling Fan 48 inch", "value": 36750, "max": 120000},
            {"name": "MCB 16A Single Pole", "value": 1320, "max": 120000},
        ],
        "SALES_BY_CHANNEL": {"counter_cash": 42, "credit": 58},
        "PENDING_ACTIONS": {
            "sales": [("To Be Packed", 3), ("To Be Shipped", 1), ("To Be Invoiced", 5)],
            "purchases": [("To Be Received", 2), ("Receive In Progress", 1)],
            "inventory": [("Below Reorder Level", 2)],
        },
    }

# Module-level mirrors (mutated by reload)
COMPANY_NAME = "—"
FINANCIAL_YEAR = "—"
FISCAL_YEARS: list[str] = []
CURRENT_USER = ""
CURRENT_ROLE = ""
DASHBOARD_WELCOME = "Welcome"
DASHBOARD_SHIFT = "Local workspace · Auto-sync: Local DB"

COMPANY: dict = {}
PARTIES: list = []
PARTY_VOUCHERS: dict = {}
PRODUCT_GROUP_RECORDS: list = []
LEDGER_GROUP_RECORDS: list = []
GODOWN_GROUP_RECORDS: list = []
GROUP_ITEMS_PREVIEW: dict = {}
ITEM_GROUPS: list = []
LEDGER_GROUPS: list = []
GODOWN_GROUPS: list = []
PRODUCTS: list = []
GODOWNS: list = []
GODOWN_STOCK: dict = {}
WAREHOUSES: list = []
USERS: list = []
AC_YEAR_ACTIVE: dict = {}
AC_YEAR_PARTITIONS: list = []
RECEIVABLES: list = []
PAYABLES: list = []
CASH_ENTRIES: list = []
CASH_FLOW_KPI: dict = {}
SALES_HISTORY: list = []
PURCHASE_HISTORY: list = []
ESTIMATES: list = []
PREV_SALES: list = []
PREV_PURCHASES: list = []
PREV_ESTIMATES: list = []
PREV_SALES_RETURNS: list = []
RECENT_TXNS: list = []
DASHBOARD_KPI: dict = {}
TODAYS_INVOICES: list = []
LOW_STOCK_ALERTS: list = []
LOW_STOCK_ITEMS: list = []
PENDING_OVERDUE: list = []
PENDING_COLLECTIONS: list = []
FAST_LOOKUP_ITEMS: list = []
TOP_SELLING: list = []
TOP_STOCKED_QTY: list = []
TOP_STOCKED_VALUE: list = []
SALES_BY_CHANNEL: dict = {"counter_cash": 0, "credit": 0}
PENDING_ACTIONS: dict = {"sales": [], "purchases": [], "inventory": []}
COUNTER_SUMMARY: list = []
LEDGER_LINES: list = []
REGISTER_ROWS: list = []
AUDIT_LOG: list = []
AC_LOG_PARTY: dict = {}
AC_LOG_LOOKUP_PARTIES: list = []
AC_LOG_KPI: dict = {}
AC_LOG_EVENTS: list = []


def _empty_company() -> dict:
    return company_svc.get_company()


def reload() -> None:
    """Refresh all module-level collections from the database."""
    global COMPANY_NAME, FINANCIAL_YEAR, FISCAL_YEARS, CURRENT_USER, CURRENT_ROLE
    global DASHBOARD_WELCOME, DASHBOARD_SHIFT, TERMINAL_NAME
    global COMPANY, PARTIES, PARTY_VOUCHERS
    global PRODUCT_GROUP_RECORDS, LEDGER_GROUP_RECORDS, GODOWN_GROUP_RECORDS
    global GROUP_ITEMS_PREVIEW, ITEM_GROUPS, LEDGER_GROUPS, GODOWN_GROUPS
    global PRODUCTS, GODOWNS, GODOWN_STOCK, WAREHOUSES, USERS
    global AC_YEAR_ACTIVE, AC_YEAR_PARTITIONS
    global RECEIVABLES, PAYABLES, CASH_ENTRIES, CASH_FLOW_KPI
    global SALES_HISTORY, PURCHASE_HISTORY, ESTIMATES
    global PREV_SALES, PREV_PURCHASES, PREV_ESTIMATES, PREV_SALES_RETURNS
    global RECENT_TXNS, DASHBOARD_KPI, TODAYS_INVOICES
    global LOW_STOCK_ALERTS, LOW_STOCK_ITEMS, PENDING_OVERDUE, PENDING_COLLECTIONS
    global FAST_LOOKUP_ITEMS, TOP_SELLING, TOP_STOCKED_QTY, TOP_STOCKED_VALUE
    global SALES_BY_CHANNEL, PENDING_ACTIONS, COUNTER_SUMMARY, COUNTER_SHIFT_LABEL
    global AC_LOG_LOOKUP_PARTIES, AC_LOG_PARTY, AC_LOG_KPI, AC_LOG_EVENTS

    COMPANY = _empty_company()
    COMPANY_NAME = company_svc.display_name()

    years = years_svc.list_years()
    AC_YEAR_PARTITIONS = years
    FISCAL_YEARS = [y["code"] for y in years]
    active = years_svc.active_year()
    if active:
        AC_YEAR_ACTIVE = active
        FINANCIAL_YEAR = active["code"]
        COMPANY["financial_year"] = active["code"]
        COMPANY["fy_display"] = active.get("period") or active["code"]
    else:
        AC_YEAR_ACTIVE = {
            "code": "—",
            "period": "No accounting year",
            "partition": "",
            "vouchers": 0,
            "schema": "",
            "terminal": TERMINAL_NAME,
        }
        FINANCIAL_YEAR = "—"

    PARTIES = parties_svc.list_parties()
    PARTY_VOUCHERS = {p["id"]: parties_svc.party_vouchers(p["id"]) for p in PARTIES}

    PRODUCT_GROUP_RECORDS = groups_svc.list_groups("product")
    LEDGER_GROUP_RECORDS = groups_svc.list_groups("ledger")
    GODOWN_GROUP_RECORDS = groups_svc.list_groups("godown")
    ITEM_GROUPS = [g["name"] for g in PRODUCT_GROUP_RECORDS]
    LEDGER_GROUPS = [g["name"] for g in LEDGER_GROUP_RECORDS]
    GODOWN_GROUPS = [g["name"] for g in GODOWN_GROUP_RECORDS]

    PRODUCTS = products_svc.list_products()
    GROUP_ITEMS_PREVIEW = {}
    for g in PRODUCT_GROUP_RECORDS:
        GROUP_ITEMS_PREVIEW[g["id"]] = [
            {
                "code": p["sku"],
                "name": p["name"],
                "unit": p["unit"],
                "rate": p["sale_rate"],
            }
            for p in PRODUCTS
            if p.get("group_id") == g["id"] or p.get("group") == g["name"]
        ][:20]

    GODOWNS = godowns_svc.list_godowns()
    WAREHOUSES = [g["name"] for g in GODOWNS]
    GODOWN_STOCK = {g["id"]: godowns_svc.stock_for(g["id"]) for g in GODOWNS}

    USERS = users_svc.list_users()

    cu = session.current_user()
    if cu:
        CURRENT_USER = cu.get("name") or cu.get("username") or ""
        CURRENT_ROLE = cu.get("role") or ""
        DASHBOARD_WELCOME = f"Welcome back, {CURRENT_USER.split()[0] if CURRENT_USER else 'User'}"
    else:
        CURRENT_USER = ""
        CURRENT_ROLE = ""
        DASHBOARD_WELCOME = "Welcome"
    DASHBOARD_SHIFT = f"{TERMINAL_NAME} · Local SQLite"

    RECEIVABLES = settlements_svc.outstanding("receivable")
    PAYABLES = settlements_svc.outstanding("payable")
    CASH_ENTRIES = cash_svc.list_entries()
    CASH_FLOW_KPI = cash_svc.kpi()

    SALES_HISTORY = vouchers_svc.sales_history()
    PURCHASE_HISTORY = vouchers_svc.purchase_history()
    ESTIMATES = vouchers_svc.estimates()
    PREV_SALES = list(SALES_HISTORY)
    PREV_PURCHASES = list(PURCHASE_HISTORY)
    PREV_ESTIMATES = list(ESTIMATES)
    PREV_SALES_RETURNS = vouchers_svc.list_by_type("Sales Return")

    # Temporary: dashboard still uses Stitch demo fixtures until live KPIs are complete.
    # (DB snapshot is available via dash_svc.build_snapshot() when we switch over.)
    _ = dash_svc  # keep import used
    demo = _dashboard_demo()
    DASHBOARD_KPI = demo["DASHBOARD_KPI"]
    TODAYS_INVOICES = demo["TODAYS_INVOICES"]
    LOW_STOCK_ALERTS = demo["LOW_STOCK_ALERTS"]
    LOW_STOCK_ITEMS = demo["LOW_STOCK_ITEMS"]
    PENDING_OVERDUE = demo["PENDING_OVERDUE"]
    PENDING_COLLECTIONS = demo["PENDING_COLLECTIONS"]
    RECENT_TXNS = demo["RECENT_TXNS"]
    FAST_LOOKUP_ITEMS = demo["FAST_LOOKUP_ITEMS"]
    TOP_SELLING = demo["TOP_SELLING"]
    TOP_STOCKED_QTY = demo["TOP_STOCKED_QTY"]
    TOP_STOCKED_VALUE = demo["TOP_STOCKED_VALUE"]
    SALES_BY_CHANNEL = demo["SALES_BY_CHANNEL"]
    PENDING_ACTIONS = demo["PENDING_ACTIONS"]
    COUNTER_SUMMARY = demo["COUNTER_SUMMARY"]
    COUNTER_SHIFT_LABEL = demo["COUNTER_SHIFT_LABEL"]
    DASHBOARD_SHIFT = demo["DASHBOARD_SHIFT"]
    if not CURRENT_USER:
        DASHBOARD_WELCOME = demo["DASHBOARD_WELCOME"]
    else:
        DASHBOARD_WELCOME = f"Welcome back, {CURRENT_USER.split()[0]}"

    AC_LOG_LOOKUP_PARTIES = [
        {
            "id": p["id"],
            "name": p["name"],
            "code": p["code"],
            "type": p["type"],
            "city": p.get("city") or "",
            "balance": p.get("balance") or 0,
            "balance_type": p.get("balance_type") or "Dr",
        }
        for p in PARTIES
    ]
    AC_LOG_PARTY = AC_LOG_LOOKUP_PARTIES[0] if AC_LOG_LOOKUP_PARTIES else {
        "id": 0, "name": "—", "code": "", "type": "", "city": "",
        "balance": 0, "balance_type": "Dr",
    }
    AC_LOG_KPI = {
        "opening": 0, "debit": 0, "credit": 0, "closing": 0,
    }
    AC_LOG_EVENTS = []
