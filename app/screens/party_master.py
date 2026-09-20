"""Party (Ledger) Master — Zoho-styled list-detail."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import (
    balance_label, card_frame, field_label, make_button, page_title, toast,
)


class PartyMasterScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parties = [dict(p) for p in D.PARTIES]
        self._index_map = []
        self._build()
        if self.list.count():
            self.list.setCurrentRow(0)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        bar = QHBoxLayout()
        bar.addWidget(page_title("1.2 Ledger Parties"))
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
        left.setMaximumWidth(T.LIST_PANEL_W + 40)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.setSpacing(6)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter Party Name…")
        self.filter.textChanged.connect(self._refresh)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._load_detail)
        ll.addWidget(self.filter)
        ll.addWidget(self.list)
        split.addWidget(left)

        right = card_frame()
        self._right_lay = QVBoxLayout(right)
        self._right_lay.setContentsMargins(16, 12, 16, 12)
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit()
        self.ptype = QComboBox()
        self.ptype.addItems(["Customer", "Supplier", "Both"])
        self.gstin = QLineEdit()
        self.phone = QLineEdit()
        self.address = QLineEdit()
        self.city = QLineEdit()
        self.credit_days = QSpinBox()
        self.credit_days.setRange(0, 365)
        self.credit_limit = QDoubleSpinBox()
        self.credit_limit.setRange(0, 99999999)
        self.credit_limit.setDecimals(2)
        self.credit_limit.setPrefix("Rs. ")
        self.balance = QDoubleSpinBox()
        self.balance.setRange(0, 99999999)
        self.balance.setDecimals(2)
        self.balance.setPrefix("Rs. ")
        self.balance_type = QComboBox()
        self.balance_type.addItems(["Dr", "Cr"])
        self.err = QLabel("")
        self.err.setStyleSheet(f"color: {T.DANGER}; font-size: {T.FONT_SIZE_SHORTCUT}pt;")

        form.addRow(field_label("Party Name"), self.name)
        form.addRow(field_label("Customer / Supplier"), self.ptype)
        form.addRow(field_label("Contact"), self.phone)
        form.addRow(field_label("Address"), self.address)
        form.addRow(field_label("City"), self.city)
        form.addRow(field_label("GSTIN"), self.gstin)
        form.addRow(field_label("Opening Balance"), self.balance)
        form.addRow(field_label("Debit / Credit"), self.balance_type)
        form.addRow(field_label("Credit Limit"), self.credit_limit)
        form.addRow(field_label("Credit Days"), self.credit_days)
        self._right_lay.addLayout(form)
        self._right_lay.addWidget(self.err)
        self.bal_preview = balance_label(0)
        self._right_lay.addWidget(self.bal_preview, alignment=Qt.AlignLeft)
        self._right_lay.addStretch()
        split.addWidget(right)
        root.addWidget(split, stretch=1)
        self._refresh()

    def _refresh(self):
        q = self.filter.text().strip().lower()
        self.list.clear()
        self._index_map = []
        for i, p in enumerate(self.parties):
            if q and q not in p["name"].lower():
                continue
            self._index_map.append(i)
            self.list.addItem(QListWidgetItem(f"{p['name']}  ({p['type']})"))

    def _set_balance_preview(self, amount: float):
        self._right_lay.removeWidget(self.bal_preview)
        self.bal_preview.deleteLater()
        self.bal_preview = balance_label(amount)
        self._right_lay.insertWidget(2, self.bal_preview, alignment=Qt.AlignLeft)

    def _load_detail(self, row: int):
        if row < 0 or row >= len(self._index_map):
            return
        p = self.parties[self._index_map[row]]
        self.name.setText(p["name"])
        self.ptype.setCurrentText(p["type"])
        self.gstin.setText(p.get("gstin", ""))
        self.phone.setText(p.get("phone", ""))
        self.address.setText(p.get("address", ""))
        self.city.setText(p.get("city", ""))
        self.credit_days.setValue(int(p.get("credit_days", 0)))
        self.credit_limit.setValue(float(p.get("credit_limit", 0)))
        signed = float(p.get("balance", 0))
        self.balance.setValue(abs(signed))
        bt = p.get("balance_type") or ("Dr" if signed >= 0 else "Cr")
        self.balance_type.setCurrentText(bt)
        self._set_balance_preview(signed)
        self.err.clear()

    def _new(self):
        self.parties.append({
            "id": max((p["id"] for p in self.parties), default=0) + 1,
            "name": "New Party", "type": "Customer", "gstin": "", "phone": "",
            "address": "", "city": "", "balance": 0.0, "balance_type": "Dr",
            "credit_limit": 0.0, "credit_days": 30,
        })
        self.filter.clear()
        self._refresh()
        self.list.setCurrentRow(self.list.count() - 1)
        toast(self, "New party drafted.")

    def _save(self):
        row = self.list.currentRow()
        if row < 0:
            return
        if not self.name.text().strip():
            self.err.setText("Party Name is required.")
            return
        p = self.parties[self._index_map[row]]
        bal = float(self.balance.value())
        bal = -abs(bal) if self.balance_type.currentText() == "Cr" else abs(bal)
        p.update({
            "name": self.name.text().strip(),
            "type": self.ptype.currentText(),
            "gstin": self.gstin.text().strip(),
            "phone": self.phone.text().strip(),
            "address": self.address.text().strip(),
            "city": self.city.text().strip(),
            "balance": bal,
            "balance_type": self.balance_type.currentText(),
            "credit_limit": float(self.credit_limit.value()),
            "credit_days": int(self.credit_days.value()),
        })
        self.err.clear()
        self._refresh()
        self.list.setCurrentRow(row)
        toast(self, "Party saved.")

    def _delete(self):
        row = self.list.currentRow()
        if row < 0:
            return
        idx = self._index_map[row]
        name = self.parties[idx]["name"]
        del self.parties[idx]
        self._refresh()
        toast(self, f"Deleted {name}.")
