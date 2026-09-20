"""Master — Godowns / Warehouses."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QSplitter, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import card_frame, field_label, make_button, page_title, toast


class GodownsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = [dict(g) for g in D.GODOWNS]
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        bar = QHBoxLayout()
        bar.addWidget(page_title("1.5 Godowns"))
        bar.addStretch()
        self.btn_new = make_button("New")
        self.btn_save = make_button("Save", "primary")
        self.btn_delete = make_button("Delete", "destructive")
        self.btn_new.clicked.connect(self._new)
        self.btn_save.clicked.connect(self._save)
        self.btn_delete.clicked.connect(self._delete)
        for b in (self.btn_new, self.btn_save, self.btn_delete):
            bar.addWidget(b)
        root.addLayout(bar)

        split = QSplitter(Qt.Horizontal)
        left = card_frame()
        left.setMinimumWidth(T.LIST_PANEL_W)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._load)
        ll.addWidget(self.list)
        split.addWidget(left)

        right = card_frame()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 12, 16, 12)
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)
        self.name = QLineEdit()
        self.incharge = QLineEdit()
        self.address = QLineEdit()
        self.capacity = QLineEdit()
        self.is_default = QCheckBox("Default Godown")
        form.addRow(field_label("Warehouse / Location"), self.name)
        form.addRow(field_label("In-charge"), self.incharge)
        form.addRow(field_label("Address"), self.address)
        form.addRow(field_label("Capacity"), self.capacity)
        form.addRow(QLabel(""), self.is_default)
        rl.addLayout(form)
        rl.addStretch()
        split.addWidget(right)
        root.addWidget(split, stretch=1)
        self._refresh()
        if self.list.count():
            self.list.setCurrentRow(0)

    def _refresh(self):
        self.list.clear()
        for g in self.rows:
            mark = " ★" if g.get("is_default") else ""
            self.list.addItem(QListWidgetItem(f"{g['name']}{mark}"))

    def _load(self, row: int):
        if row < 0 or row >= len(self.rows):
            return
        g = self.rows[row]
        self.name.setText(g["name"])
        self.incharge.setText(g["incharge"])
        self.address.setText(g["address"])
        self.capacity.setText(g["capacity"])
        self.is_default.setChecked(bool(g.get("is_default")))

    def _new(self):
        self.rows.append({
            "id": max((r["id"] for r in self.rows), default=0) + 1,
            "name": "New Godown", "incharge": "", "address": "",
            "capacity": "", "is_default": False,
        })
        self._refresh()
        self.list.setCurrentRow(self.list.count() - 1)
        toast(self, "New godown drafted.")

    def _save(self):
        row = self.list.currentRow()
        if row < 0:
            return
        g = self.rows[row]
        g.update({
            "name": self.name.text().strip() or g["name"],
            "incharge": self.incharge.text().strip(),
            "address": self.address.text().strip(),
            "capacity": self.capacity.text().strip(),
            "is_default": self.is_default.isChecked(),
        })
        if g["is_default"]:
            for other in self.rows:
                if other is not g:
                    other["is_default"] = False
        self._refresh()
        self.list.setCurrentRow(row)
        toast(self, "Godown saved.")

    def _delete(self):
        row = self.list.currentRow()
        if row < 0:
            return
        name = self.rows[row]["name"]
        del self.rows[row]
        self._refresh()
        toast(self, f"Deleted {name}.")
