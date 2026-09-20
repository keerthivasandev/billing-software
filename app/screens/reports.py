"""Payables & Receivables Summary report."""

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QMessageBox, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import field_label, format_inr, make_button, mono_font


COLS = ["Party Name", "Bill No.", "Bill Date", "Due Date", "Amount", "Balance", "Days"]


class ReportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        title = QLabel("Payables & Receivables Summary")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        root.addWidget(title)

        # Filter bar
        filt = QFrame()
        filt.setStyleSheet(
            f"QFrame {{ background-color: {T.HEADER_BAND}; border: 1px solid {T.BORDER}; }}"
        )
        fl = QHBoxLayout(filt)
        fl.setContentsMargins(8, 6, 8, 6)
        fl.setSpacing(8)

        self.from_date = QDateEdit(QDate.currentDate().addMonths(-3))
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("dd-MM-yyyy")
        self.to_date = QDateEdit(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("dd-MM-yyyy")

        self.party = QComboBox()
        self.party.setEditable(True)
        self.party.addItem("All Parties")
        for p in D.PARTIES:
            self.party.addItem(p["name"])

        self.warehouse = QComboBox()
        self.warehouse.addItem("All Warehouses")
        self.warehouse.addItems(D.WAREHOUSES)

        btn_run = make_button("Run", "primary")
        btn_csv = make_button("Export CSV")
        btn_pdf = make_button("Export PDF")
        btn_print = make_button("Print", shortcut="[Ctrl+P]")
        btn_run.clicked.connect(self._run)
        btn_csv.clicked.connect(lambda: QMessageBox.information(self, "Export", "CSV export (stub)."))
        btn_pdf.clicked.connect(lambda: QMessageBox.information(self, "Export", "PDF export (stub)."))
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Print", "Print (stub)."))

        for w in (
            self._wrap("From", self.from_date),
            self._wrap("To", self.to_date),
            self._wrap("Party Name", self.party),
            self._wrap("Warehouse / Location", self.warehouse),
        ):
            fl.addWidget(w)
        fl.addWidget(btn_run, alignment=Qt.AlignBottom)
        fl.addStretch()
        fl.addWidget(btn_csv, alignment=Qt.AlignBottom)
        fl.addWidget(btn_pdf, alignment=Qt.AlignBottom)
        fl.addWidget(btn_print, alignment=Qt.AlignBottom)
        root.addWidget(filt)

        self.tabs = QTabWidget()
        self.recv_table = self._make_table()
        self.pay_table = self._make_table()
        self.tabs.addTab(self._wrap_table(self.recv_table, "recv"), "Receivables")
        self.tabs.addTab(self._wrap_table(self.pay_table, "pay"), "Payables")
        root.addWidget(self.tabs, stretch=1)

        self._populate(self.recv_table, D.RECEIVABLES, self.recv_summary)
        self._populate(self.pay_table, D.PAYABLES, self.pay_summary)

    def _wrap(self, label, widget):
        from app.widgets.helpers import labeled_field
        return labeled_field(label, widget)

    def _make_table(self):
        t = QTableWidget(0, len(COLS))
        t.setHorizontalHeaderLabels(COLS)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.setSortingEnabled(True)
        t.setFont(mono_font(9))
        t.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        t.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        return t

    def _wrap_table(self, table, kind):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(table)
        summary = QFrame()
        summary.setStyleSheet(
            f"QFrame {{ background-color: {T.HEADER_BAND}; border: 1px solid {T.BORDER}; "
            f"border-top: none; }}"
        )
        sl = QHBoxLayout(summary)
        sl.setContentsMargins(10, 6, 10, 6)
        lbl = QLabel("Total Qty / Total Value: —")
        lbl.setFont(mono_font(10, bold=True))
        if kind == "recv":
            self.recv_summary = lbl
        else:
            self.pay_summary = lbl
        sl.addWidget(lbl)
        sl.addStretch()
        lay.addWidget(summary)
        return w

    def _populate(self, table, rows, summary_lbl):
        table.setSortingEnabled(False)
        table.setRowCount(len(rows))
        total = 0.0
        bal_total = 0.0
        for r, row in enumerate(rows):
            vals = [
                row["party"], row["bill"], row["date"], row["due"],
                f"{row['amount']:.2f}", f"{row['balance']:.2f}", str(row["days"]),
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                if c in (4, 5, 6):
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    it.setFont(mono_font(9))
                if c == 5 and row["balance"] > 0 and row["days"] > 7:
                    it.setForeground(Qt.red)
                table.setItem(r, c, it)
            total += row["amount"]
            bal_total += row["balance"]
        table.setSortingEnabled(True)
        summary_lbl.setText(
            f"Total Value: {format_inr(total)}    Outstanding Balance: {format_inr(bal_total)}"
        )

    def _run(self):
        party = self.party.currentText()
        recv = D.RECEIVABLES
        pay = D.PAYABLES
        if party and party != "All Parties":
            recv = [r for r in recv if r["party"] == party]
            pay = [r for r in pay if r["party"] == party]
        self._populate(self.recv_table, recv, self.recv_summary)
        self._populate(self.pay_table, pay, self.pay_summary)
