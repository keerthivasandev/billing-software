"""In-memory sample data for demo screens (no DB — potato-PC friendly)."""

from datetime import date, timedelta

COMPANY_NAME = "Sri Lakshmi Electricals"
COMPANY_TAGLINE = "Wholesale Billing & ERP"
FINANCIAL_YEAR = "FY 2026–27"
FISCAL_YEARS = ["FY 2024–25", "FY 2025–26", "FY 2026–27"]
CURRENT_USER = "Ramesh"
CURRENT_ROLE = "Billing Clerk"

COMPANY = {
    "legal_name": "Sri Lakshmi Electricals",
    "address": "42, Industrial Estate, Guindy",
    "city": "Chennai",
    "phone": "044-2250-1234",
    "gstin": "33AABCS1234A1Z5",
    "bank_name": "State Bank of India",
    "account_no": "30123456789",
    "ifsc": "SBIN0001234",
    "valid_from": "2026-04-01",
    "valid_to": "2027-03-31",
}

PARTIES = [
    {"id": 1, "name": "Anand Traders", "type": "Customer", "gstin": "33AABCA1234A1Z5",
     "phone": "9876543210", "address": "12 Anna Salai", "city": "Chennai",
     "balance": 45200.00, "balance_type": "Dr", "credit_limit": 100000.00, "credit_days": 30},
    {"id": 2, "name": "Bharat Electricals", "type": "Customer", "gstin": "33AABCB5678B1Z2",
     "phone": "9876501234", "address": "88 Cross Cut Rd", "city": "Coimbatore",
     "balance": -3500.00, "balance_type": "Cr", "credit_limit": 50000.00, "credit_days": 15},
    {"id": 3, "name": "Cauvery Agencies", "type": "Supplier", "gstin": "33AABCC9012C1Z9",
     "phone": "9444412345", "address": "5 Bypass Rd", "city": "Madurai",
     "balance": 128500.00, "balance_type": "Cr", "credit_limit": 200000.00, "credit_days": 45},
    {"id": 4, "name": "Delta Switchgear", "type": "Supplier", "gstin": "29AABCD3456D1Z1",
     "phone": "9988776655", "address": "Peenya Indl Area", "city": "Bengaluru",
     "balance": 0.00, "balance_type": "Dr", "credit_limit": 75000.00, "credit_days": 30},
    {"id": 5, "name": "Eastern Power Co", "type": "Customer", "gstin": "33AABCE7890E1Z8",
     "phone": "9000011122", "address": "Omalur Main Rd", "city": "Salem",
     "balance": 8750.00, "balance_type": "Dr", "credit_limit": 40000.00, "credit_days": 7},
    {"id": 6, "name": "Falcon Cables Ltd", "type": "Supplier", "gstin": "27AABCF1122F1Z3",
     "phone": "9123456780", "address": "Andheri East", "city": "Mumbai",
     "balance": 22000.00, "balance_type": "Cr", "credit_limit": 150000.00, "credit_days": 30},
    {"id": 7, "name": "Ganesh Hardware", "type": "Customer", "gstin": "33AABCG3344G1Z6",
     "phone": "9887766554", "address": "Thillai Nagar", "city": "Trichy",
     "balance": 15600.00, "balance_type": "Dr", "credit_limit": 60000.00, "credit_days": 21},
    {"id": 8, "name": "Hitech Lighting", "type": "Both", "gstin": "33AABCH5566H1Z0",
     "phone": "9776655443", "address": "Perundurai Rd", "city": "Erode",
     "balance": -1200.00, "balance_type": "Cr", "credit_limit": 35000.00, "credit_days": 15},
]

ITEM_GROUPS = [
    "Wires & Cables", "Switches & Sockets", "MCB & Distribution",
    "Lighting", "Fans", "Conduit & Fittings", "Tools", "Miscellaneous",
]

LEDGER_GROUPS = [
    "Sundry Debtors", "Sundry Creditors", "Cash-in-Hand", "Bank Accounts",
    "Sales Accounts", "Purchase Accounts", "Duties & Taxes", "Indirect Expenses",
]

GODOWN_GROUPS = ["Primary", "Retail", "Transit / Temporary"]

