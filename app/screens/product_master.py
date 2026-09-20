"""Product Master — list-detail."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import field_label, make_button


class ProductMasterScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.products = [dict(p) for p in D.PRODUCTS]
        self._build()
        if self.list.count():
            self.list.setCurrentRow(0)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        bar = QHBoxLayout()
        title = QLabel("Products")
        title.setStyleSheet(f"font-size: {T.FONT_SIZE_TITLE}pt; font-weight: bold;")
        bar.addWidget(title)
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

        left = QFrame()
        left.setStyleSheet(
            f"QFrame {{ background-color: {T.SURFACE}; border: 1px solid {T.BORDER}; }}"
        )
        left.setMinimumWidth(T.LIST_PANEL_W)
        left.setMaximumWidth(T.LIST_PANEL_W + 60)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter Product / SKU…")
        self.filter.textChanged.connect(self._filter)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._load_detail)
        ll.addWidget(self.filter)
        ll.addWidget(self.list)
        split.addWidget(left)

        right = QFrame()
        right.setStyleSheet(
            f"QFrame {{ background-color: {T.SURFACE}; border: 1px solid {T.BORDER}; }}"
        )
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 12, 16, 12)
        form_title = QLabel("Product Details")
        form_title.setStyleSheet(f"font-size: {T.FONT_SIZE_UI}pt; font-weight: bold;")
        rl.addWidget(form_title)

        form = QFormLayout()
        form.setSpacing(8)

        self.sku = QLineEdit()
        self.name = QLineEdit()
        self.group = QComboBox()
        self.group.addItems(D.ITEM_GROUPS)
        self.unit = QComboBox()
        self.unit.setEditable(True)
        self.unit.addItems(["Pcs", "Coil", "Box", "Roll", "Mtr", "Kg"])
        self.rate = QDoubleSpinBox()
        self.rate.setRange(0, 9999999)
        self.rate.setDecimals(2)
        self.rate.setPrefix("Rs. ")
        self.gst = QComboBox()
        self.gst.addItems(["0", "5", "12", "18", "28"])
        self.stock = QDoubleSpinBox()
        self.stock.setRange(0, 9999999)
        self.stock.setDecimals(3)
        self.min_stock = QDoubleSpinBox()
        self.min_stock.setRange(0, 999999)
        self.min_stock.setDecimals(3)
        self.warehouse = QComboBox()
        self.warehouse.addItems(D.WAREHOUSES)
        self.err = QLabel("")
        self.err.setStyleSheet(f"color: {T.DANGER}; font-size: {T.FONT_SIZE_SHORTCUT}pt;")

        form.addRow(field_label("SKU / Barcode"), self.sku)
        form.addRow(field_label("Product / Item"), self.name)
        form.addRow(field_label("Item Group / Category"), self.group)
        form.addRow(field_label("Unit"), self.unit)
        form.addRow(field_label("Rate"), self.rate)
        form.addRow(field_label("GST %"), self.gst)
        form.addRow(field_label("Stock Qty"), self.stock)
        form.addRow(field_label("Low Stock Alert"), self.min_stock)
        form.addRow(field_label("Warehouse / Location"), self.warehouse)
        rl.addLayout(form)
        rl.addWidget(self.err)
        rl.addStretch()
        split.addWidget(right)

        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        root.addWidget(split, stretch=1)
        self._refresh_list()

    def _refresh_list(self, select_id=None):
        self.list.clear()
        q = self.filter.text().strip().lower()
        for p in self.products:
            hay = f"{p['sku']} {p['name']}".lower()
            if q and q not in hay:
                continue
            low = " ⚠" if p["stock"] <= p["min_stock"] else ""
            item = QListWidgetItem(f"{p['sku']} — {p['name']}{low}")
            item.setData(Qt.UserRole, p["id"])
            if p["stock"] <= p["min_stock"]:
                item.setForeground(Qt.darkYellow)
            self.list.addItem(item)
            if select_id and p["id"] == select_id:
                self.list.setCurrentItem(item)

    def _filter(self, _):
        self._refresh_list()

    def _current(self):
        item = self.list.currentItem()
        if not item:
            return None
        pid = item.data(Qt.UserRole)
        return next((p for p in self.products if p["id"] == pid), None)

    def _load_detail(self, _):
        p = self._current()
        if not p:
            return
        self.sku.setText(p["sku"])
        self.name.setText(p["name"])
        self.group.setCurrentText(p["group"])
        self.unit.setCurrentText(p["unit"])
        self.rate.setValue(p["rate"])
        self.gst.setCurrentText(str(int(p["gst"])))
        self.stock.setValue(p["stock"])
        self.min_stock.setValue(p["min_stock"])
        self.warehouse.setCurrentText(p["warehouse"])
        self.err.setText("")

    def _new(self):
        new_id = max((p["id"] for p in self.products), default=0) + 1
        p = {
            "id": new_id, "sku": "NEW-SKU", "name": "New Product",
            "group": D.ITEM_GROUPS[0], "unit": "Pcs", "rate": 0.0,
            "gst": 18, "stock": 0, "warehouse": D.WAREHOUSES[0], "min_stock": 0,
        }
        self.products.append(p)
        self._refresh_list(select_id=p["id"])
        self.sku.setFocus()
        self.sku.selectAll()

    def _save(self):
        p = self._current()
        if not p:
            return
        if not self.name.text().strip() or not self.sku.text().strip():
            self.err.setText("SKU and Product / Item are required.")
            return
        p["sku"] = self.sku.text().strip()
        p["name"] = self.name.text().strip()
        p["group"] = self.group.currentText()
        p["unit"] = self.unit.currentText()
        p["rate"] = self.rate.value()
        p["gst"] = int(self.gst.currentText())
        p["stock"] = self.stock.value()
        p["min_stock"] = self.min_stock.value()
        p["warehouse"] = self.warehouse.currentText()
        self.err.setText("")
        self._refresh_list(select_id=p["id"])
        QMessageBox.information(self, "Saved", f"Product '{p['name']}' saved.")

    def _delete(self):
        p = self._current()
        if not p:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete product '{p['name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.products = [x for x in self.products if x["id"] != p["id"]]
            self._refresh_list()

    def _refresh(self):
        self.products = [dict(p) for p in D.PRODUCTS]
        self.filter.clear()
        self._refresh_list()
