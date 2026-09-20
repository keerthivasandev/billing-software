"""Shared 4-zone transaction entry — dense layout matching Windows ERP target."""

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QBrush, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QRadioButton, QButtonGroup, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import (
    balance_label, field_label, format_inr, labeled_field, make_button,
    mono_font, toast,
)

GRID_COLS = [
    "#", "Item Group", "Product / Item", "Qty", "Unit", "Rate",
    "Amount", "Disc %", "GST %", "Line Total", "WH", "✕",
]

COL_WIDTHS = [32, 110, 200, 56, 48, 72, 84, 58, 52, 92, 90, 32]
READONLY_COLS = {0, 6, 9}


class TransactionEntryScreen(QWidget):
    def __init__(self, mode="sales", parent=None):
        super().__init__(parent)
        self.mode = mode
        self._party_balances = {p["name"]: p["balance"] for p in D.PARTIES}
        self._build()
        self._wire_shortcuts()
        self._recalc()

    @property
    def doc_prefix(self):
        return "SI" if self.mode == "sales" else "PI"

    @property
    def party_label(self):
        return "Customer" if self.mode == "sales" else "Supplier"

    @property
    def amount_label(self):
        return "Amount Received" if self.mode == "sales" else "Amount Paid"

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(3)

        root.addWidget(self._build_zone_a())
        root.addWidget(self._build_zone_b())
        root.addWidget(self._build_zone_c(), stretch=1)
        root.addWidget(self._build_zone_d())

    # ---- ZONE A: compact single-band header ----
    def _build_zone_a(self) -> QFrame:
        zone = QFrame()
        zone.setObjectName("zoneA")
        zone.setStyleSheet(
            f"QFrame#zoneA {{ background-color: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; }}"
        )
        zone.setMinimumHeight(T.HEADER_ZONE_H)
        # Prefer grow over clip when DPI / long labels need space
        zone.setMaximumHeight(120)


        lay = QVBoxLayout(zone)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(4)

        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.doc_no = QLineEdit(f"{self.doc_prefix}-{1043 if self.mode == 'sales' else 389}")
        self.doc_no.setFixedWidth(110)

        self.doc_date = QDateEdit(QDate.currentDate())
        self.doc_date.setCalendarPopup(True)
        self.doc_date.setDisplayFormat("dd-MM-yyyy")
        self.doc_date.setMinimumWidth(130)

        self.party = QComboBox()
        self.party.setEditable(True)
        self.party.setInsertPolicy(QComboBox.NoInsert)
        parties = [p for p in D.PARTIES if self._party_matches(p)]
        for p in parties:
            self.party.addItem(p["name"])
        self.party.currentTextChanged.connect(self._on_party_changed)
        self.party.setMinimumWidth(200)

        bal0 = parties[0]["balance"] if parties else 0
        self.balance_lbl = balance_label(bal0)
        self._on_party_changed(parties[0]["name"] if parties else "")

        btn_last = make_button("View Last Transaction")
        btn_hist = make_button("History")

        row1.addWidget(labeled_field("Invoice No.", self.doc_no))
        row1.addWidget(labeled_field("Date", self.doc_date))
        row1.addWidget(labeled_field(f"Party Name ({self.party_label})", self.party), stretch=1)
        row1.addWidget(self.balance_lbl, alignment=Qt.AlignBottom)
        row1.addWidget(btn_last, alignment=Qt.AlignBottom)
        row1.addWidget(btn_hist, alignment=Qt.AlignBottom)
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(8)
        self.pay_mode = QComboBox()
        self.pay_mode.addItems(["Credit", "Counter Cash", "UPI", "Bank"])
        self.pay_mode.setFixedWidth(110)
        self.vehicle = QLineEdit()
        self.vehicle.setPlaceholderText("Vehicle No.")
        self.vehicle.setFixedWidth(120)
        self.ref_no = QLineEdit()
        self.ref_no.setPlaceholderText("Reference / Order No.")
        row2.addWidget(labeled_field("Payment Mode", self.pay_mode))
        row2.addWidget(labeled_field("Vehicle No.", self.vehicle))
        ref_label = (
            "Purchase Order Ref." if self.mode == "purchase" else "Reference / Order No."
        )
        row2.addWidget(labeled_field(ref_label, self.ref_no), stretch=1)
        row2.addStretch()
        lay.addLayout(row2)
        return zone

    def _party_matches(self, p):
        if self.mode == "sales":
            return p["type"] in ("Customer", "Both")
        return p["type"] in ("Supplier", "Both")

    def _on_party_changed(self, name):
        bal = self._party_balances.get(name, 0.0)
        if bal > 0:
            text, bg, fg, border = f"Rs. {bal:,.2f} DUE", "#FEE2E2", T.DANGER, T.DANGER
        elif bal < 0:
            text, bg, fg, border = (
                f"Rs. {abs(bal):,.2f} CREDIT", "#DCFCE7", T.SUCCESS, T.SUCCESS
            )
        else:
            text, bg, fg, border = "Rs. 0.00", T.HEADER_BAND, T.TEXT_SECONDARY, T.BORDER
        self.balance_lbl.setText(text)
        self.balance_lbl.setStyleSheet(
            f"color: {fg}; background: {bg}; border: 1px solid {border}; "
            f"padding: 3px 10px; font-weight: bold; font-size: {T.FONT_SIZE_UI}pt;"
        )

    # ---- ZONE B: fast input strip ----
    def _build_zone_b(self) -> QFrame:
        zone = QFrame()
        zone.setObjectName("zoneB")
        zone.setStyleSheet(
            f"QFrame#zoneB {{ background-color: {T.HEADER_BAND}; "
            f"border: 1px solid {T.BORDER}; border-left: 3px solid {T.ACCENT}; }}"
        )
        zone.setMinimumHeight(T.FAST_STRIP_H)
        zone.setMaximumHeight(70)


        lay = QHBoxLayout(zone)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(6)

        self.item_search = QComboBox()
        self.item_search.setEditable(True)
        self.item_search.setInsertPolicy(QComboBox.NoInsert)
        self.item_search.addItem("")
        for p in D.PRODUCTS:
            self.item_search.addItem(f"{p['sku']} — {p['name']}", p)
        self.item_search.setMinimumWidth(240)

        self.qty = QDoubleSpinBox()
        self.qty.setRange(0.001, 999999)
        self.qty.setDecimals(3)
        self.qty.setValue(1)
        self.qty.setFixedWidth(72)

        self.rate = QDoubleSpinBox()
        self.rate.setRange(0, 9999999)
        self.rate.setDecimals(2)
        self.rate.setFixedWidth(90)

        self.wh_quick = QComboBox()
        self.wh_quick.addItems(D.WAREHOUSES)
        self.wh_quick.setFixedWidth(120)

        self.btn_add = make_button("+ Add Line", "primary", "[Enter]")
        self.btn_add.setMinimumWidth(120)
        self.btn_add.clicked.connect(self._add_line)
        self.item_search.currentIndexChanged.connect(self._on_item_picked)

        lay.addWidget(labeled_field("Product / Item", self.item_search, "[F2]"), stretch=2)
        lay.addWidget(labeled_field("Qty", self.qty))
        lay.addWidget(labeled_field("Rate", self.rate))
        lay.addWidget(labeled_field("Warehouse", self.wh_quick))
        # Align button with input row (below label)
        btn_wrap = QWidget()
        bw = QVBoxLayout(btn_wrap)
        bw.setContentsMargins(0, 0, 0, 0)
        bw.setSpacing(2)
        bw.addWidget(QLabel(""))  # spacer matching label height
        bw.addWidget(self.btn_add)
        lay.addWidget(btn_wrap)
        return zone

    def _on_item_picked(self, idx):
        data = self.item_search.itemData(idx)
        if data:
            self.rate.setValue(float(data.get("sale_rate", data.get("rate", 0))))
            self.qty.setFocus()
            self.qty.selectAll()

    # ---- ZONE C: grid fills remaining space ----
    def _build_zone_c(self) -> QFrame:
        zone = QFrame()
        zone.setObjectName("zoneC")
        zone.setStyleSheet(
            f"QFrame#zoneC {{ background-color: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; }}"
        )
        zone.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout(zone)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        rows = T.EMPTY_GRID_ROWS
        self.grid = QTableWidget(rows, len(GRID_COLS))
        self.grid.setHorizontalHeaderLabels(GRID_COLS)
        self.grid.setAlternatingRowColors(True)
        self.grid.verticalHeader().setVisible(False)
        self.grid.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.grid.setSelectionMode(QAbstractItemView.SingleSelection)
        self.grid.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
        )
        self.grid.setFont(mono_font(T.FONT_SIZE_GRID))
        self.grid.setShowGrid(True)
        self.grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hh = self.grid.horizontalHeader()
        hh.setStretchLastSection(False)
        hh.setMinimumHeight(26)
        for i, w in enumerate(COL_WIDTHS):
            self.grid.setColumnWidth(i, w)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)

        self.grid.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
        self.grid.verticalHeader().setMinimumSectionSize(T.GRID_ROW_H)

        for r in range(rows):
            self._init_empty_row(r)

        self.grid.itemChanged.connect(self._on_cell_changed)
        self.grid.cellClicked.connect(self._on_cell_clicked)
        lay.addWidget(self.grid)
        return zone

    def _init_empty_row(self, row: int):
        self.grid.blockSignals(True)
        for c, _ in enumerate(GRID_COLS):
            item = QTableWidgetItem("")
            if c == 0:
                item.setText(str(row + 1))
                item.setFlags(Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignCenter)
            elif c in READONLY_COLS:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setBackground(QBrush(QColor(T.READONLY_CELL)))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setFont(mono_font(T.FONT_SIZE_GRID, bold=(c == 9)))
            elif c in (3, 5, 7, 8):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setFont(mono_font(T.FONT_SIZE_GRID))
            elif c == 11:
                item.setText("✕")
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QBrush(QColor(T.DANGER)))
            self.grid.setItem(row, c, item)
        self.grid.blockSignals(False)

    def _on_cell_clicked(self, row, col):
        if col == 11:
            name = self.grid.item(row, 2)
            if name and name.text().strip():
                self._init_empty_row(row)
                self._recalc()

    def _add_line(self):
        idx = self.item_search.currentIndex()
        data = self.item_search.itemData(idx)
        if not data:
            toast(self, "Select a Product / Item first. [F2]")
            self.item_search.setFocus()
            return

        target = None
        for r in range(self.grid.rowCount()):
            it = self.grid.item(r, 2)
            if it is None or not it.text().strip():
                target = r
                break
        if target is None:
            target = self.grid.rowCount()
            self.grid.insertRow(target)
            self._init_empty_row(target)

        qty = self.qty.value()
        rate = self.rate.value()
        amount = qty * rate
        gst = float(data["gst"])
        disc = 0.0
        line_total = amount * (1 - disc / 100) * (1 + gst / 100)

        self.grid.blockSignals(True)
        vals = {
            1: data["group"],
            2: data["name"],
            3: f"{qty:g}",
            4: data["unit"],
            5: f"{rate:.2f}",
            6: f"{amount:.2f}",
            7: f"{disc:.2f}",
            8: f"{gst:.0f}",
            9: f"{line_total:.2f}",
            10: self.wh_quick.currentText(),
        }
        for c, v in vals.items():
            it = self.grid.item(target, c)
            if it is None:
                it = QTableWidgetItem(v)
                self.grid.setItem(target, c, it)
            else:
                it.setText(v)
            if c in (3, 5, 6, 7, 8, 9):
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                it.setFont(mono_font(T.FONT_SIZE_GRID, bold=(c == 9)))
            if c in READONLY_COLS:
                it.setBackground(QBrush(QColor(T.READONLY_CELL)))
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.grid.blockSignals(False)

        self._recalc()
        self.item_search.setCurrentIndex(0)
        self.qty.setValue(1)
        self.item_search.setFocus()

    def _on_cell_changed(self, item: QTableWidgetItem):
        if item.column() in (3, 5, 7, 8):
            self._recalc_row(item.row())
            self._recalc()

    def _recalc_row(self, row: int):
        def num(col, default=0.0):
            it = self.grid.item(row, col)
            if not it or not it.text().strip():
                return default
            try:
                return float(it.text().replace(",", ""))
            except ValueError:
                return default

        qty, rate = num(3), num(5)
        disc, gst = num(7), num(8)
        amount = qty * rate
        line_total = amount * (1 - disc / 100) * (1 + gst / 100)

        self.grid.blockSignals(True)
        for c, v, bold in ((6, amount, False), (9, line_total, True)):
            it = self.grid.item(row, c)
            if it is None:
                it = QTableWidgetItem()
                self.grid.setItem(row, c, it)
            it.setText(f"{v:.2f}")
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            it.setFont(mono_font(T.FONT_SIZE_GRID, bold=bold))
            it.setBackground(QBrush(QColor(T.READONLY_CELL)))
            it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.grid.blockSignals(False)

    # ---- ZONE D: totals + settlement + actions ----
    def _build_zone_d(self) -> QFrame:
        zone = QFrame()
        zone.setObjectName("zoneD")
        zone.setStyleSheet(
            f"QFrame#zoneD {{ background-color: {T.HEADER_BAND}; "
            f"border: 1px solid {T.BORDER}; border-top: 2px solid {T.BORDER_STRONG}; }}"
        )
        zone.setMinimumHeight(T.FOOTER_ZONE_H)

        outer = QVBoxLayout(zone)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(28)

        summary = QGridLayout()
        summary.setHorizontalSpacing(16)
        summary.setVerticalSpacing(6)
        summary.setColumnMinimumWidth(0, 120)
        summary.setColumnMinimumWidth(1, 130)

        self.lbl_subtotal = QLabel("Rs. 0.00")
        self.lbl_discount = QLabel("Rs. 0.00")
        self.lbl_tax = QLabel("Rs. 0.00")
        self.charges = QDoubleSpinBox()
        self.charges.setRange(0, 999999)
        self.charges.setDecimals(2)
        self.charges.setPrefix("Rs. ")
        self.charges.setMinimumWidth(120)
        self.charges.valueChanged.connect(self._recalc)
        self.round_off = QDoubleSpinBox()
        self.round_off.setRange(-10, 10)
        self.round_off.setDecimals(2)
        self.round_off.setSingleStep(0.5)
        self.round_off.setMinimumWidth(120)
        self.round_off.valueChanged.connect(self._recalc)

        self.lbl_grand = QLabel("Rs. 0.00")
        self.lbl_grand.setFont(mono_font(T.FONT_SIZE_GRAND, bold=True))
        self.lbl_grand.setStyleSheet(
            f"color: white; background: {T.GRAND_TOTAL_BG}; "
            f"padding: 6px 12px; border-radius: {T.RADIUS}px; "
            f"border: 1px solid {T.GRAND_TOTAL_BG};"
        )
        self.lbl_grand.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_grand.setMinimumWidth(140)
        self.lbl_grand.setMinimumHeight(32)

        for lbl in (self.lbl_subtotal, self.lbl_discount, self.lbl_tax):
            lbl.setFont(mono_font(T.FONT_SIZE_GRID))
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setMinimumWidth(120)

        rows = [
            ("Subtotal", self.lbl_subtotal),
            ("Total Discount", self.lbl_discount),
            ("Total Tax (GST)", self.lbl_tax),
            ("Freight & Handling", self.charges),
            ("Round Off", self.round_off),
        ]
        for i, (label, w) in enumerate(rows):
            summary.addWidget(field_label(label), i, 0, Qt.AlignVCenter)
            summary.addWidget(w, i, 1, Qt.AlignVCenter)

        gt_lbl = QLabel("Grand Total")
        gt_lbl.setStyleSheet(
            f"font-size: {T.FONT_SIZE_UI}pt; font-weight: bold; color: {T.TEXT_PRIMARY};"
        )
        summary.addWidget(gt_lbl, len(rows), 0, Qt.AlignVCenter)
        summary.addWidget(self.lbl_grand, len(rows), 1, Qt.AlignVCenter)
        top.addLayout(summary)

        top.addStretch(1)

        pay = QGridLayout()
        pay.setHorizontalSpacing(12)
        pay.setVerticalSpacing(8)
        pay.setColumnMinimumWidth(0, 110)

        settle_title = QLabel("Settlement")
        settle_title.setStyleSheet(
            f"font-size: {T.FONT_SIZE_UI}pt; font-weight: bold; color: {T.TEXT_PRIMARY};"
        )
        pay.addWidget(settle_title, 0, 0, 1, 2)

        self.amount_recv = QDoubleSpinBox()
        self.amount_recv.setRange(0, 99999999)
        self.amount_recv.setDecimals(2)
        self.amount_recv.setPrefix("Rs. ")
        self.amount_recv.setMinimumWidth(130)
        self.amount_recv.valueChanged.connect(self._recalc)

        self.lbl_due = QLabel("Rs. 0.00")
        self.lbl_due.setFont(mono_font(T.FONT_SIZE_UI, bold=True))
        self.lbl_due.setMinimumWidth(130)

        self.mode_group = QButtonGroup(self)
        mode_row = QHBoxLayout()
        mode_row.setSpacing(14)
        for i, m in enumerate(["Cash", "Credit", "UPI", "Bank"]):
            rb = QRadioButton(m)
            if i == 0:
                rb.setChecked(True)
            self.mode_group.addButton(rb, i)
            mode_row.addWidget(rb)
        mode_row.addStretch()
        self.mode_group.buttonClicked.connect(self._on_pay_mode)

        self.due_date = QDateEdit(QDate.currentDate().addDays(30))
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("dd-MM-yyyy")
        self.due_date.setMinimumWidth(130)
        self.due_date_wrap = labeled_field("Due Date", self.due_date)
        self.due_date_wrap.setVisible(False)

        pay.addWidget(field_label(self.amount_label), 1, 0, Qt.AlignVCenter)
        pay.addWidget(self.amount_recv, 1, 1, Qt.AlignVCenter)
        pay.addWidget(field_label("Balance Due"), 2, 0, Qt.AlignVCenter)
        pay.addWidget(self.lbl_due, 2, 1, Qt.AlignVCenter)
        pay.addWidget(field_label("Payment Mode"), 3, 0, Qt.AlignVCenter)
        pay.addLayout(mode_row, 3, 1)
        pay.addWidget(self.due_date_wrap, 4, 0, 1, 2)
        top.addLayout(pay)

        outer.addLayout(top)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()
        self.btn_draft = make_button("Save as Draft")
        self.btn_preview = make_button("Print Preview", shortcut="[Ctrl+P]")
        self.btn_save_print = make_button("Save & Print", "primary", "[F9]")
        self.btn_save_new = make_button("Save & New", "primary", "[F10]")
        self.btn_cancel = make_button("Cancel", "ghost", "[Esc]")

        self.btn_save_new.clicked.connect(lambda: self._save("new"))
        self.btn_save_print.clicked.connect(lambda: self._save("print"))
        self.btn_draft.clicked.connect(lambda: self._save("draft"))
        self.btn_cancel.clicked.connect(self._cancel)

        for b in (
            self.btn_draft,
            self.btn_preview,
            self.btn_save_print,
            self.btn_save_new,
            self.btn_cancel,
        ):
            actions.addWidget(b)
        outer.addLayout(actions)
        return zone

    def _on_pay_mode(self, btn):
        self.due_date_wrap.setVisible(btn.text() == "Credit")

    def _recalc(self):
        subtotal = discount = tax = 0.0
        for r in range(self.grid.rowCount()):
            name = self.grid.item(r, 2)
            if not name or not name.text().strip():
                continue

            def num(col):
                it = self.grid.item(r, col)
                try:
                    return float(it.text().replace(",", "")) if it and it.text() else 0.0
                except ValueError:
                    return 0.0

            amount = num(6)
            disc_pct = num(7)
            gst_pct = num(8)
            disc_amt = amount * disc_pct / 100
            taxable = amount - disc_amt
            tax_amt = taxable * gst_pct / 100
            subtotal += amount
            discount += disc_amt
            tax += tax_amt

        charges = self.charges.value()
        round_off = self.round_off.value()
        grand = subtotal - discount + tax + charges + round_off

        self.lbl_subtotal.setText(format_inr(subtotal))
        self.lbl_discount.setText(format_inr(discount))
        self.lbl_tax.setText(format_inr(tax))
        self.lbl_grand.setText(format_inr(grand))

        due = grand - self.amount_recv.value()
        self.lbl_due.setText(format_inr(due))
        color = (
            T.DANGER if due > 0.009
            else T.SUCCESS if due < -0.009
            else T.TEXT_PRIMARY
        )
        self.lbl_due.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: {T.FONT_SIZE_UI}pt;"
        )

    def _save(self, kind):
        toast(
            self,
            f"Saved {self.doc_no.text()} ({kind}) · {self.lbl_grand.text()}",
        )
        if kind == "new":
            self._clear_form()

    def _cancel(self):
        self._clear_form()
        toast(self, "Entry cleared.")

    def _clear_form(self):
        for r in range(self.grid.rowCount()):
            self._init_empty_row(r)
        self.charges.setValue(0)
        self.round_off.setValue(0)
        self.amount_recv.setValue(0)
        self._recalc()
        self.item_search.setFocus()

    def _wire_shortcuts(self):
        QShortcut(QKeySequence("F2"), self, activated=lambda: self.item_search.setFocus())
        QShortcut(QKeySequence("F9"), self, activated=lambda: self._save("print"))
        QShortcut(QKeySequence("F10"), self, activated=lambda: self._save("new"))
        QShortcut(
            QKeySequence("Ctrl+P"),
            self,
            activated=lambda: toast(self, "Print preview ready (thermal / tax)."),
        )
        QShortcut(QKeySequence("Esc"), self, activated=self._cancel)
        QShortcut(QKeySequence("Return"), self.btn_add, activated=self._add_line)

    def focus_entry(self):
        self.item_search.setFocus()
