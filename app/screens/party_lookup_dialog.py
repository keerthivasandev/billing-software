"""Stitch — 2.4 Billwise Party Lookup Dialog [F4] & Payment Options."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QButtonGroup, QDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QRadioButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian
from app.widgets.icons import icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.55)"


def _billwise_outstanding(name: str, kind: str) -> float:
    src = D.RECEIVABLES if kind == "Customer" else D.PAYABLES
    bills = [r for r in src if r.get("party") == name]
    if bills:
        return sum(float(r.get("balance", 0)) for r in bills)
    return 0.0


def billwise_lookup_parties(mode: str = "receipt") -> list[dict]:
    """Parties available for Billwise F4 lookup (customers or suppliers)."""
    want = "Customer" if mode == "receipt" else "Supplier"
    # Seed names used on Billwise settlement screen
    extras = []
    if mode == "receipt":
        extras.append({
            "id": 101,
            "name": "Balaji Electricals & Hardware",
            "type": "Customer",
            "group": "Sundry Debtor",
            "gstin": "36AABCU9603R1ZM",
            "city": "Hyderabad",
            "phone": "+91 98480 11223",
            "balance": _billwise_outstanding("Balaji Electricals & Hardware", "Customer") or 42500.0,
            "balance_type": "Dr",
            "active": True,
        })
    else:
        extras.append({
            "id": 102,
            "name": "Polycab India Ltd",
            "type": "Supplier",
            "group": "Sundry Creditor",
            "gstin": "27AAACP1234A1Z5",
            "city": "Secunderabad",
            "phone": "+91 40 2784 3311",
            "balance": _billwise_outstanding("Polycab India Ltd", "Supplier") or 117600.0,
            "balance_type": "Cr",
            "active": True,
        })

    rows = []
    seen = set()
    for p in extras + list(D.PARTIES):
        if p.get("type") != want:
            continue
        name = p["name"]
        if name in seen:
            continue
        seen.add(name)
        pend = _billwise_outstanding(name, want)
        bal = pend if pend > 0 else float(p.get("balance", 0))
        rows.append({
            "id": p.get("id"),
            "name": name,
            "type": p.get("type", want),
            "group": p.get("group", ""),
            "gstin": p.get("gstin", "—"),
            "city": p.get("city", "—"),
            "phone": p.get("phone", ""),
            "balance": bal,
            "balance_type": p.get("balance_type", "Dr" if want == "Customer" else "Cr"),
            "active": p.get("active", True),
        })
    # Prefer parties with outstanding first
    rows.sort(key=lambda r: (-r["balance"], r["name"]))
    return rows


class PartyLookupDialog(QDialog):
    """Centered modal — Party Lookup [F4] + Cash/Bank/Cheque payment options."""

    def __init__(
        self,
        mode: str = "receipt",
        current_party: str = "",
        pay_mode: str = "Bank",
        parent=None,
    ):
        super().__init__(parent)
        self.mode = mode  # receipt | payment
        self.pay_mode = pay_mode  # Cash | Bank | Cheque
        self.selected_party = None
        self.selected_pay_mode = pay_mode
        self._filter = "customers" if mode == "receipt" else "suppliers"
        # Full pools so All / Customers / Suppliers chips all work
        self._customers = billwise_lookup_parties("receipt")
        self._suppliers = billwise_lookup_parties("payment")
        self._current = current_party

        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._backdrop = QFrame()
        self._backdrop.setObjectName("partyLookupBackdrop")
        self._backdrop.setStyleSheet(
            f"QFrame#partyLookupBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(self._backdrop)
        shell.setContentsMargins(28, 24, 28, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("partyLookupCard")
        self._card.setFixedWidth(920)
        self._card.setMinimumHeight(560)
        self._card.setMaximumHeight(680)
        self._card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self._card.setStyleSheet(
            f"QFrame#partyLookupCard {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 8px; }}"
        )
        card = QVBoxLayout(self._card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)
        card.addWidget(self._header())
        card.addWidget(self._toolbar())
        card.addWidget(self._table(), stretch=1)
        card.addWidget(self._payment_options())
        card.addWidget(self._footer())

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(self._backdrop)
        self._backdrop.mousePressEvent = self._on_backdrop

        self._reload()
        self._select_current()

        QShortcut(QKeySequence("Esc"), self, activated=self.reject)
        QShortcut(QKeySequence("Return"), self, activated=self._accept)
        QShortcut(QKeySequence("Enter"), self, activated=self._accept)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())
        QShortcut(QKeySequence("F4"), self, activated=self._accept)

    def showEvent(self, event):
        parent = self.parentWidget()
        win = parent.window() if parent is not None else None
        if win is not None:
            top_left = win.mapToGlobal(win.rect().topLeft())
            self.setGeometry(top_left.x(), top_left.y(), win.width(), win.height())
        else:
            screen = self.screen()
            if screen:
                self.setGeometry(screen.availableGeometry())
        super().showEvent(event)
        self.search.setFocus()
        self.search.selectAll()

    def _on_backdrop(self, e):
        if e.button() != Qt.LeftButton:
            return
        if not self._card.geometry().contains(e.position().toPoint()):
            self.reject()

    def _header(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top-left-radius: 8px; border-top-right-radius: 8px; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 12, 12, 12)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(32, 32)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: {S.R}px; border: none;"
        )
        ic.setPixmap(icon_pixmap("switch_account", size=18, color=S.PRIMARY))
        lay.addWidget(ic)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        mid.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ttl = QLabel("Party Lookup")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 15px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        title_row.addWidget(S.pill("F4", "primary"))
        if self.mode == "receipt":
            title_row.addWidget(S.pill("Customer / Debtor", "success"))
        else:
            title_row.addWidget(S.pill("Supplier / Creditor", "supplier"))
        title_row.addStretch()
        mid.addLayout(title_row)
        sub = QLabel(
            "Select sundry debtor ledger for billwise receipt allocation"
            if self.mode == "receipt"
            else "Select sundry creditor ledger for billwise payment settlement"
        )
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        mid.addWidget(sub)
        lay.addLayout(mid, stretch=1)

        close_btn = QFrame()
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(
            f"QFrame {{ background: transparent; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        cl = QHBoxLayout(close_btn)
        cl.setContentsMargins(0, 0, 0, 0)
        cic = QLabel()
        cic.setAlignment(Qt.AlignCenter)
        cic.setPixmap(icon_pixmap("close", size=18, color=S.SECONDARY))
        cic.setStyleSheet("background: transparent; border: none;")
        cl.addWidget(cic)
        close_btn.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(close_btn)
        return box

    def _toolbar(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(f"QFrame {{ background: {T.SURFACE}; border: none; }}")
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 12, 16, 8)
        lay.setSpacing(10)

        search_wrap = QFrame()
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        sw = QHBoxLayout(search_wrap)
        sw.setContentsMargins(10, 0, 10, 0)
        sw.setSpacing(8)
        sic = QLabel()
        sic.setFixedSize(18, 18)
        sic.setPixmap(icon_pixmap("search", size=18, color=S.SECONDARY))
        sic.setStyleSheet("background: transparent; border: none;")
        sw.addWidget(sic)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search party name, GSTIN, city, phone…")
        self.search.setClearButtonEnabled(True)
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; "
            f"font-size: 13px; font-weight: 600; color: {T.TEXT_PRIMARY}; "
            f"padding: 10px 0; }}"
        )
        self.search.textChanged.connect(self._reload)
        sw.addWidget(self.search, stretch=1)
        lay.addWidget(search_wrap, stretch=1)

        # Type filter chips
        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border-radius: {S.R}px; "
            f"border: none; }}"
        )
        sl = QHBoxLayout(seg)
        sl.setContentsMargins(2, 2, 2, 2)
        sl.setSpacing(2)
        self._filter_btns = {}
        for key, label in (
            ("all", "All"),
            ("customers", "Customers"),
            ("suppliers", "Suppliers"),
        ):
            b = QLabel(label)
            b.setAlignment(Qt.AlignCenter)
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setFixedHeight(28)
            b.setMinimumWidth(78)
            b.mousePressEvent = (
                lambda e, k=key: self._set_filter(k)
                if e.button() == Qt.LeftButton else None
            )
            self._filter_btns[key] = b
            sl.addWidget(b)
        self._paint_filters()
        lay.addWidget(seg)
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
        self._reload()

    def _table(self) -> QFrame:
        wrap = QFrame()
        wrap.setStyleSheet("QFrame { background: transparent; border: none; }")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(16, 4, 16, 8)
        lay.setSpacing(0)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Party / Ledger", "GSTIN", "City", "Outstanding", "Type"]
        )
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._accept)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        S.apply_table_style(self.table)
        lay.addWidget(self.table, stretch=1)

        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; "
            f"background: transparent; padding: 6px 2px 0 2px;"
        )
        lay.addWidget(self.count_lbl)
        return wrap

    def _payment_options(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)

        cap = QLabel(
            "COLLECTION MODE" if self.mode == "receipt" else "PAYMENT MODE"
        )
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        lay.addWidget(cap)

        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        sl = QHBoxLayout(seg)
        sl.setContentsMargins(4, 4, 4, 4)
        sl.setSpacing(4)
        self._pay_group = QButtonGroup(self)
        for i, m in enumerate(("Cash", "Bank", "Cheque")):
            rb = QRadioButton(m)
            rb.setChecked(m == self.pay_mode)
            rb.setStyleSheet(
                f"QRadioButton {{ color: {T.TEXT_PRIMARY}; font-size: 12px; "
                f"font-weight: 600; spacing: 6px; padding: 4px 10px; }}"
            )
            self._pay_group.addButton(rb, i)
            sl.addWidget(rb)
        lay.addWidget(seg)
        lay.addStretch()

        hint = QLabel("Enter / F4 to select · Esc to cancel")
        hint.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        lay.addWidget(hint)
        return box

    def _footer(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-top: 1px solid {T.BORDER}; "
            f"border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)
        lay.addStretch()
        lay.addWidget(
            S.action_btn("Cancel", shortcut="Esc", kind="secondary", on_click=self.reject)
        )
        lay.addWidget(
            S.action_btn(
                "Select Party",
                shortcut="Enter",
                icon="check",
                kind="primary",
                on_click=self._accept,
            )
        )
        return box

    def _visible(self):
        q = self.search.text().strip().lower()
        if self._filter == "customers":
            pool = self._customers
        elif self._filter == "suppliers":
            pool = self._suppliers
        else:
            pool = self._customers + self._suppliers
        rows = []
        seen = set()
        for p in pool:
            if p["name"] in seen:
                continue
            seen.add(p["name"])
            blob = " ".join(
                str(p.get(k, "")) for k in ("name", "gstin", "city", "phone", "group")
            ).lower()
            if q and q not in blob:
                continue
            rows.append(p)
        rows.sort(key=lambda r: (-r["balance"], r["name"]))
        return rows

    def _reload(self):
        rows = self._visible()
        self.table.setRowCount(len(rows))
        self._row_data = rows
        for r, p in enumerate(rows):
            name = QTableWidgetItem(p["name"])
            f = name.font()
            f.setBold(True)
            name.setFont(f)
            name.setForeground(QBrush(QColor(T.TEXT_PRIMARY)))
            self.table.setItem(r, 0, name)

            gst = QTableWidgetItem(p.get("gstin") or "—")
            gst.setForeground(QBrush(QColor(S.SECONDARY)))
            self.table.setItem(r, 1, gst)

            city = QTableWidgetItem(p.get("city") or "—")
            self.table.setItem(r, 2, city)

            bal = float(p.get("balance", 0))
            suffix = p.get("balance_type", "Dr")
            amt = QTableWidgetItem(f"{format_inr_indian(bal)} {suffix}")
            amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amt.setForeground(QBrush(QColor(T.DANGER if bal > 0 else S.SECONDARY)))
            f = amt.font()
            f.setBold(True)
            amt.setFont(f)
            self.table.setItem(r, 3, amt)

            kind = p.get("type", "")
            type_it = QTableWidgetItem(kind)
            type_it.setForeground(
                QBrush(QColor(T.SUCCESS_FG if kind == "Customer" else T.DOC_PILL_FG))
            )
            self.table.setItem(r, 4, type_it)

        kind_lbl = "parties" if self._filter == "all" else (
            "customers" if self._filter == "customers" else "suppliers"
        )
        self.count_lbl.setText(f"Showing {len(rows)} {kind_lbl}")
        if rows and self.table.currentRow() < 0:
            self.table.selectRow(0)

    def _select_current(self):
        if not self._current:
            return
        for r, p in enumerate(getattr(self, "_row_data", [])):
            if p["name"] == self._current:
                self.table.selectRow(r)
                return

    def _current_pay_mode(self) -> str:
        btn = self._pay_group.checkedButton()
        return btn.text() if btn else self.pay_mode

    def _accept(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(getattr(self, "_row_data", [])):
            return
        self.selected_party = dict(self._row_data[row])
        self.selected_pay_mode = self._current_pay_mode()
        self.accept()
