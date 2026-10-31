"""2.3 Cash Flow Register — Stitch-faithful Cash In & Out."""

from PySide6.QtCore import Qt, QDate, QRectF, QSize
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap

# Stitch MD3 tertiary (Cash In KPI / type / amounts)
_TERTIARY = "#4e5562"
_INVERSE_SURFACE = "#2e3132"  # status bar bg-inverse-surface


class _TypePill(QWidget):
    """Compact type chip — centered text, tight background, 6px gap after dot."""

    _DOT = 5
    _GAP = 6
    _PAD_L = 8
    _PAD_R = 8

    def __init__(self, is_in: bool, parent=None):
        super().__init__(parent)
        self._is_in = is_in
        self._text = "Cash In" if is_in else "Cash Out"
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setFixedHeight(22)
        font = QFont()
        font.setPixelSize(11)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)
        text_w = self.fontMetrics().boundingRect(self._text).width()
        w = self._PAD_L + self._DOT + self._GAP + text_w + self._PAD_R + 2
        self.setFixedWidth(w)

    def sizeHint(self):
        return QSize(self.width(), 22)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        if self._is_in:
            bg = QColor(T.SUCCESS_BG)
            dot_c = QColor(T.SUCCESS)
            fg = QColor(T.SUCCESS_FG)
        else:
            bg = QColor(T.DANGER_BG)
            dot_c = QColor(T.DANGER)
            fg = QColor(T.DANGER)

        # Compact pill height (less background)
        pill_h = 18
        pill_rect = QRectF(0.5, (self.height() - pill_h) / 2, self.width() - 1, pill_h)
        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(pill_rect, 4, 4)

        content_w = self._DOT + self._GAP + self.fontMetrics().boundingRect(self._text).width()
        start_x = (self.width() - content_w) / 2

        dy = (self.height() - self._DOT) / 2
        p.setBrush(dot_c)
        p.drawEllipse(QRectF(start_x, dy, self._DOT, self._DOT))

        tx = start_x + self._DOT + self._GAP
        p.setPen(fg)
        p.setFont(self.font())
        p.drawText(
            QRectF(tx, 0, self.width() - tx, self.height()),
            int(Qt.AlignVCenter | Qt.AlignLeft),
            self._text,
        )
        p.end()


class CashFlowScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = [dict(e) for e in D.CASH_ENTRIES]
        self.kpi = dict(D.CASH_FLOW_KPI)
        self.kpi.setdefault("in_count", sum(1 for e in self.entries if e.get("kind") == "In"))
        self.kpi.setdefault("out_count", sum(1 for e in self.entries if e.get("kind") == "Out"))
        self._kind = "In"
        self._filter = "all"
        self._seq_in = 1
        self._seq_out = 1
        self.setStyleSheet(f"background: {T.BG_CANVAS};")
        self._build()
        self._reload_table()
        QShortcut(QKeySequence("Return"), self, activated=self._post)

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

        # Stitch: w-9 h-9 rounded bg-primary payments icon
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
            f"color: {T.TEXT_PRIMARY}; font-size: 15px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        # Stitch FY: bg-surface-container-high text-primary
        fy = QLabel("FY 2026-27")
        fy.setStyleSheet(
            f"color: {S.PRIMARY}; background: {T.SURFACE_CONTAINER_HIGH}; "
            f"border: none; border-radius: {S.R}px; padding: 2px 6px; "
            f"font-size: 10px; font-weight: 700;"
        )
        title_row.addWidget(fy)
        title_row.addStretch()
        mid.addLayout(title_row)
        sub = QLabel("Cash Counter Drawer  ·  Date: 20-Sep-2026")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        mid.addWidget(sub)
        lay.addLayout(mid, stretch=1)

        # Stitch Print: bg-surface-container (soft), not bordered white
        print_btn = QFrame()
        print_btn.setCursor(QCursor(Qt.PointingHandCursor))
        print_btn.setFixedHeight(28)
        print_btn.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_HIGH}; }}"
        )
        pl = QHBoxLayout(print_btn)
        pl.setContentsMargins(10, 0, 10, 0)
        pl.setSpacing(4)
        pic = QLabel()
        pic.setFixedSize(16, 16)
        pic.setPixmap(icon_pixmap("print", size=16, color=T.TEXT_PRIMARY))
        pic.setStyleSheet("background: transparent; border: none;")
        pl.addWidget(pic)
        pt = QLabel("Print Register")
        pt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        pl.addWidget(pt)
        print_btn.mousePressEvent = (
            lambda e: toast(self, "Printing register…")
            if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(print_btn)
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
            # title, amount, icon, icon/title/amt color, hint, filled
            ("Opening Balance", k["opening"], "lock_clock", S.SECONDARY, T.TEXT_PRIMARY,
             "Day start counter float", False),
            ("Total Cash In", k["cash_in"], "arrow_downward", T.SUCCESS_FG, T.SUCCESS_FG,
             f"{k['in_count']} Receipts recorded today", False),
            ("Total Cash Out", k["cash_out"], "arrow_upward", T.DANGER, T.DANGER,
             f"{k['out_count']} Payments made today", False),
            ("REMAINING AMOUNT", k["remaining"], "point_of_sale", "white", "white",
             "Available in physical drawer", True),
        ]
        for title, amt, icon, tone, amt_col, hint, filled in cards:
            lay.addWidget(
                self._kpi_card(title, amt, icon, tone, amt_col, hint, filled), 1
            )
        return wrap

    def _kpi_card(self, title, amount, icon, tone, amt_col, hint, filled) -> QFrame:
        card = QFrame()
        if filled:
            # Stitch: bg-primary (MD3 primary deep)
            card.setStyleSheet(
                f"QFrame {{ background: {T.PRIMARY_DEEP}; border: none; "
                f"border-radius: {S.CR}px; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.CR}px; }}"
            )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)

        top = QHBoxLayout()
        cap = QLabel(title.upper() if not filled else title)
        cap.setStyleSheet(
            f"color: {'rgba(238,239,255,0.9)' if filled else tone}; "
            f"font-size: 10px; font-weight: 700; letter-spacing: 0.4px; "
            f"border: none; background: transparent;"
        )
        top.addWidget(cap)
        top.addStretch()
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap(icon, size=18, color="white" if filled else tone))
        ic.setStyleSheet("background: transparent; border: none;")
        top.addWidget(ic)
        lay.addLayout(top)

        # Stitch: integer + smaller .00
        full = format_inr_indian(amount)
        if "." in full:
            rupee, dec = full.rsplit(".", 1)
            val = QLabel(
                f"<span style='font-size:22px;font-weight:700;color:{amt_col};'>"
                f"{rupee}</span>"
                f"<span style='font-size:14px;font-weight:600;color:{amt_col};'>"
                f".{dec}</span>"
            )
        else:
            val = QLabel(full)
            val.setStyleSheet(
                f"color: {amt_col}; font-size: 22px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
        val.setTextFormat(Qt.RichText)
        val.setStyleSheet("border: none; background: transparent;")
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

        # Transaction type row + bottom border (Stitch)
        head_wrap = QFrame()
        head_wrap.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        head = QHBoxLayout(head_wrap)
        head.setContentsMargins(0, 0, 0, 8)
        head.setSpacing(8)
        cap = QLabel("TRANSACTION TYPE:")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        head.addWidget(cap)

        # Segmented control: bg-surface-container
        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        segl = QHBoxLayout(seg)
        segl.setContentsMargins(2, 2, 2, 2)
        segl.setSpacing(0)
        self.btn_in = self._mode_chip("Cash In (Receipt)", "add_circle", True)
        self.btn_out = self._mode_chip("Cash Out (Payment)", "remove_circle", False)
        self.btn_in.mousePressEvent = (
            lambda e: self._set_kind("In") if e.button() == Qt.LeftButton else None
        )
        self.btn_out.mousePressEvent = (
            lambda e: self._set_kind("Out") if e.button() == Qt.LeftButton else None
        )
        segl.addWidget(self.btn_in)
        segl.addWidget(self.btn_out)
        head.addWidget(seg)
        head.addStretch()

        # Next Voucher with check_circle (Stitch)
        vrow = QHBoxLayout()
        vrow.setSpacing(4)
        vrow.setContentsMargins(0, 0, 0, 0)
        vic = QLabel()
        vic.setFixedSize(16, 16)
        vic.setPixmap(icon_pixmap("check_circle", size=16, color=_TERTIARY))
        vic.setStyleSheet("background: transparent; border: none;")
        vrow.addWidget(vic)
        self.voucher_prefix = QLabel("Next Voucher:")
        self.voucher_prefix.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        vrow.addWidget(self.voucher_prefix)
        self.voucher_lbl = QLabel("#CSH-IN-049")
        self.voucher_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        vrow.addWidget(self.voucher_lbl)
        head.addLayout(vrow)
        lay.addWidget(head_wrap)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.date = QDateEdit(QDate(2026, 9, 20))
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd-MMM-yyyy")
        self.date.setEnabled(False)
        row.addWidget(S.labeled_input("Date", self.date), 2)

        # Party with "+ New Ledger" (Stitch)
        party_wrap = QWidget()
        party_wrap.setStyleSheet("background: transparent;")
        pwl = QVBoxLayout(party_wrap)
        pwl.setContentsMargins(0, 0, 0, 0)
        pwl.setSpacing(4)
        ptop = QHBoxLayout()
        ptop.setContentsMargins(0, 0, 0, 0)
        pcap = QLabel("Party / Expense Ledger")
        pcap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        ptop.addWidget(pcap)
        ptop.addStretch()
        new_led = QLabel("+ New Ledger")
        new_led.setCursor(QCursor(Qt.PointingHandCursor))
        new_led.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 10px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        new_led.mousePressEvent = (
            lambda e: toast(self, "Open New Ledger…")
            if e.button() == Qt.LeftButton else None
        )
        ptop.addWidget(new_led)
        pwl.addLayout(ptop)

        self.party = QComboBox()
        self.party.setEditable(False)
        for p in D.PARTIES:
            self.party.addItem(p["name"])
        self.party.addItem("+ Add / Select Ledger...")
        self.party.setCurrentIndex(0)
        from app.widgets.icons import combo_dropdown_qss
        self.party.setStyleSheet(
            f"""
            QComboBox {{
                background: {T.SURFACE}; border: 1px solid {T.BORDER};
                border-radius: {S.R}px; padding: 6px 28px 6px 10px;
                min-height: 18px; font-size: 13px; font-weight: 600;
                color: {T.TEXT_PRIMARY};
            }}
            {combo_dropdown_qss(width=22, background=T.SURFACE)}
            """
        )
        pwl.addWidget(self.party)
        row.addWidget(party_wrap, 5)

        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 9_999_999)
        self.amount.setDecimals(2)
        self.amount.setGroupSeparatorShown(True)
        row.addWidget(S.labeled_input("Amount (₹)", self.amount), 2)

        rec = S.action_btn(
            "Record", shortcut="↵", icon="save", kind="primary", on_click=self._post
        )
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
        chip.setFixedHeight(26)
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
        lbl.setStyleSheet(
            "border: none; background: transparent; font-size: 12px; font-weight: 600;"
        )
        lay.addWidget(lbl)
        self._paint_mode_chip(chip, icon, active, kind="In" if "In" in text else "Out")
        return chip

    def _paint_mode_chip(self, chip: QFrame, icon: str, active: bool, kind: str):
        ic = chip.findChild(QLabel, "modeIcon")
        lbl = chip.findChild(QLabel, "modeText")
        if active:
            # Stitch: bg-primary-container text-on-primary
            chip.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; "
                f"border-radius: {S.R}px; }}"
            )
            fg = "white"
        else:
            chip.setStyleSheet(
                f"QFrame {{ background: transparent; border: none; "
                f"border-radius: {S.R}px; }}"
            )
            fg = T.TEXT_PRIMARY
        if ic:
            ic.setPixmap(
                icon_pixmap(icon, size=16, color=fg if active else S.SECONDARY)
            )
        if lbl:
            lbl.setStyleSheet(
                f"color: {fg}; font-size: 12px; font-weight: "
                f"{'700' if active else '500'}; border: none; background: transparent;"
            )

    def _set_kind(self, kind: str):
        self._kind = kind
        self._paint_mode_chip(self.btn_in, "add_circle", kind == "In", "In")
        self._paint_mode_chip(self.btn_out, "remove_circle", kind == "Out", "Out")
        if kind == "In":
            self.voucher_lbl.setText(f"#CSH-IN-{self._seq_in:03d}")
        else:
            self.voucher_lbl.setText(f"#CSH-OUT-{self._seq_out:03d}")
        self.voucher_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
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
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border-radius: {S.R}px; "
            f"border: none; }}"
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
                lambda e, k=key: self._set_filter(k)
                if e.button() == Qt.LeftButton else None
            )
            self._filter_btns[key] = b
            tw.addWidget(b)
        self._paint_filters()
        tl.addWidget(tab_wrap)
        tl.addStretch()

        search_wrap = QFrame()
        search_wrap.setFixedWidth(280)
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.INPUT_BG}; border: none; "
            f"border-radius: {S.R}px; }}"
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
        # Compact centered type chips
        hdr.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 120)
        hdr.setMinimumSectionSize(80)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 140)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 72)
        S.apply_table_style(self.table)
        self.table.setTextElideMode(Qt.TextElideMode.ElideNone)
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
        # Stitch: bg-inverse-surface
        bar = QFrame()
        bar.setStyleSheet(
            f"QFrame {{ background: {_INVERSE_SURFACE}; border-radius: {S.R}px; "
            f"border: none; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 8, 14, 8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {T.SUCCESS}; border-radius: 4px; border: none;")
        lay.addWidget(dot)
        lbl = QLabel("Cash Drawer:  <b>Active & Ready</b>")
        lbl.setTextFormat(Qt.RichText)
        lbl.setStyleSheet(
            "color: #f0f1f3; font-size: 12px; border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        lay.addStretch()
        tip = QLabel("Shortcut: Enter to Record transaction")
        tip.setStyleSheet(
            "color: #c3c6d7; font-size: 11px; border: none; background: transparent;"
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
            date_s = e.get("date", "")
            try:
                y, m, d = date_s.split("-")
                months = [
                    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                ]
                date_disp = f"{int(d):02d}-{months[int(m)]} · {e.get('time', '')}"
            except Exception:
                date_disp = f"{date_s} · {e.get('time', '')}"

            self.table.setItem(r, 0, self._item(date_disp, secondary=True))

            # Cash In = green, Cash Out = red (same as Type pill)
            in_color = T.SUCCESS_FG
            out_color = T.DANGER
            vch = QTableWidgetItem(f"#{e['ref']}")
            vch.setForeground(QBrush(QColor(in_color if is_in else out_color)))
            f = vch.font()
            f.setBold(True)
            vch.setFont(f)
            self.table.setItem(r, 1, vch)

            self.table.setCellWidget(r, 2, self._type_pill(is_in))

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
            amt.setForeground(QBrush(QColor(in_color if is_in else out_color)))
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
        """Compact centered type chip."""
        cell = QWidget()
        cell.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(0)
        lay.addStretch(1)
        lay.addWidget(_TypePill(is_in), 0, Qt.AlignVCenter)
        lay.addStretch(1)
        return cell

    def _delete(self, row: dict):
        if row in self.entries:
            self.entries.remove(row)
            signed = row["amount"] if row["kind"] == "In" else -row["amount"]
            self.kpi["remaining"] -= signed
            if row["kind"] == "In":
                self.kpi["cash_in"] -= row["amount"]
                self.kpi["in_count"] = max(0, self.kpi.get("in_count", 1) - 1)
            else:
                self.kpi["cash_out"] -= row["amount"]
                self.kpi["out_count"] = max(0, self.kpi.get("out_count", 1) - 1)
            self._reload_table()
            toast(self, f"Deleted #{row['ref']}")

    def _post(self):
        from app.services import cash as cash_svc
        from app import session

        amt = float(self.amount.value())
        if amt <= 0:
            toast(self, "Enter a valid amount.")
            return
        party = self.party.currentText().strip()
        if not party or party.startswith("+"):
            toast(self, "Select a party / ledger.")
            return
        ledger = next((p for p in D.PARTIES if p["name"] == party), None)
        user = session.current_user()
        try:
            saved = cash_svc.create_entry(
                {
                    "kind": self._kind,
                    "date": self.date.date().toString("yyyy-MM-dd"),
                    "party": party,
                    "ledger_id": ledger["id"] if ledger else None,
                    "purpose": "Manual counter entry",
                    "amount": amt,
                    "mode": "Cash",
                },
                created_by=user["id"] if user else None,
            )
        except Exception as exc:
            toast(self, f"Post failed: {exc}")
            return
        D.reload()
        self.entries = [dict(e) for e in D.CASH_ENTRIES]
        self.kpi = dict(D.CASH_FLOW_KPI)
        self.kpi.setdefault("in_count", sum(1 for e in self.entries if e["kind"] == "In"))
        self.kpi.setdefault("out_count", sum(1 for e in self.entries if e["kind"] == "Out"))
        self.amount.setValue(0)
        self._set_kind(self._kind)
        self._reload_table()
        toast(self, f"Recorded #{saved['ref']}")
