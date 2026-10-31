"""4.1 A/c Log Customer (Audit & History Trail) — Stitch pixel-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.screens.ac_log_party_switch_dialog import AcLogPartySwitchDialog
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import combo_dropdown_qss, icon_pixmap

# Stitch MD3 tertiary — credit / settlement amounts
_TERTIARY = "#0f766e"


class AuditTrailScreen(QWidget):
    """Nav key ``audit_trail`` — 4.1 A/c Log Customer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.party = dict(D.AC_LOG_PARTY)
        self.kpi = dict(D.AC_LOG_KPI)
        self.events = [dict(e) for e in D.AC_LOG_EVENTS]
        self._quick = "all"
        self.setStyleSheet(f"background: {T.BG_CANVAS};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        body = QWidget()
        body.setStyleSheet(f"background: {T.BG_CANVAS};")
        self.root = QVBoxLayout(body)
        self.root.setContentsMargins(16, 12, 16, 12)
        self.root.setSpacing(10)
        scroll.setWidget(body)
        outer.addWidget(scroll)

        self.root.addWidget(self._filter_ribbon())
        self.root.addWidget(self._kpi_row())
        self.root.addWidget(self._table_card(), stretch=1)
        self.root.addWidget(self._hotkey_bar())

        QShortcut(QKeySequence("F4"), self, activated=self._switch_party)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())
        QShortcut(QKeySequence("Ctrl+E"), self, activated=lambda: toast(self, "Excel export…"))
        QShortcut(QKeySequence("Ctrl+P"), self, activated=lambda: toast(self, "Printing audit trail…"))
        QShortcut(QKeySequence("Esc"), self, activated=lambda: toast(self, "Back to Reports"))

        self._reload_table()

    # ── Filter ribbon ────────────────────────────────────────
    def _filter_ribbon(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(10)

        # Target customer
        party = QFrame()
        party.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
        )
        pl = QHBoxLayout(party)
        pl.setContentsMargins(10, 6, 8, 6)
        pl.setSpacing(8)
        pic = QLabel()
        pic.setFixedSize(18, 18)
        pic.setPixmap(icon_pixmap("manage_accounts", size=18, color=S.PRIMARY))
        pic.setStyleSheet("background: transparent; border: none;")
        pl.addWidget(pic)
        pinfo = QVBoxLayout()
        pinfo.setSpacing(1)
        pinfo.setContentsMargins(0, 0, 0, 0)
        prow = QHBoxLayout()
        prow.setSpacing(6)
        cap = QLabel("TARGET CUSTOMER LEDGER:")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        prow.addWidget(cap)
        self.party_name_lbl = QLabel(self.party["name"])
        self.party_name_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        prow.addWidget(self.party_name_lbl)
        prow.addStretch()
        pinfo.addLayout(prow)
        self.party_meta_lbl = QLabel(
            f"{self.party['city']}  ·  GSTIN: {self.party['gstin']}"
        )
        self.party_meta_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        pinfo.addWidget(self.party_meta_lbl)
        pl.addLayout(pinfo, stretch=1)

        switch = QFrame()
        switch.setCursor(QCursor(Qt.PointingHandCursor))
        switch.setFixedHeight(28)
        switch.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_HIGH}; }}"
        )
        sl = QHBoxLayout(switch)
        sl.setContentsMargins(8, 0, 8, 0)
        sl.setSpacing(4)
        sic = QLabel()
        sic.setFixedSize(14, 14)
        sic.setPixmap(icon_pixmap("swap_horiz", size=14, color=S.PRIMARY))
        sic.setStyleSheet("background: transparent; border: none;")
        sl.addWidget(sic)
        st = QLabel("[F4 Switch]")
        st.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        sl.addWidget(st)
        switch.mousePressEvent = (
            lambda e: self._switch_party() if e.button() == Qt.LeftButton else None
        )
        pl.addWidget(switch)
        top.addWidget(party)

        top.addWidget(self._filter_combo(
            "date_range", "Period:",
            [
                "Current FY 2026-27 (Full Year)",
                "Q2 (Jul - Sep 2026)",
                "Last 30 Days",
                "Custom Range",
            ],
        ))
        top.addWidget(self._filter_combo(
            "filter_alt", "Classification:",
            [
                "All Activity Events (38)",
                "Voucher Invoices (Dr)",
                "Receipts & Settlements (Cr)",
                "Credit Notes / Returns",
                "Ledger Limit & Terms Modification",
                "Master Record Edits",
            ],
        ))
        top.addStretch()

        top.addWidget(
            S.action_btn(
                "Excel Export", shortcut="Ctrl+E", icon="file_download",
                kind="secondary",
                on_click=lambda: toast(self, "Excel export…"),
            )
        )
        top.addWidget(
            S.action_btn(
                "Print Audit Trail", shortcut="Ctrl+P", icon="print",
                kind="primary",
                on_click=lambda: toast(self, "Printing audit trail…"),
            )
        )
        lay.addLayout(top)

        # Search + quick filters
        bot = QFrame()
        bot.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        bl = QHBoxLayout(bot)
        bl.setContentsMargins(0, 8, 0, 0)
        bl.setSpacing(10)

        search_wrap = QFrame()
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
        )
        search_wrap.setFixedHeight(28)
        search_wrap.setMinimumWidth(280)
        search_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sw = QHBoxLayout(search_wrap)
        sw.setContentsMargins(8, 0, 6, 0)
        sw.setSpacing(6)
        sic2 = QLabel()
        sic2.setFixedSize(14, 14)
        sic2.setPixmap(icon_pixmap("search", size=14, color=S.SECONDARY))
        sic2.setStyleSheet("background: transparent; border: none;")
        sw.addWidget(sic2)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search by Voucher #, Item SKU, Cheque/UTR, Operator, narrative…"
        )
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; "
            f"font-size: 12px; color: {T.TEXT_PRIMARY}; }}"
        )
        self.search.textChanged.connect(self._reload_table)
        sw.addWidget(self.search, stretch=1)
        sw.addWidget(S.kbd("Ctrl+F"))
        bl.addWidget(search_wrap, stretch=1)

        qf = QLabel("Quick Filters:")
        qf.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bl.addWidget(qf)
        self._chip_btns = {}
        for key, label in (
            ("all", "All (38)"),
            ("debit", "Debit Impact (14)"),
            ("credit", "Credit Impact (24)"),
            ("system", "System Overrides (3)"),
        ):
            chip = self._quick_chip(key, label, key == "all")
            self._chip_btns[key] = chip
            bl.addWidget(chip)

        lay.addWidget(bot)
        return box

    def _filter_combo(self, icon: str, label: str, options: list) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
        )
        box.setFixedHeight(36)
        lay = QHBoxLayout(box)
        lay.setContentsMargins(8, 0, 6, 0)
        lay.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap(icon, size=14, color=S.SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        cap = QLabel(label)
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        lay.addWidget(cap)
        combo = QComboBox()
        combo.addItems(options)
        combo.setStyleSheet(
            f"""
            QComboBox {{
                background: transparent; border: none; padding: 0 18px 0 2px;
                font-size: 11px; font-weight: 700; color: {T.TEXT_PRIMARY};
            }}
            {combo_dropdown_qss(width=18, background="transparent")}
            """
        )
        lay.addWidget(combo)
        return box

    def _quick_chip(self, key: str, text: str, active: bool) -> QFrame:
        chip = QFrame()
        chip.setCursor(QCursor(Qt.PointingHandCursor))
        chip.setProperty("filterKey", key)
        self._style_chip(chip, active)
        lay = QHBoxLayout(chip)
        lay.setContentsMargins(8, 3, 8, 3)
        lay.setSpacing(0)
        lbl = QLabel(text)
        lbl.setObjectName("chipLbl")
        lbl.setStyleSheet(
            f"color: {'white' if active else S.SECONDARY}; font-size: 11px; "
            f"font-weight: {'700' if active else '500'}; border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        chip.mousePressEvent = (
            lambda e, k=key: self._set_quick(k) if e.button() == Qt.LeftButton else None
        )
        return chip

    def _style_chip(self, chip: QFrame, active: bool):
        if active:
            chip.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; "
                f"border-radius: {S.R}px; }}"
            )
        else:
            chip.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER}; "
                f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
            )

    def _set_quick(self, key: str):
        self._quick = key
        for k, chip in self._chip_btns.items():
            active = k == key
            self._style_chip(chip, active)
            lbl = chip.findChild(QLabel, "chipLbl")
            if lbl:
                lbl.setStyleSheet(
                    f"color: {'white' if active else S.SECONDARY}; font-size: 11px; "
                    f"font-weight: {'700' if active else '500'}; "
                    f"border: none; background: transparent;"
                )
        self._reload_table()

    def _switch_party(self):
        dlg = AcLogPartySwitchDialog(
            current_party=self.party.get("name", ""),
            parent=self.window(),
        )
        if dlg.exec() != QDialog.Accepted or not dlg.selected_party:
            return
        p = dlg.selected_party
        city = p.get("city", "")
        state = p.get("state", "")
        loc = f"{city}, {state}" if state and state not in city else city
        self.party = {
            "name": p["name"],
            "city": loc,
            "gstin": p.get("gstin", self.party.get("gstin", "")),
            "code": p.get("code", ""),
            "address": p.get("address", ""),
            "phone": p.get("phone", ""),
            "credit_limit": p.get("credit_limit", 0),
            "balance": p.get("balance", 0),
            "balance_type": p.get("balance_type", "Dr"),
            "type": p.get("type", "Customer"),
            "group": p.get("group", ""),
            "events": p.get("events", 0),
            "last_txn": p.get("last_txn", ""),
            "overdue": p.get("overdue", False),
        }
        self.party_name_lbl.setText(self.party["name"])
        self.party_meta_lbl.setText(
            f"{self.party['city']}  ·  GSTIN: {self.party['gstin']}"
        )
        toast(self, f"Ledger switched to {self.party['name']}")

    # ── KPI cards ────────────────────────────────────────────
    def _kpi_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        k = self.kpi
        lay.addWidget(self._kpi_card(
            "Total Invoiced (FY 26-27)", "receipt_long", S.PRIMARY,
            format_inr_indian(k["invoiced"]), T.DANGER,
            f"{k['bills']} Bills [F2]",
            f"Dr Gross · Avg Ticket {format_inr_indian(k['avg_ticket'])}",
            f"{k['gst_pct']}% GST Compliant", T.SUCCESS_FG,
        ), 1)
        lay.addWidget(self._kpi_card(
            "Total Payments Collected", "payments", T.SUCCESS_FG,
            format_inr_indian(k["collected"]), _TERTIARY,
            f"{k['receipts']} Receipts",
            "Cr Applied to Invoices",
            f"UPI/NEFT: {k['upi_pct']}% · Cash: {k['cash_pct']}%", T.TEXT_PRIMARY,
        ), 1)
        # Outstanding with mini progress bar
        out = self._kpi_card(
            "Current Outstanding Balance", "account_balance_wallet", T.DANGER,
            f"{format_inr_indian(k['outstanding'])} Dr", T.DANGER,
            f"Limit: ₹{k['limit_lakh']:.2f}L",
            f"Dr O/S ({k['safe_pct']}% Safe Limit)",
            None, None,
        )
        # inject progress into last row of outstanding card
        bar_wrap = QFrame()
        bar_wrap.setFixedSize(64, 6)
        bar_wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: 3px; }}"
        )
        fill = QFrame(bar_wrap)
        fill.setGeometry(0, 0, max(4, int(64 * k["safe_pct"] / 100)), 6)
        fill.setStyleSheet(
            f"QFrame {{ background: {T.SUCCESS}; border: none; border-radius: 3px; }}"
        )
        out_lay = out.layout()
        foot = out_lay.itemAt(out_lay.count() - 1).layout()
        if foot is not None:
            foot.addWidget(bar_wrap)
        lay.addWidget(out, 1)

        lay.addWidget(self._kpi_card(
            "Last Recorded Action", "history_toggle_off", S.PRIMARY,
            k["last_action"], T.TEXT_PRIMARY,
            None,
            f"By: {k['last_by']}",
            k["last_terminal"], T.TEXT_PRIMARY,
            amount_small=True,
        ), 1)
        return wrap

    def _kpi_card(
        self, title, icon, icon_color, amount, amt_color, amount_hint,
        foot_left, foot_right, foot_right_color=None, *, amount_small=False,
    ) -> QFrame:
        card = S.card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        top = QHBoxLayout()
        cap = QLabel(title.upper())
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        top.addWidget(cap)
        top.addStretch()
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap(icon, size=18, color=icon_color))
        ic.setStyleSheet("background: transparent; border: none;")
        top.addWidget(ic)
        lay.addLayout(top)

        mid = QHBoxLayout()
        mid.setSpacing(8)
        val = QLabel(amount)
        fs = "12px" if amount_small else "16px"
        val.setStyleSheet(
            f"color: {amt_color}; font-size: {fs}; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        mid.addWidget(val)
        if amount_hint:
            hint = QLabel(amount_hint)
            hint.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 11px; border: none; "
                f"background: transparent;"
            )
            mid.addWidget(hint)
        mid.addStretch()
        lay.addLayout(mid)

        foot = QHBoxLayout()
        foot.setContentsMargins(0, 4, 0, 0)
        if foot_left:
            fl = QLabel(foot_left)
            fl.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 11px; border: none; "
                f"border-top: 1px solid {T.BORDER}; background: transparent; "
                f"padding-top: 4px;"
            )
            foot.addWidget(fl, stretch=1)
        if foot_right:
            fr = QLabel(foot_right)
            fr.setStyleSheet(
                f"color: {foot_right_color or S.SECONDARY}; font-size: 11px; "
                f"font-weight: 600; border: none; border-top: 1px solid {T.BORDER}; "
                f"background: transparent; padding-top: 4px;"
            )
            foot.addWidget(fr)
        lay.addLayout(foot)
        return card

    # ── Audit table ──────────────────────────────────────────
    def _table_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        ic_wrap = QLabel()
        ic_wrap.setFixedSize(24, 24)
        ic_wrap.setAlignment(Qt.AlignCenter)
        ic_wrap.setStyleSheet(
            f"background: {T.PRIMARY_FIXED}; border-radius: {S.R}px; border: none;"
        )
        ic_wrap.setPixmap(icon_pixmap("manage_search", size=14, color=S.PRIMARY))
        head.addWidget(ic_wrap)
        title = QLabel("Ledger Activity Audit Trail")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        head.addWidget(title)
        self.showing = QLabel("— Showing 8 of 38 Historical Events (Chronological Order)")
        self.showing.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        head.addWidget(self.showing)
        head.addStretch()
        for color, text in (
            (T.DANGER, "Debit Inflow / Charge"),
            (_TERTIARY, "Credit Outflow / Settlement"),
            (S.PRIMARY, "System Governance"),
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
                f"color: {S.SECONDARY}; font-size: 11px; border: none; "
                f"background: transparent;"
            )
            ll.addWidget(lbl)
            head.addWidget(leg)
        lay.addLayout(head)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Date & Timestamp",
            "Classification",
            "Voucher / Ref No",
            "Operator & Terminal",
            "Action Audit Details & Change Metadata",
            "Impact (Dr/Cr)",
            "Running Balance",
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        S.apply_table_style(self.table)
        self.table.verticalHeader().setDefaultSectionSize(56)
        self.table.verticalHeader().setMinimumSectionSize(52)
        lay.addWidget(self.table, stretch=1)

        # Footer integrity + pager
        foot = QHBoxLayout()
        foot.setSpacing(8)
        ver = QFrame()
        ver.setStyleSheet("background: transparent; border: none;")
        vl = QHBoxLayout(ver)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)
        vic = QLabel()
        vic.setFixedSize(14, 14)
        vic.setPixmap(icon_pixmap("verified_user", size=14, color=T.SUCCESS_FG))
        vic.setStyleSheet("background: transparent; border: none;")
        vl.addWidget(vic)
        vt = QLabel("SHA-256 Ledger Block: Tamper-Proof Verification PASSED")
        vt.setStyleSheet(
            f"color: {T.SUCCESS_FG}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        vl.addWidget(vt)
        foot.addWidget(ver)
        sep = QLabel("|")
        sep.setStyleSheet(f"color: {T.BORDER}; border: none; background: transparent;")
        foot.addWidget(sep)
        tot = QLabel("Total 38 events recorded across 180 days")
        tot.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        foot.addWidget(tot)
        foot.addStretch()

        rows_lbl = QLabel("Rows per view:")
        rows_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        foot.addWidget(rows_lbl)
        rows = QComboBox()
        rows.addItems(["25", "50", "100"])
        rows.setFixedWidth(64)
        rows.setStyleSheet(
            f"""
            QComboBox {{
                background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER};
                border-radius: {S.R}px; padding: 2px 6px; font-size: 11px;
                font-weight: 600; color: {T.TEXT_PRIMARY};
            }}
            {combo_dropdown_qss(width=18, background=T.SURFACE_CONTAINER)}
            """
        )
        foot.addWidget(rows)
        foot.addWidget(self._page_btn("chevron_left", enabled=False))
        page = QLabel("Page 1 of 5")
        page.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent; padding: 0 6px;"
        )
        foot.addWidget(page)
        foot.addWidget(self._page_btn("chevron_right", enabled=True))
        lay.addLayout(foot)
        return box

    def _page_btn(self, icon: str, enabled: bool) -> QFrame:
        btn = QFrame()
        btn.setFixedSize(24, 24)
        btn.setCursor(QCursor(Qt.PointingHandCursor) if enabled else Qt.ArrowCursor)
        btn.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        bl = QHBoxLayout(btn)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setAlignment(Qt.AlignCenter)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        col = S.SECONDARY if enabled else T.BORDER
        ic.setPixmap(icon_pixmap(icon, size=14, color=col))
        ic.setStyleSheet("background: transparent; border: none;")
        bl.addWidget(ic)
        if enabled:
            btn.mousePressEvent = (
                lambda e: toast(self, "Next page")
                if e.button() == Qt.LeftButton else None
            )
        return btn

    def _filtered_events(self):
        q = (self.search.text() or "").strip().lower()
        rows = []
        for e in self.events:
            if self._quick != "all" and e["kind"] != self._quick:
                continue
            if q:
                blob = " ".join([
                    e["date"], e["class"], e["voucher"], e["voucher_sub"],
                    e["operator"], e["detail"], e["detail_sub"] or "",
                ]).lower()
                if q not in blob:
                    continue
            rows.append(e)
        return rows

    def _reload_table(self):
        rows = self._filtered_events()
        self.showing.setText(
            f"— Showing {len(rows)} of 38 Historical Events (Chronological Order)"
        )
        self.table.setRowCount(len(rows))
        for r, e in enumerate(rows):
            self.table.setRowHeight(r, 56)
            self.table.setCellWidget(r, 0, self._two_line(e["date"], e["time"], bold_top=True))
            self.table.setCellWidget(r, 1, self._class_pill(e["class"], e["kind"]))
            self.table.setCellWidget(
                r, 2,
                self._two_line(
                    e["voucher"], e["voucher_sub"],
                    top_color=S.PRIMARY if e["kind"] != "system" else T.TEXT_PRIMARY,
                    bold_top=True,
                ),
            )
            self.table.setCellWidget(
                r, 3, self._two_line(e["operator"], e["terminal"], bold_top=True)
            )
            self.table.setCellWidget(
                r, 4,
                self._detail_cell(e["detail"], e["detail_sub"], e.get("badge")),
            )
            impact_color = {
                "debit": T.DANGER, "credit": _TERTIARY, "none": S.SECONDARY,
            }.get(e["impact_kind"], T.TEXT_PRIMARY)
            bal_color = {
                "debit": T.DANGER, "credit": _TERTIARY,
            }.get(e["balance_kind"], T.TEXT_PRIMARY)
            self.table.setItem(r, 5, self._amt_cell(e["impact"], impact_color))
            self.table.setItem(r, 6, self._amt_cell(e["balance"], bal_color))

    def _amt_cell(self, text: str, color: str) -> QTableWidgetItem:
        it = QTableWidgetItem(text)
        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        from PySide6.QtGui import QBrush, QColor
        it.setForeground(QBrush(QColor(color)))
        f = it.font()
        f.setBold(True)
        it.setFont(f)
        return it

    def _two_line(
        self, top: str, bottom: str, *, top_color: str = None, bold_top: bool = False,
    ) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(1)
        t = QLabel(top)
        t.setStyleSheet(
            f"color: {top_color or T.TEXT_PRIMARY}; font-size: 12px; "
            f"font-weight: {'700' if bold_top else '600'}; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(t)
        b = QLabel(bottom)
        b.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        lay.addWidget(b)
        return w

    def _class_pill(self, text: str, kind: str) -> QWidget:
        colors = {
            "debit": (T.DANGER, T.DANGER_BG),
            "credit": (S.SECONDARY, T.SURFACE_CONTAINER),
            "system": (S.PRIMARY, T.PRIMARY_FIXED),
        }
        fg, bg = colors.get(kind, (S.SECONDARY, T.SURFACE_CONTAINER))
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(8, 10, 8, 10)
        pill = QFrame()
        pill.setStyleSheet(
            f"QFrame {{ background: {bg}; border: none; border-radius: {S.R}px; }}"
        )
        pl = QHBoxLayout(pill)
        pl.setContentsMargins(8, 3, 8, 3)
        pl.setSpacing(5)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            f"background: {fg}; border-radius: 3px; border: none;"
        )
        pl.addWidget(dot)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {fg}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        pl.addWidget(lbl)
        lay.addWidget(pill)
        lay.addStretch()
        return wrap

    def _detail_cell(self, top: str, bottom: str, badge=None) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(2)
        t = QLabel(top)
        t.setWordWrap(True)
        t.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(t)
        row = QHBoxLayout()
        row.setSpacing(8)
        b = QLabel(bottom)
        b.setWordWrap(True)
        b.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        row.addWidget(b, stretch=1)
        if badge:
            tag = QLabel(badge)
            tag.setStyleSheet(
                f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; "
                f"border: none; border-radius: {S.R}px; padding: 1px 6px; "
                f"font-size: 10px; font-weight: 700;"
            )
            row.addWidget(tag)
        lay.addLayout(row)
        return w

    # ── Hotkeys ──────────────────────────────────────────────
    def _hotkey_bar(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)

        title_ic = QLabel()
        title_ic.setFixedSize(14, 14)
        title_ic.setPixmap(icon_pixmap("keyboard", size=14, color=S.PRIMARY))
        title_ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(title_ic)
        title = QLabel("HOTKEYS:")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        lay.addWidget(title)

        for key, desc in (
            ("F4", "Switch Party"),
            ("Ctrl+F", "Filter Logs"),
            ("Ctrl+E", "Export Excel"),
            ("Ctrl+P", "Print Trail"),
            ("Alt+D", "Date Range"),
            ("Esc", "Back to Reports"),
        ):
            lay.addWidget(S.kbd(key))
            d = QLabel(desc)
            d.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 11px; border: none; "
                f"background: transparent;"
            )
            lay.addWidget(d)

        lay.addStretch()
        sess = QLabel("Sri Lakshmi Electricals ERP v4.8 · Authorized Session: RAMESH-T1")
        sess.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        lay.addWidget(sess)
        return box
