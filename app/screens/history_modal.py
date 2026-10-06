"""Stitch — Sales / Purchase History modal [Alt+H]."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import combo_dropdown_qss, icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.55)"


class PartyHistoryDialog(QDialog):
    """Full party history overlay — Stitch Sales/Purchase History modal."""

    def __init__(self, mode: str = "sales", party_name: str = "", parent=None):
        super().__init__(parent)
        self.mode = mode  # sales | purchase
        self.party_name = party_name
        self.selected_rate = None
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._backdrop = QFrame()
        self._backdrop.setObjectName("histBackdrop")
        self._backdrop.setStyleSheet(
            f"QFrame#histBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(self._backdrop)
        shell.setContentsMargins(28, 24, 28, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("histCard")
        self._card.setMinimumWidth(1320)
        self._card.setMaximumWidth(1560)
        self._card.setMinimumHeight(720)
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._card.setStyleSheet(
            f"QFrame#histCard {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: 8px; }}"
        )
        card = QVBoxLayout(self._card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)
        card.addWidget(self._header())
        card.addWidget(self._toolbar())
        card.addWidget(self._table(), stretch=1)
        card.addWidget(self._footer())
        self._reload()

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(self._backdrop)
        self._backdrop.mousePressEvent = self._on_backdrop

        QShortcut(QKeySequence("Esc"), self, activated=self.reject)
        QShortcut(QKeySequence("Return"), self, activated=self._apply)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())

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

    def _on_backdrop(self, e):
        if e.button() != Qt.LeftButton:
            return
        if not self._card.geometry().contains(e.position().toPoint()):
            self.reject()

    def _is_sales(self):
        return self.mode == "sales"

    def _rows(self):
        return list(D.SALES_HISTORY if self._is_sales() else D.PURCHASE_HISTORY)

    def _header(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(28, 28)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: {S.R}px; border: none;"
        )
        ic.setPixmap(
            icon_pixmap(
                "receipt_long" if self._is_sales() else "description",
                size=18,
                color=S.PRIMARY,
            )
        )
        lay.addWidget(ic)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        mid.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        if self._is_sales():
            name = self.party_name or "Balaji Electricals & Hardware"
            ttl = QLabel(f"Sales History — {name}")
            badge = S.pill("Active Customer", "success")
            meta = (
                "Customer Code: CUST-0182 · GSTIN: 36ABCDE1234F1Z5 · "
                "Total Lifetime Invoices: 38 · "
                f"<span style='color:{T.DANGER};font-weight:700'>Pending Bal: "
                f"{format_inr_indian(42500)} Dr</span>"
            )
        else:
            name = self.party_name or "Polycab India Ltd (Factory Depot)"
            ttl = QLabel(f"Purchase History — {name}")
            badge = S.pill("Active Vendor", "success")
            meta = (
                "Supplier Code: SUP-0042 · GSTIN: 36AABCP1234F1Z1 · "
                "Total Inward Invoices: 24"
            )
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 15px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        title_row.addWidget(badge)
        title_row.addStretch()
        mid.addLayout(title_row)
        meta_lbl = QLabel(meta)
        meta_lbl.setTextFormat(Qt.RichText)
        meta_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        mid.addWidget(meta_lbl)
        lay.addLayout(mid, stretch=1)

        close = S.action_btn(
            "Close", shortcut="Esc", icon="close", kind="secondary", on_click=self.reject
        )
        lay.addWidget(close)
        return box

    def _toolbar(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(f"QFrame {{ background: {T.SURFACE}; border: none; }}")
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        search_wrap = QFrame()
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.INPUT_BG}; border: 1px solid {T.BORDER}; "
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
        self.search.setPlaceholderText(
            "Search by Invoice No, Item Name, Batch, or HSN... (Ctrl+F)"
            if self._is_sales()
            else "Search by Pur No, Item Name, Batch, or Invoice #..."
        )
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; padding: 7px 0; "
            f"font-size: 12px; color: {T.TEXT_PRIMARY}; }}"
        )
        self.search.textChanged.connect(self._reload)
        sw.addWidget(self.search, stretch=1)
        lay.addWidget(search_wrap, stretch=3)

        self.period = QComboBox()
        self.period.addItems(["Last 6 Months", "Last 12 Months", "This FY", "All Time"])
        self.category = QComboBox()
        self.category.addItems(["All Item Categories", "Wires & Cables", "Switches", "Lighting"])
        for cb in (self.period, self.category):
            cb.setStyleSheet(
                f"""
                QComboBox {{
                    background: {T.SURFACE}; border: 1px solid {T.BORDER};
                    border-radius: {S.R}px; padding: 6px 28px 6px 10px;
                    font-size: 12px; font-weight: 600; min-width: 140px;
                }}
                {combo_dropdown_qss(width=22, background="transparent")}
                """
            )
            cb.currentIndexChanged.connect(self._reload)
            lay.addWidget(cb)

        lay.addStretch()
        lay.addWidget(
            S.action_btn(
                "Export Excel",
                icon="file_download",
                kind="secondary",
                on_click=lambda: toast(self, "Exporting Excel…"),
            )
        )
        lay.addWidget(
            S.action_btn(
                "Print Register",
                icon="print",
                kind="secondary",
                on_click=lambda: toast(self, "Printing register…"),
            )
        )
        return box

    def _table(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(20, 12, 20, 12)
        lay.setSpacing(0)

        if self._is_sales():
            cols = [
                "Inv. No.", "Date", "Vehicle No.", "Item Description", "Qty", "Unit",
                "Rate (₹)", "Disc %", "GST %", "Net Amount (₹)",
            ]
        else:
            cols = [
                "Pur. No.", "Date", "Party Inv #", "Item Description", "Qty", "Unit",
                "Rate (₹)", "Disc %", "GST %", "Net Amount (₹)",
            ]
        self.table = QTableWidget(0, len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setFocusPolicy(Qt.StrongFocus)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        for c in range(len(cols)):
            if c != 3:
                hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        S.apply_table_style(self.table)
        # Extra roomy padding for history modal table
        row_h = max(T.GRID_ROW_H + 8, 46)
        header_h = max(T.TABLE_HEADER_H + 6, 42)
        pad_x = max(T.TABLE_PAD_X + 4, 16)
        pad_y = max(T.TABLE_PAD_Y + 4, 12)
        self.table.verticalHeader().setDefaultSectionSize(row_h)
        self.table.verticalHeader().setMinimumSectionSize(row_h)
        self.table.horizontalHeader().setFixedHeight(header_h)
        self.table.setStyleSheet(
            self.table.styleSheet()
            + f"""
            QHeaderView::section {{
                padding: {pad_y}px {pad_x}px;
            }}
            QTableWidget::item {{
                padding: {pad_y}px {pad_x}px;
            }}
            """
        )
        self.table.cellDoubleClicked.connect(lambda *_: self._apply())
        lay.addWidget(self.table)
        return wrap

    def _footer(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(10)

        rows = self._rows()
        total = sum(r["amount"] for r in rows)
        if self._is_sales():
            summary = (
                f"Showing: {len(rows)} of 38 records  ·  "
                f"Customer Total Billed: <b style='color:{S.PRIMARY}'>"
                f"{format_inr_indian(582450)}</b>  ·  Avg Payment Cycle: 22 Days"
            )
        else:
            summary = (
                f"Showing {len(rows)} of 24 records  ·  "
                f"Supplier Inward Total: <b style='color:{S.PRIMARY}'>"
                f"{format_inr_indian(total if total else 942850)}</b>"
            )
        self.summary = QLabel(summary)
        self.summary.setTextFormat(Qt.RichText)
        self.summary.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        lay.addWidget(self.summary)
        lay.addStretch()
        lay.addWidget(
            S.action_btn("Close", shortcut="Esc", kind="secondary", on_click=self.reject)
        )
        lay.addWidget(
            S.action_btn(
                "Apply Selected Rate",
                shortcut="Enter",
                icon="check_circle",
                kind="primary",
                on_click=self._apply,
            )
        )
        return box

    def _reload(self):
        q = self.search.text().strip().lower()
        rows = []
        for r in self._rows():
            blob = " ".join(str(v) for v in r.values()).lower()
            if q and q not in blob:
                continue
            rows.append(r)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            if self._is_sales():
                vals = [
                    f"#{row['inv']}", row["date"], row.get("vehicle", "—"), row["item"],
                    f"{row['qty']:g}", row["unit"], f"{row['rate']:,.2f}",
                    f"{row['disc']:.1f}", f"{row['gst']:.1f}%",
                    format_inr_indian(row["amount"]),
                ]
            else:
                vals = [
                    f"#{row['inv']}", row["date"], row.get("party_inv", "—"), row["item"],
                    f"{row['qty']:g}", row["unit"], f"{row['rate']:,.2f}",
                    f"{row['disc']:.1f}", f"{row['gst']:.1f}%",
                    format_inr_indian(row["amount"]),
                ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                if c == 0:
                    it.setForeground(QBrush(QColor(S.PRIMARY)))
                    f = it.font()
                    f.setBold(True)
                    it.setFont(f)
                if c in (4, 6, 7, 8, 9):
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if c == 8:
                    it.setForeground(QBrush(QColor(S.PRIMARY)))
                if c in (4, 9):
                    f = it.font()
                    f.setBold(True)
                    it.setFont(f)
                self.table.setItem(i, c, it)

        n = len(rows)
        if not hasattr(self, "summary"):
            return
        if self._is_sales():
            self.summary.setText(
                f"Showing: {n} of 38 records  ·  "
                f"Customer Total Billed: <b style='color:{S.PRIMARY}'>"
                f"{format_inr_indian(582450)}</b>  ·  Avg Payment Cycle: 22 Days"
            )
        else:
            tot = sum(r["amount"] for r in rows)
            self.summary.setText(
                f"Showing {n} of 24 records  ·  "
                f"Supplier Inward Total: <b style='color:{S.PRIMARY}'>"
                f"{format_inr_indian(tot if tot else 942850)}</b>"
            )

    def _apply(self):
        row = self.table.currentRow()
        if row < 0:
            toast(self, "Select a history row first.")
            return
        it = self.table.item(row, 6)
        try:
            self.selected_rate = float((it.text() if it else "0").replace(",", ""))
        except ValueError:
            self.selected_rate = 0.0
        self.accept()
