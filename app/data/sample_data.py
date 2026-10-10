"""In-memory sample data for demo screens (no DB — potato-PC friendly)."""

from datetime import date, timedelta

COMPANY_NAME = "Sri Lakshmi Electricals"
COMPANY_TAGLINE = "Wholesale Billing & ERP"
FINANCIAL_YEAR = "FY 2026–27"
FISCAL_YEARS = ["FY 2024–25", "FY 2025–26", "FY 2026–27"]
CURRENT_USER = "Ramesh"
CURRENT_ROLE = "Billing Clerk"

# 4.3 / 4.4 A/c Year Management (Stitch)
AC_YEAR_ACTIVE = {
    "code": "FY 2026–27",
    "period": "01-Apr-2026 to 31-Mar-2027",
    "partition": "SLE_DATA_2026_V1",
    "vouchers": 1482,
    "schema": "Sri Lakshmi Wholesale FY26-27",
    "terminal": "Terminal-01 (Main Counter)",
}
AC_YEAR_PARTITIONS = [
    {
        "code": "FY 2026–27",
        "status": "Current",
        "partition": "SLE_DATA_2026_V1",
        "period": "01-Apr-2026 – 31-Mar-2027",
        "vouchers": 1482,
        "access": "Unlocked (Active)",
        "locked": False,
    },
    {
        "code": "FY 2025–26",
        "status": "Archived",
        "partition": "SLE_DATA_2025_FINAL",
        "period": "01-Apr-2025 – 31-Mar-2026",
        "vouchers": 8924,
        "access": "Locked (Audit)",
        "locked": True,
    },
    {
        "code": "FY 2024–25",
        "status": "Archived",
        "partition": "SLE_DATA_2024_FINAL",
        "period": "01-Apr-2024 – 31-Mar-2025",
        "vouchers": 7610,
        "access": "Locked (Audit)",
        "locked": True,
    },
]
AC_YEAR_NEW = {
    "code": "FY 2027–28",
    "period": "01-Apr-2027 to 31-Mar-2028",
    "sales_prefix": "SLE/27-28/",
    "purchase_prefix": "PUR/27-28/",
}

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
     "incharge": "Suresh Kumar - Warehouse Supervisor", "phone": "+91 98481 12345",
     "alt_phone": "040-27845612",
     "address": "Plot # 12, Phase-1, IDA Jeedimetla, Hyderabad, Telangana - 500055",
     "location_label": "Ranigunj Shed #4", "pin_zone": "Secunderabad Pin Zone",
     "item_count": 342, "status": "Primary / Active", "role_tag": "Inward Hub",
     "active": True, "is_default": True, "icon": "location_on"},
    {"id": 2, "code": "GDN-02", "name": "Counter / Retail Floor", "ref_id": "GDN-REC-00105",
     "incharge": "Priya", "phone": "+91 98480 11002", "alt_phone": "",
     "address": "Ranigunj Shop Front, Secunderabad, Telangana - 500003",
     "location_label": "Ranigunj Shop Front", "pin_zone": "Secunderabad Pin Zone",
     "item_count": 128, "status": "Active Retail", "role_tag": "Direct POS",
     "active": True, "is_default": False, "icon": "store"},
    {"id": 3, "code": "GDN-03", "name": "Station Road Depot", "ref_id": "GDN-REC-00106",
     "incharge": "Karthik", "phone": "+91 98480 11003", "alt_phone": "",
     "address": "IDA Jeedimetla Phase-1, Hyderabad, Telangana - 500055",
     "location_label": "IDA Jeedimetla Phase-1", "pin_zone": "Jeedimetla Pin Zone",
     "item_count": 85, "status": "Active Secondary", "role_tag": "Bulk Cable Racks",
     "active": True, "is_default": False, "icon": "warehouse"},
    {"id": 4, "code": "GDN-04", "name": "Transit & Yard Dump", "ref_id": "GDN-REC-00107",
     "incharge": "Senthil", "phone": "+91 98480 11004", "alt_phone": "",
     "address": "Loading Bay Buffer, Ranigunj Yard, Secunderabad - 500003",
     "location_label": "Loading Bay Buffer", "pin_zone": "Secunderabad Pin Zone",
     "item_count": 14, "status": "Buffer Clearance", "role_tag": "Temporary",
     "active": True, "is_default": False, "icon": "local_shipping"},
]

