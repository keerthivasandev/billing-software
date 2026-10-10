"""Stitch — 4.1 A/c Log Customer Party Switch Modal [F4]."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian
from app.widgets.icons import icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.55)"


class AcLogPartySwitchDialog(QDialog):
    """Centered modal — Switch Target Customer / Party [F4]."""

    def __init__(self, current_party: str = "", parent=None):
        super().__init__(parent)
        self.parties = [dict(p) for p in D.AC_LOG_LOOKUP_PARTIES]
        self._group = "all"
        self._current = current_party or D.AC_LOG_PARTY.get("name", "")
        self.selected_party = None
        self._rows = []

        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._backdrop = QFrame()
        self._backdrop.setObjectName("acLogSwitchBackdrop")
        self._backdrop.setStyleSheet(
            f"QFrame#acLogSwitchBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(self._backdrop)
        shell.setContentsMargins(28, 24, 28, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("acLogSwitchCard")
        self._card.setFixedWidth(760)
        self._card.setMinimumHeight(520)
        self._card.setMaximumHeight(640)
        self._card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self._card.setStyleSheet(
            f"QFrame#acLogSwitchCard {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 8px; }}"
        )
        card = QVBoxLayout(self._card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)
        card.addWidget(self._header())
        card.addWidget(self._toolbar())
        card.addWidget(self._body(), stretch=1)
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
        QShortcut(QKeySequence("Up"), self, activated=lambda: self._move(-1))
        QShortcut(QKeySequence("Down"), self, activated=lambda: self._move(1))

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

    # ── Header ───────────────────────────────────────────────
    def _header(self) -> QFrame:
        box = QFrame()
        box.setFixedHeight(48)
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top-left-radius: 8px; border-top-right-radius: 8px; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(28, 28)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {S.PRIMARY}; border-radius: {S.R}px; border: none;"
        )
        ic.setPixmap(icon_pixmap("manage_accounts", size=16, color="white"))
        lay.addWidget(ic)

        mid = QVBoxLayout()
        mid.setSpacing(0)
        mid.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ttl = QLabel("Switch Target Customer / Party")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        title_row.addWidget(S.kbd("F4"))
        title_row.addStretch()
        mid.addLayout(title_row)
        sub = QLabel("Select customer or vendor ledger to load audit history & event trail")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        mid.addWidget(sub)
        lay.addLayout(mid, stretch=1)

        close_btn = QFrame()
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet(
            f"QFrame {{ background: transparent; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_HIGH}; }}"
        )
        cl = QHBoxLayout(close_btn)
        cl.setContentsMargins(0, 0, 0, 0)
        cic = QLabel()
        cic.setAlignment(Qt.AlignCenter)
        cic.setPixmap(icon_pixmap("close", size=16, color=S.SECONDARY))
        cic.setStyleSheet("background: transparent; border: none;")
        cl.addWidget(cic)
        close_btn.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(close_btn)
        return box

    # ── Search + group chips ─────────────────────────────────
    def _toolbar(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        search_wrap = QFrame()
        search_wrap.setFixedHeight(32)
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
            f"border: 1px solid {S.PRIMARY}; border-radius: {S.R}px; }}"
        )
        sw = QHBoxLayout(search_wrap)
        sw.setContentsMargins(10, 0, 8, 0)
        sw.setSpacing(6)
        sic = QLabel()
        sic.setFixedSize(14, 14)
        sic.setPixmap(icon_pixmap("search", size=14, color=S.SECONDARY))
        sic.setStyleSheet("background: transparent; border: none;")
        sw.addWidget(sic)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search Party Name, Ledger Code, GSTIN, Phone, City…"
        )
        self.search.setText("Balaji" if "Balaji" in self._current else "")
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; "
            f"font-size: 12px; font-weight: 600; color: {T.TEXT_PRIMARY}; }}"
        )
        self.search.textChanged.connect(self._reload)
        sw.addWidget(self.search, stretch=1)
        sw.addWidget(S.kbd("Ctrl+F"))
        lay.addWidget(search_wrap)

        row = QHBoxLayout()
        row.setSpacing(6)
        gl = QLabel("Group:")
        gl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent; padding-right: 4px;"
        )
        row.addWidget(gl)

        n_all = len(self.parties)
        n_debt = sum(1 for p in self.parties if p["group"] == "Sundry Debtor")
        n_cred = sum(1 for p in self.parties if p["group"] == "Sundry Creditor")
        n_od = sum(1 for p in self.parties if p.get("overdue"))
        self._chips = {}
        for key, label in (
            ("all", f"All ({n_all})"),
            ("debtors", f"Sundry Debtors ({n_debt})"),
            ("creditors", f"Sundry Creditors ({n_cred})"),
            ("overdue", f"Overdue Only ({n_od})"),
        ):
            chip = self._chip(key, label, key == "all")
            self._chips[key] = chip
            row.addWidget(chip)
        row.addStretch()
        self.match_lbl = QLabel("0 matches found")
        self.match_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        row.addWidget(self.match_lbl)
        lay.addLayout(row)
        return box

    def _chip(self, key: str, text: str, active: bool) -> QFrame:
        chip = QFrame()
        chip.setCursor(QCursor(Qt.PointingHandCursor))
        self._style_chip(chip, active)
        lay = QHBoxLayout(chip)
        lay.setContentsMargins(8, 3, 8, 3)
        lbl = QLabel(text)
        lbl.setObjectName("chipLbl")
        lbl.setStyleSheet(
            f"color: {'white' if active else S.SECONDARY}; font-size: 11px; "
            f"font-weight: {'700' if active else '500'}; border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        chip.mousePressEvent = (
            lambda e, k=key: self._set_group(k) if e.button() == Qt.LeftButton else None
        )
        return chip

    def _style_chip(self, chip: QFrame, active: bool):
        if active:
            chip.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            )
        else:
            chip.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
            )

    def _set_group(self, key: str):
        self._group = key
        for k, chip in self._chips.items():
            active = k == key
            self._style_chip(chip, active)
            lbl = chip.findChild(QLabel, "chipLbl")
            if lbl:
                lbl.setStyleSheet(
                    f"color: {'white' if active else S.SECONDARY}; font-size: 11px; "
                    f"font-weight: {'700' if active else '500'}; "
                    f"border: none; background: transparent;"
                )
        self._reload()

    # ── Split body ───────────────────────────────────────────
    def _body(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(f"QFrame {{ background: {T.SURFACE}; border: none; }}")
        lay = QHBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Left list
        left = QFrame()
        left.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-right: 1px solid {T.BORDER}; }}"
        )
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Code", "Party Name", "Balance (₹)"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setFixedHeight(28)
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {T.SURFACE}; border: none; outline: 0;
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background: {T.SURFACE_CONTAINER_LOW}; color: {S.SECONDARY};
                font-size: 10px; font-weight: 700; border: none;
                border-bottom: 1px solid {T.BORDER}; padding: 4px 10px;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {T.BORDER}; padding: 4px 8px;
            }}
            QTableWidget::item:selected {{
                background: {S.PRIMARY}; color: white;
            }}
            """
        )
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.table.cellDoubleClicked.connect(lambda *_: self._accept())
        ll.addWidget(self.table)
        lay.addWidget(left, stretch=7)

        # Right snapshot
        self.snap = QFrame()
        self.snap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; }}"
        )
        self.snap.setFixedWidth(280)
        self.snap_lay = QVBoxLayout(self.snap)
        self.snap_lay.setContentsMargins(12, 12, 12, 12)
        self.snap_lay.setSpacing(10)
        lay.addWidget(self.snap)
        return box

    def _footer(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top: 1px solid {T.BORDER}; "
            f"border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        for widgets in (
            [S.kbd("↑"), S.kbd("↓"), self._hint("Navigate")],
            [self._sep(), S.kbd("Enter"), self._hint("Select")],
            [self._sep(), S.kbd("Esc"), self._hint("Close")],
        ):
            for w in widgets:
                lay.addWidget(w)
        lay.addStretch()

        cancel = QFrame()
        cancel.setCursor(QCursor(Qt.PointingHandCursor))
        cancel.setFixedHeight(28)
        cancel.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        cl = QHBoxLayout(cancel)
        cl.setContentsMargins(12, 0, 12, 0)
        ct = QLabel("Cancel")
        ct.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        cl.addWidget(ct)
        ce = QLabel("[Esc]")
        ce.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        cl.addWidget(ce)
        cancel.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(cancel)

        ok = QFrame()
        ok.setCursor(QCursor(Qt.PointingHandCursor))
        ok.setFixedHeight(28)
        ok.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        ol = QHBoxLayout(ok)
        ol.setContentsMargins(12, 0, 10, 0)
        ol.setSpacing(6)
        oic = QLabel()
        oic.setFixedSize(14, 14)
        oic.setPixmap(icon_pixmap("check", size=14, color="white"))
        oic.setStyleSheet("background: transparent; border: none;")
        ol.addWidget(oic)
        ot = QLabel("Switch Ledger")
        ot.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        ol.addWidget(ot)
        ol.addWidget(S.kbd("Enter", on_primary=True))
        ok.mousePressEvent = (
            lambda e: self._accept() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(ok)
        return box

    def _hint(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        return lbl

    def _sep(self) -> QLabel:
        s = QLabel("·")
        s.setStyleSheet(
            f"color: {T.BORDER}; font-size: 11px; border: none; background: transparent; "
            f"padding: 0 4px;"
        )
        return s

    # ── Data / selection ─────────────────────────────────────
    def _filtered(self):
        q = (self.search.text() or "").strip().lower()
        rows = []
        for p in self.parties:
            if self._group == "debtors" and p["group"] != "Sundry Debtor":
                continue
            if self._group == "creditors" and p["group"] != "Sundry Creditor":
                continue
            if self._group == "overdue" and not p.get("overdue"):
                continue
            if q:
                blob = " ".join([
                    p.get("code", ""), p["name"], p.get("gstin", ""),
                    p.get("phone", ""), p.get("city", ""), p.get("state", ""),
                ]).lower()
                if q not in blob:
                    continue
            rows.append(p)
        return rows

    def _reload(self):
        self._rows = self._filtered()
        self.match_lbl.setText(f"{len(self._rows)} matches found")
        self.table.blockSignals(True)
        self.table.setRowCount(len(self._rows))
        for r, p in enumerate(self._rows):
            code = QTableWidgetItem(p["code"])
            code.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(r, 0, code)

            name_w = QWidget()
            name_w.setStyleSheet("background: transparent;")
            nl = QVBoxLayout(name_w)
            nl.setContentsMargins(6, 4, 6, 4)
            nl.setSpacing(1)
            nt = QLabel(p["name"])
            nt.setObjectName("partyName")
            nt.setStyleSheet(
                f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
            nl.addWidget(nt)
            loc = QLabel(f"{p.get('city', '')} · {p.get('state', '')}")
            loc.setObjectName("partyLoc")
            loc.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
            )
            nl.addWidget(loc)
            self.table.setCellWidget(r, 1, name_w)

            bal = p["balance"]
            btype = p.get("balance_type", "Dr")
            if bal <= 0 and btype == "Nil":
                bal_txt = "0.00 Nil"
                bal_col = S.SECONDARY
            else:
                bal_txt = f"{format_inr_indian(bal, with_symbol=False)} {btype}"
                bal_col = T.DANGER if btype == "Dr" else (
                    "#0f766e" if btype == "Cr" else S.SECONDARY
                )
            bal_it = QTableWidgetItem(bal_txt)
            bal_it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            bal_it.setForeground(QBrush(QColor(bal_col)))
            f = bal_it.font()
            f.setBold(True)
            bal_it.setFont(f)
            bal_it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(r, 2, bal_it)
        self.table.blockSignals(False)
        if self._rows:
            self.table.selectRow(0)
            self._paint_selection()
            self._fill_snapshot(self._rows[0])
        else:
            self._fill_snapshot(None)

    def _select_current(self):
        for i, p in enumerate(self._rows):
            if p["name"] == self._current:
                self.table.selectRow(i)
                self._paint_selection()
                self._fill_snapshot(p)
                return

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        idx = rows[0].row()
        if 0 <= idx < len(self._rows):
            self._paint_selection()
            self._fill_snapshot(self._rows[idx])

    def _paint_selection(self):
        """Restyle name widgets — selected row uses white text on primary."""
        sel = {i.row() for i in self.table.selectionModel().selectedRows()}
        for r in range(self.table.rowCount()):
            active = r in sel
            w = self.table.cellWidget(r, 1)
            if w is None:
                continue
            name = w.findChild(QLabel, "partyName")
            loc = w.findChild(QLabel, "partyLoc")
            if name:
                name.setStyleSheet(
                    f"color: {'white' if active else T.TEXT_PRIMARY}; font-size: 12px; "
                    f"font-weight: 700; border: none; background: transparent;"
                )
            if loc:
                loc.setStyleSheet(
                    f"color: {'rgba(255,255,255,0.85)' if active else S.SECONDARY}; "
                    f"font-size: 10px; border: none; background: transparent;"
                )
            # check_circle on selected
            # remove old check if any beyond name/loc
            for child in w.findChildren(QLabel):
                if child.objectName() == "selCheck":
                    child.setParent(None)
                    child.deleteLater()
            if active and name is not None:
                lay = name.parentWidget().layout() if name.parentWidget() else None
                # put check next to name via wrapping — skip for simplicity

    def _fill_snapshot(self, p):
        while self.snap_lay.count():
            item = self.snap_lay.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            elif item.layout():
                sub = item.layout()
                while sub.count():
                    si = sub.takeAt(0)
                    sw = si.widget()
                    if sw:
                        sw.setParent(None)
                        sw.deleteLater()

        if p is None:
            empty = QLabel("No party selected")
            empty.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
            )
            self.snap_lay.addWidget(empty)
            self.snap_lay.addStretch()
            return

        head = QHBoxLayout()
        cap = QLabel("Selected Party Snapshot")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        head.addWidget(cap)
        head.addStretch()
        badge = QLabel(
            "Active Customer" if p["type"] == "Customer" else "Active Supplier"
        )
        badge.setStyleSheet(
            f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; "
            f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; "
            f"padding: 1px 6px; font-size: 10px; font-weight: 700;"
        )
        head.addWidget(badge)
        self.snap_lay.addLayout(head)

        name = QLabel(p["name"])
        name.setWordWrap(True)
        name.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        self.snap_lay.addWidget(name)
        addr = QLabel(p.get("address", ""))
        addr.setWordWrap(True)
        addr.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        self.snap_lay.addWidget(addr)

        meta = QFrame()
        meta.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        ml = QVBoxLayout(meta)
        ml.setContentsMargins(8, 8, 8, 8)
        ml.setSpacing(4)
        for label, value, color in (
            ("GSTIN:", p.get("gstin", "—"), T.TEXT_PRIMARY),
            ("Contact:", p.get("phone", "—"), T.TEXT_PRIMARY),
            ("Credit Limit:", format_inr_indian(p.get("credit_limit", 0)), T.TEXT_PRIMARY),
            (
                "Trail Events:",
                f"{p.get('events', 0)} Records (FY 26-27)",
                S.PRIMARY,
            ),
        ):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
            )
            row.addWidget(l)
            v = QLabel(value)
            v.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
            row.addWidget(v, alignment=Qt.AlignRight)
            ml.addLayout(row)
        self.snap_lay.addWidget(meta)

        self.snap_lay.addStretch()

        bal_row = QHBoxLayout()
        bl = QLabel("Current O/S Balance:")
        bl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bal_row.addWidget(bl)
        btype = p.get("balance_type", "Dr")
        bal_val = p.get("balance", 0)
        if bal_val <= 0 and btype == "Nil":
            bt = "₹ 0.00 Nil"
            bc = S.SECONDARY
        else:
            bt = f"{format_inr_indian(bal_val)} {btype}"
            bc = T.DANGER if btype == "Dr" else "#0f766e"
        bv = QLabel(bt)
        bv.setStyleSheet(
            f"color: {bc}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        bal_row.addWidget(bv, alignment=Qt.AlignRight)
        self.snap_lay.addLayout(bal_row)

        last = QFrame()
        last.setStyleSheet("background: transparent; border: none;")
        ll = QHBoxLayout(last)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(4)
        lic = QLabel()
        lic.setFixedSize(14, 14)
        lic.setPixmap(icon_pixmap("verified", size=14, color=T.SUCCESS_FG))
        lic.setStyleSheet("background: transparent; border: none;")
        ll.addWidget(lic)
        lt = QLabel(p.get("last_txn", ""))
        lt.setWordWrap(True)
        lt.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        ll.addWidget(lt, stretch=1)
        self.snap_lay.addWidget(last)

    def _move(self, delta: int):
        if not self._rows:
            return
        row = self.table.currentRow()
        if row < 0:
            row = 0
        else:
            row = max(0, min(len(self._rows) - 1, row + delta))
        self.table.selectRow(row)
        self._paint_selection()
        self._fill_snapshot(self._rows[row])

    def _accept(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        idx = rows[0].row()
        if 0 <= idx < len(self._rows):
            self.selected_party = dict(self._rows[idx])
            self.accept()
