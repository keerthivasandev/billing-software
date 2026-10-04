"""Operations — Bill-wise payment / receipt settlement."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QHBoxLayout, QHeaderView,
    QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import (
    card_frame, format_inr, labeled_field, make_button, page_title, toast, ui_font,
)


class BillwiseScreen(QWidget):
    def __init__(self, mode="receipt", parent=None):
        super().__init__(parent)
        self.mode = mode  # receipt | payment
        self.source = D.RECEIVABLES if mode == "receipt" else D.PAYABLES
        self.rows = [dict(r) for r in self.source]
        title = (
            "2.4 Bill-wise Settlement (Receipts)"
            if mode == "receipt"
            else "2.4 Bill-wise Settlement (Payments)"
        )
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        root.addWidget(page_title(title))

        filt = card_frame()
        fl = QHBoxLayout(filt)
        fl.setContentsMargins(10, 8, 10, 8)
        self.party = QComboBox()
        self.party.setEditable(True)
        self.party.addItem("All Parties")
        for p in D.PARTIES:
            self.party.addItem(p["name"])
        self.party.currentTextChanged.connect(self._filter)
        self.settle_amt = QDoubleSpinBox()
        self.settle_amt.setRange(0, 99999999)
        self.settle_amt.setDecimals(2)
        self.settle_amt.setPrefix("Rs. ")
        btn = make_button("Apply Settlement", "primary")
        btn.clicked.connect(self._settle)
        fl.addWidget(labeled_field("Party", self.party))
        fl.addWidget(labeled_field("Settlement Amount", self.settle_amt))
        fl.addWidget(btn, alignment=Qt.AlignBottom)
        fl.addStretch()
        root.addWidget(filt)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Party", "Bill No.", "Original", "Paid", "Pending", "Days"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        S.apply_table_style(self.table)
        root.addWidget(self.table, stretch=1)
        self.summary = QLabel()
        self.summary.setStyleSheet(
            f"background: {T.HEADER_BAND}; border: 1px solid {T.BORDER}; "
            f"padding: 6px 10px; border-radius: {T.RADIUS}px;"
        )
        root.addWidget(self.summary)
        self._reload()

    def _visible_rows(self):
        q = self.party.currentText().strip()
        if not q or q == "All Parties":
            return self.rows
        return [r for r in self.rows if r["party"] == q]

    def _reload(self):
        rows = self._visible_rows()
        self.table.setRowCount(len(rows))
        pending_total = 0.0
        for r, row in enumerate(rows):
            paid = row["amount"] - row["balance"]
            pending_total += row["balance"]
            vals = [
                row["party"], row["bill"], format_inr(row["amount"]),
                format_inr(paid), format_inr(row["balance"]), str(row["days"]),
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 4)))
                if c in (2, 3, 4, 5):
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r, c, it)
        self.summary.setText(f"Pending balance total:  {format_inr(pending_total)}")

    def _filter(self, _=None):
        self._reload()

    def _settle(self):
        row = self.table.currentRow()
        rows = self._visible_rows()
        if row < 0 or row >= len(rows):
            toast(self, "Select a pending bill first.")
            return
        amt = float(self.settle_amt.value())
        if amt <= 0:
            toast(self, "Enter settlement amount.")
            return
        target = rows[row]
        apply = min(amt, target["balance"])
        target["balance"] = round(target["balance"] - apply, 2)
        self.settle_amt.setValue(0)
        self._reload()
        kind = "Receipt" if self.mode == "receipt" else "Payment"
        toast(self, f"{kind} of {format_inr(apply)} applied to {target['bill']}.")