GODOWN_STOCK = {
    1: [
        {"sku": "CAB-1025", "name": "Finolex 1.5 Sqmm Copper Wire (Red)",
         "group": "Cables & Flexible Wires", "qty": 140.00, "unit": "ROL", "value": 238000.00},
        {"sku": "CAB-1028", "name": "Polycab 2.5 Sqmm FR Industrial (Yellow)",
         "group": "Cables & Flexible Wires", "qty": 95.00, "unit": "ROL", "value": 261250.00},
        {"sku": "SWT-4002", "name": "Schneider 16A 1-Way Modular Switch",
         "group": "Modular Switches & Sockets", "qty": 1250.00, "unit": "NOS", "value": 143750.00},
        {"sku": "MCB-2016", "name": "Legrand DX3 32A Double Pole MCB",
         "group": "Switchgear & Protection", "qty": 320.00, "unit": "NOS", "value": 214400.00},
        {"sku": "LGT-8012", "name": "Philips 20W LED Slim Batten 4ft Cool Day",
         "group": "Commercial Lighting", "qty": 410.00, "unit": "NOS", "value": 127100.00},
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

# Stitch 2.4 Billwise — Balaji Electricals pending sales invoices
RECEIVABLES = [
    # Stitch 2.4 Billwise — Balaji demo rows (exact invoice nos / amounts)
    {"party": "Balaji Electricals & Hardware", "bill": "SLE/26-27/0742",
     "date": "2026-08-15", "due": "2026-09-14",
     "amount": 18250.00, "balance": 13250.00, "days": 36, "overdue": True},
    {"party": "Balaji Electricals & Hardware", "bill": "SLE/26-27/0799",
     "date": "2026-09-02", "due": "2026-10-02",
     "amount": 20400.00, "balance": 20400.00, "days": 18, "overdue": False},
    {"party": "Balaji Electricals & Hardware", "bill": "SLE/26-27/0843",
     "date": "2026-09-20", "due": "2026-10-20",
     "amount": 8850.00, "balance": 8850.00, "days": 0, "overdue": False},
    {"party": "Venkateshwara Electricals & Hardware", "bill": "SLE/26-27/0801",
     "date": "2026-08-22", "due": "2026-09-12",
     "amount": 28500.00, "balance": 28500.00, "days": 29, "overdue": True},
    {"party": "Venkateshwara Electricals & Hardware", "bill": "SLE/26-27/0825",
     "date": "2026-09-10", "due": "2026-10-01",
     "amount": 20000.00, "balance": 20000.00, "days": 10, "overdue": False},
    {"party": "Sri Sai Builders & Infra Pvt Ltd", "bill": "SLE/26-27/0790",
     "date": "2026-08-05", "due": "2026-09-04",
     "amount": 75000.00, "balance": 62000.00, "days": 46, "overdue": True},
    {"party": "Sri Sai Builders & Infra Pvt Ltd", "bill": "SLE/26-27/0840",
     "date": "2026-09-18", "due": "2026-10-18",
     "amount": 50000.00, "balance": 50000.00, "days": 2, "overdue": False},
    {"party": "Meenakshi Enterprises", "bill": "SLE/26-27/0835",
     "date": "2026-09-15", "due": "2026-09-30",
     "amount": 14350.00, "balance": 14350.00, "days": 5, "overdue": False},
]

PAYABLES = [
    # Default supplier view — Polycab (same pattern as Balaji receivables)
    {"party": "Polycab India Ltd", "bill": "PI/26-27/0362",
     "date": "2026-08-10", "due": "2026-09-24",
     "amount": 48200.00, "balance": 22000.00, "days": 41, "overdue": True},
    {"party": "Polycab India Ltd", "bill": "PI/26-27/0379",
     "date": "2026-08-28", "due": "2026-10-12",
     "amount": 38500.00, "balance": 38500.00, "days": 23, "overdue": False},
    {"party": "Polycab India Ltd", "bill": "PI/26-27/0388",
     "date": "2026-09-12", "due": "2026-10-27",
     "amount": 57100.00, "balance": 57100.00, "days": 8, "overdue": False},
    {"party": "Havells India Limited", "bill": "PI/26-27/0380",
     "date": "2026-08-28", "due": "2026-09-27",
     "amount": 45000.00, "balance": 22000.00, "days": 23, "overdue": True},
    {"party": "Havells India Limited", "bill": "PI/26-27/0391",
     "date": "2026-09-14", "due": "2026-10-29",
     "amount": 68000.00, "balance": 68000.00, "days": 6, "overdue": False},
    {"party": "Polycab Wires Pvt Ltd", "bill": "PI/26-27/0371",
     "date": "2026-08-20", "due": "2026-09-19",
     "amount": 92000.00, "balance": 54000.00, "days": 31, "overdue": True},
    {"party": "Polycab Wires Pvt Ltd", "bill": "PI/26-27/0395",
     "date": "2026-09-16", "due": "2026-10-16",
     "amount": 41200.00, "balance": 41200.00, "days": 4, "overdue": False},
    {"party": "Finolex Cables", "bill": "PI/26-27/0375",
     "date": "2026-08-15", "due": "2026-09-14",
     "amount": 31200.00, "balance": 0.00, "days": 36, "overdue": False},
]

# Stitch 2.3 Cash Flow Register sample rows
CASH_ENTRIES = [
    {"date": "2026-09-20", "time": "02:15 PM", "kind": "In", "mode": "Cash",
     "ref": "CSH-IN-048", "party": "Balaji Electricals & Hardwares",
     "purpose": "Debtors Collection · Against Bill #SLE/26-27/0839", "amount": 18500.00},
    {"date": "2026-09-20", "time": "01:40 PM", "kind": "Out", "mode": "Cash",
     "ref": "CSH-OUT-019", "party": "Hamali & Loading Charges",
     "purpose": "Warehouse Expense · Tempo TS09-UB-4421 unloading", "amount": 850.00},
    {"date": "2026-09-20", "time": "12:30 PM", "kind": "In", "mode": "Cash",
     "ref": "CSH-IN-047", "party": "Counter Cash Sale (Walk-in)",
     "purpose": "Direct Retail Bill · 2 Rolls 1.5mm Wire (Slip #104)", "amount": 2450.00},
    {"date": "2026-09-20", "time": "11:15 AM", "kind": "Out", "mode": "Cash",
     "ref": "CSH-OUT-018", "party": "Polycab India Limited",
     "purpose": "Supplier Advance · Urgent booking #882", "amount": 35000.00},
]

CASH_FLOW_KPI = {
    "opening": 15000.00,
    "cash_in": 142850.00,
    "cash_out": 38400.00,
    "remaining": 119450.00,
    "in_count": 28,
    "out_count": 14,
}

# Stitch previous-history tables under Sales / Purchase entry
PREV_SALES = [
    {"inv": "SLE/26-27/0710", "date": "10-Aug-2026", "item": "Polycab 2.5 sq mm FR Red",
     "rate": 1420.00, "qty": 15, "unit": "ROL", "amount": 21300.00},
    {"inv": "SLE/26-27/0688", "date": "24-Jul-2026", "item": "Havells 16A Modular Switch 1-Way",
     "rate": 82.00, "qty": 120, "unit": "NOS", "amount": 9840.00},
    {"inv": "SLE/26-27/0651", "date": "05-Jul-2026", "item": "Philips 20W LED Batten Tube Light",
     "rate": 235.00, "qty": 40, "unit": "NOS", "amount": 9400.00},
    {"inv": "SLE/26-27/0612", "date": "18-Jun-2026", "item": "Finolex 1.5 sq mm 90m Copper Wire",
     "rate": 1090.00, "qty": 20, "unit": "ROL", "amount": 21800.00},
]

PREV_PURCHASES = [
    {"inv": "PI/26-27/0340", "date": "12-Aug-2026", "item": "Polycab 2.5 sq mm FR Red",
     "rate": 1210.00, "qty": 40, "unit": "Coil", "amount": 48400.00},
    {"inv": "PI/26-27/0318", "date": "28-Jul-2026", "item": "Polycab 4.0 sq mm FR Green",
     "rate": 1880.00, "qty": 25, "unit": "Coil", "amount": 47000.00},
    {"inv": "PI/26-27/0295", "date": "15-Jul-2026", "item": "Havells 16A Modular Switch Crabtree",
     "rate": 66.50, "qty": 150, "unit": "Pcs", "amount": 9975.00},
    {"inv": "PI/26-27/0271", "date": "02-Jun-2026", "item": "Finolex 1.5 sq mm Blue FR",
     "rate": 925.00, "qty": 50, "unit": "Coil", "amount": 46250.00},
]

# Previous estimates shown under Sales Entry when voucher type = Estimate
PREV_ESTIMATES = [
    {"inv": "EST/26-27/0088", "date": "28-Aug-2026", "item": "Polycab 2.5 sq mm FR Red",
     "rate": 1380.00, "qty": 20, "unit": "ROL", "amount": 27600.00},
    {"inv": "EST/26-27/0084", "date": "12-Aug-2026", "item": "Havells 16A Modular Switch 1-Way",
     "rate": 78.00, "qty": 150, "unit": "NOS", "amount": 11700.00},
    {"inv": "EST/26-27/0079", "date": "30-Jul-2026", "item": "Philips 20W LED Batten Tube Light",
     "rate": 225.00, "qty": 50, "unit": "NOS", "amount": 11250.00},
    {"inv": "EST/26-27/0072", "date": "15-Jul-2026", "item": "Finolex 1.5 sq mm 90m Copper Wire",
     "rate": 1050.00, "qty": 25, "unit": "ROL", "amount": 26250.00},
]

# Previous sales returns (voucher type = Sales Return)
PREV_SALES_RETURNS = [
    {"inv": "SR/26-27/0042", "date": "22-Aug-2026", "item": "Polycab 2.5 sq mm FR Red",
     "rate": 1420.00, "qty": 2, "unit": "ROL", "amount": 2840.00},
    {"inv": "SR/26-27/0038", "date": "08-Aug-2026", "item": "Havells 16A Modular Switch 1-Way",
     "rate": 82.00, "qty": 10, "unit": "NOS", "amount": 820.00},
    {"inv": "SR/26-27/0031", "date": "19-Jul-2026", "item": "Philips 20W LED Batten Tube Light",
     "rate": 235.00, "qty": 5, "unit": "NOS", "amount": 1175.00},
    {"inv": "SR/26-27/0025", "date": "02-Jul-2026", "item": "Finolex 1.5 sq mm 90m Copper Wire",
     "rate": 1090.00, "qty": 3, "unit": "ROL", "amount": 3270.00},
]

# Stitch Alt+H history modals (Purchase / Sales)
PURCHASE_HISTORY = [
    {"inv": "PUR-8420", "date": "12-Aug-2026", "party_inv": "PC/INV/8821",
     "item": "Polycab 2.5 sq mm FR Red", "qty": 40, "unit": "Coil",
     "rate": 1210.00, "disc": 0.0, "gst": 18.0, "amount": 48400.00, "status": "Received"},
    {"inv": "PUR-8219", "date": "28-Jul-2026", "party_inv": "PC/INV/8710",
     "item": "Polycab 4.0 sq mm FR Green", "qty": 25, "unit": "Coil",
     "rate": 1880.00, "disc": 0.0, "gst": 18.0, "amount": 47000.00, "status": "Received"},
    {"inv": "PUR-7984", "date": "15-Jul-2026", "party_inv": "HV/882",
     "item": "Havells 16A Modular Switch Crabtree", "qty": 150, "unit": "Pcs",
     "rate": 66.50, "disc": 0.0, "gst": 18.0, "amount": 9975.00, "status": "Received"},
    {"inv": "PUR-7702", "date": "02-Jun-2026", "party_inv": "FX/4410",
     "item": "Finolex 1.5 sq mm Blue FR", "qty": 50, "unit": "Coil",
     "rate": 925.00, "disc": 0.0, "gst": 18.0, "amount": 46250.00, "status": "Received"},
    {"inv": "PUR-7510", "date": "18-May-2026", "party_inv": "PC/INV/8502",
     "item": "Polycab 1.0 sq mm FR Yellow", "qty": 80, "unit": "Coil",
     "rate": 680.00, "disc": 2.0, "gst": 18.0, "amount": 53312.00, "status": "Received"},
    {"inv": "PUR-7340", "date": "04-May-2026", "party_inv": "PC/INV/8411",
     "item": "Polycab 6.0 sq mm FR Black", "qty": 30, "unit": "Coil",
     "rate": 2850.00, "disc": 0.0, "gst": 18.0, "amount": 85500.00, "status": "Verified"},
    {"inv": "PUR-7102", "date": "21-Apr-2026", "party_inv": "PC/INV/8300",
     "item": "Polycab 2.5 sq mm FR Red", "qty": 60, "unit": "Coil",
     "rate": 1195.00, "disc": 0.0, "gst": 18.0, "amount": 71700.00, "status": "Verified"},
    {"inv": "PUR-6901", "date": "08-Apr-2026", "party_inv": "HV/801",
     "item": "Havells 16A Modular Switch Crabtree", "qty": 200, "unit": "Pcs",
     "rate": 64.00, "disc": 0.0, "gst": 18.0, "amount": 12800.00, "status": "Received"},
]

SALES_HISTORY = [
    {"inv": "SLE-8102", "date": "10-Aug-2026", "vehicle": "TS09 UB 2211",
     "item": "Polycab 2.5 sq mm FR Red Wire", "qty": 15, "unit": "ROL",
     "rate": 1420.00, "disc": 0.0, "gst": 18.0, "amount": 21300.00, "status": "Paid"},
    {"inv": "SLE-7984", "date": "24-Jul-2026", "vehicle": "—",
     "item": "Havells 16A Modular Switch 1-Way Crabtree", "qty": 120, "unit": "NOS",
     "rate": 82.00, "disc": 0.0, "gst": 18.0, "amount": 9840.00, "status": "Paid"},
    {"inv": "SLE-7811", "date": "05-Jul-2026", "vehicle": "TS07 EN 1092",
     "item": "Philips 20W LED Batten Tube Light 6500K", "qty": 40, "unit": "NOS",
     "rate": 235.00, "disc": 0.0, "gst": 18.0, "amount": 9400.00, "status": "Paid"},
    {"inv": "SLE-7640", "date": "18-Jun-2026", "vehicle": "—",
     "item": "Finolex 1.5 sq mm 90m Copper Wire (Blue)", "qty": 20, "unit": "ROL",
     "rate": 1090.00, "disc": 0.0, "gst": 18.0, "amount": 21800.00, "status": "Paid"},
    {"inv": "SLE-7512", "date": "28-May-2026", "vehicle": "TS09 AB 4410",
     "item": "Polycab 4.0 sq mm FR Green Wire", "qty": 10, "unit": "ROL",
     "rate": 2150.00, "disc": 0.0, "gst": 18.0, "amount": 21500.00, "status": "Paid"},
    {"inv": "SLE-7390", "date": "12-May-2026", "vehicle": "—",
     "item": "Havells 6A Modular Socket", "qty": 200, "unit": "NOS",
     "rate": 34.00, "disc": 0.0, "gst": 18.0, "amount": 6800.00, "status": "Paid"},
    {"inv": "SLE-7288", "date": "02-May-2026", "vehicle": "TS08 CD 1199",
     "item": "Polycab 2.5 sq mm FR Red Wire", "qty": 12, "unit": "ROL",
     "rate": 1410.00, "disc": 1.0, "gst": 18.0, "amount": 16729.00, "status": "Paid"},
    {"inv": "SLE-7105", "date": "18-Apr-2026", "vehicle": "—",
     "item": "Philips 20W LED Batten Tube Light 6500K", "qty": 25, "unit": "NOS",
     "rate": 230.00, "disc": 0.0, "gst": 18.0, "amount": 5750.00, "status": "Paid"},
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

# Stitch 4.1 A/c Log Customer — Balaji Electricals audit trail (exact design rows)
AC_LOG_PARTY = {
    "name": "Balaji Electricals & Hardware",
    "city": "Secunderabad, Telangana",
    "gstin": "36ABCDE1234F1Z5",
    "code": "DB-104",
    "address": "Shop #14-2-89, M.G. Road, Ranigunj, Secunderabad - 500003",
    "phone": "+91 98480 23411",
    "credit_limit": 750000.00,
    "balance": 42500.00,
    "balance_type": "Dr",
    "type": "Customer",
    "group": "Sundry Debtor",
    "events": 38,
    "last_txn": "Last transaction posted today at 02:45 PM",
    "overdue": True,
}

# Stitch 4.1 Party Switch Modal [F4] — lookup rows
AC_LOG_LOOKUP_PARTIES = [
    {
        "code": "DB-104", "name": "Balaji Electricals & Hardware",
        "city": "Secunderabad", "state": "Telangana",
        "address": "Shop #14-2-89, M.G. Road, Ranigunj, Secunderabad - 500003",
        "gstin": "36ABCDE1234F1Z5", "phone": "+91 98480 23411",
        "credit_limit": 750000.00, "balance": 42500.00, "balance_type": "Dr",
        "type": "Customer", "group": "Sundry Debtor", "active": True,
        "events": 38, "overdue": True,
        "last_txn": "Last transaction posted today at 02:45 PM",
    },
    {
        "code": "DB-108", "name": "Sri Sai Krupa Electrical Works",
        "city": "Balanagar", "state": "Hyderabad",
        "address": "Plot 12, IDA Balanagar, Hyderabad - 500037",
        "gstin": "36AABCS9012K1Z8", "phone": "+91 90000 11822",
        "credit_limit": 200000.00, "balance": 18340.00, "balance_type": "Dr",
        "type": "Customer", "group": "Sundry Debtor", "active": True,
        "events": 22, "overdue": True,
        "last_txn": "Last transaction posted 2 days ago",
    },
    {
        "code": "DB-112", "name": "Meenakshi Power & Lighting Systems",
        "city": "Ranigunj", "state": "Secunderabad",
        "address": "Shop 8, Ranigunj Main Road, Secunderabad - 500003",
        "gstin": "36AABCM5566H1Z0", "phone": "+91 90000 44556",
        "credit_limit": 100000.00, "balance": 6400.00, "balance_type": "Dr",
        "type": "Customer", "group": "Sundry Debtor", "active": True,
        "events": 14, "overdue": False,
        "last_txn": "Last transaction posted 5 days ago",
    },
    {
        "code": "DB-119", "name": "Venkateshwara Cables & Wires",
        "city": "Kukatpally", "state": "Hyderabad",
        "address": "KPHB Phase 3, Kukatpally, Hyderabad - 500072",
        "gstin": "36AABCV5678B1Z2", "phone": "+91 94401 88290",
        "credit_limit": 150000.00, "balance": 0.00, "balance_type": "Nil",
        "type": "Customer", "group": "Sundry Debtor", "active": True,
        "events": 9, "overdue": False,
        "last_txn": "Last transaction posted 12 days ago",
    },
    {
        "code": "CR-044", "name": "Polycab India Ltd",
        "city": "Secunderabad", "state": "Telangana",
        "address": "MG Road, Secunderabad - 500003",
        "gstin": "27AAACP1234A1Z5", "phone": "+91 40 2784 3311",
        "credit_limit": 500000.00, "balance": 117600.00, "balance_type": "Cr",
        "type": "Supplier", "group": "Sundry Creditor", "active": True,
        "events": 31, "overdue": True,
        "last_txn": "Last payment posted yesterday at 11:20 AM",
    },
    {
        "code": "CR-051", "name": "Havells India Limited",
        "city": "Nacharam", "state": "Hyderabad",
        "address": "Nacharam Industrial Area, Hyderabad",
        "gstin": "07AAACH7456L1Z0", "phone": "+91 40 2715 2200",
        "credit_limit": 500000.00, "balance": 245000.00, "balance_type": "Cr",
        "type": "Supplier", "group": "Sundry Creditor", "active": True,
        "events": 27, "overdue": False,
        "last_txn": "Last GRN posted 4 days ago",
    },
]
AC_LOG_KPI = {
    "invoiced": 582450.00,
    "bills": 38,
    "avg_ticket": 15327.60,
    "gst_pct": 98.2,
    "collected": 539950.00,
    "receipts": 24,
    "upi_pct": 84,
    "cash_pct": 16,
    "outstanding": 42500.00,
    "limit_lakh": 7.50,
    "safe_pct": 5.6,
    "last_action": "20-Sep-2026 02:45 PM",
    "last_by": "Ramesh (Billing Clerk)",
    "last_terminal": "Terminal-01",
}
# kind: debit | credit | system
AC_LOG_EVENTS = [
    {
        "date": "20-Sep-2026", "time": "14:45:12 IST",
        "class": "Sales Invoice", "kind": "debit",
        "voucher": "#SLE/26-27/0843", "voucher_sub": "Original Print #1",
        "operator": "Ramesh (Clerk)", "terminal": "T-01 [192.168.1.104]",
        "detail": "Tax Invoice Created: 12x Polycab 2.5mm Wire + 4x Havells 32A MCB",
        "detail_sub": "HSN: 8544 · CGST: 9% + SGST: 9% (₹8,460.00)",
        "badge": "E-Way: Generated",
        "impact": "+ ₹ 55,460.00 Dr", "impact_kind": "debit",
        "balance": "₹ 42,500.00 Dr", "balance_kind": "debit",
    },
    {
        "date": "18-Sep-2026", "time": "11:20:04 IST",
        "class": "Bank Receipt", "kind": "credit",
        "voucher": "#REC-BNK-1092", "voucher_sub": "UTR: HDFC0094821",
        "operator": "Suresh (Accounts)", "terminal": "T-02 [192.168.1.108]",
        "detail": "Payment Realized via HDFC Bank Current A/c #4928",
        "detail_sub": "Settled against Bill #SLE/26-27/0798 (Full) & #0812 (Partial ₹15,000)",
        "badge": None,
        "impact": "- ₹ 65,000.00 Cr", "impact_kind": "credit",
        "balance": "₹ 12,960.00 Cr", "balance_kind": "credit",
    },
    {
        "date": "15-Sep-2026", "time": "17:05:39 IST",
        "class": "System Audit", "kind": "system",
        "voucher": "#SYS-CR-MOD-88", "voucher_sub": "Audit Log #88",
        "operator": "Admin (Lakshmi N.)", "terminal": "SRV-MAIN-AUTH",
        "detail": "Credit Terms Modified: Credit Limit increased from ₹5,00,000 to ₹7,50,000",
        "detail_sub": "Approved based on 3-year track record and security cheque verification (Chq #449201)",
        "badge": None,
        "impact": "[No Balance Impact]", "impact_kind": "none",
        "balance": "₹ 52,040.00 Dr", "balance_kind": "debit",
    },
    {
        "date": "12-Sep-2026", "time": "16:14:22 IST",
        "class": "Cash Flow", "kind": "credit",
        "voucher": "#CSH-IN-0492", "voucher_sub": "Counter Receipt",
        "operator": "Ramesh (Clerk)", "terminal": "T-01 [192.168.1.104]",
        "detail": "Counter Cash Settlement by Representative (Venkatesh)",
        "detail_sub": "Denominations: 500x37 = ₹18,500. Cash drawer counter verified.",
        "badge": None,
        "impact": "- ₹ 18,500.00 Cr", "impact_kind": "credit",
        "balance": "₹ 52,040.00 Dr", "balance_kind": "debit",
    },
    {
        "date": "10-Sep-2026", "time": "09:40:15 IST",
        "class": "Master Record", "kind": "system",
        "voucher": "#AUD-MST-0312", "voucher_sub": "Profile Revision 4",
        "operator": "Suresh (Accounts)", "terminal": "T-02 [192.168.1.108]",
        "detail": "Customer Master Updated: Added Secondary Delivery Address (IDA Cherlapally Site)",
        "detail_sub": "Contact added: Site Engineer Srikanth (+91 97011 44552) for on-site dispatches",
        "badge": None,
        "impact": "[No Balance Impact]", "impact_kind": "none",
        "balance": "₹ 70,540.00 Dr", "balance_kind": "debit",
    },
    {
        "date": "05-Sep-2026", "time": "15:10:55 IST",
        "class": "Sales Invoice", "kind": "debit",
        "voucher": "#SLE/26-27/0812", "voucher_sub": "Original Print #1",
        "operator": "Ramesh (Clerk)", "terminal": "T-01 [192.168.1.104]",
        "detail": "Tax Invoice Created: 50x Philips 18W LED Downlights + 8x Distribution Boxes",
        "detail_sub": "Dispatched via Driver Mallesh (Auto TS09-UA-4821) to Secunderabad site",
        "badge": None,
        "impact": "+ ₹ 41,536.00 Dr", "impact_kind": "debit",
        "balance": "₹ 70,540.00 Dr", "balance_kind": "debit",
    },
    {
        "date": "02-Sep-2026", "time": "12:35:10 IST",
        "class": "Credit Note", "kind": "credit",
        "voucher": "#CN/26-27/0042", "voucher_sub": "Sales Return",
        "operator": "Suresh (Accounts)", "terminal": "T-02 [192.168.1.108]",
        "detail": "Return of 4x Damaged 18W Downlights against Bill #SLE/26-27/0798",
        "detail_sub": "Inspected by Stores; Goods returned into Godown-02 Secondary Scrap/RMA",
        "badge": None,
        "impact": "- ₹ 4,720.00 Cr", "impact_kind": "credit",
        "balance": "₹ 29,004.00 Dr", "balance_kind": "debit",
    },
    {
        "date": "28-Aug-2026", "time": "10:15:30 IST",
        "class": "Billwise Settle", "kind": "credit",
        "voucher": "#REC-BNK-0994", "voucher_sub": "IMPS: 62918804",
        "operator": "Ramesh (Clerk)", "terminal": "T-01 [192.168.1.104]",
        "detail": "Direct Bank Transfer Realized against Opening Balance Overdue",
        "detail_sub": "Receipt voucher generated and SMS acknowledgment triggered to +91 98480 23411",
        "badge": None,
        "impact": "- ₹ 50,000.00 Cr", "impact_kind": "credit",
        "balance": "₹ 33,724.00 Dr", "balance_kind": "debit",
    },
]

USERS = [
    {
        "id": 1,
        "initials": "RK",
        "username": "ramesh_clerk",
        "name": "Ramesh Kumar",
        "role": "Billing Clerk",
        "role_label": "Billing Clerk",
        "role_full": "Billing Clerk (POS Counter & Invoicing)",
        "terminal": "Terminal-01 (Main Counter)",
        "terminal_short": "T-01 Main Counter",
        "terminal_icon": "desktop_windows",
        "mobile": "+91 98480 23411",
        "last_login": "Login: 20-Sep 09:15 AM",
        "active": True,
        "privileges": ["sales", "purchase", "cash"],
    },
    {
        "id": 2,
        "initials": "LN",
        "username": "admin_lakshmi",
        "name": "K. Lakshmi Narayan (Managing Partner)",
        "role": "Admin",
        "role_label": "Admin",
        "role_full": "Admin (Full System Access)",
        "terminal": "Terminal-02 (Back Office)",
        "terminal_short": "T-02 Back Office",
        "terminal_icon": "laptop_mac",
        "mobile": "+91 98480 10001",
        "last_login": "Login: 20-Sep 08:30 AM",
        "active": True,
        "privileges": ["sales", "purchase", "cash", "master", "fy", "delete"],
    },
    {
        "id": 3,
        "initials": "SN",
        "username": "godown_suresh",
        "name": "Suresh Naidu",
        "role": "Inventory Manager",
        "role_label": "Inventory Mgr",
        "role_full": "Inventory Manager (Godown Inward/Stock)",
        "terminal": "Godown Desk (Stationary)",
        "terminal_short": "Godown Desk (Disabled)",
        "terminal_icon": "warehouse",
        "mobile": "+91 98480 33445",
        "last_login": "Login: 18-Sep 06:10 PM",
        "active": False,
        "privileges": ["purchase"],
    },
]

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

MACHINE_ID = "HW-A7F3-C91E-4B2D-88E0"
LICENSE_STATUS = "Not Activated"
