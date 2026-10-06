"""2.3 Cash Flow Register — Stitch-faithful Cash In & Out."""

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QBrush, QColor, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap


_LEDGERS = [
    "Sri Balaji Hardware & Electricals",
    "Polycab India Limited",
    "Counter Cash Sale (Walk-in)",
    "Hamali & Loading Charges",
    "Havells India Ltd",
    "General Petty Cash Expense",
]


class CashFlowScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = [dict(e) for e in D.CASH_ENTRIES]
        self.kpi = dict(D.CASH_FLOW_KPI)
        self._kind = "In"
        self._filter = "all"
        self._seq_in = 49
        self._seq_out = 20
        self.setStyleSheet(f"background: {T.BG_CANVAS};")
        self._build()
        self._reload_table()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        root.addWidget(self._title_bar())
        root.addWidget(self._kpi_row())
        root.addWidget(self._entry_card())
        root.addWidget(self._table_card(), stretch=1)
        root.addWidget(self._status_bar())

    # ── Title ────────────────────────────────────────────────
    def _title_bar(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(12)

        ic = QLabel()
        ic.setFixedSize(36, 36)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {S.PRIMARY}; border-radius: {S.R}px; border: none;"
        )
        ic.setPixmap(icon_pixmap("payments", size=20, color="white"))
        lay.addWidget(ic)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        mid.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ttl = QLabel("2.3 Cash Flow Register")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        title_row.addWidget(S.pill("FY 2026-27", "primary"))
        title_row.addStretch()
        mid.addLayout(title_row)
        sub = QLabel("Cash Counter Drawer  ·  Date: 20-Sep-2026")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        mid.addWidget(sub)
        lay.addLayout(mid, stretch=1)

        lay.addWidget(
            S.action_btn("Print Register", icon="print", kind="secondary",
                         on_click=lambda: toast(self, "Printing register…"))
        )
        return box

    # ── KPI cards ────────────────────────────────────────────
    def _kpi_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        k = self.kpi
        cards = [
            ("Opening Balance", k["opening"], "lock_clock", S.SECONDARY, T.TEXT_PRIMARY,
             "Day start counter float", False),
            ("Total Cash In", k["cash_in"], "arrow_downward", S.PRIMARY, S.PRIMARY,
             f"{k['in_count']} Receipts recorded today", False),
            ("Total Cash Out", k["cash_out"], "arrow_upward", T.DANGER, T.DANGER,
             f"{k['out_count']} Payments made today", False),
            ("REMAINING AMOUNT", k["remaining"], "point_of_sale", "white", "white",
             "Available in physical drawer", True),
        ]
        for title, amt, icon, ic_col, amt_col, hint, filled in cards:
            lay.addWidget(self._kpi_card(title, amt, icon, ic_col, amt_col, hint, filled), 1)
        return wrap

    def _kpi_card(self, title, amount, icon, ic_col, amt_col, hint, filled) -> QFrame:
        card = QFrame()
        if filled:
            card.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; "
                f"border-radius: {S.CR}px; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.CR}px; }}"
            )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        top = QHBoxLayout()
        cap = QLabel(title.upper())
        cap.setStyleSheet(
            f"color: {'rgba(255,255,255,0.85)' if filled else S.SECONDARY}; "
            f"font-size: 10px; font-weight: 700; letter-spacing: 0.4px; "
            f"border: none; background: transparent;"
        )
        top.addWidget(cap)
        top.addStretch()
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap(icon, size=18, color=ic_col))
        ic.setStyleSheet("background: transparent; border: none;")
        top.addWidget(ic)
        lay.addLayout(top)

        val = QLabel(format_inr_indian(amount))
        val.setStyleSheet(
            f"color: {amt_col}; font-size: 22px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(val)
        hint_lbl = QLabel(hint)
        hint_lbl.setStyleSheet(
            f"color: {'rgba(255,255,255,0.75)' if filled else S.SECONDARY}; "
            f"font-size: 11px; border: none; background: transparent;"
        )
        lay.addWidget(hint_lbl)
        return card

    # ── Entry form ───────────────────────────────────────────
    def _entry_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        cap = QLabel("TRANSACTION TYPE:")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        head.addWidget(cap)

        self.btn_in = self._mode_chip("Cash In (Receipt)", "add_circle", True)
        self.btn_out = self._mode_chip("Cash Out (Payment)", "remove_circle", False)
        self.btn_in.mousePressEvent = lambda e: self._set_kind("In") if e.button() == Qt.LeftButton else None
        self.btn_out.mousePressEvent = lambda e: self._set_kind("Out") if e.button() == Qt.LeftButton else None
        head.addWidget(self.btn_in)
        head.addWidget(self.btn_out)
        head.addStretch()

        self.voucher_lbl = QLabel("Next Voucher:  #CSH-IN-049")
        self.voucher_lbl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        head.addWidget(self.voucher_lbl)
        lay.addLayout(head)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.date = QDateEdit(QDate(2026, 9, 20))
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd-MM-yyyy")
        self.date.setEnabled(False)
        row.addWidget(S.labeled_input("Date", self.date), 1)

        self.party = QComboBox()
        self.party.setEditable(True)
        self.party.addItem("+ Add / Select Ledger...")
        for name in _LEDGERS:
            self.party.addItem(name)
        row.addWidget(S.labeled_input("Party / Expense Ledger", self.party), 3)

        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 9_999_999)
        self.amount.setDecimals(2)
        self.amount.setGroupSeparatorShown(True)
        row.addWidget(S.labeled_input("Amount (₹)", self.amount), 1)

        rec = S.action_btn("Record", shortcut="↵", icon="save", kind="primary",
                           on_click=self._post)
        rec.setFixedHeight(32)
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(4)
        spacer = QLabel(" ")
        spacer.setFixedHeight(15)
        spacer.setStyleSheet("border: none; background: transparent;")
        wl.addWidget(spacer)
        wl.addWidget(rec)
        row.addWidget(wrap)
        lay.addLayout(row)
        return box

    def _mode_chip(self, text: str, icon: str, active: bool) -> QFrame:
        chip = QFrame()
        chip.setCursor(QCursor(Qt.PointingHandCursor))
        chip.setFixedHeight(28)
        lay = QHBoxLayout(chip)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setObjectName("modeIcon")
        ic.setFixedSize(16, 16)
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        lbl = QLabel(text)
        lbl.setObjectName("modeText")
        lbl.setStyleSheet("border: none; background: transparent; font-size: 12px; font-weight: 600;")
        lay.addWidget(lbl)
        self._paint_mode_chip(chip, icon, active, kind="In" if "In" in text else "Out")
        return chip

    def _paint_mode_chip(self, chip: QFrame, icon: str, active: bool, kind: str):
        ic = chip.findChild(QLabel, "modeIcon")
        lbl = chip.findChild(QLabel, "modeText")
        if active and kind == "In":
            chip.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            )
            fg = "white"
        elif active and kind == "Out":
            chip.setStyleSheet(
                f"QFrame {{ background: {T.DANGER}; border: none; border-radius: {S.R}px; }}"
            )
            fg = "white"
        else:
            chip.setStyleSheet(
                f"QFrame {{ background: transparent; border: none; border-radius: {S.R}px; }}"
            )
            fg = T.TEXT_PRIMARY
        if ic:
            ic.setPixmap(icon_pixmap(icon, size=16, color=fg if active else S.SECONDARY))
        if lbl:
            lbl.setStyleSheet(
                f"color: {fg if active else T.TEXT_PRIMARY}; font-size: 12px; "
                f"font-weight: 600; border: none; background: transparent;"
            )

    def _set_kind(self, kind: str):
        self._kind = kind
        self._paint_mode_chip(self.btn_in, "add_circle", kind == "In", "In")
        self._paint_mode_chip(self.btn_out, "remove_circle", kind == "Out", "Out")
        if kind == "In":
            self.voucher_lbl.setText(f"Next Voucher:  #CSH-IN-{self._seq_in:03d}")
            self.voucher_lbl.setStyleSheet(
                f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
        else:
            self.voucher_lbl.setText(f"Next Voucher:  #CSH-OUT-{self._seq_out:03d}")
            self.voucher_lbl.setStyleSheet(
                f"color: {T.DANGER}; font-size: 12px; font-weight: 700; "
                f"border: none; background: transparent;"
            )

    # ── Table card ───────────────────────────────────────────
    def _table_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        tools = QFrame()
        tools.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        tl = QHBoxLayout(tools)
        tl.setContentsMargins(12, 10, 12, 10)
        tl.setSpacing(8)

        tab_wrap = QFrame()
        tab_wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border-radius: {S.R}px; border: none; }}"
        )
        tw = QHBoxLayout(tab_wrap)
        tw.setContentsMargins(2, 2, 2, 2)
        tw.setSpacing(2)
        self._filter_btns = {}
        for key, label in (("all", "All"), ("in", "Cash In"), ("out", "Cash Out")):
            b = QLabel(label)
            b.setAlignment(Qt.AlignCenter)
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setFixedHeight(26)
            b.setMinimumWidth(64)
            b.mousePressEvent = (
                lambda e, k=key: self._set_filter(k) if e.button() == Qt.LeftButton else None
            )
            self._filter_btns[key] = b
            tw.addWidget(b)
        self._paint_filters()
        tl.addWidget(tab_wrap)
        tl.addStretch()

        search_wrap = QFrame()
        search_wrap.setFixedWidth(280)
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.INPUT_BG}; border: none; border-radius: {S.R}px; }}"
        )
        sw = QHBoxLayout(search_wrap)
        sw.setContentsMargins(8, 0, 8, 0)
        sw.setSpacing(6)
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setPixmap(icon_pixmap("search", size=16, color=S.SECONDARY))
        sic.setStyleSheet("background: transparent; border: none;")
        sw.addWidget(sic)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search party, description, voucher...")
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; "
            f"font-size: 12px; color: {T.TEXT_PRIMARY}; padding: 6px 0; }}"
        )
        self.search.textChanged.connect(self._reload_table)
        sw.addWidget(self.search, stretch=1)
        tl.addWidget(search_wrap)
        lay.addWidget(tools)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Date & Time", "Voucher #", "Type", "Ledger / Description", "Amount (₹)", "Actions"]
        )
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 72)
        S.apply_table_style(self.table)
        lay.addWidget(self.table, stretch=1)

        foot = QFrame()
        foot.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(T.TABLE_PAD_X, T.TABLE_PAD_Y, T.TABLE_PAD_X, T.TABLE_PAD_Y)
        self.count_lbl = QLabel("Showing 0 transactions")
        self.count_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        fl.addWidget(self.count_lbl)
        fl.addStretch()
        net_cap = QLabel("Net Cash in Hand:")
        net_cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        fl.addWidget(net_cap)
        self.net_lbl = QLabel(format_inr_indian(self.kpi["remaining"]))
        self.net_lbl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 14px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        fl.addWidget(self.net_lbl)
        lay.addWidget(foot)
        return box

    def _paint_filters(self):
        for key, b in self._filter_btns.items():
            active = key == self._filter
            b.setStyleSheet(
                f"background: {T.SURFACE if active else 'transparent'}; "
                f"color: {T.TEXT_PRIMARY if active else S.SECONDARY}; "
                f"border: none; border-radius: {S.R}px; padding: 0 10px; "
                f"font-size: 12px; font-weight: {'700' if active else '500'};"
            )

    def _set_filter(self, key: str):
        self._filter = key
        self._paint_filters()
        self._reload_table()

    def _status_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"QFrame {{ background: {T.NAV_BG}; border-radius: {S.R}px; border: none; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 8, 14, 8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {T.SUCCESS}; border-radius: 4px; border: none;")
        lay.addWidget(dot)
        lbl = QLabel("Cash Drawer:  Active & Ready")
        lbl.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 600; border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        lay.addStretch()
        tip = QLabel("Shortcut: Enter to Record transaction")
        tip.setStyleSheet(
            f"color: {T.NAV_TEXT}; font-size: 11px; border: none; background: transparent;"
        )
        lay.addWidget(tip)
        return bar

    # ── Data ─────────────────────────────────────────────────
    def _visible(self):
        q = self.search.text().strip().lower()
        rows = []
        for e in self.entries:
            if self._filter == "in" and e["kind"] != "In":
                continue
            if self._filter == "out" and e["kind"] != "Out":
                continue
            blob = " ".join(
                str(e.get(k, "")) for k in ("ref", "party", "purpose", "date", "time")
            ).lower()
            if q and q not in blob:
                continue
            rows.append(e)
        return rows

    def _reload_table(self):
        rows = self._visible()
        self.table.setRowCount(len(rows))
        for r, e in enumerate(rows):
            is_in = e["kind"] == "In"
            dt = f"{e.get('date', '')[5:].replace('-', '-') if False else ''}"
            # Prefer stitch display: 20-Sep · 02:15 PM
            date_s = e.get("date", "")
            try:
                y, m, d = date_s.split("-")
                months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                date_disp = f"{int(d):02d}-{months[int(m)]} · {e.get('time', '')}"
            except Exception:
                date_disp = f"{date_s} · {e.get('time', '')}"

            self.table.setItem(r, 0, self._item(date_disp, secondary=True))

            vch = QTableWidgetItem(f"#{e['ref']}")
            vch.setForeground(QBrush(QColor(S.PRIMARY if is_in else T.DANGER)))
            f = vch.font()
            f.setBold(True)
            vch.setFont(f)
            self.table.setItem(r, 1, vch)

            pill = self._type_pill(is_in)
            self.table.setCellWidget(r, 2, pill)

            ledger = QLabel(
                f"<div style='font-weight:600;color:{T.TEXT_PRIMARY};font-size:12px;'>"
                f"{e.get('party', '—')}</div>"
                f"<div style='color:{S.SECONDARY};font-size:11px;margin-top:1px;'>"
                f"{e.get('purpose', '')}</div>"
            )
            ledger.setStyleSheet("background: transparent; border: none; padding: 4px 8px;")
            self.table.setCellWidget(r, 3, ledger)

            sign = "+ " if is_in else "- "
            amt = QTableWidgetItem(sign + format_inr_indian(e["amount"]))
            amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amt.setForeground(QBrush(QColor(S.PRIMARY if is_in else T.DANGER)))
            f = amt.font()
            f.setBold(True)
            amt.setFont(f)
            self.table.setItem(r, 4, amt)

            acts = QWidget()
            acts.setStyleSheet("background: transparent;")
            al = QHBoxLayout(acts)
            al.setContentsMargins(4, 0, 4, 0)
            al.setSpacing(4)
            al.setAlignment(Qt.AlignCenter)
            for icon, tip, color in (
                ("print", "Print", S.SECONDARY),
                ("delete", "Delete", S.SECONDARY),
            ):
                b = QLabel()
                b.setFixedSize(22, 22)
                b.setAlignment(Qt.AlignCenter)
                b.setCursor(QCursor(Qt.PointingHandCursor))
                b.setToolTip(tip)
                b.setPixmap(icon_pixmap(icon, size=16, color=color))
                b.setStyleSheet("background: transparent; border: none;")
                if icon == "delete":
                    b.mousePressEvent = (
                        lambda ev, row=e: self._delete(row)
                        if ev.button() == Qt.LeftButton else None
                    )
                else:
                    b.mousePressEvent = (
                        lambda ev, ref=e["ref"]: toast(self, f"Printing {ref}…")
                        if ev.button() == Qt.LeftButton else None
                    )
                al.addWidget(b)
            self.table.setCellWidget(r, 5, acts)

        self.count_lbl.setText(
            f"Showing <b style='color:{T.TEXT_PRIMARY}'>{len(rows)} transactions</b>"
        )
        self.count_lbl.setText(f"Showing {len(rows)} transactions")
        self.net_lbl.setText(format_inr_indian(self.kpi["remaining"]))

    def _item(self, text, *, secondary=False, bold=False, align=None):
        it = QTableWidgetItem(text)
        if secondary:
            it.setForeground(QBrush(QColor(S.SECONDARY)))
        if bold:
            f = it.font()
            f.setBold(True)
            it.setFont(f)
        if align:
            it.setTextAlignment(align)
        return it

    def _type_pill(self, is_in: bool) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(8, 4, 8, 4)
        pill = QLabel("Cash In" if is_in else "Cash Out")
        if is_in:
            pill.setStyleSheet(
                f"background: {T.ACCENT_SOFT}; color: {S.PRIMARY}; border: none; "
                f"border-radius: {S.R}px; padding: 2px 8px; font-size: 11px; font-weight: 700;"
            )
        else:
            pill.setStyleSheet(
                f"background: {T.DANGER_BG}; color: {T.DANGER}; border: none; "
                f"border-radius: {S.R}px; padding: 2px 8px; font-size: 11px; font-weight: 700;"
            )
        lay.addWidget(pill)
        lay.addStretch()
        return wrap

    def _delete(self, row: dict):
        if row in self.entries:
            self.entries.remove(row)
            signed = row["amount"] if row["kind"] == "In" else -row["amount"]
            self.kpi["remaining"] -= signed
            if row["kind"] == "In":
                self.kpi["cash_in"] -= row["amount"]
            else:
                self.kpi["cash_out"] -= row["amount"]
            self._reload_table()
            toast(self, f"Deleted #{row['ref']}")

    def _post(self):
        amt = float(self.amount.value())
        if amt <= 0:
            toast(self, "Enter a valid amount.")
            return
        party = self.party.currentText().strip()
        if not party or party.startswith("+"):
            toast(self, "Select a party / ledger.")
            return
        if self._kind == "In":
            ref = f"CSH-IN-{self._seq_in:03d}"
            self._seq_in += 1
            self.kpi["cash_in"] += amt
            self.kpi["remaining"] += amt
            self.kpi["in_count"] += 1
        else:
            ref = f"CSH-OUT-{self._seq_out:03d}"
            self._seq_out += 1
            self.kpi["cash_out"] += amt
            self.kpi["remaining"] -= amt
            self.kpi["out_count"] += 1

        self.entries.insert(0, {
            "date": self.date.date().toString("yyyy-MM-dd"),
            "time": "Just now",
            "kind": self._kind,
            "mode": "Cash",
            "ref": ref,
            "party": party,
            "purpose": "Manual counter entry",
            "amount": amt,
        })
        self.amount.setValue(0)
        self._set_kind(self._kind)
        self._reload_table()
        toast(self, f"Recorded #{ref}")
