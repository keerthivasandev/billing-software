"""Reports — Ledger Statement, Sales/Purchase Registers, Export Tools."""

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import (
    card_frame, format_inr, labeled_field, make_button, page_title, toast, ui_font,
)


class LedgerStatementScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        root.addWidget(page_title("3.1 Ledger Statement"))

        filt = card_frame()
        fl = QHBoxLayout(filt)
        fl.setContentsMargins(10, 8, 10, 8)
        self.party = QComboBox()
        for p in D.PARTIES:
            self.party.addItem(p["name"])
        self.from_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.to_date = QDateEdit(QDate.currentDate())
        for d in (self.from_date, self.to_date):
            d.setCalendarPopup(True)
            d.setDisplayFormat("dd-MM-yyyy")
        run = make_button("Run", "primary")
        run.clicked.connect(self._run)
        fl.addWidget(labeled_field("Party", self.party))
        fl.addWidget(labeled_field("From", self.from_date))
        fl.addWidget(labeled_field("To", self.to_date))
        fl.addWidget(run, alignment=Qt.AlignBottom)
        fl.addStretch()
        root.addWidget(filt)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Particulars", "Voucher", "Debit", "Credit", "Balance"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        root.addWidget(self.table, stretch=1)
        self._run()

    def _run(self):
        bal = 0.0
        rows = D.LEDGER_LINES
        self.table.setRowCount(len(rows))
        for r, line in enumerate(rows):
            bal += line["debit"] - line["credit"]
            side = "Dr" if bal >= 0 else "Cr"
            vals = [
                line["date"], line["particulars"], line["vch"],
                f"{line['debit']:,.2f}" if line["debit"] else "",
                f"{line['credit']:,.2f}" if line["credit"] else "",
                f"{abs(bal):,.2f} {side}",
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 5)))
                if c >= 3:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r, c, it)
        toast(self, f"Ledger loaded for {self.party.currentText()}.")


class RegistersScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        root.addWidget(page_title("3.2 Sales & Purchase Registers"))

        filt = card_frame()
        fl = QHBoxLayout(filt)
        fl.setContentsMargins(10, 8, 10, 8)
        self.from_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.to_date = QDateEdit(QDate.currentDate())
        for d in (self.from_date, self.to_date):
            d.setCalendarPopup(True)
            d.setDisplayFormat("dd-MM-yyyy")
        run = make_button("Run", "primary")
        run.clicked.connect(lambda: toast(self, "Register refreshed."))
        fl.addWidget(labeled_field("From", self.from_date))
        fl.addWidget(labeled_field("To", self.to_date))
        fl.addWidget(run, alignment=Qt.AlignBottom)
        fl.addStretch()
        root.addWidget(filt)

        tabs = QTabWidget()
        tabs.addTab(self._make_table("Sale"), "Sales Register")
        tabs.addTab(self._make_table("Purchase"), "Purchase Register")
        root.addWidget(tabs, stretch=1)

    def _make_table(self, kind: str) -> QTableWidget:
        rows = [r for r in D.REGISTER_ROWS if r["kind"] == kind]
        t = QTableWidget(len(rows), 8)
        t.setHorizontalHeaderLabels(
            ["Date", "Doc", "Party", "Taxable", "CGST", "SGST", "IGST", "Total"]
        )
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        t.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        for r, row in enumerate(rows):
            vals = [
                row["date"], row["doc"], row["party"],
                f"{row['taxable']:,.2f}", f"{row['cgst']:,.2f}",
                f"{row['sgst']:,.2f}", f"{row['igst']:,.2f}", f"{row['total']:,.2f}",
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                if c >= 3:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 7)))
                t.setItem(r, c, it)
        return t


class ExportToolsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        root.addWidget(page_title("3.3 Export Tools"))

        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)
        hint = QLabel(
            "One-click export of registers and ledgers. Files are generated locally — "
            "no cloud dependency (potato-PC safe)."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {T.TEXT_SECONDARY}; border: none;")
        lay.addWidget(hint)
        row = QHBoxLayout()
        csv = make_button("Export CSV", "primary")
        xls = make_button("Export Excel")
        print_btn = make_button("Printable View")
        csv.clicked.connect(lambda: toast(self, "CSV export ready (demo)."))
        xls.clicked.connect(lambda: toast(self, "Excel export ready (demo)."))
        print_btn.clicked.connect(lambda: toast(self, "Print preview opened (demo)."))
        row.addWidget(csv)
        row.addWidget(xls)
        row.addWidget(print_btn)
        row.addStretch()
        lay.addLayout(row)
        root.addWidget(box)
        root.addStretch()


class ReportsARAPScreen(QWidget):
    """Kept under Reports for AR/AP summary (legacy reports.py replacement wrapper)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from app.screens.reports import ReportsScreen
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(ReportsScreen())
