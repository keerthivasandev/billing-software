"""Dashboard — Zoho Inventory split-grid (KPI + panels, no heavy charts)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QProgressBar, QScrollArea, QTabWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import (
    card_frame, format_inr, growth_pill, section_title, ui_font,
)


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        body = QWidget()
        root = QVBoxLayout(body)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        head = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet(
            f"font-size: {T.FONT_SIZE_TITLE}pt; font-weight: bold; color: {T.TEXT_PRIMARY};"
        )
        sub = QLabel("Today's overview — sales, stock & collections")
        sub.setStyleSheet(f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt;")
        head.addWidget(title)
        head.addStretch()
        head.addWidget(sub)
        root.addLayout(head)

        kpi = QGridLayout()
        kpi.setSpacing(10)
        cards = [
            ("Today's Sales", format_inr(D.DASHBOARD_KPI["todays_sales"]), T.ACCENT),
            ("Today's Purchases", format_inr(D.DASHBOARD_KPI["todays_purchases"]), T.WARNING),
            ("Cash in Hand", format_inr(D.DASHBOARD_KPI["cash_in_hand"]), T.SUCCESS),
            ("Receivables Due", format_inr(D.DASHBOARD_KPI["receivables_due"]), T.DANGER),
        ]
        for i, (label, value, color) in enumerate(cards):
            kpi.addWidget(self._kpi_card(label, value, color), 0, i)
            kpi.setColumnStretch(i, 1)
        root.addLayout(kpi)

        mid = QHBoxLayout()
        mid.setSpacing(12)
        mid.addWidget(self._left_panel(), stretch=3)
        mid.addWidget(self._right_panel(), stretch=2)
        root.addLayout(mid, stretch=1)

        scroll.setWidget(body)
        outer.addWidget(scroll)

    def _kpi_card(self, label: str, value: str, color: str) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-left: 4px solid {color}; border-radius: {T.CARD_RADIUS}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 12, 12)
        lay.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt; "
            f"border: none; background: transparent;"
        )
        val = QLabel(value)
        val.setFont(ui_font(T.FONT_SIZE_GRAND, bold=True))
        val.setStyleSheet(
            f"color: {color}; border: none; background: transparent; "
            f"font-size: {T.FONT_SIZE_GRAND}pt; font-weight: bold;"
        )
        lay.addWidget(lbl)
        lay.addWidget(val)
        return box

    def _left_panel(self) -> QWidget:
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        lay.addWidget(self._top_selling())
        lay.addWidget(self._top_stocked())
        lay.addWidget(self._sales_channel())
        lay.addWidget(self._recent_txns(), stretch=1)
        return wrap

    def _top_selling(self) -> QFrame:
        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)
        lay.addWidget(section_title("Top Selling Items"))
        row = QHBoxLayout()
        row.setSpacing(8)
        for item in D.TOP_SELLING:
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{ background: {T.HEADER_BAND}; border: 1px solid {T.BORDER}; "
                f"border-radius: {T.RADIUS}px; }}"
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 8, 10, 8)
            cl.setSpacing(4)
            name = QLabel(item["name"])
            name.setWordWrap(True)
            name.setStyleSheet(
                f"font-weight: bold; font-size: {T.FONT_SIZE_LABEL}pt; "
                f"border: none; background: transparent;"
            )
            units = QLabel(f"{item['units']} units sold")
            units.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt; "
                f"border: none; background: transparent;"
            )
            cl.addWidget(name)
            cl.addWidget(units)
            cl.addWidget(growth_pill(item["growth"]), alignment=Qt.AlignLeft)
            row.addWidget(card)
        lay.addLayout(row)
        return box

    def _top_stocked(self) -> QFrame:
        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(6)
        lay.addWidget(section_title("Top Stocked Items"))

        tabs = QTabWidget()
        tabs.addTab(self._stock_list(D.TOP_STOCKED_QTY, "qty"), "By Quantity")
        tabs.addTab(self._stock_list(D.TOP_STOCKED_VALUE, "value"), "By Value")
        lay.addWidget(tabs)
        return box

    def _stock_list(self, rows, mode: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)
        for item in rows:
            row = QHBoxLayout()
            name = QLabel(item["name"])
            name.setMinimumWidth(140)
            name.setStyleSheet(f"border: none; font-size: {T.FONT_SIZE_LABEL}pt;")
            bar = QProgressBar()
            bar.setRange(0, int(item["max"]))
            bar.setValue(int(min(item["value"], item["max"])))
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            if mode == "qty":
                val = QLabel(str(int(item["value"])))
            else:
                val = QLabel(format_inr(item["value"]))
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            val.setMinimumWidth(90)
            val.setStyleSheet(
                f"border: none; font-size: {T.FONT_SIZE_LABEL}pt; font-weight: bold;"
            )
            row.addWidget(name)
            row.addWidget(bar, stretch=1)
            row.addWidget(val)
            lay.addLayout(row)
        lay.addStretch()
        return w

    def _sales_channel(self) -> QFrame:
        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)
        lay.addWidget(section_title("Sales By Channel"))
        cash = D.SALES_BY_CHANNEL["counter_cash"]
        credit = D.SALES_BY_CHANNEL["credit"]
        bar = QFrame()
        bar.setFixedHeight(18)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(0)
        left = QFrame()
        left.setStyleSheet(
            f"background: {T.SUCCESS}; border-radius: 3px 0 0 3px; border: none;"
        )
        right = QFrame()
        right.setStyleSheet(
            f"background: {T.ACCENT}; border-radius: 0 3px 3px 0; border: none;"
        )
        bl.addWidget(left, stretch=cash)
        bl.addWidget(right, stretch=credit)
        lay.addWidget(bar)
        legend = QHBoxLayout()
        legend.addWidget(self._legend_dot(T.SUCCESS, f"Counter Cash  {cash}%"))
        legend.addStretch()
        legend.addWidget(self._legend_dot(T.ACCENT, f"Credit Invoices  {credit}%"))
        lay.addLayout(legend)
        return box

    def _legend_dot(self, color: str, text: str) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; border: none;")
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt; border: none;"
        )
        lay.addWidget(dot)
        lay.addWidget(lbl)
        return w

    def _recent_txns(self) -> QFrame:
        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QFrame()
        head.setStyleSheet(
            f"QFrame {{ background: {T.HEADER_BAND}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; "
            f"border-top-left-radius: {T.CARD_RADIUS}px; "
            f"border-top-right-radius: {T.CARD_RADIUS}px; }}"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(12, 8, 12, 8)
        hl.addWidget(section_title("Recent Transactions"))
        hl.addStretch()
        lay.addWidget(head)

        table = QTableWidget(len(D.RECENT_TXNS), 5)
        table.setHorizontalHeaderLabels(
            ["Date", "Type", "Document No.", "Party Name", "Amount"]
        )
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setShowGrid(False)
        table.setFont(ui_font(T.FONT_SIZE_GRID))
        table.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.setColumnWidth(0, 100)
        table.setColumnWidth(1, 90)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(4, 110)
        table.setStyleSheet(f"QTableWidget {{ border: none; border-radius: 0; }}")

        for r, txn in enumerate(D.RECENT_TXNS):
            vals = [txn["date"], txn["type"], txn["doc"], txn["party"], format_inr(txn["amount"])]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 4)))
                if c == 4:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if c == 1:
                    color = {
                        "Sale": T.SUCCESS,
                        "Purchase": T.WARNING,
                        "Receipt": T.ACCENT,
                        "Payment": T.DANGER,
                    }.get(txn["type"], T.TEXT_SECONDARY)
                    it.setForeground(QBrush(QColor(color)))
                    it.setFont(ui_font(T.FONT_SIZE_GRID, bold=True))
                table.setItem(r, c, it)

        lay.addWidget(table)
        return box

    def _right_panel(self) -> QWidget:
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._pending_actions())
        lay.addWidget(self._low_stock_banner())
        lay.addStretch()
        return wrap

    def _pending_actions(self) -> QFrame:
        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(10)
        lay.addWidget(section_title("Pending Actions"))

        for group, color, items in (
            ("Sales", T.ACCENT, D.PENDING_ACTIONS["sales"]),
            ("Purchases", T.WARNING, D.PENDING_ACTIONS["purchases"]),
            ("Inventory", T.DANGER, D.PENDING_ACTIONS["inventory"]),
        ):
            g = QLabel(group.upper())
            g.setStyleSheet(
                f"color: {color}; font-size: {T.FONT_SIZE_SHORTCUT}pt; "
                f"font-weight: bold; border: none; background: transparent;"
            )
            lay.addWidget(g)
            for label, count in items:
                row = QFrame()
                row.setStyleSheet(
                    f"QFrame {{ background: {T.HEADER_BAND}; border: 1px solid {T.BORDER}; "
                    f"border-radius: {T.RADIUS}px; }}"
                )
                rl = QHBoxLayout(row)
                rl.setContentsMargins(10, 6, 10, 6)
                name = QLabel(label)
                name.setStyleSheet("border: none; background: transparent;")
                badge = QLabel(str(count))
                badge.setAlignment(Qt.AlignCenter)
                badge.setFixedWidth(28)
                badge.setStyleSheet(
                    f"background: {T.SURFACE}; color: {color}; border: 1px solid {T.BORDER}; "
                    f"border-radius: 10px; font-weight: bold; "
                    f"font-size: {T.FONT_SIZE_SHORTCUT}pt;"
                )
                rl.addWidget(name)
                rl.addStretch()
                rl.addWidget(badge)
                lay.addWidget(row)
        return box

    def _low_stock_banner(self) -> QFrame:
        low = [p for p in D.PRODUCTS if p["stock"] <= p["min_stock"]]
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.DANGER_BG}; border: 1px solid #fecaca; "
            f"border-left: 4px solid {T.DANGER}; border-radius: {T.CARD_RADIUS}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(4)
        title = QLabel("Low Stock Alert")
        title.setStyleSheet(
            f"color: {T.DANGER}; font-weight: bold; font-size: {T.FONT_SIZE_UI}pt; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(title)
        if not low:
            hint = QLabel("All items are above reorder level.")
            hint.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; border: none; background: transparent;"
            )
            lay.addWidget(hint)
        else:
            text = "  ·  ".join(f"{p['name']} ({int(p['stock'])})" for p in low)
            hint = QLabel(text)
            hint.setWordWrap(True)
            hint.setStyleSheet(
                f"color: {T.TEXT_PRIMARY}; font-size: {T.FONT_SIZE_LABEL}pt; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(hint)
        return box