PRODUCTS = [
    {"id": 1, "sku": "WR-1.5-CU", "name": "1.5 sq.mm Copper Wire (90m)", "group": "Wires & Cables",
     "hsn": "8544", "unit": "Coil", "sale_rate": 1850.00, "purchase_rate": 1620.00,
     "gst": 18, "stock": 42, "warehouse": "Main Godown", "min_stock": 10, "opening_qty": 40},
    {"id": 2, "sku": "WR-2.5-CU", "name": "2.5 sq.mm Copper Wire (90m)", "group": "Wires & Cables",
     "hsn": "8544", "unit": "Coil", "sale_rate": 2850.00, "purchase_rate": 2480.00,
     "gst": 18, "stock": 28, "warehouse": "Main Godown", "min_stock": 8, "opening_qty": 30},
    {"id": 3, "sku": "SW-MOD-1W", "name": "Modular Switch 1-Way", "group": "Switches & Sockets",
     "hsn": "8536", "unit": "Pcs", "sale_rate": 45.00, "purchase_rate": 32.00,
     "gst": 18, "stock": 500, "warehouse": "Main Godown", "min_stock": 100, "opening_qty": 480},
    {"id": 4, "sku": "SW-SOCK-6A", "name": "6A Socket Outlet", "group": "Switches & Sockets",
     "hsn": "8536", "unit": "Pcs", "sale_rate": 85.00, "purchase_rate": 58.00,
     "gst": 18, "stock": 320, "warehouse": "Showroom", "min_stock": 50, "opening_qty": 300},
    {"id": 5, "sku": "MCB-16A-SP", "name": "MCB 16A Single Pole", "group": "MCB & Distribution",
     "hsn": "8536", "unit": "Pcs", "sale_rate": 165.00, "purchase_rate": 118.00,
     "gst": 18, "stock": 8, "warehouse": "Main Godown", "min_stock": 20, "opening_qty": 25},
    {"id": 6, "sku": "LED-9W", "name": "LED Bulb 9W", "group": "Lighting",
     "hsn": "8539", "unit": "Pcs", "sale_rate": 95.00, "purchase_rate": 62.00,
     "gst": 12, "stock": 210, "warehouse": "Showroom", "min_stock": 40, "opening_qty": 200},
    {"id": 7, "sku": "FAN-CLG-48", "name": "Ceiling Fan 48 inch", "group": "Fans",
     "hsn": "8414", "unit": "Pcs", "sale_rate": 2450.00, "purchase_rate": 1980.00,
     "gst": 18, "stock": 15, "warehouse": "Main Godown", "min_stock": 5, "opening_qty": 12},
    {"id": 8, "sku": "PVC-20MM", "name": "PVC Conduit 20mm (3m)", "group": "Conduit & Fittings",
     "hsn": "3917", "unit": "Pcs", "sale_rate": 28.00, "purchase_rate": 18.00,
     "gst": 18, "stock": 800, "warehouse": "Main Godown", "min_stock": 200, "opening_qty": 750},
    {"id": 9, "sku": "TL-TESTER", "name": "Neon Tester", "group": "Tools",
     "hsn": "9030", "unit": "Pcs", "sale_rate": 35.00, "purchase_rate": 18.00,
     "gst": 18, "stock": 4, "warehouse": "Showroom", "min_stock": 15, "opening_qty": 20},
    {"id": 10, "sku": "MISC-TAPE", "name": "Insulation Tape (Roll)", "group": "Miscellaneous",
     "hsn": "3919", "unit": "Roll", "sale_rate": 18.00, "purchase_rate": 10.00,
     "gst": 18, "stock": 150, "warehouse": "Main Godown", "min_stock": 30, "opening_qty": 140},
]

# Back-compat alias used by older screens
for _p in PRODUCTS:
    _p.setdefault("rate", _p["sale_rate"])

GODOWNS = [
    {"id": 1, "name": "Main Godown", "incharge": "Murugan", "address": "Yard A, Guindy",
     "capacity": "5000 sq.ft", "is_default": True},
    {"id": 2, "name": "Showroom", "incharge": "Priya", "address": "Front Counter",
     "capacity": "800 sq.ft", "is_default": False},
    {"id": 3, "name": "Transit", "incharge": "Karthik", "address": "Loading Bay",
     "capacity": "200 sq.ft", "is_default": False},
]

WAREHOUSES = [g["name"] for g in GODOWNS]

