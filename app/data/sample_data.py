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
    "trade_name": "Sri Lakshmi Electricals",
    "entity_type": "Proprietorship / Partnership Firm",
    "address": "42, Industrial Estate, Guindy",
    "landmark": "Near Guindy Metro / SIDCO Estate Gate",
    "city": "Chennai",
    "district": "Chennai",
    "pincode": "600032",
    "state_code": "33 — Tamil Nadu",
    "phone": "044-2250-1234",
    "mobile": "98765 43210",
    "landline": "044-2250-1234",
    "email": "accounts@srilakshmi-electricals.in",
    "contact_person": "Ramesh Kumar",
    "gstin": "33AABCS1234A1Z5",
    "pan": "AABCS1234A",
    "business_activity": "Wholesale of electrical wires, switches, MCBs & lighting",
    "financial_year": "FY 2026–27",
    "fy_display": "2026–2027 (01-Apr-2026 to 31-Mar-2027)",
    "assessment_year": "Assessment Yr 2027–28",
    "city_display": "Chennai, Chennai District",
    "bank_name": "State Bank of India",
    "beneficiary": "Sri Lakshmi Electricals",
    "account_no": "30123456789",
    "account_type": "Current Account",
    "ifsc": "SBIN0001234",
    "branch": "Guindy Industrial Estate Branch",
    "upi": "srilakshmi@sbi",
    "invoice_note": "Goods once sold will not be taken back. Interest @ 18% p.a. after due date. Subject to Chennai jurisdiction.",
    "valid_from": "2026-04-01",
    "valid_to": "2027-03-31",
    "gst_filing_status": "GSTR-1 & 3B Compliant",
    "einvoice_status": "NIC Portal Linked",
    "terminal_id": "CHN-GUINDY-POS-01",
    "compliance_version": "V1.4.2",
    "distributor_status": "Authorized Distributor",
    "compliance_note": "Registered under Central Goods & Services Tax Act, Chennai South Division.",
    "einvoice_portal": "Active (Live)",
    "hsn_chapters": "8544, 8536 (Wires, MCBs)",
    "tds_exemption": "Standard 0.1% u/s 194Q",
}

PARTIES = [
    {"id": 1, "code": "SLE-PTY-0001",
     "name": "Sri Sai Builders & Infra Pvt Ltd", "short_name": "Sri Sai Builders & Infra",
     "type": "Customer", "group": "Sundry Debtor",
     "contact_person": "Mr. K. Sai Srinivas (Managing Partner)",
     "gstin": "36AAACS8214M1Z2", "state_code": "36 — Telangana",
     "phone": "+91 98480 23411", "address": "Ranigunj, Secunderabad - 500003",
     "city": "Secunderabad",
     "balance": 112000.00, "balance_type": "Dr", "opening_balance": 85000.00,
     "credit_limit": 75000.00, "credit_days": 30, "active": True, "whatsapp": True},
    {"id": 2, "code": "SLE-PTY-0002",
     "name": "Venkateshwara Electricals & Hardware", "short_name": "Venkateshwara Elec. & Hdw",
     "type": "Customer", "group": "Sundry Debtor", "contact_person": "Mr. Venkat",
     "gstin": "36AABCV5678B1Z2", "state_code": "36 — Telangana",
     "phone": "+91 94401 88290", "address": "Troop Bazar", "city": "Troop Bazar, Hyderabad",
     "balance": 48500.00, "balance_type": "Dr", "opening_balance": 30000.00,
     "credit_limit": 60000.00, "credit_days": 21, "active": True, "whatsapp": True},
    {"id": 3, "code": "SLE-PTY-0003",
     "name": "Havells India Limited", "short_name": "Havells India Limited",
     "type": "Supplier", "group": "Sundry Creditor", "contact_person": "Mr. Rajesh",
     "gstin": "07AAACH7456L1Z0", "state_code": "36 — Telangana",
     "phone": "+91 40 2715 2200", "address": "Nacharam", "city": "Nacharam, Hyderabad",
     "balance": 245000.00, "balance_type": "Cr", "opening_balance": 200000.00,
     "credit_limit": 500000.00, "credit_days": 45, "active": True, "whatsapp": False},
    {"id": 4, "code": "SLE-PTY-0004",
     "name": "Balaji Power Systems & Transformers", "short_name": "Balaji Power Systems & Trans.",
     "type": "Customer", "group": "Sundry Debtor", "contact_person": "Mr. Balaji",
     "gstin": "36AABCB9012C1Z9", "state_code": "36 — Telangana",
     "phone": "+91 99887 11223", "address": "IDA Jeedimetla", "city": "IDA Jeedimetla, Secunderabad",
     "balance": 72000.00, "balance_type": "Dr", "opening_balance": 50000.00,
     "credit_limit": 100000.00, "credit_days": 30, "active": True, "whatsapp": True},
    {"id": 5, "code": "SLE-PTY-0005",
     "name": "Polycab Wires Pvt Ltd", "short_name": "Polycab Wires Pvt Ltd",
     "type": "Supplier", "group": "Sundry Creditor", "contact_person": "Ms. Anitha",
     "gstin": "27AABCP3344G1Z6", "state_code": "36 — Telangana",
     "phone": "+91 40 2784 3311", "address": "MG Road", "city": "MG Road, Secunderabad",
     "balance": 184200.00, "balance_type": "Cr", "opening_balance": 150000.00,
     "credit_limit": 400000.00, "credit_days": 30, "active": True, "whatsapp": False},
    {"id": 6, "code": "SLE-PTY-0006",
     "name": "Meenakshi Enterprises", "short_name": "Meenakshi Enterprises",
     "type": "Customer", "group": "Sundry Debtor", "contact_person": "Ms. Meenakshi",
     "gstin": "36AABCM5566H1Z0", "state_code": "36 — Telangana",
     "phone": "+91 90000 44556", "address": "Balanagar", "city": "Balanagar, Hyderabad",
     "balance": 14350.00, "balance_type": "Dr", "opening_balance": 10000.00,
     "credit_limit": 40000.00, "credit_days": 15, "active": True, "whatsapp": True},
]

