"""2.4 Billwise Settlement & Aging Knockoff — Stitch-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QDoubleSpinBox, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QRadioButton, QButtonGroup, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap


class BillwiseScreen(QWidget):
    def __init__(self, mode="receipt", parent=None):
        super().__init__(parent)
        self.mode = mode  # receipt | payment
        self.source = D.RECEIVABLES if mode == "receipt" else D.PAYABLES
        self.rows = [dict(r) for r in self.source]
        self._settle = {r["bill"]: 0.0 for r in self.rows}
        self._checked = {r["bill"]: False for r in self.rows}
        self.setStyleSheet(f"background: {T.BG_CANVAS};")
        self._build()
        self._reload()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        root.addWidget(self._header())
        root.addWidget(self._mode_tabs())
        root.addWidget(self._party_amount_row())
        root.addWidget(self._invoices_card(), stretch=1)
        root.addWidget(self._footer())

    def _header(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        top = QHBoxLayout()
        ttl = QLabel("Billwise Settlement & Aging Knockoff")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        top.addWidget(ttl)
        top.addStretch()
        top.addWidget(S.pill("Voucher: RCP/26-27/0219", "primary"))
        lay.addLayout(top)
        sub = QLabel(
            "Customer Inflow (Cr) — Allocate incoming customer receipts against unpaid "
            "date-wise sales invoices"
            if self.mode == "receipt"
            else "Supplier Outflow (Dr) — Settle outgoing payments against unpaid purchase invoices"
        )
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        lay.addWidget(sub)
        return wrap

    def _mode_tabs(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.tab_receipt = self._tab_btn(
            "Billwise Receipt (Customer / Debtor)", "arrow_downward", self.mode == "receipt"
        )
        self.tab_payment = self._tab_btn(
            "Billwise Payment (Supplier / Creditor)", "arrow_upward", self.mode == "payment"
        )
        self.tab_receipt.mousePressEvent = (
            lambda e: self._switch_mode("receipt") if e.button() == Qt.LeftButton else None
        )
        self.tab_payment.mousePressEvent = (
            lambda e: self._switch_mode("payment") if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(self.tab_receipt)
        lay.addWidget(self.tab_payment)
        lay.addStretch()

        date_chip = QLabel()
        date_chip.setText("  Date: 20-Sep-2026")
        date_chip.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; font-weight: 600; "
            f"background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; padding: 6px 10px;"
        )
        lay.addWidget(date_chip)
        return box

    def _tab_btn(self, text: str, icon: str, active: bool) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(36)
        if active:
            btn.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            )
            fg = "white"
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
            )
            fg = T.TEXT_PRIMARY
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 14, 0)
        lay.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap(icon, size=16, color=fg))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        return btn

    def _switch_mode(self, mode: str):
        if mode == self.mode:
            return
        self.mode = mode
        self.source = D.RECEIVABLES if mode == "receipt" else D.PAYABLES
        self.rows = [dict(r) for r in self.source]
        self._settle = {r["bill"]: 0.0 for r in self.rows}
        self._checked = {r["bill"]: False for r in self.rows}
        # rebuild UI quickly
        lay = self.layout()
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._build()
        self._reload()

    def _party_amount_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        # Party card
        party = S.card()
        pl = QVBoxLayout(party)
        pl.setContentsMargins(14, 12, 14, 12)
        pl.setSpacing(8)
        cap = QLabel(
            "CUSTOMER / SUNDRY DEBTOR" if self.mode == "receipt" else "SUPPLIER / SUNDRY CREDITOR"
        )
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        pl.addWidget(cap)

        row = QHBoxLayout()
        name = QLabel(
            "Balaji Electricals & Hardware"
            if self.mode == "receipt"
            else "Polycab India Ltd"
        )
        name.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 15px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        row.addWidget(name)
        row.addStretch()
        change = S.action_btn(
            "Change", shortcut="F4", icon="switch_account", kind="secondary",
            on_click=lambda: toast(self, "Open party picker…"),
        )
        row.addWidget(change)
        pl.addLayout(row)

        if self.mode == "receipt":
            meta = QLabel(
                "GSTIN: 36AABCU9603R1ZM · Pending Invoices: 3 · Outstanding: "
                f"<span style='color:{T.DANGER};font-weight:700'>"
                f"{format_inr_indian(42500)} Dr</span>"
            )
        else:
            meta = QLabel(
                "Pending Bills: 2 · Outstanding: "
                f"<span style='color:{T.DANGER};font-weight:700'>"
                f"{format_inr_indian(117600)} Cr</span>"
            )
        meta.setTextFormat(Qt.RichText)
        meta.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        pl.addWidget(meta)

        rule = QLabel("Rule: FIFO Auto-Settlement Enabled")
        rule.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        pl.addWidget(rule)
        lay.addWidget(party, stretch=3)

        # Amount received card
        amt_card = S.card()
        al = QVBoxLayout(amt_card)
        al.setContentsMargins(14, 12, 14, 12)
        al.setSpacing(8)
        alabel = QLabel("AMOUNT RECEIVED (₹)" if self.mode == "receipt" else "AMOUNT PAID (₹)")
        alabel.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        al.addWidget(alabel)

        self.recv = QDoubleSpinBox()
        self.recv.setRange(0, 9_999_999)
        self.recv.setDecimals(2)
        self.recv.setValue(25000.00)
        self.recv.setGroupSeparatorShown(True)
        self.recv.setPrefix("₹ ")
        self.recv.setStyleSheet(
            f"QDoubleSpinBox {{ background: {T.INPUT_BG}; border: none; "
            f"border-radius: {S.R}px; padding: 10px 12px; font-size: 22px; "
            f"font-weight: 700; color: {T.TEXT_PRIMARY}; min-height: 28px; }}"
        )
        self.recv.valueChanged.connect(self._on_recv_changed)
        al.addWidget(self.recv)

        modes = QHBoxLayout()
        modes.setSpacing(12)
        self.mode_group = QButtonGroup(self)
        for i, m in enumerate(("Cash", "Bank", "Cheque")):
            rb = QRadioButton(m)
            if i == 1:
                rb.setChecked(True)
            self.mode_group.addButton(rb, i)
            modes.addWidget(rb)
        modes.addStretch()
        save = S.action_btn(
            "Save", shortcut="F9", icon="save", kind="primary", on_click=self._save
        )
        modes.addWidget(save)
        al.addLayout(modes)
        lay.addWidget(amt_card, stretch=2)
        return wrap

    def _invoices_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QFrame()
        head.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(14, 10, 14, 10)
        title = QLabel(
            "Pending Sales Invoices (Debtor Receivables)"
            if self.mode == "receipt"
            else "Pending Purchase Invoices (Creditor Payables)"
        )
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        hl.addWidget(title)
        hl.addWidget(S.pill(f"{len(self.rows)} Invoices Loaded", "neutral"))
        hl.addStretch()
        for text, kind in (
            ("Overdue Invoices", "danger"),
            ("Within Credit Period", "success"),
            ("FIFO Match: Oldest Invoice First", "primary"),
        ):
            hl.addWidget(S.pill(text, kind))
        lay.addWidget(head)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["", "Invoice No.", "Date", "Bill Amount", "Pending Amount",
             "Amount to Settle (₹)", "Remaining"]
        )
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 36)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        for c in (2, 3, 4, 5, 6):
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        S.apply_table_style(self.table)
        lay.addWidget(self.table, stretch=1)
        return box

    def _footer(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        self.stat_recv = self._stat("RECEIPT INFLOW (Cr)" if self.mode == "receipt" else "PAYMENT OUTFLOW (Dr)", "—")
        self.stat_knock = self._stat("KNOCKED-OFF BILLS", "—", color=T.DANGER)
        self.stat_adv = self._stat("UNALLOCATED / ADVANCE Cr", "—")
        self.stat_due = self._stat("UPDATED PARTY NET DUE", "—", color=S.PRIMARY)
        for w in (self.stat_recv, self.stat_knock, self.stat_adv, self.stat_due):
            lay.addWidget(w, 1)

        lay.addStretch(1)
        lay.addWidget(
            S.action_btn("Back", shortcut="Esc", kind="secondary",
                         on_click=lambda: toast(self, "Back"))
        )
        lay.addWidget(
            S.action_btn(
                "Save & Print Receipt" if self.mode == "receipt" else "Save & Print Payment",
                shortcut="F9",
                icon="receipt",
                kind="primary",
                on_click=self._save,
            )
        )
        return box

    def _stat(self, label: str, value: str, color: str = None) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(4)
        cap = QLabel(label)
        cap.setObjectName("statCap")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        lay.addWidget(cap)
        val = QLabel(value)
        val.setObjectName("statVal")
        val.setStyleSheet(
            f"color: {color or T.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(val)
        return box

    def _set_stat(self, box: QFrame, value: str, color: str = None):
        val = box.findChild(QLabel, "statVal")
        if val:
            val.setText(value)
            if color:
                val.setStyleSheet(
                    f"color: {color}; font-size: 16px; font-weight: 700; "
                    f"border: none; background: transparent;"
                )

    def _reload(self):
        self.table.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            bill = row["bill"]
            cb = QCheckBox()
            cb.setChecked(self._checked.get(bill, False))
            cb.stateChanged.connect(lambda st, b=bill: self._toggle(b, st == Qt.Checked))
            wrap = QWidget()
            wrap.setStyleSheet("background: transparent;")
            wl = QHBoxLayout(wrap)
            wl.setContentsMargins(8, 0, 0, 0)
            wl.addWidget(cb)
            self.table.setCellWidget(r, 0, wrap)

            inv = QTableWidgetItem(f"#{bill}")
            inv.setForeground(QBrush(QColor(S.PRIMARY)))
            f = inv.font()
            f.setBold(True)
            inv.setFont(f)
            self.table.setItem(r, 1, inv)

            try:
                y, m, d = row["date"].split("-")
                months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                date_txt = f"{int(d):02d}-{months[int(m)]}-{y}"
            except Exception:
                date_txt = row["date"]
            self.table.setItem(r, 2, QTableWidgetItem(date_txt))

            bill_amt = QTableWidgetItem(format_inr_indian(row["amount"]))
            bill_amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 3, bill_amt)

            pend = QTableWidgetItem(format_inr_indian(row["balance"]))
            pend.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if row.get("overdue"):
                pend.setForeground(QBrush(QColor(T.DANGER)))
            f = pend.font()
            f.setBold(True)
            pend.setFont(f)
            self.table.setItem(r, 4, pend)

            spin = QDoubleSpinBox()
            spin.setRange(0, float(row["balance"]))
            spin.setDecimals(2)
            spin.setValue(self._settle.get(bill, 0.0))
            spin.setGroupSeparatorShown(True)
            spin.setPrefix("₹ ")
            spin.setStyleSheet(
                f"QDoubleSpinBox {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; padding: 4px 6px; font-size: 12px; "
                f"font-weight: 700; }}"
            )
            spin.valueChanged.connect(lambda v, b=bill: self._set_settle(b, v))
            self.table.setCellWidget(r, 5, spin)

            rem = max(0.0, row["balance"] - self._settle.get(bill, 0.0))
            rem_it = QTableWidgetItem(format_inr_indian(rem))
            rem_it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rem_it.setForeground(QBrush(QColor(S.PRIMARY)))
            self.table.setItem(r, 6, rem_it)

        self._refresh_stats()

    def _toggle(self, bill: str, on: bool):
        self._checked[bill] = on
        if on and self._settle.get(bill, 0) <= 0:
            row = next(r for r in self.rows if r["bill"] == bill)
            self._settle[bill] = float(row["balance"])
            self._reload()
        elif not on:
            self._settle[bill] = 0.0
            self._reload()

    def _set_settle(self, bill: str, value: float):
        self._settle[bill] = float(value)
        self._checked[bill] = value > 0
        # update remaining cell only
        for r, row in enumerate(self.rows):
            if row["bill"] != bill:
                continue
            rem = max(0.0, row["balance"] - value)
            it = QTableWidgetItem(format_inr_indian(rem))
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            it.setForeground(QBrush(QColor(S.PRIMARY)))
            self.table.setItem(r, 6, it)
            break
        self._refresh_stats()

    def _on_recv_changed(self, _=None):
        # FIFO auto allocate
        remaining = float(self.recv.value())
        for row in sorted(self.rows, key=lambda r: r["date"]):
            bill = row["bill"]
            apply = min(remaining, float(row["balance"]))
            self._settle[bill] = apply
            self._checked[bill] = apply > 0
            remaining -= apply
        self._reload()

    def _refresh_stats(self):
        recv = float(self.recv.value())
        knocked = sum(self._settle.values())
        unalloc = max(0.0, recv - knocked)
        outstanding = sum(r["balance"] for r in self.rows) - knocked
        self._set_stat(self.stat_recv, format_inr_indian(recv))
        self._set_stat(self.stat_knock, format_inr_indian(knocked), T.DANGER)
        self._set_stat(self.stat_adv, format_inr_indian(unalloc))
        self._set_stat(
            self.stat_due,
            f"{format_inr_indian(outstanding)} Dr",
            S.PRIMARY,
        )

    def _save(self):
        knocked = sum(self._settle.values())
        if knocked <= 0:
            toast(self, "Allocate amount against at least one bill.")
            return
        for row in self.rows:
            apply = self._settle.get(row["bill"], 0.0)
            row["balance"] = round(max(0.0, row["balance"] - apply), 2)
            self._settle[row["bill"]] = 0.0
            self._checked[row["bill"]] = False
        self.recv.setValue(0)
        self._reload()
        kind = "Receipt" if self.mode == "receipt" else "Payment"
        toast(self, f"{kind} of {format_inr_indian(knocked)} saved.")
