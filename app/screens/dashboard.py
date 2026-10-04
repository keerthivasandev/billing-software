"""Dashboard — Stitch ERP Dashboard (Fast Lookup & Counter Summary)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import format_inr_indian, toast, ui_font
from app.widgets.icons import icon_pixmap

_PRIMARY = "#1D4ED8"
_PRIMARY_HOVER = "#1d4ed8"


def _card() -> QFrame:
    box = QFrame()
    box.setStyleSheet(
        f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
        f"border-radius: {T.CARD_RADIUS}px; }}"
    )
    return box


def _kbd(text: str, on_primary: bool = False) -> QLabel:
    chip = QLabel(text)
    chip.setAlignment(Qt.AlignCenter)
    if on_primary:
        chip.setStyleSheet(
            "background: rgba(255,255,255,0.22); color: white; "
            "border: 1px solid rgba(255,255,255,0.35); border-radius: 3px; "
            f"padding: 1px 5px; font-size: {T.FONT_SIZE_MICRO}pt; font-weight: 700;"
        )
    else:
        chip.setStyleSheet(
            f"background: {T.HEADER_BAND}; color: {T.TEXT_MUTED}; "
            f"border: 1px solid {T.BORDER_STRONG}; border-radius: 3px; "
            f"padding: 1px 5px; font-size: {T.FONT_SIZE_MICRO}pt; font-weight: 700;"
        )
    return chip


class DashboardScreen(QWidget):
    def __init__(self, parent=None, navigate_cb=None):
        super().__init__(parent)
        self._navigate = navigate_cb or (lambda *_: None)
        self.setObjectName("dashboardRoot")
        self.setStyleSheet(f"QWidget#dashboardRoot {{ background: {T.BG_CANVAS}; }}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {T.BG_CANVAS}; border: none; }}")

        body = QWidget()
        body.setStyleSheet(f"background: {T.BG_CANVAS};")
        root = QVBoxLayout(body)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        root.addWidget(self._welcome_and_actions())
        root.addLayout(self._kpi_row())
        root.addWidget(self._counter_summary())

        mid = QHBoxLayout()
        mid.setSpacing(12)
        mid.setAlignment(Qt.AlignTop)
        lookup = self._fast_lookup()
        alerts = self._alerts_column()
        alerts.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        mid.addWidget(lookup, stretch=7, alignment=Qt.AlignTop)
        mid.addWidget(alerts, stretch=4, alignment=Qt.AlignTop)
        root.addLayout(mid)
        root.addWidget(self._hotkeys_bar())
        root.addStretch(1)

        scroll.setWidget(body)
        outer.addWidget(scroll)

    # ── Welcome + quick actions ──────────────────────────────
    def _welcome_and_actions(self) -> QFrame:
        box = _card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)

        icon = QLabel()
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: 4px; border: none;"
        )
        icon.setPixmap(icon_pixmap("home", size=22, color=_PRIMARY))

        text = QVBoxLayout()
        text.setSpacing(2)
        greet = QLabel(getattr(D, "DASHBOARD_WELCOME", f"Welcome back, {D.CURRENT_USER}"))
        greet.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        sub = QLabel(getattr(D, "DASHBOARD_SHIFT", "Main Wholesale Counter"))
        sub.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        text.addWidget(greet)
        text.addWidget(sub)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self._action("+ New Sale Invoice", "F2", "primary", "sales"))
        actions.addWidget(self._action("+ New Purchase Entry", "F3", "secondary", "purchase"))
        actions.addWidget(self._action("Receipt / Payment", "F1", "secondary", "cash_flow"))
        actions.addWidget(self._action("Add Party / Ledger", "F4", "secondary", "parties"))

        lay.addWidget(icon)
        lay.addLayout(text, stretch=1)
        lay.addLayout(actions)
        return box

    def _action(self, label: str, shortcut: str, kind: str, go: str) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(32)
        if kind == "primary":
            btn.setStyleSheet(
                f"QFrame {{ background: {_PRIMARY}; border: none; border-radius: 4px; }}"
                f"QFrame:hover {{ background: {_PRIMARY_HOVER}; }}"
            )
            fg = "white"
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
                f"QFrame:hover {{ background: {T.HEADER_BAND}; }}"
            )
            fg = T.TEXT_PRIMARY
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(8)
        text = QLabel(label)
        text.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(text)
        lay.addWidget(_kbd(shortcut, on_primary=(kind == "primary")))
        btn.mousePressEvent = lambda e, k=go: self._navigate(k)
        return btn

    # ── KPI cards ────────────────────────────────────────────
    def _kpi_row(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(12)
        kpi = D.DASHBOARD_KPI
        specs = [
            (
                "Today's Sales",
                kpi["todays_sales"],
                f"{kpi['todays_sales_bills']} Invoices Billed",
                f"↑ {kpi['sales_growth_pct']}% vs yesterday",
                "growth",
            ),
            (
                "Today's Purchases",
                kpi["todays_purchases"],
                f"{kpi['purchase_vouchers']} Inward Vouchers",
                kpi["purchase_godown"],
                "neutral",
            ),
            (
                "Cash in Drawer",
                kpi["cash_in_hand"],
                f"{kpi['drawer_txns']} Drawer Transactions",
                kpi["drawer_status"],
                "success",
            ),
            (
                "Total Receivables (Dr)",
                kpi["receivables_due"],
                f"{kpi['active_debtors']} Active Debtors",
                kpi["overdue_amount_label"],
                "danger",
            ),
        ]
        for i, spec in enumerate(specs):
            grid.addWidget(self._kpi_card(*spec), 0, i)
            grid.setColumnStretch(i, 1)
        return grid

    def _kpi_card(self, title, amount, meta, foot, kind) -> QFrame:
        box = _card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        top = QHBoxLayout()
        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        top.addWidget(lbl)
        top.addStretch()
        lay.addLayout(top)

        amount_row = QHBoxLayout()
        amount_row.setSpacing(4)
        danger = kind == "danger"
        rupee = QLabel("₹")
        rupee.setStyleSheet(
            f"color: {T.DANGER if danger else T.TEXT_SECONDARY}; font-size: 14px; "
            f"font-weight: 500; border: none; background: transparent;"
        )
        val = QLabel(format_inr_indian(amount, with_symbol=False))
        val.setStyleSheet(
            f"color: {T.DANGER if danger else T.TEXT_PRIMARY}; font-size: 18px; "
            f"font-weight: 700; border: none; background: transparent;"
        )
        amount_row.addWidget(rupee)
        amount_row.addWidget(val)
        amount_row.addStretch()
        lay.addLayout(amount_row)

        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(meta_lbl)

        if kind == "growth":
            foot_box = QLabel(foot)
            foot_box.setStyleSheet(
                f"color: #047857; background: {T.SUCCESS_BG}; border: 1px solid #a7f3d0; "
                f"border-radius: 4px; padding: 3px 8px; font-size: 10px; font-weight: 700;"
            )
            lay.addWidget(foot_box, 0, Qt.AlignLeft)
        elif kind == "danger":
            foot_box = QLabel(f"{foot}")
            foot_box.setStyleSheet(
                f"color: #b91c1c; background: {T.DANGER_BG}; border: 1px solid #fecaca; "
                f"border-radius: 4px; padding: 4px 8px; font-size: 10px; font-weight: 700;"
            )
            lay.addWidget(foot_box, 0, Qt.AlignLeft)
        elif kind == "success":
            foot_box = QLabel(foot)
            foot_box.setStyleSheet(
                f"color: #047857; background: {T.SUCCESS_BG}; border: 1px solid #a7f3d0; "
                f"border-radius: 4px; padding: 3px 8px; font-size: 10px; font-weight: 600;"
            )
            lay.addWidget(foot_box, 0, Qt.AlignLeft)
        else:
            foot_lbl = QLabel(foot)
            foot_lbl.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(foot_lbl)
        return box

    # ── Counter summary strip ────────────────────────────────
    def _counter_summary(self) -> QFrame:
        box = _card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 10, 14, 12)
        lay.setSpacing(10)

        head = QHBoxLayout()
        title = QLabel("Today's Counter Summary & Cash Split")
        title.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        shift = QLabel(getattr(D, "COUNTER_SHIFT_LABEL", "Shift: 08:30 AM - Ongoing"))
        shift.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        head.addWidget(title)
        head.addStretch()
        head.addWidget(shift)
        lay.addLayout(head)

        row = QHBoxLayout()
        row.setSpacing(10)
        for item in D.COUNTER_SUMMARY:
            row.addWidget(self._split_card(item), stretch=1)
        lay.addLayout(row)
        return box

    def _split_card(self, item: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: #F8FAFC; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        top = QHBoxLayout()
        ttl = QLabel(item["title"].upper())
        ttl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        top.addWidget(ttl)
        top.addStretch()
        badge = QLabel(item["badge"])
        if item.get("badge_kind") == "success":
            badge.setStyleSheet(
                f"color: #047857; background: {T.SUCCESS_BG}; border: 1px solid #a7f3d0; "
                f"border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: 700;"
            )
        else:
            badge.setStyleSheet(
                f"color: {T.TEXT_MUTED}; background: {T.HEADER_BAND}; "
                f"border: 1px solid {T.BORDER}; border-radius: 4px; "
                f"padding: 2px 6px; font-size: 10px; font-weight: 700;"
            )
        top.addWidget(badge)
        lay.addLayout(top)

        amt = QLabel(format_inr_indian(item["amount"]))
        amt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        meta = QLabel(item["meta"])
        meta.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(amt)
        lay.addWidget(meta)
        return card

    # ── Fast item lookup ─────────────────────────────────────
    def _fast_lookup(self) -> QFrame:
        box = _card()
        # Prefer content height — do not stretch to match right-column alerts.
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QFrame()
        head.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        head.setFixedHeight(36)
        head.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(12, 6, 12, 6)
        hl.setSpacing(8)
        title = QLabel("Fast Item Lookup & Wholesale Rates")
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        title.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        chip = QLabel("Fast Moving")
        chip.setAlignment(Qt.AlignCenter)
        chip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        chip.setFixedHeight(22)
        chip.setStyleSheet(
            f"color: {_PRIMARY}; background: {T.ACCENT_SOFT}; border: 1px solid #bfdbfe; "
            f"border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
        hl.addWidget(title, 0, Qt.AlignVCenter)
        hl.addStretch(1)
        hl.addWidget(chip, 0, Qt.AlignVCenter)
        lay.addWidget(head)

        # Inline search — tight under title
        search_row = QHBoxLayout()
        search_row.setContentsMargins(12, 8, 12, 6)
        search_row.setSpacing(0)
        search = QLineEdit()
        search.setPlaceholderText("Search item code / description…")
        search.setFixedHeight(28)
        search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search.setStyleSheet(
            f"QLineEdit {{ background: {T.HEADER_BAND}; border: 1px solid {T.BORDER_STRONG}; "
            f"border-radius: 4px; padding: 2px 10px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border: 1px solid {_PRIMARY}; background: {T.SURFACE}; }}"
        )
        self._lookup_search = search
        search.textChanged.connect(self._filter_lookup)
        search_row.addWidget(search)
        lay.addLayout(search_row)

        rows = D.FAST_LOOKUP_ITEMS
        table = QTableWidget(len(rows), 6)
        self._lookup_table = table
        table.setHorizontalHeaderLabels(
            ["ITEM CODE", "PRODUCT DESCRIPTION", "CATEGORY", "GODOWN STOCK", "WHOLESALE RATE", ""]
        )
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setDefaultSectionSize(42)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        table.setColumnWidth(5, 72)
        table.setMinimumHeight(42 * len(rows) + 40)
        table.setMaximumHeight(42 * len(rows) + 44)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        table.setStyleSheet(
            f"""
            QTableWidget {{
                border: none; background: {T.SURFACE};
                alternate-background-color: #F8FAFC;
            }}
            QHeaderView::section {{
                background: {T.HEADER_BAND};
                color: {T.TEXT_MUTED};
                border: none;
                border-bottom: 1px solid {T.BORDER};
                padding: 8px 10px;
                font-size: 10px;
                font-weight: 700;
            }}
            QTableWidget::item {{
                padding: 4px 10px;
                border-bottom: 1px solid {T.BORDER};
            }}
            QTableWidget::item:selected {{
                background: {T.ACCENT_SOFT};
                color: {T.TEXT_PRIMARY};
            }}
            """
        )
        self._fill_lookup_table(rows)
        lay.addWidget(table)

        foot = QFrame()
        foot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        foot.setStyleSheet(
            f"QFrame {{ background: #F8FAFC; border: none; border-top: 1px solid {T.BORDER}; }}"
        )
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(12, 8, 12, 8)
        tip = QLabel("Tip: Press Alt+S anywhere for full product catalog query")
        tip.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        catalog = QPushButton("Open Full Master Catalog  Alt+S")
        catalog.setCursor(Qt.PointingHandCursor)
        catalog.setStyleSheet(
            f"QPushButton {{ background: {T.SURFACE}; color: {_PRIMARY}; "
            f"border: 1px solid {T.BORDER}; border-radius: 4px; padding: 5px 12px; "
            f"font-size: 11px; font-weight: 600; min-height: 26px; }}"
            f"QPushButton:hover {{ background: {T.ACCENT_SOFT}; }}"
        )
        catalog.clicked.connect(lambda: self._navigate("products"))
        fl.addWidget(tip)
        fl.addStretch()
        fl.addWidget(catalog)
        lay.addWidget(foot)
        return box

    def _fill_lookup_table(self, rows):
        table = self._lookup_table
        table.setRowCount(len(rows))
        for r, item in enumerate(rows):
            code = QTableWidgetItem(item["code"])
            code.setForeground(QBrush(QColor(_PRIMARY)))
            code.setFont(ui_font(9, bold=True))
            name = QTableWidgetItem(item["name"])
            name.setFont(ui_font(9, bold=True))
            cat = QTableWidgetItem(item["category"])
            stock = QTableWidgetItem(item["stock"])
            if item.get("low"):
                stock.setForeground(QBrush(QColor(T.DANGER)))
                stock.setFont(ui_font(9, bold=True))
            rate = QTableWidgetItem(
                f"{format_inr_indian(item['rate'])} {item['unit']}"
            )
            rate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rate.setFont(ui_font(9, bold=True))
            table.setItem(r, 0, code)
            table.setItem(r, 1, name)
            table.setItem(r, 2, cat)
            table.setItem(r, 3, stock)
            table.setItem(r, 4, rate)

            bill = QPushButton("Bill")
            bill.setCursor(Qt.PointingHandCursor)
            bill.setFixedHeight(24)
            bill.setStyleSheet(
                f"QPushButton {{ background: {_PRIMARY}; color: white; border: none; "
                f"border-radius: 4px; padding: 2px 10px; font-size: 10px; font-weight: 700; }}"
                f"QPushButton:hover {{ background: {_PRIMARY_HOVER}; }}"
            )
            bill.clicked.connect(lambda *_: self._navigate("sales"))
            wrap = QWidget()
            wl = QHBoxLayout(wrap)
            wl.setContentsMargins(6, 0, 6, 0)
            wl.addStretch()
            wl.addWidget(bill)
            wl.addStretch()
            table.setCellWidget(r, 5, wrap)

    def _filter_lookup(self, text: str):
        q = text.strip().lower()
        if not q:
            rows = D.FAST_LOOKUP_ITEMS
        else:
            rows = [
                i for i in D.FAST_LOOKUP_ITEMS
                if q in i["code"].lower() or q in i["name"].lower() or q in i["category"].lower()
            ]
        self._fill_lookup_table(rows)
        self._lookup_table.setMinimumHeight(max(120, 42 * max(len(rows), 1) + 40))
        self._lookup_table.setMaximumHeight(max(160, 42 * max(len(rows), 1) + 44))

    # ── Alerts column ────────────────────────────────────────
    def _alerts_column(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._low_stock_alert())
        lay.addWidget(self._pending_overdue())
        lay.addStretch()
        return wrap

    def _section_head(self, title: str, badge: str, badge_danger=False) -> QWidget:
        head = QFrame()
        head.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(12, 8, 12, 8)
        ttl = QLabel(title)
        ttl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        badge_lbl = QLabel(badge)
        if badge_danger:
            badge_lbl.setStyleSheet(
                f"color: #b91c1c; background: {T.DANGER_BG}; border: 1px solid #fecaca; "
                f"border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700;"
            )
        else:
            badge_lbl.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; background: {T.HEADER_BAND}; "
                f"border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 600;"
            )
        hl.addWidget(ttl)
        hl.addStretch()
        hl.addWidget(badge_lbl)
        return head

    def _low_stock_alert(self) -> QFrame:
        box = _card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(
            self._section_head(
                "Low Stock Alert (Immediate Reorder)",
                f"{len(D.LOW_STOCK_ALERTS)} SKUs",
                badge_danger=True,
            )
        )
        body = QVBoxLayout()
        body.setContentsMargins(10, 10, 10, 10)
        body.setSpacing(8)
        for item in D.LOW_STOCK_ALERTS:
            row = QFrame()
            row.setStyleSheet(
                f"QFrame {{ background: #F8FAFC; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
            )
            rl = QVBoxLayout(row)
            rl.setContentsMargins(10, 8, 10, 8)
            rl.setSpacing(2)
            name = QLabel(item["name"])
            name.setStyleSheet(
                f"font-weight: 700; font-size: 12px; color: {T.TEXT_PRIMARY}; "
                f"border: none; background: transparent;"
            )
            note = QLabel(item["note"])
            note.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
                f"border: none; background: transparent;"
            )
            stock = QLabel(item["stock"])
            stock.setStyleSheet(
                f"color: #b91c1c; background: {T.DANGER_BG}; border: 1px solid #fecaca; "
                f"border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: 700;"
            )
            rl.addWidget(name)
            rl.addWidget(note)
            rl.addWidget(stock, 0, Qt.AlignLeft)
            body.addWidget(row)

        po = QPushButton("Create Purchase PO  →")
        po.setCursor(Qt.PointingHandCursor)
        po.setStyleSheet(
            f"QPushButton {{ background: {_PRIMARY}; color: white; border: none; "
            f"border-radius: 4px; padding: 8px 12px; font-size: 12px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: {_PRIMARY_HOVER}; }}"
        )
        po.clicked.connect(lambda: self._navigate("purchase"))
        body.addWidget(po)
        lay.addLayout(body)
        return box

    def _pending_overdue(self) -> QFrame:
        box = _card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self._section_head("Pending Overdue Collections", "Dr Ledger Audit"))

        body = QVBoxLayout()
        body.setContentsMargins(10, 10, 10, 10)
        body.setSpacing(8)
        for row in D.PENDING_OVERDUE:
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{ background: #F8FAFC; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
            )
            rl = QVBoxLayout(card)
            rl.setContentsMargins(10, 8, 10, 8)
            rl.setSpacing(4)

            top = QHBoxLayout()
            name = QLabel(row["party"])
            name.setStyleSheet(
                f"font-weight: 700; font-size: 12px; color: {T.TEXT_PRIMARY}; "
                f"border: none; background: transparent;"
            )
            amt = QLabel(format_inr_indian(row["amount"]).replace(".00", ""))
            amt.setStyleSheet(
                f"font-weight: 700; font-size: 12px; color: {T.TEXT_PRIMARY}; "
                f"border: none; background: transparent;"
            )
            top.addWidget(name)
            top.addStretch()
            top.addWidget(amt)
            rl.addLayout(top)

            note = QLabel(row["note"])
            note.setStyleSheet(
                f"color: {T.DANGER}; font-size: 10px; font-weight: 600; "
                f"border: none; background: transparent;"
            )
            rl.addWidget(note)

            actions = QHBoxLayout()
            actions.setSpacing(6)
            for act in row["actions"]:
                b = QPushButton(act)
                b.setCursor(Qt.PointingHandCursor)
                b.setFixedHeight(24)
                if act in ("Call", "WA"):
                    b.setStyleSheet(
                        f"QPushButton {{ background: {T.SURFACE}; color: {_PRIMARY}; "
                        f"border: 1px solid {T.BORDER}; border-radius: 4px; "
                        f"padding: 2px 10px; font-size: 10px; font-weight: 700; }}"
                        f"QPushButton:hover {{ background: {T.ACCENT_SOFT}; }}"
                    )
                else:
                    b.setStyleSheet(
                        f"QPushButton {{ background: {T.WARNING_BG}; color: #b45309; "
                        f"border: 1px solid #fde68a; border-radius: 4px; "
                        f"padding: 2px 10px; font-size: 10px; font-weight: 700; }}"
                        f"QPushButton:hover {{ background: #fef3c7; }}"
                    )
                b.clicked.connect(
                    lambda *_, a=act, p=row["party"]: toast(self, f"{a} — {p}")
                )
                actions.addWidget(b)
            actions.addStretch()
            rl.addLayout(actions)
            body.addWidget(card)
        lay.addLayout(body)
        return box

    # ── Hotkeys footer ───────────────────────────────────────
    def _hotkeys_bar(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: #0F172A; border: 1px solid #1e293b; "
            f"border-radius: {T.CARD_RADIUS}px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)

        title = QLabel("QUICK POS HOTKEYS:")
        title.setStyleSheet(
            "color: #94a3b8; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; "
            "border: none; background: transparent;"
        )
        lay.addWidget(title)

        for key, label in (
            ("F2", "New Sale"),
            ("F3", "New Purchase"),
            ("F1", "Cash Flow"),
            ("F4", "Add Party"),
            ("F8", "Daybook"),
            ("F10", "Refresh Dashboard"),
        ):
            chip = QLabel(key)
            chip.setStyleSheet(
                "background: #1e293b; color: #e2e8f0; border: 1px solid #334155; "
                "border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: 700;"
            )
            text = QLabel(label)
            text.setStyleSheet(
                "color: #cbd5e1; font-size: 10px; border: none; background: transparent;"
            )
            lay.addWidget(chip)
            lay.addWidget(text)
            lay.addSpacing(6)

        lay.addStretch()
        online_dot = QFrame()
        online_dot.setFixedSize(10, 10)
        online_dot.setStyleSheet(
            f"background: {T.SUCCESS}; border-radius: 5px; border: none;"
        )
        online = QLabel("Online · 0 ms Latency")
        online.setStyleSheet(
            "color: #94a3b8; font-size: 10px; border: none; background: transparent;"
        )
        lay.addWidget(online_dot)
        lay.addWidget(online)
        return box