PARTY_VOUCHERS = {
    1: [
        {"date": "18-Oct-2026", "voucher_type": "Tax Invoice", "voucher_no": "#INV-26-0842",
         "voucher": "Tax Invoice #INV-26-0842",
         "debit": 45200.00, "credit": 0.00, "balance": 112000.00, "balance_type": "Dr"},
        {"date": "02-Oct-2026", "voucher_type": "Tax Invoice", "voucher_no": "#INV-26-0791",
         "voucher": "Tax Invoice #INV-26-0791",
         "debit": 66800.00, "credit": 0.00, "balance": 66800.00, "balance_type": "Dr"},
        {"date": "15-Sep-2026", "voucher_type": "Bank Receipt", "voucher_no": "#REC-26-0310",
         "voucher": "Bank Receipt #REC-26-0310",
         "debit": 0.00, "credit": 50000.00, "balance": 0.00, "balance_type": ""},
    ],
}

# Rich Group Master records (Stitch). Flat name lists kept for older screens.
PRODUCT_GROUP_RECORDS = [
    {"id": 1, "name": "Wires & Cables", "gst": 18, "parent": "Primary / Top-Level [Root]",
     "kind": "product", "active": True,
     "notes": "All copper, multi-strand, and flexible electrical cabling for domestic and commercial projects.",
     "item_count": 142},
    {"id": 2, "name": "Switchgear & Modular", "gst": 18, "parent": "Primary / Top-Level [Root]",
     "kind": "product", "active": True, "notes": "Modular switches, sockets, plates, and switchgear.",
     "item_count": 86},
    {"id": 3, "name": "Commercial Lighting", "gst": 12, "parent": "Primary / Top-Level [Root]",
     "kind": "product", "active": True, "notes": "LED bulbs, battens, panels, and commercial fixtures.",
     "item_count": 64},
    {"id": 4, "name": "PVC Conduit & Piping", "gst": 18, "parent": "Primary / Top-Level [Root]",
     "kind": "product", "active": True, "notes": "PVC conduits, bends, and junction boxes.",
     "item_count": 38},
    {"id": 5, "name": "Motors & Pumps", "gst": 18, "parent": "Primary / Top-Level [Root]",
     "kind": "product", "active": True, "notes": "Motors, pumps, and drive accessories.",
     "item_count": 22},
    {"id": 6, "name": "Industrial MCB & DBs", "gst": 18, "parent": "Primary / Top-Level [Root]",
     "kind": "product", "active": True, "notes": "MCBs, RCCBs, and distribution boards.",
     "item_count": 45},
]

