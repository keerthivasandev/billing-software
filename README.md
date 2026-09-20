# Wholesale Billing & Inventory (Desktop ERP)

Native Python desktop ERP for wholesale electrical-goods distribution — purchase, sales, stock, and GST accounts. Designed for high-frequency keyboard data entry on low-end shop PCs (Windows 7/10, 2–4 GB RAM).

## Stack

- **Primary:** PyQt5 + QSS (flat Windows ERP theme)
- **Style:** Qt **Fusion** (same look on Mac preview and Windows `.exe`)
- **Grids:** `QTableWidget`
- **Target resolution:** 1366×768 (primary), 1920×1080 (secondary)
- **Target OS:** Windows 7/10 shop PCs (develop on Mac is fine)

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| F2 | Search item (transaction screens) |
| F5 | New entry |
| F9 | Save & Print |
| F10 | Save & New |
| Ctrl+P | Print Preview |
| Esc | Cancel |
| Ctrl+D | Duplicate row |
| Delete | Remove row |
| Enter | Add line (fast input strip) |

## Screens

1. Dashboard  
2. Sales Invoice Entry  
3. Purchase Entry  
4. Party (Ledger) Master  
5. Product Master  
6. Payables & Receivables Summary  
7. License Activation  
