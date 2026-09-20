"""Dashboard — flat KPI boxes + recent transactions feed."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHeaderView,
    QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import format_inr, ui_font


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
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
        items = [
            ("Today's Sales", format_inr(D.DASHBOARD_KPI["todays_sales"]), T.ACCENT),
            ("Today's Purchases", format_inr(D.DASHBOARD_KPI["todays_purchases"]), T.TEXT_PRIMARY),
            ("Cash in Hand", format_inr(D.DASHBOARD_KPI["cash_in_hand"]), T.SUCCESS),
            ("Receivables Due", format_inr(D.DASHBOARD_KPI["receivables_due"]), T.DANGER),
            ("Low Stock Alert", str(D.DASHBOARD_KPI["low_stock_count"]), T.WARNING),
        ]
        for i, (label, value, color) in enumerate(items):
            kpi.addWidget(self._kpi_box(label, value, color), 0, i)
            kpi.setColumnStretch(i, 1)
        root.addLayout(kpi)

        panel = QFrame()
        panel.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; }}"
        )
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(0)

        section_bar = QFrame()
        section_bar.setStyleSheet(
            f"QFrame {{ background: {T.HEADER_BAND}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        sbl = QHBoxLayout(section_bar)
        sbl.setContentsMargins(12, 8, 12, 8)
        section = QLabel("Recent Transactions")
        section.setStyleSheet(
            f"font-size: {T.FONT_SIZE_UI}pt; font-weight: bold; color: {T.TEXT_PRIMARY};"
        )
        sbl.addWidget(section)
        sbl.addStretch()
        pl.addWidget(section_bar)

        table = QTableWidget(len(D.RECENT_TXNS), 5)
        table.setHorizontalHeaderLabels(
            ["Date", "Type", "Document No.", "Party Name", "Amount"]
        )
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setShowGrid(True)
        table.setFont(ui_font(T.FONT_SIZE_GRID))
        table.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.setColumnWidth(0, 110)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 120)
        table.setColumnWidth(4, 140)
        table.setStyleSheet(
            f"QTableWidget {{ border: none; font-family: '{getattr(T, 'FONT_UI_RESOLVED', T.FONT_UI)}'; "
            f"font-size: {T.FONT_SIZE_GRID}pt; }}"
        )

        for r, txn in enumerate(D.RECENT_TXNS):
            vals = [txn["date"], txn["type"], txn["doc"], txn["party"], format_inr(txn["amount"])]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFont(ui_font(T.FONT_SIZE_GRID, bold=(c == 4)))
                if c == 4:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if c == 1:
                    color = {
                        "Sale": T.ACCENT,
                        "Purchase": T.TEXT_PRIMARY,
                        "Receipt": T.SUCCESS,
                        "Payment": T.WARNING,
                    }.get(txn["type"], T.TEXT_SECONDARY)
                    from PyQt5.QtGui import QBrush, QColor
                    it.setForeground(QBrush(QColor(color)))
                table.setItem(r, c, it)

        pl.addWidget(table, stretch=1)
        root.addWidget(panel, stretch=1)

        low = [p for p in D.PRODUCTS if p["stock"] <= p["min_stock"]]
        if low:
            warn = QFrame()
            warn.setStyleSheet(
                f"QFrame {{ background: #FFF7ED; border: 1px solid #FDBA74; }}"
            )
            wl = QHBoxLayout(warn)
            wl.setContentsMargins(10, 6, 10, 6)
            hint = QLabel(
                "Low Stock Alert: "
                + "  ·  ".join(f"{p['name']} ({p['stock']})" for p in low)
            )
            hint.setStyleSheet(
                f"color: {T.WARNING}; font-size: {T.FONT_SIZE_SHORTCUT}pt; font-weight: bold;"
            )
            wl.addWidget(hint)
            root.addWidget(warn)

    def _kpi_box(self, label: str, value: str, color: str) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background-color: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-left: 4px solid {color}; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 12, 12)
        lay.setSpacing(6)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt; border: none;"
        )
        val = QLabel(value)
        val.setFont(ui_font(T.FONT_SIZE_GRAND, bold=True))
        val.setStyleSheet(f"color: {color}; border: none; font-size: {T.FONT_SIZE_GRAND}pt;")
        lay.addWidget(lbl)
        lay.addWidget(val)
        return box