# Preview rows shown in Group Master items table (Stitch demo).
GROUP_ITEMS_PREVIEW = {
    1: [
        {"code": "SKU-WIR-001", "name": "Polycab 2.5mm² FR Single Core Flame Retardant (Red)",
         "unit": "ROL (90m)", "rate": 1450.00},
        {"code": "SKU-WIR-002", "name": "Finolex 1.5mm² FRLS Industrial Grade (Blue)",
         "unit": "ROL (90m)", "rate": 1120.00},
        {"code": "SKU-WIR-003", "name": "Anchor Advance 1.0mm² PVC Flexible Cable (Yellow)",
         "unit": "ROL (90m)", "rate": 890.00},
        {"code": "SKU-WIR-004", "name": "RR Kabel 4.0mm² Multi-strand Heavy Duty (Black)",
         "unit": "ROL (90m)", "rate": 2340.00},
    ],
}

LEDGER_GROUP_RECORDS = [
    {"id": 101, "name": "Sundry Debtors", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Customer receivable accounts.", "item_count": 5},
    {"id": 102, "name": "Sundry Creditors", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Supplier payable accounts.", "item_count": 3},
    {"id": 103, "name": "Cash-in-Hand", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Petty cash and drawer.", "item_count": 1},
    {"id": 104, "name": "Bank Accounts", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Operating bank ledgers.", "item_count": 2},
    {"id": 105, "name": "Sales Accounts", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Sales income heads.", "item_count": 2},
    {"id": 106, "name": "Purchase Accounts", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Purchase expense heads.", "item_count": 2},
    {"id": 107, "name": "Duties & Taxes", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "GST input/output ledgers.", "item_count": 4},
    {"id": 108, "name": "Indirect Expenses", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Overheads and admin expenses.", "item_count": 6},
    {"id": 109, "name": "Direct Expenses", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Carriage, freight, and job work.", "item_count": 3},
    {"id": 110, "name": "Fixed Assets", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Furniture, vehicles, and equipment.", "item_count": 4},
    {"id": 111, "name": "Current Assets", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Deposits and other current assets.", "item_count": 2},
    {"id": 112, "name": "Loans & Advances", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Staff and party advances.", "item_count": 3},
    {"id": 113, "name": "Capital Account", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Owner capital and drawings.", "item_count": 2},
    {"id": 114, "name": "Suspense Account", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "ledger", "active": True, "notes": "Temporary holding ledgers.", "item_count": 1},
]

GODOWN_GROUP_RECORDS = [
    {"id": 201, "name": "Primary", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "godown", "active": True, "notes": "Main wholesale storage classification.", "item_count": 2},
    {"id": 202, "name": "Retail", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "godown", "active": True, "notes": "Counter / showroom floors.", "item_count": 1},
    {"id": 203, "name": "Transit / Temporary", "gst": 0, "parent": "Primary / Top-Level [Root]",
     "kind": "godown", "active": True, "notes": "Loading bay and buffer yards.", "item_count": 1},
]

ITEM_GROUPS = [g["name"] for g in PRODUCT_GROUP_RECORDS]
LEDGER_GROUPS = [g["name"] for g in LEDGER_GROUP_RECORDS]
GODOWN_GROUPS = [g["name"] for g in GODOWN_GROUP_RECORDS]

PRODUCTS = [
    {"id": 1, "sku": "SKU-WIR-001", "name": "Polycab 2.5mm² FR Single Core Flame Retardant (Red)",
     "group": "Wires & Cables", "hsn": "8544", "unit": "ROL (90m)", "sale_rate": 1450.00,
     "purchase_rate": 1280.00, "gst": 18, "stock": 42, "warehouse": "Main Wholesale Godown",
     "min_stock": 10, "opening_qty": 40},
    {"id": 2, "sku": "SKU-WIR-002", "name": "Finolex 1.5mm² FRLS Industrial Grade (Blue)",
     "group": "Wires & Cables", "hsn": "8544", "unit": "ROL (90m)", "sale_rate": 1120.00,
     "purchase_rate": 980.00, "gst": 18, "stock": 28, "warehouse": "Main Wholesale Godown",
     "min_stock": 8, "opening_qty": 30},
    {"id": 3, "sku": "SKU-WIR-003", "name": "Anchor Advance 1.0mm² PVC Flexible Cable (Yellow)",
     "group": "Wires & Cables", "hsn": "8544", "unit": "ROL (90m)", "sale_rate": 890.00,
     "purchase_rate": 760.00, "gst": 18, "stock": 36, "warehouse": "Main Wholesale Godown",
     "min_stock": 10, "opening_qty": 35},
    {"id": 4, "sku": "SKU-WIR-004", "name": "RR Kabel 4.0mm² Multi-strand Heavy Duty (Black)",
     "group": "Wires & Cables", "hsn": "8544", "unit": "ROL (90m)", "sale_rate": 2340.00,
     "purchase_rate": 2050.00, "gst": 18, "stock": 18, "warehouse": "Main Wholesale Godown",
     "min_stock": 6, "opening_qty": 20},
    {"id": 5, "sku": "SW-MOD-1W", "name": "Modular Switch 1-Way", "group": "Switchgear & Modular",
     "hsn": "8536", "unit": "Pcs", "sale_rate": 45.00, "purchase_rate": 32.00,
     "gst": 18, "stock": 500, "warehouse": "Main Wholesale Godown", "min_stock": 100, "opening_qty": 480},
    {"id": 6, "sku": "SW-SOCK-6A", "name": "6A Socket Outlet", "group": "Switchgear & Modular",
     "hsn": "8536", "unit": "Pcs", "sale_rate": 85.00, "purchase_rate": 58.00,
     "gst": 18, "stock": 320, "warehouse": "Counter / Retail Floor", "min_stock": 50, "opening_qty": 300},
    {"id": 7, "sku": "MCB-16A-SP", "name": "MCB 16A Single Pole", "group": "Industrial MCB & DBs",
     "hsn": "8536", "unit": "Pcs", "sale_rate": 165.00, "purchase_rate": 118.00,
     "gst": 18, "stock": 8, "warehouse": "Main Wholesale Godown", "min_stock": 20, "opening_qty": 25},
    {"id": 8, "sku": "LED-9W", "name": "LED Bulb 9W", "group": "Commercial Lighting",
     "hsn": "8539", "unit": "Pcs", "sale_rate": 95.00, "purchase_rate": 62.00,
     "gst": 12, "stock": 210, "warehouse": "Counter / Retail Floor", "min_stock": 40, "opening_qty": 200},
    {"id": 9, "sku": "PVC-20MM", "name": "PVC Conduit 20mm (3m)", "group": "PVC Conduit & Piping",
     "hsn": "3917", "unit": "Pcs", "sale_rate": 28.00, "purchase_rate": 18.00,
     "gst": 18, "stock": 800, "warehouse": "Main Wholesale Godown", "min_stock": 200, "opening_qty": 750},
    {"id": 10, "sku": "MTR-1HP", "name": "1 HP Single Phase Motor", "group": "Motors & Pumps",
     "hsn": "8501", "unit": "Pcs", "sale_rate": 4850.00, "purchase_rate": 4120.00,
     "gst": 18, "stock": 6, "warehouse": "Main Wholesale Godown", "min_stock": 2, "opening_qty": 8},
]

# Back-compat alias used by older screens
for _p in PRODUCTS:
    _p.setdefault("rate", _p["sale_rate"])

GODOWNS = [
    {"id": 1, "code": "GDN-01", "name": "Main Wholesale Godown", "ref_id": "GDN-REC-00104",
     "incharge": "Murugan", "phone": "+91 98480 11001", "alt_phone": "044-2250-1100",
     "address": "Yard A, Guindy Industrial Estate, Chennai - 600032",
     "location_label": "Guindy Shed #4", "item_count": 342, "status": "Primary / Active",
     "role_tag": "Inward Hub", "active": True, "is_default": True,
     "icon": "location_on"},
    {"id": 2, "code": "GDN-02", "name": "Counter / Retail Floor", "ref_id": "GDN-REC-00105",
     "incharge": "Priya", "phone": "+91 98480 11002", "alt_phone": "",
     "address": "Front Counter, Guindy Showroom, Chennai - 600032",
     "location_label": "Shop Front", "item_count": 128, "status": "Active Retail",
     "role_tag": "Direct POS", "active": True, "is_default": False,
     "icon": "store"},
    {"id": 3, "code": "GDN-03", "name": "Station Road Depot", "ref_id": "GDN-REC-00106",
     "incharge": "Karthik", "phone": "+91 98480 11003", "alt_phone": "",
     "address": "Station Road Warehouse, Guindy, Chennai - 600032",
     "location_label": "IDA Guindy Phase-1", "item_count": 85, "status": "Active Secondary",
     "role_tag": "Bulk Cable Racks", "active": True, "is_default": False,
     "icon": "warehouse"},
    {"id": 4, "code": "GDN-04", "name": "Transit & Yard Dump", "ref_id": "GDN-REC-00107",
     "incharge": "Senthil", "phone": "+91 98480 11004", "alt_phone": "",
     "address": "Loading Bay Buffer, Guindy Yard, Chennai - 600032",
     "location_label": "Loading Bay Buffer", "item_count": 14, "status": "Buffer Clearance",
     "role_tag": "Temporary", "active": True, "is_default": False,
     "icon": "local_shipping"},
]

GODOWN_STOCK = {
    1: [
        {"sku": "SKU-WIR-001", "name": "Polycab 2.5mm² FR Single Core Flame Retardant (Red)",
         "group": "Wires & Cables", "qty": 42, "unit": "ROL (90m)", "value": 60900.00},
        {"sku": "SKU-WIR-002", "name": "Finolex 1.5mm² FRLS Industrial Grade (Blue)",
         "group": "Wires & Cables", "qty": 28, "unit": "ROL (90m)", "value": 31360.00},
        {"sku": "MCB-16A-SP", "name": "MCB 16A Single Pole", "group": "Industrial MCB & DBs",
         "qty": 8, "unit": "Pcs", "value": 1320.00},
        {"sku": "MTR-1HP", "name": "1 HP Single Phase Motor", "group": "Motors & Pumps",
         "qty": 6, "unit": "Pcs", "value": 29100.00},
        {"sku": "PVC-20MM", "name": "PVC Conduit 20mm (3m)", "group": "PVC Conduit & Piping",
         "qty": 800, "unit": "Pcs", "value": 22400.00},
    ],
}

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
}

# Stitch — Today's Counter Summary & Cash Split
COUNTER_SUMMARY = [
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
]

# Stitch — Fast Item Lookup table
FAST_LOOKUP_ITEMS = [
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
]

LOW_STOCK_ALERTS = [
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

PENDING_OVERDUE = [
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

# Back-compat aliases used by older dashboard widgets / screens
TODAYS_INVOICES = [
    {"doc": "INV-2026-0842", "party": "Sri Venkateshwara Electricals", "amount": 41400.00},
    {"doc": "INV-2026-0841", "party": "Sai Balaji Electricals", "amount": 12675.00},
    {"doc": "INV-2026-0840", "party": "Maruthi Power Controls", "amount": 9200.00},
    {"doc": "INV-2026-0839", "party": "Kiran Infra & Projects", "amount": 8400.00},
    {"doc": "INV-2026-0838", "party": "S.K. Enterprises (Cash Sale)", "amount": 13750.00},
]

LOW_STOCK_ITEMS = [
    {"name": a["name"], "left": 0, "out": False} for a in LOW_STOCK_ALERTS
]

PENDING_COLLECTIONS = [
    {"party": p["party"], "note": p["note"], "amount": p["amount"]} for p in PENDING_OVERDUE
]

TERMINAL_NAME = "Terminal-01 (Main Counter)"
SERVER_STATUS = "Server: 192.168.1.104 (Connected)"
SYNC_STATUS = "Sync: Instant"
DASHBOARD_WELCOME = "Welcome back, Ramesh"
DASHBOARD_SHIFT = "Main Wholesale Counter · Shift active since 08:30 AM · Auto-sync: Active"
COUNTER_SHIFT_LABEL = "Shift: 08:30 AM - Ongoing"

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
