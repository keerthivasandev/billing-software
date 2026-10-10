"""2.4 Billwise Settlement — pixel-matched to updated Stitch screenshot."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QAbstractSpinBox, QCheckBox, QComboBox, QDialog,
    QDoubleSpinBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.screens.party_lookup_dialog import PartyLookupDialog
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import combo_dropdown_qss, icon_pixmap

_PARTY_RECEIPT = "Balaji Electricals & Hardware"
_PARTY_PAYMENT = "Polycab India Ltd"

_PAY_OPTIONS_RECEIPT = [
    "Online Payment (HDFC Current A/c - 4091)",
    "Cash Counter",
    "Cheque / DD",
    "UPI / NEFT",
]
_PAY_OPTIONS_PAYMENT = [
    "Online Payment (HDFC Current A/c - 4091)",
    "Cash Counter",
    "Cheque / DD",
    "RTGS / NEFT",
]


class BillwiseScreen(QWidget):
    def __init__(self, mode="receipt", parent=None):
        super().__init__(parent)
        self.mode = mode  # receipt | payment
        self.party_name = _PARTY_RECEIPT if mode == "receipt" else _PARTY_PAYMENT
        self.party_gstin = (
            "36AABCU9603R1ZM" if mode == "receipt" else "27AAACP1234A1Z5"
        )
        self.pay_option = _PAY_OPTIONS_RECEIPT[0]
        self.rows = self._party_rows()
        self._settle = {r["bill"]: 0.0 for r in self.rows}
        self._checked = {r["bill"]: False for r in self.rows}
        self._reloading = False
        self.setStyleSheet(f"background: {T.BG_CANVAS};")
        self._build()
        self._apply_fifo_default()
        QShortcut(QKeySequence("F4"), self, activated=self._open_party_lookup)
        QShortcut(QKeySequence("F9"), self, activated=self._save)

    def _party_rows(self):
        src = D.RECEIVABLES if self.mode == "receipt" else D.PAYABLES
        return [
            dict(r) for r in src
            if r.get("party") == self.party_name and float(r.get("balance", 0)) > 0
        ]

    def _outstanding(self) -> float:
        return sum(float(r["balance"]) for r in self.rows)

    def _clear_root(self):
        root = self.layout()
        if root is None:
            return
        while root.count():
            item = root.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _build(self):
        root = self.layout()
        if root is None:
            root = QVBoxLayout(self)
            root.setContentsMargins(16, 12, 16, 12)
            root.setSpacing(12)
        else:
            self._clear_root()

        root.addWidget(self._master_card())
        root.addWidget(self._invoices_card(), stretch=1)
        root.addWidget(self._summary_card())

    def _apply_fifo_default(self):
        if hasattr(self, "recv"):
            self.recv.blockSignals(True)
            self.recv.setValue(25000.00 if self.mode == "receipt" else 50000.00)
            self.recv.blockSignals(False)
        self._on_recv_changed()

    # ── Master card ──────────────────────────────────────────
    def _master_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)
        lay.addWidget(self._title_block())
        lay.addWidget(self._mode_date_row())
        lay.addWidget(self._party_amount_row())
        return box

    def _title_block(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(36, 36)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {S.PRIMARY}; border-radius: {S.R}px; border: none;"
        )
        ic.setPixmap(icon_pixmap("price_check", size=20, color="white"))
        lay.addWidget(ic)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        mid.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ttl = QLabel("Billwise Settlement")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)

        vch = QLabel(
            "Voucher: RCP/26-27/0219"
            if self.mode == "receipt"
            else "Voucher: PAY/26-27/0112"
        )
        vch.setStyleSheet(
            f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; "
            f"padding: 2px 8px; font-size: 11px; font-weight: 700;"
        )
        title_row.addWidget(vch)
        title_row.addWidget(self._flow_badge())
        title_row.addStretch()
        mid.addLayout(title_row)

        sub = QLabel(
            "Allocate incoming customer receipts against unpaid date-wise sales invoices"
            if self.mode == "receipt"
            else "Settle outgoing supplier payments against unpaid purchase invoices"
        )
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        mid.addWidget(sub)
        lay.addLayout(mid, stretch=1)
        return wrap

    def _flow_badge(self) -> QFrame:
        badge = QFrame()
        badge.setStyleSheet(
            f"QFrame {{ background: {T.SUCCESS_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(badge)
        lay.setContentsMargins(8, 2, 8, 2)
        lay.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            f"background: {T.SUCCESS}; border-radius: 3px; border: none;"
        )
        lay.addWidget(dot)
        txt = QLabel(
            "Customer Inflow (Cr)" if self.mode == "receipt" else "Supplier Outflow (Dr)"
        )
        txt.setStyleSheet(
            f"color: {T.SUCCESS_FG}; font-size: 10px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(txt)
        return badge

    def _mode_date_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
        )
        sl = QHBoxLayout(seg)
        sl.setContentsMargins(3, 3, 3, 3)
        sl.setSpacing(3)
        sl.addWidget(
            self._mode_btn(
                "Billwise Receipt (Customer / Debtor)",
                "arrow_downward",
                self.mode == "receipt",
                "receipt",
            )
        )
        sl.addWidget(
            self._mode_btn(
                "Billwise Payment (Supplier / Creditor)",
                "arrow_upward",
                self.mode == "payment",
                "payment",
            )
        )
        lay.addWidget(seg)
        lay.addStretch()

        date = QFrame()
        date.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        dl = QHBoxLayout(date)
        dl.setContentsMargins(10, 6, 12, 6)
        dl.setSpacing(6)
        dic = QLabel()
        dic.setFixedSize(16, 16)
        dic.setPixmap(icon_pixmap("calendar_today", size=16, color=S.PRIMARY))
        dic.setStyleSheet("background: transparent; border: none;")
        dl.addWidget(dic)
        dtxt = QLabel("Date: 20-Sep-2026")
        dtxt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        dl.addWidget(dtxt)
        lay.addWidget(date)
        return wrap

    def _mode_btn(self, text: str, icon: str, active: bool, mode: str) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(34)
        if active:
            btn.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; "
                f"border-radius: {S.R}px; }}"
            )
            fg = "white"
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: none; "
                f"border-radius: {S.R}px; }}"
            )
            fg = S.SECONDARY
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 14, 0)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap(icon, size=16, color=fg))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: {'700' if active else '500'}; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        btn.mousePressEvent = (
            lambda e, m=mode: self._switch_mode(m)
            if e.button() == Qt.LeftButton else None
        )
        return btn

    def _party_amount_row(self) -> QWidget:
        # Design: light grey band holding party + amount + payment option
        wrap = QFrame()
        wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(12)

        # Party column
        party_col = QVBoxLayout()
        party_col.setSpacing(4)
        label_row = QHBoxLayout()
        label_row.setContentsMargins(0, 0, 0, 0)
        label_row.setSpacing(10)
        plbl = QLabel(
            "CUSTOMER / SUNDRY DEBTOR"
            if self.mode == "receipt"
            else "SUPPLIER / SUNDRY CREDITOR"
        )
        plbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        label_row.addWidget(plbl)
        ledger_link = QLabel(
            "Customer Ledger & Outstandings"
            if self.mode == "receipt"
            else "Supplier Ledger & Outstandings"
        )
        ledger_link.setCursor(QCursor(Qt.PointingHandCursor))
        ledger_link.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 10px; font-weight: 600; "
            f"border: none; background: transparent; text-decoration: underline;"
        )
        ledger_link.mousePressEvent = (
            lambda e: toast(self, "Open party ledger")
            if e.button() == Qt.LeftButton else None
        )
        label_row.addWidget(ledger_link)
        label_row.addStretch()
        party_col.addLayout(label_row)

        party_box = QFrame()
        party_box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
        )
        pb = QHBoxLayout(party_box)
        pb.setContentsMargins(10, 8, 8, 8)
        pb.setSpacing(8)
        pinfo = QVBoxLayout()
        pinfo.setSpacing(2)
        pname = QLabel(self.party_name)
        pname.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        pinfo.addWidget(pname)
        due = self._outstanding()
        suffix = "Dr" if self.mode == "receipt" else "Cr"
        meta = QLabel(
            f"GSTIN: {self.party_gstin} · Outstanding: "
            f"<span style='color:{T.DANGER};font-weight:700'>"
            f"{format_inr_indian(due)} {suffix}</span>"
        )
        meta.setTextFormat(Qt.RichText)
        meta.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        pinfo.addWidget(meta)
        pb.addLayout(pinfo, stretch=1)

        # Design: Change [F4] is solid primary blue
        change = QFrame()
        change.setCursor(QCursor(Qt.PointingHandCursor))
        change.setFixedHeight(32)
        change.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        cl = QHBoxLayout(change)
        cl.setContentsMargins(10, 0, 10, 0)
        cl.setSpacing(6)
        cic = QLabel()
        cic.setFixedSize(14, 14)
        cic.setPixmap(icon_pixmap("switch_account", size=14, color="white"))
        cic.setStyleSheet("background: transparent; border: none;")
        cl.addWidget(cic)
        ct = QLabel("Change")
        ct.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        cl.addWidget(ct)
        cl.addWidget(S.kbd("F4", on_primary=True))
        change.mousePressEvent = (
            lambda e: self._open_party_lookup()
            if e.button() == Qt.LeftButton else None
        )
        pb.addWidget(change)
        party_col.addWidget(party_box)
        lay.addLayout(party_col, stretch=5)

        # Amount column
        amt_col = QVBoxLayout()
        amt_col.setSpacing(4)
        albl = QLabel(
            "AMOUNT RECEIVED (₹)" if self.mode == "receipt" else "AMOUNT PAID (₹)"
        )
        albl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        amt_col.addWidget(albl)
        self.recv = QDoubleSpinBox()
        self.recv.setRange(0, 9_999_999)
        self.recv.setDecimals(2)
        self.recv.setValue(25000.00 if self.mode == "receipt" else 50000.00)
        self.recv.setGroupSeparatorShown(True)
        self.recv.setPrefix("₹ ")
        self.recv.setAlignment(Qt.AlignRight)
        self.recv.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.recv.setFixedHeight(40)
        self.recv.setStyleSheet(
            f"QDoubleSpinBox {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; padding: 6px 10px; font-size: 18px; "
            f"font-weight: 700; color: {T.TEXT_PRIMARY}; }}"
        )
        self.recv.valueChanged.connect(self._on_recv_changed)
        amt_col.addWidget(self.recv)
        lay.addLayout(amt_col, stretch=3)

        # Payment Option & Account dropdown (design)
        pay_col = QVBoxLayout()
        pay_col.setSpacing(4)
        pay_lbl = QLabel("PAYMENT OPTION & ACCOUNT")
        pay_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        pay_col.addWidget(pay_lbl)
        self.pay_combo = QComboBox()
        opts = _PAY_OPTIONS_RECEIPT if self.mode == "receipt" else _PAY_OPTIONS_PAYMENT
        self.pay_combo.addItems(opts)
        if self.pay_option in opts:
            self.pay_combo.setCurrentText(self.pay_option)
        self.pay_combo.setFixedHeight(40)
        self.pay_combo.setStyleSheet(
            f"""
            QComboBox {{
                background: {T.SURFACE}; border: 1px solid {T.BORDER};
                border-radius: {S.R}px; padding: 6px 10px; padding-right: 28px;
                font-size: 12px; font-weight: 600; color: {T.TEXT_PRIMARY};
            }}
            {combo_dropdown_qss(width=24, background=T.SURFACE)}
            """
        )
        self.pay_combo.currentTextChanged.connect(
            lambda t: setattr(self, "pay_option", t)
        )
        pay_col.addWidget(self.pay_combo)
        lay.addLayout(pay_col, stretch=4)

        return wrap

    def _switch_mode(self, mode: str):
        if mode == self.mode:
            return
        self.mode = mode
        self.party_name = _PARTY_RECEIPT if mode == "receipt" else _PARTY_PAYMENT
        self.party_gstin = (
            "36AABCU9603R1ZM" if mode == "receipt" else "27AAACP1234A1Z5"
        )
        self.pay_option = (
            _PAY_OPTIONS_RECEIPT[0] if mode == "receipt" else _PAY_OPTIONS_PAYMENT[0]
        )
        self.rows = self._party_rows()
        self._settle = {r["bill"]: 0.0 for r in self.rows}
        self._checked = {r["bill"]: False for r in self.rows}
        self._build()
        self._apply_fifo_default()

    # ── Invoices ─────────────────────────────────────────────
    def _invoices_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QFrame()
        head.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top-left-radius: {S.CR}px; border-top-right-radius: {S.CR}px; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(14, 10, 14, 10)
        hl.setSpacing(8)

        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap("receipt_long", size=18, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        hl.addWidget(ic)

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

        # Legend: overdue = red, within credit = primary blue (updated design)
        for color, text, fg in (
            (T.DANGER, "Overdue Invoices", T.DANGER),
            (S.PRIMARY, "Within Credit Period", S.PRIMARY),
        ):
            leg = QFrame()
            leg.setStyleSheet("background: transparent; border: none;")
            ll = QHBoxLayout(leg)
            ll.setContentsMargins(0, 0, 0, 0)
            ll.setSpacing(5)
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(
                f"background: {color}; border-radius: 4px; border: none;"
            )
            ll.addWidget(dot)
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"color: {fg}; font-size: 11px; font-weight: 600; "
                f"border: none; background: transparent;"
            )
            ll.addWidget(lbl)
            hl.addWidget(leg)

        fifo = QLabel("FIFO Match: Oldest Invoice First")
        fifo.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; "
            f"background: transparent; padding-left: 10px; "
            f"border-left: 1px solid {T.BORDER};"
        )
        hl.addWidget(fifo)
        lay.addWidget(head)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "",
                "Invoice No.",
                "Date",
                "Bill Amount",
                "Pending Amount",
                "Amount to Settle (₹)",
                "Remaining",
            ]
        )
        # Only "Amount to Settle" cells are editable (flags set in _reload)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
        )
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setFocusPolicy(Qt.StrongFocus)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 40)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        for c in (2, 3, 4, 5, 6):
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        S.apply_table_style(self.table)
        self.table.itemChanged.connect(self._on_settle_edited)
        lay.addWidget(self.table, stretch=1)
        return box

    # ── Footer: 3 stats only (updated design) ────────────────
    def _summary_card(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(0)

        stats = QHBoxLayout()
        stats.setSpacing(0)
        self.stat_recv = self._inline_stat(
            "RECEIPT INFLOW (CR)" if self.mode == "receipt" else "PAYMENT OUTFLOW (DR)",
            "—",
        )
        self.stat_adv = self._inline_stat(
            "UNALLOCATED / ADVANCE CR"
            if self.mode == "receipt"
            else "UNALLOCATED / ADVANCE DR",
            "—",
        )
        self.stat_due = self._inline_stat(
            "UPDATED PARTY NET DUE", "—", color=T.DANGER
        )
        for i, w in enumerate((self.stat_recv, self.stat_adv, self.stat_due)):
            if i:
                stats.addWidget(self._vdiv())
            stats.addWidget(w)
        lay.addLayout(stats, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        actions.addWidget(
            S.action_btn(
                "Back", shortcut="Esc", icon="arrow_back", kind="secondary",
                on_click=lambda: toast(self, "Back"),
            )
        )

        actions.addWidget(
            S.action_btn(
                "Save & Print Receipt"
                if self.mode == "receipt"
                else "Save & Print Payment",
                shortcut="F9",
                icon="print",
                kind="primary",
                on_click=self._save,
            )
        )
        lay.addLayout(actions)
        return box

    def _vdiv(self) -> QWidget:
        line = QFrame()
        line.setFixedWidth(1)
        line.setFixedHeight(36)
        line.setStyleSheet(f"background: {T.BORDER}; border: none;")
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wl = QHBoxLayout(wrap)
        wl.setContentsMargins(18, 0, 18, 0)
        wl.addWidget(line)
        return wrap

    def _inline_stat(self, label: str, value: str, color: str = None) -> QFrame:
        box = QFrame()
        box.setStyleSheet("QFrame { background: transparent; border: none; }")
        box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(4, 0, 4, 0)
        lay.setSpacing(2)
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
            col = color or T.TEXT_PRIMARY
            val.setStyleSheet(
                f"color: {col}; font-size: 16px; font-weight: 700; "
                f"border: none; background: transparent;"
            )

    # ── Party lookup ─────────────────────────────────────────
    def _open_party_lookup(self):
        pay_mode = "Bank"
        if "Cash" in (self.pay_option or ""):
            pay_mode = "Cash"
        elif "Cheque" in (self.pay_option or ""):
            pay_mode = "Cheque"
        dlg = PartyLookupDialog(
            mode=self.mode,
            current_party=self.party_name,
            pay_mode=pay_mode,
            parent=self.window(),
        )
        if dlg.exec() != QDialog.Accepted or not dlg.selected_party:
            return
        party = dlg.selected_party
        self.party_name = party["name"]
        self.party_gstin = party.get("gstin") or self.party_gstin
        if party.get("type") == "Supplier" and self.mode != "payment":
            self.mode = "payment"
        elif party.get("type") == "Customer" and self.mode != "receipt":
            self.mode = "receipt"
        self.rows = self._party_rows()
        self._settle = {r["bill"]: 0.0 for r in self.rows}
        self._checked = {r["bill"]: False for r in self.rows}
        self._build()
        self._apply_fifo_default()
        toast(self, f"Ledger set to {self.party_name}")

    # ── Table / settle ───────────────────────────────────────
    def _fmt_date(self, iso: str) -> str:
        try:
            y, m, d = iso.split("-")
            months = [
                "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            ]
            return f"{int(d):02d}-{months[int(m)]}-{y}"
        except Exception:
            return iso

    def _amt_item(
        self,
        amount: float,
        *,
        color: str = None,
        bold: bool = True,
        editable: bool = False,
        bill: str = None,
    ) -> QTableWidgetItem:
        it = QTableWidgetItem(format_inr_indian(amount))
        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if color:
            it.setForeground(QBrush(QColor(color)))
        if bold:
            f = it.font()
            f.setBold(True)
            it.setFont(f)
        if editable:
            it.setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
            )
            if bill is not None:
                it.setData(Qt.UserRole, bill)
        else:
            it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        return it

    @staticmethod
    def _parse_amount(text: str) -> float:
        raw = (
            (text or "")
            .replace("₹", "")
            .replace("Rs.", "")
            .replace(",", "")
            .strip()
        )
        try:
            return float(raw) if raw else 0.0
        except ValueError:
            return 0.0

    def _reload(self):
        self._reloading = True
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            bill = row["bill"]
            settle = float(self._settle.get(bill, 0.0))
            rem = max(0.0, float(row["balance"]) - settle)

            cb = QCheckBox()
            cb.setChecked(self._checked.get(bill, False))
            cb.stateChanged.connect(
                lambda st, b=bill: self._toggle(b, st == Qt.Checked)
            )
            wrap = QWidget()
            wrap.setStyleSheet("background: transparent;")
            wl = QHBoxLayout(wrap)
            wl.setContentsMargins(0, 0, 0, 0)
            wl.setAlignment(Qt.AlignCenter)
            wl.addWidget(cb)
            self.table.setCellWidget(r, 0, wrap)

            inv = QTableWidgetItem(f"#{bill}")
            inv.setForeground(QBrush(QColor(S.PRIMARY)))
            f = inv.font()
            f.setBold(True)
            inv.setFont(f)
            inv.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(r, 1, inv)

            date_it = QTableWidgetItem(self._fmt_date(row["date"]))
            date_it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(r, 2, date_it)

            self.table.setItem(r, 3, self._amt_item(row["amount"], bold=False))
            self.table.setItem(
                r, 4,
                self._amt_item(
                    row["balance"],
                    color=T.DANGER if row.get("overdue") else None,
                ),
            )
            # Only this column is editable (double-click / type to edit)
            self.table.setItem(
                r, 5,
                self._amt_item(settle, editable=True, bill=bill),
            )
            self.table.setItem(r, 6, self._amt_item(rem, color=S.PRIMARY))

        self.table.blockSignals(False)
        self._reloading = False
        self._refresh_stats()

    def _on_settle_edited(self, item: QTableWidgetItem):
        if self._reloading or item is None or item.column() != 5:
            return
        bill = item.data(Qt.UserRole)
        if not bill:
            return
        row = next((r for r in self.rows if r["bill"] == bill), None)
        if row is None:
            return
        pending = float(row["balance"])
        value = max(0.0, min(pending, self._parse_amount(item.text())))
        self._settle[bill] = value
        self._checked[bill] = value > 0

        self.table.blockSignals(True)
        item.setText(format_inr_indian(value))
        rem_it = self.table.item(item.row(), 6)
        if rem_it is not None:
            rem_it.setText(format_inr_indian(max(0.0, pending - value)))
        # Keep checkbox in sync without full table rebuild
        wrap = self.table.cellWidget(item.row(), 0)
        if wrap is not None:
            cb = wrap.findChild(QCheckBox)
            if cb is not None:
                cb.blockSignals(True)
                cb.setChecked(value > 0)
                cb.blockSignals(False)
        self.table.blockSignals(False)
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

    def _on_recv_changed(self, _=None):
        if not hasattr(self, "recv"):
            return
        remaining = float(self.recv.value())
        for row in sorted(self.rows, key=lambda r: r["date"]):
            bill = row["bill"]
            apply = min(remaining, float(row["balance"]))
            self._settle[bill] = apply
            self._checked[bill] = apply > 0
            remaining -= apply
        self._reload()

    def _refresh_stats(self):
        if not hasattr(self, "stat_recv"):
            return
        recv = float(self.recv.value()) if hasattr(self, "recv") else 0.0
        knocked = sum(self._settle.values())
        unalloc = max(0.0, recv - knocked)
        outstanding = self._outstanding() - knocked
        self._set_stat(self.stat_recv, format_inr_indian(recv))
        self._set_stat(self.stat_adv, format_inr_indian(unalloc))
        suffix = " Dr" if self.mode == "receipt" else " Cr"
        self._set_stat(
            self.stat_due,
            f"{format_inr_indian(outstanding)}{suffix}",
            T.DANGER,
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
        toast(self, f"{kind} of {format_inr_indian(knocked)} saved · {self.pay_option}")
