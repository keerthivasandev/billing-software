"""Operations — Cash Flow register (In / Out) with live drawer balance."""

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QFormLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import (
    card_frame, field_label, format_inr, make_button, page_title, toast, ui_font,
)


class CashFlowScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = [dict(e) for e in D.CASH_ENTRIES]
        self.balance = float(D.DASHBOARD_KPI["cash_in_hand"])
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        bar = QHBoxLayout()
        bar.addWidget(page_title("2.3 Cash Flow"))
        bar.addStretch()
        self.bal_lbl = QLabel()
        self._update_balance_label()
        bar.addWidget(self.bal_lbl)
        root.addLayout(bar)

        entry = card_frame()
        fl = QFormLayout(entry)
        fl.setContentsMargins(12, 12, 12, 12)
        fl.setSpacing(8)
        self.kind = QComboBox()
        self.kind.addItems(["In", "Out"])
        self.mode = QComboBox()
        self.mode.addItems(["Cash", "Bank Transfer"])
        self.ref = QLineEdit()
        self.purpose = QLineEdit()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 99999999)
        self.amount.setDecimals(2)
        self.amount.setPrefix("Rs. ")
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd-MM-yyyy")
        fl.addRow(field_label("Type"), self.kind)
        fl.addRow(field_label("Mode"), self.mode)
        fl.addRow(field_label("Reference No"), self.ref)
        fl.addRow(field_label("Purpose / Category"), self.purpose)
        fl.addRow(field_label("Amount"), self.amount)
        fl.addRow(field_label("Date"), self.date)
        btn_row = QHBoxLayout()
        add = make_button("Post Entry", "primary")
        add.clicked.connect(self._post)
        btn_row.addWidget(add)
        btn_row.addStretch()
        fl.addRow(QLabel(""), btn_row)
        root.addWidget(entry)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Type", "Mode", "Reference", "Purpose", "Amount"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        root.addWidget(self.table, stretch=1)
        self._reload_table()

    def _update_balance_label(self):
        self.bal_lbl.setText(f"Net Drawer Balance:  {format_inr(self.balance)}")
        self.bal_lbl.setStyleSheet(
            f"background: {T.SUCCESS_BG}; color: {T.SUCCESS}; border: 1px solid {T.SUCCESS}; "
            f"border-radius: 10px; padding: 4px 12px; font-weight: bold;"
        )

    def _reload_table(self):
        self.table.setRowCount(len(self.entries))
        for r, e in enumerate(self.entries):
            vals = [e["date"], e["kind"], e["mode"], e["ref"], e["purpose"], format_inr(e["amount"])]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 5)))
                if c == 1:
                    color = T.SUCCESS if e["kind"] == "In" else T.DANGER
                    it.setForeground(QBrush(QColor(color)))
                if c == 5:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r, c, it)

    def _post(self):
        amt = float(self.amount.value())
        if amt <= 0:
            toast(self, "Enter a valid amount.")
            return
        kind = self.kind.currentText()
        self.entries.insert(0, {
            "date": self.date.date().toString("yyyy-MM-dd"),
            "kind": kind,
            "mode": self.mode.currentText(),
            "ref": self.ref.text().strip() or "—",
            "purpose": self.purpose.text().strip() or "—",
            "amount": amt,
        })
        self.balance += amt if kind == "In" else -amt
        self._update_balance_label()
        self._reload_table()
        self.amount.setValue(0)
        self.ref.clear()
        self.purpose.clear()
        toast(self, f"Cash {kind.lower()} posted. Balance updated.")
