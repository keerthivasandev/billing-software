"""Operations — Estimates / Quotations with convert-to-invoice."""

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QHBoxLayout,
    QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import (
    card_frame, format_inr, labeled_field, make_button, page_title, toast, ui_font,
)


class EstimateScreen(QWidget):
    def __init__(self, navigate_cb=None, parent=None):
        super().__init__(parent)
        self.navigate_cb = navigate_cb
        self.quotes = [dict(q) for q in D.ESTIMATES]
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        bar = QHBoxLayout()
        bar.addWidget(page_title("2.5 Estimates / Quotations"))
        bar.addStretch()
        self.btn_new = make_button("New Quotation", "primary")
        self.btn_convert = make_button("Convert to Sales Invoice")
        self.btn_new.clicked.connect(self._new)
        self.btn_convert.clicked.connect(self._convert)
        bar.addWidget(self.btn_new)
        bar.addWidget(self.btn_convert)
        root.addLayout(bar)

        builder = card_frame()
        bl = QHBoxLayout(builder)
        bl.setContentsMargins(10, 8, 10, 8)
        self.party = QComboBox()
        self.party.setEditable(True)
        for p in D.PARTIES:
            if p["type"] in ("Customer", "Both"):
                self.party.addItem(p["name"])
        self.item = QComboBox()
        for p in D.PRODUCTS:
            self.item.addItem(p["name"])
        self.qty = QDoubleSpinBox()
        self.qty.setRange(0.001, 999999)
        self.qty.setValue(1)
        self.rate = QDoubleSpinBox()
        self.rate.setRange(0, 9999999)
        self.rate.setDecimals(2)
        self.rate.setPrefix("Rs. ")
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        add_line = make_button("Add Line")
        add_line.clicked.connect(self._add_line)
        for w in (
            labeled_field("Customer", self.party),
            labeled_field("Item", self.item),
            labeled_field("Qty", self.qty),
            labeled_field("Rate", self.rate),
            labeled_field("Date", self.date),
        ):
            bl.addWidget(w)
        bl.addWidget(add_line, alignment=Qt.AlignBottom)
        root.addWidget(builder)

        self.lines = QTableWidget(0, 4)
        self.lines.setHorizontalHeaderLabels(["Item", "Qty", "Rate", "Amount"])
        self.lines.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.lines.verticalHeader().setVisible(False)
        self.lines.setMaximumHeight(140)
        root.addWidget(self.lines)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Quotation No.", "Party", "Date", "Amount", "Status"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        root.addWidget(self.table, stretch=1)
        self._line_total = 0.0
        self._reload()

    def _reload(self):
        self.table.setRowCount(len(self.quotes))
        for r, q in enumerate(self.quotes):
            vals = [q["id"], q["party"], q["date"], format_inr(q["amount"]), q["status"]]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 3)))
                if c == 3:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if c == 4 and v == "Open":
                    it.setForeground(QBrush(QColor(T.SUCCESS)))
                self.table.setItem(r, c, it)

    def _add_line(self):
        qty = float(self.qty.value())
        rate = float(self.rate.value())
        if rate <= 0:
            # auto-fill rate from product
            name = self.item.currentText()
            prod = next((p for p in D.PRODUCTS if p["name"] == name), None)
            rate = float(prod["sale_rate"]) if prod else 0.0
            self.rate.setValue(rate)
        amt = round(qty * rate, 2)
        r = self.lines.rowCount()
        self.lines.insertRow(r)
        for c, v in enumerate([self.item.currentText(), f"{qty:g}", f"{rate:.2f}", f"{amt:.2f}"]):
            it = QTableWidgetItem(v)
            if c > 0:
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.lines.setItem(r, c, it)
        self._line_total += amt
        toast(self, f"Line added. Running total {format_inr(self._line_total)}")

    def _new(self):
        if self.lines.rowCount() == 0:
            toast(self, "Add at least one line item.")
            return
        nid = f"QT-{88 + len(self.quotes):04d}"[-7:]
        # nicer id
        nid = f"QT-{100 + len(self.quotes)}"
        self.quotes.insert(0, {
            "id": nid,
            "party": self.party.currentText(),
            "date": self.date.date().toString("yyyy-MM-dd"),
            "amount": self._line_total,
            "status": "Open",
        })
        self.lines.setRowCount(0)
        self._line_total = 0.0
        self._reload()
        toast(self, f"Quotation {nid} created.")

    def _convert(self):
        row = self.table.currentRow()
        if row < 0:
            toast(self, "Select an open quotation.")
            return
        q = self.quotes[row]
        if q["status"] != "Open":
            toast(self, "Already converted.")
            return
        q["status"] = "Converted"
        self._reload()
        toast(self, f"{q['id']} converted to Sales Invoice.")
        if callable(self.navigate_cb):
            self.navigate_cb("sales")
