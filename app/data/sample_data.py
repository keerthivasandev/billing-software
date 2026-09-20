"""In-memory sample data for demo screens (no DB required for UI)."""

from datetime import date, timedelta

COMPANY_NAME = "Sri Lakshmi Electricals"
FINANCIAL_YEAR = "FY 2026–27"
CURRENT_USER = "Ramesh"
CURRENT_ROLE = "Billing Clerk"

PARTIES = [
    {"id": 1, "name": "Anand Traders", "type": "Customer", "gstin": "33AABCA1234A1Z5",
     "phone": "9876543210", "city": "Chennai", "balance": 45200.00, "credit_days": 30},
    {"id": 2, "name": "Bharat Electricals", "type": "Customer", "gstin": "33AABCB5678B1Z2",
     "phone": "9876501234", "city": "Coimbatore", "balance": -3500.00, "credit_days": 15},
    {"id": 3, "name": "Cauvery Agencies", "type": "Supplier", "gstin": "33AABCC9012C1Z9",
     "phone": "9444412345", "city": "Madurai", "balance": 128500.00, "credit_days": 45},
    {"id": 4, "name": "Delta Switchgear", "type": "Supplier", "gstin": "29AABCD3456D1Z1",
     "phone": "9988776655", "city": "Bengaluru", "balance": 0.00, "credit_days": 30},
    {"id": 5, "name": "Eastern Power Co", "type": "Customer", "gstin": "33AABCE7890E1Z8",
     "phone": "9000011122", "city": "Salem", "balance": 8750.00, "credit_days": 7},
    {"id": 6, "name": "Falcon Cables Ltd", "type": "Supplier", "gstin": "27AABCF1122F1Z3",
     "phone": "9123456780", "city": "Mumbai", "balance": 22000.00, "credit_days": 30},
    {"id": 7, "name": "Ganesh Hardware", "type": "Customer", "gstin": "33AABCG3344G1Z6",
     "phone": "9887766554", "city": "Trichy", "balance": 15600.00, "credit_days": 21},
    {"id": 8, "name": "Hitech Lighting", "type": "Both", "gstin": "33AABCH5566H1Z0",
     "phone": "9776655443", "city": "Erode", "balance": -1200.00, "credit_days": 15},
]

ITEM_GROUPS = [
    "Wires & Cables", "Switches & Sockets", "MCB & Distribution",
    "Lighting", "Fans", "Conduit & Fittings", "Tools", "Miscellaneous",
]

PRODUCTS = [
    {"id": 1, "sku": "WR-1.5-CU", "name": "1.5 sq.mm Copper Wire (90m)", "group": "Wires & Cables",
     "unit": "Coil", "rate": 1850.00, "gst": 18, "stock": 42, "warehouse": "Main Godown", "min_stock": 10},
    {"id": 2, "sku": "WR-2.5-CU", "name": "2.5 sq.mm Copper Wire (90m)", "group": "Wires & Cables",
     "unit": "Coil", "rate": 2850.00, "gst": 18, "stock": 28, "warehouse": "Main Godown", "min_stock": 8},
    {"id": 3, "sku": "SW-MOD-1W", "name": "Modular Switch 1-Way", "group": "Switches & Sockets",
     "unit": "Pcs", "rate": 45.00, "gst": 18, "stock": 500, "warehouse": "Main Godown", "min_stock": 100},
    {"id": 4, "sku": "SW-SOCK-6A", "name": "6A Socket Outlet", "group": "Switches & Sockets",
     "unit": "Pcs", "rate": 85.00, "gst": 18, "stock": 320, "warehouse": "Showroom", "min_stock": 50},
    {"id": 5, "sku": "MCB-16A-SP", "name": "MCB 16A Single Pole", "group": "MCB & Distribution",
     "unit": "Pcs", "rate": 165.00, "gst": 18, "stock": 8, "warehouse": "Main Godown", "min_stock": 20},
    {"id": 6, "sku": "LED-9W", "name": "LED Bulb 9W", "group": "Lighting",
     "unit": "Pcs", "rate": 95.00, "gst": 12, "stock": 210, "warehouse": "Showroom", "min_stock": 40},
    {"id": 7, "sku": "FAN-CLG-48", "name": "Ceiling Fan 48 inch", "group": "Fans",
     "unit": "Pcs", "rate": 2450.00, "gst": 18, "stock": 15, "warehouse": "Main Godown", "min_stock": 5},
    {"id": 8, "sku": "PVC-20MM", "name": "PVC Conduit 20mm (3m)", "group": "Conduit & Fittings",
     "unit": "Pcs", "rate": 28.00, "gst": 18, "stock": 800, "warehouse": "Main Godown", "min_stock": 200},
    {"id": 9, "sku": "TL-TESTER", "name": "Neon Tester", "group": "Tools",
     "unit": "Pcs", "rate": 35.00, "gst": 18, "stock": 4, "warehouse": "Showroom", "min_stock": 15},
    {"id": 10, "sku": "MISC-TAPE", "name": "Insulation Tape (Roll)", "group": "Miscellaneous",
     "unit": "Roll", "rate": 18.00, "gst": 18, "stock": 150, "warehouse": "Main Godown", "min_stock": 30},
]

WAREHOUSES = ["Main Godown", "Showroom", "Transit"]

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

RECEIVABLES = [
    {"party": "Anand Traders", "bill": "SI-1042", "date": date.today().isoformat(), "due": (date.today() + timedelta(days=30)).isoformat(), "amount": 28450.00, "balance": 28450.00, "days": 0},
    {"party": "Ganesh Hardware", "bill": "SI-1041", "date": (date.today() - timedelta(days=1)).isoformat(), "due": (date.today() + timedelta(days=20)).isoformat(), "amount": 12300.00, "balance": 12300.00, "days": 1},
    {"party": "Eastern Power Co", "bill": "SI-1035", "date": (date.today() - timedelta(days=12)).isoformat(), "due": (date.today() - timedelta(days=5)).isoformat(), "amount": 8750.00, "balance": 8750.00, "days": 12},
    {"party": "Bharat Electricals", "bill": "SI-1028", "date": (date.today() - timedelta(days=40)).isoformat(), "due": (date.today() - timedelta(days=25)).isoformat(), "amount": 15600.00, "balance": 0.00, "days": 40},
]

PAYABLES = [
    {"party": "Cauvery Agencies", "bill": "PI-0388", "date": date.today().isoformat(), "due": (date.today() + timedelta(days=45)).isoformat(), "amount": 95600.00, "balance": 95600.00, "days": 0},
    {"party": "Falcon Cables Ltd", "bill": "PI-0380", "date": (date.today() - timedelta(days=18)).isoformat(), "due": (date.today() + timedelta(days=12)).isoformat(), "amount": 45000.00, "balance": 22000.00, "days": 18},
    {"party": "Delta Switchgear", "bill": "PI-0375", "date": (date.today() - timedelta(days=35)).isoformat(), "due": (date.today() - timedelta(days=5)).isoformat(), "amount": 31200.00, "balance": 0.00, "days": 35},
]

MACHINE_ID = "HW-A7F3-C91E-4B2D-88E0"
LICENSE_STATUS = "Not Activated"
