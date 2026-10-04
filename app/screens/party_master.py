"""2. Ledger (Parties & Accounts) — Stitch-faithful master screen."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.screens.ledger_dialog import LedgerEditDialog
from app.styles import tokens as T
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap
from app.widgets import stitch_ui as S


class PartyMasterScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parties = [dict(p) for p in D.PARTIES]
        self._selected_id = self.parties[0]["id"] if self.parties else None
        self._list_cards = []

        self.setObjectName("ledgerRoot")
        self.setStyleSheet(f"QWidget#ledgerRoot {{ background: {T.BG_CANVAS}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {T.BG_CANVAS}; border: none; }}")

        host = QWidget()
        host.setStyleSheet(f"background: {T.BG_CANVAS};")
        body = QVBoxLayout(host)
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(12)

        body.addWidget(self._page_header())
        body.addWidget(self._workspace(), stretch=1)

        scroll.setWidget(host)
        root.addWidget(scroll)

        QShortcut(QKeySequence("F3"), self, activated=self._new_ledger)
        QShortcut(QKeySequence("F4"), self, activated=self._edit_ledger)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=lambda: toast(self, "Ledger saved."))
        QShortcut(QKeySequence("Delete"), self, activated=self._delete_ledger)
        QShortcut(QKeySequence("F8"), self, activated=lambda: toast(self, "Opening ledger statement…"))
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())

        self._rebuild_list()
        self._show_detail()

    # ── Header ribbon ────────────────────────────────────────
    def _page_header(self) -> QFrame:
        box = S.card()
        outer = QVBoxLayout(box)
        outer.setContentsMargins(14, 12, 14, 10)
        outer.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(10)
        ic = QLabel()
        ic.setFixedSize(32, 32)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: 6px; border: none;"
        )
        ic.setPixmap(icon_pixmap("group", size=18, color=S.PRIMARY))
        col = QVBoxLayout()
        col.setSpacing(2)
        ttl = QLabel("2. Ledger (Parties & Accounts)")
        ttl.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        sub = QLabel("Customer & supplier accounts directory, address, and opening balances")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        col.addWidget(ttl)
        col.addWidget(sub)

        recv, pay = self._totals()
        stats = QHBoxLayout()
        stats.setSpacing(8)
        stats.addWidget(self._stat_chip("Total Receivables (Dr):", recv, danger=True))
        stats.addWidget(self._stat_chip("Total Payables (Cr):", pay, danger=False))
        top.addWidget(ic)
        top.addLayout(col, stretch=1)
        top.addLayout(stats)
        outer.addLayout(top)

        # Action row — matches Stitch: New / Edit / Save / Delete | View Statement
        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(
            S.action_btn("+ New Ledger", "F3", "person_add", "primary", self._new_ledger)
        )
        actions.addWidget(S.action_btn("Edit", "F4", "edit", "secondary", self._edit_ledger))
        actions.addWidget(
            S.action_btn("Save", "Ctrl+S", "save", "save",
                         lambda: toast(self, "Ledger saved."))
        )
        actions.addWidget(
            S.action_btn("Delete", "Del", "delete", "danger", self._delete_ledger)
        )
        sep = QFrame()
        sep.setFixedSize(1, 20)
        sep.setStyleSheet(f"background: {T.BORDER}; border: none;")
        actions.addWidget(sep)
        actions.addWidget(
            S.action_btn("View Statement", "F8", "receipt_long", "secondary",
                         lambda: toast(self, "Opening ledger statement…"))
        )
        actions.addStretch()
        self.count_lbl = QLabel()
        self.count_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        self._update_count()
        actions.addWidget(self.count_lbl)
        outer.addLayout(actions)
        return box

    def _stat_chip(self, label: str, amount: float, danger: bool) -> QFrame:
        chip = QFrame()
        chip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if danger:
            chip.setStyleSheet(
                f"QFrame {{ background: {T.DANGER_BG}; border: 1px solid #fecaca; "
                f"border-radius: 4px; }}"
            )
            amt_color = S.ERROR
        else:
            chip.setStyleSheet(
                f"QFrame {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
            )
            amt_color = T.TEXT_PRIMARY
        lay = QHBoxLayout(chip)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(6)
        k = QLabel(label.upper())
        k.setStyleSheet(
            f"color: {amt_color if danger else S.SECONDARY}; font-size: 10px; "
            f"font-weight: 700; border: none; background: transparent;"
        )
        v = QLabel(format_inr_indian(amount))
        v.setStyleSheet(
            f"color: {amt_color}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(k)
        lay.addWidget(v)
        return chip

    def _totals(self):
        recv = sum(p["balance"] for p in self.parties if p.get("balance_type") == "Dr")
        pay = sum(p["balance"] for p in self.parties if p.get("balance_type") == "Cr")
        return recv, pay

    def _update_count(self):
        n = len(self.parties)
        self.count_lbl.setText(
            f"Total: <b style='color:{T.TEXT_PRIMARY}'>{n} Parties</b>"
        )

    # ── Workspace ────────────────────────────────────────────
    def _workspace(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._left_panel(), stretch=4)
        lay.addWidget(self._right_panel(), stretch=8)
        return wrap

    def _left_panel(self) -> QWidget:
        """Search card + free-floating party cards (Stitch left column)."""
        wrap = QWidget()
        wrap.setMinimumWidth(280)
        wrap.setMaximumWidth(380)
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Search in its own white card
        search_card = S.card()
        sc_lay = QVBoxLayout(search_card)
        sc_lay.setContentsMargins(10, 10, 10, 10)
        sc_lay.setSpacing(0)

        search_box = QFrame()
        search_box.setFixedHeight(32)
        search_box.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        sw = QHBoxLayout(search_box)
        sw.setContentsMargins(8, 0, 6, 0)
        sw.setSpacing(6)
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setPixmap(icon_pixmap("search", size=16, color=S.SECONDARY))
        sic.setStyleSheet("background: transparent; border: none;")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search Ledger (Ctrl+F)...")
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; font-size: 12px; "
            f"color: {T.TEXT_PRIMARY}; }}"
        )
        self.search.textChanged.connect(self._rebuild_list)
        kbd = S.kbd("Ctrl+F")
        sw.addWidget(sic)
        sw.addWidget(self.search, stretch=1)
        sw.addWidget(kbd)
        sc_lay.addWidget(search_box)
        lay.addWidget(search_card)

        # Scrollable party list (cards outside search card)
        self.list_host = QVBoxLayout()
        self.list_host.setSpacing(6)
        self.list_host.setContentsMargins(0, 0, 0, 0)
        list_wrap = QWidget()
        list_wrap.setStyleSheet("background: transparent;")
        list_wrap.setLayout(self.list_host)
        list_scroll = QScrollArea()
        list_scroll.setWidgetResizable(True)
        list_scroll.setFrameShape(QFrame.Shape.NoFrame)
        list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        list_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        list_scroll.setWidget(list_wrap)
        lay.addWidget(list_scroll, stretch=1)
        return wrap

    def _filtered(self):
        q = self.search.text().strip().lower()
        rows = self.parties
        if q:
            rows = [
                p for p in rows
                if q in p.get("name", "").lower()
                or q in p.get("short_name", "").lower()
                or q in p.get("city", "").lower()
                or q in p.get("phone", "").lower()
                or q in p.get("gstin", "").lower()
            ]
        return rows

    def _rebuild_list(self):
        while self.list_host.count():
            item = self.list_host.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._list_cards = []
        for p in self._filtered():
            card = self._party_card(p)
            self.list_host.addWidget(card)
            self._list_cards.append(card)
        self.list_host.addStretch(1)

    def _party_card(self, p: dict) -> QFrame:
        selected = p["id"] == self._selected_id
        card = QFrame()
        card.setCursor(QCursor(Qt.PointingHandCursor))
        if selected:
            card.setStyleSheet(
                f"QFrame {{ background: {S.HEADER_GREY}; "
                f"border: 1px solid #93c5fd; border-radius: 4px; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
                f"QFrame:hover {{ background: {S.HEADER_GREY}; }}"
            )

        outer = QHBoxLayout(card)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        if selected:
            bar = QFrame()
            bar.setFixedWidth(4)
            bar.setStyleSheet(f"background: {S.PRIMARY}; border: none;")
            outer.addWidget(bar)

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(body)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        left = QVBoxLayout()
        left.setSpacing(2)
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        display = p.get("short_name") or p["name"]
        name = QLabel(display)
        name.setStyleSheet(
            f"font-size: 12px; font-weight: {'700' if selected else '600'}; "
            f"color: {T.TEXT_PRIMARY}; border: none; background: transparent;"
        )
        name_row.addWidget(name)
        ptype = p.get("type", "Customer")
        if ptype == "Supplier":
            badge = S.pill("Supplier", "supplier")
        elif selected and ptype == "Customer":
            badge = S.pill("Customer", "primary")
        else:
            badge = S.pill(ptype if ptype != "Both" else "Customer", "neutral")
        name_row.addWidget(badge)
        name_row.addStretch()
        left.addLayout(name_row)

        city = p.get("city", "")
        phone = p.get("phone", "")
        meta_txt = f"{city} • {phone}" if phone else city
        meta = QLabel(meta_txt)
        meta.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        left.addWidget(meta)

        bal = abs(float(p.get("balance", 0)))
        bt = p.get("balance_type", "Dr")
        color = S.ERROR if bt == "Dr" else T.TEXT_PRIMARY
        amount = QLabel(f"{format_inr_indian(bal)} {bt}")
        amount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amount.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )

        lay.addLayout(left, stretch=1)
        lay.addWidget(amount)
        outer.addWidget(body, stretch=1)
        card.mousePressEvent = lambda e, pid=p["id"]: self._select(pid)
        return card

    def _select(self, pid: int):
        self._selected_id = pid
        self._rebuild_list()
        self._show_detail()

    def _current(self) -> dict | None:
        for p in self.parties:
            if p["id"] == self._selected_id:
                return p
        return None

    # ── Right detail ─────────────────────────────────────────
    def _right_panel(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        self.detail_lay = QVBoxLayout(wrap)
        self.detail_lay.setContentsMargins(0, 0, 0, 0)
        self.detail_lay.setSpacing(12)
        return wrap

    def _show_detail(self):
        while self.detail_lay.count():
            item = self.detail_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        p = self._current()
        if not p:
            empty = S.card()
            el = QVBoxLayout(empty)
            lbl = QLabel("Select a ledger to view details")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {S.SECONDARY}; padding: 40px; border: none;")
            el.addWidget(lbl)
            self.detail_lay.addWidget(empty)
            return

        self.detail_lay.addWidget(self._account_card(p))
        self.detail_lay.addWidget(self._financial_card(p))
        self.detail_lay.addWidget(self._voucher_card(p))
        self.detail_lay.addStretch(1)

    def _account_card(self, p: dict) -> QFrame:
        card = S.card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(10)

        group_label = p.get("group", "Sundry Debtor")
        if p.get("type") == "Supplier":
            group_label = "Sundry Creditor"
        elif "Debtor" not in group_label and "Creditor" not in group_label:
            group_label = "Sundry Debtor"
        # Singular form as in Stitch
        group_label = group_label.replace("Debtors", "Debtor").replace("Creditors", "Creditor")

        lay.addWidget(S.section_head(
            "1. Customer / Account Information", "badge",
            S.pill(group_label, "primary"),
            variant="flat",
        ))

        grid = QWidget()
        grid.setStyleSheet("background: transparent;")
        gl = QVBoxLayout(grid)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(8)

        contact = p.get("contact_person", "—")
        contact_lbl = QLabel(contact)
        gl.addWidget(self._pair(
            S.info_cell("Customer / Trade Business Name", QLabel(p["name"])),
            S.info_cell("Contact Person", contact_lbl),
        ))

        phone_val = QWidget()
        phone_val.setStyleSheet("background: transparent; border: none;")
        ph = QHBoxLayout(phone_val)
        ph.setContentsMargins(0, 0, 0, 0)
        ph.setSpacing(8)
        pl = QLabel(p.get("phone", "—"))
        pl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent; font-family: Consolas, monospace;"
        )
        ph.addWidget(pl)
        if p.get("whatsapp"):
            ph.addWidget(S.pill("WhatsApp Active", "success"))
        ph.addStretch()

        addr = p.get("address", "")
        city = p.get("city", "")
        state = p.get("state_code", "")
        # Compact address line matching Stitch e.g. "Ranigunj, Secunderabad - 500003 (Telangana - 36)"
        base = addr if addr else city
        if city and city not in base:
            base = f"{base}, {city}" if base else city
        if state and "—" in state:
            parts = [x.strip() for x in state.split("—")]
            if len(parts) == 2:
                addr_line = f"{base} ({parts[1]} - {parts[0]})"
            else:
                addr_line = base
        else:
            addr_line = base

        gl.addWidget(self._pair(
            S.info_cell("Phone / WhatsApp", phone_val),
            S.info_cell("Address & City", QLabel(addr_line)),
        ))
        lay.addWidget(grid)
        return card

    def _financial_card(self, p: dict) -> QFrame:
        card = S.card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(10)
        lay.addWidget(S.section_head(
            "2. Financial & Tax Settings", "account_balance", variant="flat",
        ))

        row = QWidget()
        row.setStyleSheet("background: transparent;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(8)

        ob = abs(float(p.get("opening_balance", p.get("balance", 0))))
        bt = p.get("balance_type", "Dr")
        ob_val = QWidget()
        ob_val.setStyleSheet("background: transparent; border: none;")
        ob_lay = QHBoxLayout(ob_val)
        ob_lay.setContentsMargins(0, 0, 0, 0)
        ob_lay.setSpacing(6)
        amt = QLabel(format_inr_indian(ob))
        amt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        ob_lay.addWidget(amt)
        ob_lay.addWidget(S.pill(bt, "danger" if bt == "Dr" else "neutral"))
        ob_lay.addStretch()

        rl.addWidget(S.info_cell("Opening Balance", ob_val), stretch=1)
        rl.addWidget(
            S.info_cell("Credit Limit", QLabel(format_inr_indian(p.get("credit_limit", 0)))),
            stretch=1,
        )
        rl.addWidget(
            S.info_cell("Credit Days / Terms", QLabel(f"{p.get('credit_days', 0)} Days")),
            stretch=1,
        )
        gst = QLabel(p.get("gstin", "—"))
        gst.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent; font-family: Consolas, monospace;"
        )
        rl.addWidget(S.info_cell("GSTIN", gst), stretch=1)
        lay.addWidget(row)
        return card

    def _voucher_card(self, p: dict) -> QFrame:
        card = S.card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(10)

        link = QFrame()
        link.setCursor(QCursor(Qt.PointingHandCursor))
        link.setStyleSheet("background: transparent; border: none;")
        ll = QHBoxLayout(link)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(4)
        link_lbl = QLabel("Full Statement [F8]")
        link_lbl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        arr = QLabel()
        arr.setFixedSize(16, 16)
        arr.setPixmap(icon_pixmap("arrow_forward", size=14, color=S.PRIMARY))
        arr.setStyleSheet("background: transparent; border: none;")
        ll.addWidget(link_lbl)
        ll.addWidget(arr)
        link.mousePressEvent = lambda e: toast(self, "Opening ledger statement…")

        lay.addWidget(S.section_head(
            "3. Recent Voucher Summary", "history", link, variant="flat",
        ))
        lay.addWidget(self._voucher_table(p["id"]))
        return card

    def _pair(self, a: QWidget, b: QWidget) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(a, stretch=1)
        lay.addWidget(b, stretch=1)
        return wrap

    def _voucher_table(self, party_id: int) -> QFrame:
        """Stitch Recent Voucher table — custom rows (not QTableWidget)."""
        rows = D.PARTY_VOUCHERS.get(party_id) or []

        box = QFrame()
        box.setObjectName("voucherTable")
        box.setStyleSheet(
            f"QFrame#voucherTable {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 4px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header row — surface-container, uppercase secondary
        head = QFrame()
        head.setStyleSheet(
            f"background: {S.HEADER_GREY}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; "
            f"border-top-left-radius: 4px; border-top-right-radius: 4px;"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(10, 7, 10, 7)
        hl.setSpacing(8)
        cols = (
            ("Date", 1, Qt.AlignLeft),
            ("Voucher Type / No", 3, Qt.AlignLeft),
            ("Debit", 2, Qt.AlignRight),
            ("Credit", 2, Qt.AlignRight),
            ("Running Balance", 2, Qt.AlignRight),
        )
        for title, stretch, align in cols:
            lbl = QLabel(title.upper())
            lbl.setAlignment(align | Qt.AlignVCenter)
            lbl.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
            hl.addWidget(lbl, stretch=stretch)
        lay.addWidget(head)

        if not rows:
            empty = QLabel("No recent vouchers")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 12px; padding: 16px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(empty)
            return box

        for i, row in enumerate(rows):
            last = i == len(rows) - 1
            # Alternating: low / lowest (white)
            bg = S.HEADER_GREY if i % 2 == 0 else T.SURFACE
            border = "" if last else f"border-bottom: 1px solid {T.BORDER};"
            row_f = QFrame()
            row_f.setStyleSheet(
                f"QFrame {{ background: {bg}; border: none; {border} }}"
            )
            rl = QHBoxLayout(row_f)
            rl.setContentsMargins(10, 8, 10, 8)
            rl.setSpacing(8)

            # Date — mono secondary
            date_lbl = QLabel(row.get("date", "—"))
            date_lbl.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 12px; font-weight: 500; "
                f"font-family: Consolas, 'Courier New', monospace; "
                f"border: none; background: transparent;"
            )
            rl.addWidget(date_lbl, stretch=1)

            # Voucher type (semibold) + no (mono secondary)
            vwrap = QWidget()
            vwrap.setStyleSheet("background: transparent; border: none;")
            vl = QHBoxLayout(vwrap)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(6)
            vtype = row.get("voucher_type") or ""
            vno = row.get("voucher_no") or ""
            if not vtype and not vno:
                plain = QLabel(row.get("voucher", "—"))
                plain.setStyleSheet(
                    f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
                    f"border: none; background: transparent;"
                )
                vl.addWidget(plain)
            else:
                t_lbl = QLabel(vtype)
                t_lbl.setStyleSheet(
                    f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
                    f"border: none; background: transparent;"
                )
                n_lbl = QLabel(vno)
                n_lbl.setStyleSheet(
                    f"color: {S.SECONDARY}; font-size: 12px; font-weight: 500; "
                    f"font-family: Consolas, 'Courier New', monospace; "
                    f"border: none; background: transparent;"
                )
                vl.addWidget(t_lbl)
                vl.addWidget(n_lbl)
            vl.addStretch()
            rl.addWidget(vwrap, stretch=3)

            # Debit — bold error or secondary dash
            debit = float(row.get("debit") or 0)
            if debit:
                d_lbl = QLabel(format_inr_indian(debit))
                d_lbl.setStyleSheet(
                    f"color: {S.ERROR}; font-size: 12px; font-weight: 700; "
                    f"border: none; background: transparent;"
                )
            else:
                d_lbl = QLabel("—")
                d_lbl.setStyleSheet(
                    f"color: {S.SECONDARY}; font-size: 12px; font-weight: 500; "
                    f"border: none; background: transparent;"
                )
            d_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rl.addWidget(d_lbl, stretch=2)

            # Credit — bold tertiary or secondary dash
            credit = float(row.get("credit") or 0)
            if credit:
                c_lbl = QLabel(format_inr_indian(credit))
                c_lbl.setStyleSheet(
                    f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
                    f"border: none; background: transparent;"
                )
            else:
                c_lbl = QLabel("—")
                c_lbl.setStyleSheet(
                    f"color: {S.SECONDARY}; font-size: 12px; font-weight: 500; "
                    f"border: none; background: transparent;"
                )
            c_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rl.addWidget(c_lbl, stretch=2)

            # Running balance — bold error+Dr or bold on-surface
            bal = float(row.get("balance") or 0)
            bal_type = row.get("balance_type") or ""
            bal_txt = format_inr_indian(bal)
            if bal_type:
                bal_txt = f"{bal_txt} {bal_type}"
            bal_color = S.ERROR if bal_type == "Dr" else T.TEXT_PRIMARY
            b_lbl = QLabel(bal_txt)
            b_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            b_lbl.setStyleSheet(
                f"color: {bal_color}; font-size: 12px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
            rl.addWidget(b_lbl, stretch=2)

            lay.addWidget(row_f)

        return box

    # ── Actions ──────────────────────────────────────────────
    def _new_ledger(self):
        dlg = LedgerEditDialog(self, party=None)
        if dlg.exec() == LedgerEditDialog.Accepted and dlg.result_data:
            data = dlg.result_data
            data["id"] = max((p["id"] for p in self.parties), default=0) + 1
            data["code"] = f"SLE-PTY-{data['id']:04d}"
            self.parties.append(data)
            self._selected_id = data["id"]
            self._update_count()
            self._rebuild_list()
            self._show_detail()
            toast(self, f"Created ledger: {data['name']}")

    def _edit_ledger(self):
        p = self._current()
        if not p:
            return
        dlg = LedgerEditDialog(self, party=p)
        if dlg.exec() == LedgerEditDialog.Accepted and dlg.result_data:
            for i, row in enumerate(self.parties):
                if row["id"] == p["id"]:
                    self.parties[i] = {**row, **dlg.result_data, "id": p["id"]}
                    break
            self._rebuild_list()
            self._show_detail()
            toast(self, "Ledger updated.")

    def _delete_ledger(self):
        p = self._current()
        if not p:
            return
        self.parties = [x for x in self.parties if x["id"] != p["id"]]
        self._selected_id = self.parties[0]["id"] if self.parties else None
        self._update_count()
        self._rebuild_list()
        self._show_detail()
        toast(self, f"Deleted: {p['name']}")
