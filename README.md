# Wholesale Billing & Inventory (Desktop ERP)

Native Python desktop ERP for wholesale electrical-goods distribution — purchase, sales, stock, and GST accounts. Designed for high-frequency keyboard data entry on low-end shop PCs (Windows 7/10, 2–4 GB RAM).

## Stack

- **Primary:** PyQt5 + QSS (Zoho Inventory palette)
- **Style:** Qt **Fusion** (same look on Mac preview and Windows `.exe`)
- **Nav:** Collapsible accordion (Master / Operations / Reports / Settings)
- **Grids:** `QTableWidget` (no heavy chart libs)
- **Target resolution:** 1366×768 (primary), 1920×1080 (secondary)
- **Target OS:** Windows 7/10 shop PCs (2–4 GB RAM)

## Run

```bash
conda activate billing-software
pip install -r requirements.txt
python main.py
```

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+K / `/` | Global search |
| Alt+1 | Master Setup |
| Alt+2 | Sales Invoice |
| Alt+3 | Purchase Entry |
| Alt+4 | Cash Flow |
| F2 | Search item (transaction screens) |
| F5 | New sales entry |
| F9 | Save & Print |
| F10 | Save & New |
| Ctrl+P | Print Preview |
| Esc | Cancel / clear focus |

## Screens

**Dashboard** — KPI cards, top sellers, stocked items, channel mix, pending actions, low stock  
**1. Master Setup** — Company, Parties, Groups, Products, Godowns  
**2. Operations** — Purchases, Sales, Cash Flow, Billwise Settlement, Estimates  
**3. Reports** — Ledger Statement, Sales/Purchase Registers, AR/AP, Export Tools  
**4. Settings** — Audit Trail, Users, Change FY, Year Rollover, License  
