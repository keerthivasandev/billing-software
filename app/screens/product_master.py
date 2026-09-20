"""Product Catalog — Zoho-styled list-detail."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QSplitter, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import card_frame, field_label, make_button, page_title, toast


class ProductMasterScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.products = [dict(p) for p in D.PRODUCTS]
        self._index_map = []
        self._build()
        if self.list.count():
            self.list.setCurrentRow(0)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        bar = QHBoxLayout()
        bar.addWidget(page_title("1.4 Product Catalog"))
        bar.addStretch()
        self.btn_new = make_button("New")
        self.btn_save = make_button("Save", "primary")
        self.btn_delete = make_button("Delete", "destructive")
        self.btn_refresh = make_button("Refresh")
        self.btn_new.clicked.connect(self._new)
        self.btn_save.clicked.connect(self._save)
        self.btn_delete.clicked.connect(self._delete)
        self.btn_refresh.clicked.connect(self._refresh)
        for b in (self.btn_new, self.btn_save, self.btn_delete, self.btn_refresh):
            bar.addWidget(b)
        root.addLayout(bar)

        split = QSplitter(Qt.Horizontal)

        left = card_frame()
        left.setMinimumWidth(T.LIST_PANEL_W)
        left.setMaximumWidth(T.LIST_PANEL_W + 60)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter Product / SKU…")
        self.filter.textChanged.connect(self._refresh)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._load_detail)
        ll.addWidget(self.filter)
        ll.addWidget(self.list)
        split.addWidget(left)

        right = card_frame()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 12, 16, 12)
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        self.sku = QLineEdit()
        self.name = QLineEdit()
        self.hsn = QLineEdit()
        self.group = QComboBox()
        self.group.addItems(D.ITEM_GROUPS)
        self.unit = QComboBox()
        self.unit.setEditable(True)
        self.unit.addItems(["Pcs", "Box", "Mtr", "Kg", "Coil", "Roll"])
        self.sale_rate = QDoubleSpinBox()
        self.sale_rate.setRange(0, 9999999)
        self.sale_rate.setDecimals(2)
        self.sale_rate.setPrefix("Rs. ")
        self.purchase_rate = QDoubleSpinBox()
        self.purchase_rate.setRange(0, 9999999)
        self.purchase_rate.setDecimals(2)
        self.purchase_rate.setPrefix("Rs. ")
        self.gst = QComboBox()
        self.gst.addItems(["0", "5", "12", "18", "28"])
        self.stock = QDoubleSpinBox()
        self.stock.setRange(0, 9999999)
        self.stock.setDecimals(3)
        self.min_stock = QDoubleSpinBox()
        self.min_stock.setRange(0, 999999)
        self.min_stock.setDecimals(3)
        self.opening_qty = QDoubleSpinBox()
        self.opening_qty.setRange(0, 9999999)
        self.opening_qty.setDecimals(3)
        self.warehouse = QComboBox()
        self.warehouse.addItems(D.WAREHOUSES)
        self.err = QLabel("")
        self.err.setStyleSheet(f"color: {T.DANGER}; font-size: {T.FONT_SIZE_SHORTCUT}pt;")

        form.addRow(field_label("Item Name"), self.name)
        form.addRow(field_label("SKU / Barcode"), self.sku)
        form.addRow(field_label("HSN Code"), self.hsn)
        form.addRow(field_label("Product Group"), self.group)
        form.addRow(field_label("Unit of Sale"), self.unit)
        form.addRow(field_label("Sale Rate"), self.sale_rate)
        form.addRow(field_label("Purchase Rate"), self.purchase_rate)
        form.addRow(field_label("Tax Rate (GST %)"), self.gst)
        form.addRow(field_label("Minimum Alert Level"), self.min_stock)
        form.addRow(field_label("Opening Quantity"), self.opening_qty)
        form.addRow(field_label("Current Stock"), self.stock)
        form.addRow(field_label("Godown"), self.warehouse)
        rl.addLayout(form)
        rl.addWidget(self.err)
        rl.addStretch()
        split.addWidget(right)
        root.addWidget(split, stretch=1)
        self._refresh()

    def _refresh(self):
        q = self.filter.text().strip().lower()
        self.list.clear()
        self._index_map = []
        for i, p in enumerate(self.products):
            hay = f"{p['name']} {p['sku']}".lower()
            if q and q not in hay:
                continue
            self._index_map.append(i)
            self.list.addItem(QListWidgetItem(f"{p['sku']} — {p['name']}"))

    def _load_detail(self, row: int):
        if row < 0 or row >= len(self._index_map):
            return
        p = self.products[self._index_map[row]]
        self.sku.setText(p.get("sku", ""))
        self.name.setText(p.get("name", ""))
        self.hsn.setText(p.get("hsn", ""))
        self.group.setCurrentText(p.get("group", D.ITEM_GROUPS[0]))
        self.unit.setCurrentText(p.get("unit", "Pcs"))
        self.sale_rate.setValue(float(p.get("sale_rate", p.get("rate", 0))))
        self.purchase_rate.setValue(float(p.get("purchase_rate", 0)))
        self.gst.setCurrentText(str(int(p.get("gst", 18))))
        self.stock.setValue(float(p.get("stock", 0)))
        self.min_stock.setValue(float(p.get("min_stock", 0)))
        self.opening_qty.setValue(float(p.get("opening_qty", 0)))
        self.warehouse.setCurrentText(p.get("warehouse", D.WAREHOUSES[0]))
        self.err.clear()

    def _new(self):
        self.products.append({
            "id": max((p["id"] for p in self.products), default=0) + 1,
            "sku": "NEW-SKU", "name": "New Product", "group": D.ITEM_GROUPS[0],
            "hsn": "", "unit": "Pcs", "sale_rate": 0.0, "purchase_rate": 0.0,
            "rate": 0.0, "gst": 18, "stock": 0, "warehouse": D.WAREHOUSES[0],
            "min_stock": 0, "opening_qty": 0,
        })
        self.filter.clear()
        self._refresh()
        self.list.setCurrentRow(self.list.count() - 1)
        toast(self, "New product drafted.")

    def _save(self):
        row = self.list.currentRow()
        if row < 0:
            return
        if not self.name.text().strip():
            self.err.setText("Item Name is required.")
            return
        p = self.products[self._index_map[row]]
        sale = float(self.sale_rate.value())
        p.update({
            "sku": self.sku.text().strip(),
            "name": self.name.text().strip(),
            "hsn": self.hsn.text().strip(),
            "group": self.group.currentText(),
            "unit": self.unit.currentText(),
            "sale_rate": sale,
            "purchase_rate": float(self.purchase_rate.value()),
            "rate": sale,
            "gst": int(self.gst.currentText()),
            "stock": float(self.stock.value()),
            "min_stock": float(self.min_stock.value()),
            "opening_qty": float(self.opening_qty.value()),
            "warehouse": self.warehouse.currentText(),
        })
        self.err.clear()
        self._refresh()
        self.list.setCurrentRow(row)
        toast(self, "Product saved.")

    def _delete(self):
        row = self.list.currentRow()
        if row < 0:
            return
        idx = self._index_map[row]
        name = self.products[idx]["name"]
        del self.products[idx]
        self._refresh()
        toast(self, f"Deleted {name}.")
