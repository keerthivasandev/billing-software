"""Party (Ledger) Master — list-detail."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import balance_label, field_label, make_button, mono_font


class PartyMasterScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parties = [dict(p) for p in D.PARTIES]
        self._build()
        if self.list.count():
            self.list.setCurrentRow(0)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # Toolbar
        bar = QHBoxLayout()
        title = QLabel("Parties (Customers & Suppliers)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        bar.addWidget(title)
        bar.addStretch()
        self.btn_new = make_button("New", "secondary")
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

        # Left list panel
        left = QFrame()
        left.setStyleSheet(
            f"QFrame {{ background-color: {T.SURFACE}; border: 1px solid {T.BORDER}; }}"
        )
        left.setMinimumWidth(T.LIST_PANEL_W)
        left.setMaximumWidth(T.LIST_PANEL_W + 40)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.setSpacing(6)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter Party Name…")
        self.filter.textChanged.connect(self._filter)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._load_detail)
        ll.addWidget(self.filter)
        ll.addWidget(self.list)
        split.addWidget(left)

        # Right detail form
        right = QFrame()
        right.setStyleSheet(
            f"QFrame {{ background-color: {T.SURFACE}; border: 1px solid {T.BORDER}; }}"
        )
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 12, 16, 12)
        form_title = QLabel("Party Details")
        form_title.setStyleSheet("font-size: 11pt; font-weight: bold;")
        rl.addWidget(form_title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit()
        self.ptype = QComboBox()
        self.ptype.addItems(["Customer", "Supplier", "Both"])
        self.gstin = QLineEdit()
        self.phone = QLineEdit()
        self.city = QLineEdit()
        self.credit_days = QSpinBox()
        self.credit_days.setRange(0, 365)
        self.balance = QDoubleSpinBox()
        self.balance.setRange(-99999999, 99999999)
        self.balance.setDecimals(2)
        self.balance.setPrefix("Rs. ")
        self.agent = QLineEdit()
        self.agent.setPlaceholderText("Referred By / Agent Name")
        self.notes = QLineEdit()
        self.notes.setPlaceholderText("Notes")
        self.err = QLabel("")
        self.err.setStyleSheet(f"color: {T.DANGER}; font-size: 8pt;")

        form.addRow(field_label("Party Name"), self.name)
        form.addRow(field_label("Type"), self.ptype)
        form.addRow(field_label("GSTIN"), self.gstin)
        form.addRow(field_label("Phone"), self.phone)
        form.addRow(field_label("City"), self.city)
        form.addRow(field_label("Credit Days"), self.credit_days)
        form.addRow(field_label("Outstanding Balance"), self.balance)
        form.addRow(field_label("Referred By / Agent Name"), self.agent)
        form.addRow(field_label("Notes"), self.notes)
        rl.addLayout(form)
        rl.addWidget(self.err)
        rl.addStretch()
        split.addWidget(right)

        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        root.addWidget(split, stretch=1)

        self._refresh_list()

    def _refresh_list(self, select_name=None):
        self.list.clear()
        q = self.filter.text().strip().lower()
        for p in self.parties:
            if q and q not in p["name"].lower():
                continue
            bal = p["balance"]
            if bal > 0:
                suffix = f"  Rs. {bal:,.0f} due"
            elif bal < 0:
                suffix = f"  Rs. {abs(bal):,.0f} cr"
            else:
                suffix = ""
            item = QListWidgetItem(f"{p['name']}{suffix}")
            item.setData(Qt.UserRole, p["id"])
            self.list.addItem(item)
            if select_name and p["name"] == select_name:
                self.list.setCurrentItem(item)

    def _filter(self, _text):
        self._refresh_list()

    def _current_party(self):
        item = self.list.currentItem()
        if not item:
            return None
        pid = item.data(Qt.UserRole)
        return next((p for p in self.parties if p["id"] == pid), None)

    def _load_detail(self, _row):
        p = self._current_party()
        if not p:
            return
        self.name.setText(p["name"])
        self.ptype.setCurrentText(p["type"])
        self.gstin.setText(p.get("gstin", ""))
        self.phone.setText(p.get("phone", ""))
        self.city.setText(p.get("city", ""))
        self.credit_days.setValue(p.get("credit_days", 0))
        self.balance.setValue(p.get("balance", 0))
        self.agent.setText(p.get("agent", ""))
        self.notes.setText(p.get("notes", ""))
        self.err.setText("")

    def _new(self):
        new_id = max((p["id"] for p in self.parties), default=0) + 1
        p = {
            "id": new_id, "name": "New Party", "type": "Customer",
            "gstin": "", "phone": "", "city": "", "balance": 0.0,
            "credit_days": 30, "agent": "", "notes": "",
        }
        self.parties.append(p)
        self._refresh_list(select_name=p["name"])
        self.name.setFocus()
        self.name.selectAll()

    def _save(self):
        p = self._current_party()
        if not p:
            return
        if not self.name.text().strip():
            self.err.setText("Party Name is required.")
            return
        p["name"] = self.name.text().strip()
        p["type"] = self.ptype.currentText()
        p["gstin"] = self.gstin.text().strip()
        p["phone"] = self.phone.text().strip()
        p["city"] = self.city.text().strip()
        p["credit_days"] = self.credit_days.value()
        p["balance"] = self.balance.value()
        p["agent"] = self.agent.text().strip()
        p["notes"] = self.notes.text().strip()
        self.err.setText("")
        self._refresh_list(select_name=p["name"])
        QMessageBox.information(self, "Saved", f"Party '{p['name']}' saved.")

    def _delete(self):
        p = self._current_party()
        if not p:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete party '{p['name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.parties = [x for x in self.parties if x["id"] != p["id"]]
            self._refresh_list()

    def _refresh(self):
        self.parties = [dict(p) for p in D.PARTIES]
        self.filter.clear()
        self._refresh_list()