RECENT_TXNS = [
    {"date": date.today().isoformat(), "type": "Sale", "doc": "SI-1042", "party": "Anand Traders", "amount": 28450.00},
    {"date": date.today().isoformat(), "type": "Purchase", "doc": "PI-0388", "party": "Cauvery Agencies", "amount": 95600.00},
    {"date": (date.today() - timedelta(days=1)).isoformat(), "type": "Sale", "doc": "SI-1041", "party": "Ganesh Hardware", "amount": 12300.00},
    {"date": (date.today() - timedelta(days=1)).isoformat(), "type": "Receipt", "doc": "RC-0211", "party": "Eastern Power Co", "amount": 5000.00},
    {"date": (date.today() - timedelta(days=2)).isoformat(), "type": "Sale", "doc": "SI-1040", "party": "Bharat Electricals", "amount": 6780.00},
    {"date": (date.today() - timedelta(days=2)).isoformat(), "type": "Payment", "doc": "PY-0155", "party": "Falcon Cables Ltd", "amount": 22000.00},
    {"date": (date.today() - timedelta(days=3)).isoformat(), "type": "Sale", "doc": "SI-1039", "party": "Hitech Lighting", "amount": 18900.00},
]

DASHBOARD_KPI = {
    "todays_sales": 40750.00,
    "todays_purchases": 95600.00,
    "cash_in_hand": 34280.00,
    "receivables_due": 69550.00,
    "low_stock_count": 2,
}

TOP_SELLING = [
    {"name": "1.5 sq.mm Copper Wire", "units": 86, "growth": 12.4},
    {"name": "Modular Switch 1-Way", "units": 420, "growth": 8.1},
    {"name": "LED Bulb 9W", "units": 310, "growth": -2.3},
    {"name": "MCB 16A Single Pole", "units": 95, "growth": 18.6},
]

TOP_STOCKED_QTY = [
    {"name": "PVC Conduit 20mm", "value": 800, "max": 1000},
    {"name": "Modular Switch 1-Way", "value": 500, "max": 1000},
    {"name": "6A Socket Outlet", "value": 320, "max": 1000},
    {"name": "LED Bulb 9W", "value": 210, "max": 1000},
]

TOP_STOCKED_VALUE = [
    {"name": "2.5 sq.mm Copper Wire", "value": 79800, "max": 120000},
    {"name": "1.5 sq.mm Copper Wire", "value": 77700, "max": 120000},
    {"name": "Ceiling Fan 48 inch", "value": 36750, "max": 120000},
    {"name": "MCB 16A Single Pole", "value": 1320, "max": 120000},
]

SALES_BY_CHANNEL = {"counter_cash": 42, "credit": 58}

PENDING_ACTIONS = {
    "sales": [("To Be Packed", 3), ("To Be Shipped", 1), ("To Be Invoiced", 5)],
    "purchases": [("To Be Received", 2), ("Receive In Progress", 1)],
    "inventory": [("Below Reorder Level", 2)],
}

RECEIVABLES = [
    {"party": "Anand Traders", "bill": "SI-1042", "date": date.today().isoformat(),
     "due": (date.today() + timedelta(days=30)).isoformat(), "amount": 28450.00, "balance": 28450.00, "days": 0},
    {"party": "Ganesh Hardware", "bill": "SI-1041", "date": (date.today() - timedelta(days=1)).isoformat(),
     "due": (date.today() + timedelta(days=20)).isoformat(), "amount": 12300.00, "balance": 12300.00, "days": 1},
    {"party": "Eastern Power Co", "bill": "SI-1035", "date": (date.today() - timedelta(days=12)).isoformat(),
     "due": (date.today() - timedelta(days=5)).isoformat(), "amount": 8750.00, "balance": 8750.00, "days": 12},
    {"party": "Bharat Electricals", "bill": "SI-1028", "date": (date.today() - timedelta(days=40)).isoformat(),
     "due": (date.today() - timedelta(days=25)).isoformat(), "amount": 15600.00, "balance": 0.00, "days": 40},
]

PAYABLES = [
    {"party": "Cauvery Agencies", "bill": "PI-0388", "date": date.today().isoformat(),
     "due": (date.today() + timedelta(days=45)).isoformat(), "amount": 95600.00, "balance": 95600.00, "days": 0},
    {"party": "Falcon Cables Ltd", "bill": "PI-0380", "date": (date.today() - timedelta(days=18)).isoformat(),
     "due": (date.today() + timedelta(days=12)).isoformat(), "amount": 45000.00, "balance": 22000.00, "days": 18},
    {"party": "Delta Switchgear", "bill": "PI-0375", "date": (date.today() - timedelta(days=35)).isoformat(),
     "due": (date.today() - timedelta(days=5)).isoformat(), "amount": 31200.00, "balance": 0.00, "days": 35},
]

CASH_ENTRIES = [
    {"date": date.today().isoformat(), "kind": "In", "mode": "Cash", "ref": "RC-0211",
     "purpose": "Customer receipt", "amount": 5000.00},
    {"date": date.today().isoformat(), "kind": "Out", "mode": "Cash", "ref": "PY-0156",
     "purpose": "Petty cash — courier", "amount": 350.00},
    {"date": (date.today() - timedelta(days=1)).isoformat(), "kind": "In", "mode": "Bank Transfer",
     "ref": "NEFT-8821", "purpose": "Eastern Power Co", "amount": 8750.00},
    {"date": (date.today() - timedelta(days=1)).isoformat(), "kind": "Out", "mode": "Bank Transfer",
     "ref": "PY-0155", "purpose": "Falcon Cables Ltd", "amount": 22000.00},
]

ESTIMATES = [
    {"id": "QT-0088", "party": "Anand Traders", "date": date.today().isoformat(),
     "amount": 15600.00, "status": "Open"},
    {"id": "QT-0087", "party": "Ganesh Hardware", "date": (date.today() - timedelta(days=2)).isoformat(),
     "amount": 9200.00, "status": "Open"},
    {"id": "QT-0085", "party": "Hitech Lighting", "date": (date.today() - timedelta(days=5)).isoformat(),
     "amount": 21400.00, "status": "Converted"},
]

LEDGER_LINES = [
    {"date": (date.today() - timedelta(days=5)).isoformat(), "particulars": "Opening Balance",
     "vch": "—", "debit": 40000.00, "credit": 0.00},
    {"date": (date.today() - timedelta(days=3)).isoformat(), "particulars": "Sales Invoice SI-1039",
     "vch": "SI-1039", "debit": 18900.00, "credit": 0.00},
    {"date": (date.today() - timedelta(days=1)).isoformat(), "particulars": "Receipt RC-0211",
     "vch": "RC-0211", "debit": 0.00, "credit": 5000.00},
    {"date": date.today().isoformat(), "particulars": "Sales Invoice SI-1042",
     "vch": "SI-1042", "debit": 28450.00, "credit": 0.00},
]

REGISTER_ROWS = [
    {"date": date.today().isoformat(), "doc": "SI-1042", "party": "Anand Traders", "taxable": 24110.17,
     "cgst": 2169.92, "sgst": 2169.92, "igst": 0.00, "total": 28450.00, "kind": "Sale"},
    {"date": date.today().isoformat(), "doc": "PI-0388", "party": "Cauvery Agencies", "taxable": 81016.95,
     "cgst": 7291.53, "sgst": 7291.53, "igst": 0.00, "total": 95600.00, "kind": "Purchase"},
    {"date": (date.today() - timedelta(days=1)).isoformat(), "doc": "SI-1041", "party": "Ganesh Hardware",
     "taxable": 10423.73, "cgst": 938.14, "sgst": 938.14, "igst": 0.00, "total": 12300.00, "kind": "Sale"},
]

AUDIT_LOG = [
    {"ts": f"{date.today().isoformat()} 09:12:04", "user": "Ramesh", "action": "Created Sales Invoice SI-1042", "module": "Sales"},
    {"ts": f"{date.today().isoformat()} 09:40:18", "user": "Ramesh", "action": "Updated Party Anand Traders", "module": "Masters"},
    {"ts": f"{date.today().isoformat()} 10:05:33", "user": "Priya", "action": "Received Purchase PI-0388", "module": "Purchase"},
    {"ts": f"{(date.today() - timedelta(days=1)).isoformat()} 16:22:01", "user": "Ramesh", "action": "Settled RC-0211", "module": "Cash"},
    {"ts": f"{(date.today() - timedelta(days=1)).isoformat()} 17:01:44", "user": "Admin", "action": "Backup completed", "module": "Settings"},
]

USERS = [
    {"id": 1, "name": "Admin", "username": "admin", "role": "Admin", "active": True},
    {"id": 2, "name": "Ramesh", "username": "ramesh", "role": "Billing Clerk", "active": True},
    {"id": 3, "name": "Priya", "username": "priya", "role": "Inventory Manager", "active": True},
    {"id": 4, "name": "Karthik", "username": "karthik", "role": "Billing Clerk", "active": False},
]

MACHINE_ID = "HW-A7F3-C91E-4B2D-88E0"
LICENSE_STATUS = "Not Activated"
