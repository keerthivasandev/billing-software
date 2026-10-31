"""2.1 Purchase / 2.2 Sales Entry — Stitch-faithful wholesale invoice screens."""

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap


GRID_COLS = ["#", "Item Name", "Qty", "Rate (₹)", "Disc %", "GST %", "Amount (₹)", "Action"]


class TransactionEntryScreen(QWidget):
    def __init__(self, mode="sales", parent=None):
        super().__init__(parent)
        self.mode = mode  # sales | purchase
        self._party_balances = {p["name"]: p["balance"] for p in D.PARTIES}
        self.setStyleSheet(f"background: {T.BG_CANVAS};")
        self._build()
        self._wire_shortcuts()
        self._recalc()

    @property
    def is_sales(self):
        return self.mode == "sales"

    @property
    def is_estimate(self) -> bool:
        if not self.is_sales or not hasattr(self, "vtype"):
            return False
        return "estimate" in (self.vtype.currentText() or "").lower()

    @property
    def is_sales_return(self) -> bool:
        if not self.is_sales or not hasattr(self, "vtype"):
            return False
        return "return" in (self.vtype.currentText() or "").lower()

    def _voucher_kind(self) -> str:
        """sales | return | estimate | purchase | purchase_return"""
        if not self.is_sales:
            txt = (self.vtype.currentText() if hasattr(self, "vtype") else "").lower()
            return "purchase_return" if "return" in txt else "purchase"
        if self.is_estimate:
            return "estimate"
        if self.is_sales_return:
            return "return"
        return "sales"

    def _build(self):
        self._party_new_mode = False
        self._addr_delivery_wrap = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Stitch sales is a tall page — scroll body + sticky action bar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: {T.BG_CANVAS}; border: none; }}"
            f"QScrollBar:vertical {{ width: 10px; background: transparent; }}"
            f"QScrollBar::handle:vertical {{ background: {T.BORDER_STRONG}; "
            f"border-radius: 4px; min-height: 32px; }}"
        )

        body = QWidget()
        body.setStyleSheet(f"background: {T.BG_CANVAS};")
        root = QVBoxLayout(body)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        root.addWidget(self._title_toolbar())
        root.addWidget(self._header_card())
        if self.is_sales:
            root.addWidget(self._address_section())
        root.addWidget(self._fast_bar())
        root.addWidget(self._items_card(), stretch=1)
        root.addWidget(self._bottom_row())
        root.addStretch(0)

        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)

        # Sticky footer actions (always visible)
        foot = QFrame()
        foot.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        fl = QVBoxLayout(foot)
        fl.setContentsMargins(16, 8, 16, 10)
        fl.setSpacing(0)
        fl.addWidget(self._actions())
        outer.addWidget(foot)

        if self.is_sales:
            self.vtype.currentIndexChanged.connect(self._on_voucher_type_changed)

    # ── Title toolbar (Stitch) ───────────────────────────────
    def _title_toolbar(self) -> QFrame:
        # Stitch: py-1.5 compact ops bar
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 10, 4)
        lay.setSpacing(6)

        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(
            icon_pixmap(
                "receipt_long" if self.is_sales else "shopping_cart",
                size=16,
                color=S.PRIMARY,
            )
        )
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, 0, Qt.AlignVCenter)

        title = QLabel("Sales Entry" if self.is_sales else "Purchase Entry")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(title, 0, Qt.AlignVCenter)
        slash = QLabel("/")
        slash.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        lay.addWidget(slash, 0, Qt.AlignVCenter)
        sub = QLabel("Tax Invoice Entry (F2)" if self.is_sales else "Voucher Entry (F3)")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
        )
        lay.addWidget(sub, 0, Qt.AlignVCenter)
        lay.addStretch()

        # Voucher type chip — override global INPUT_H (32px) so text can center
        chip_h = 28
        vt_wrap = QFrame()
        vt_wrap.setObjectName("vtChip")
        vt_wrap.setFixedHeight(chip_h)
        vt_wrap.setStyleSheet(
            f"QFrame#vtChip {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        vtl = QHBoxLayout(vt_wrap)
        vtl.setContentsMargins(8, 0, 2, 0)
        vtl.setSpacing(4)
        vtl.setAlignment(Qt.AlignVCenter)

        vcap = QLabel("VOUCHER TYPE:")
        vcap.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        vcap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent; "
            f"padding: 0; margin: 0; min-height: 0; max-height: none;"
        )
        vtl.addWidget(vcap, 0, Qt.AlignVCenter)

        self.vtype = QComboBox()
        self.vtype.setObjectName("vtCombo")
        if self.is_sales:
            opts = [
                "Sales Invoice (Standard Wholesale)",
                "Sales Return (Credit Note / Outward)",
                "Estimate (Quotation / Proforma)",
            ]
        else:
            opts = [
                "Purchase (Inward / Receipt)",
                "Purchase Return (Debit Note / Outward)",
            ]
        self.vtype.addItems(opts)
        # Editable + read-only line edit = true vertical text centering (Fusion paints
        # non-editable combo text high; global theme also locks min/max-height to 32px).
        self.vtype.setEditable(True)
        self.vtype.setInsertPolicy(QComboBox.NoInsert)
        le = self.vtype.lineEdit()
        le.setReadOnly(True)
        le.setFocusPolicy(Qt.NoFocus)
        le.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        le.setCursor(QCursor(Qt.ArrowCursor))
        vf = QFont(self.vtype.font())
        vf.setPixelSize(12)
        vf.setWeight(QFont.Weight.DemiBold)
        self.vtype.setFont(vf)
        le.setFont(vf)
        fm = self.vtype.fontMetrics()
        text_w = max(fm.horizontalAdvance(t) for t in opts)
        arrow_w = 18
        self.vtype.setFixedSize(text_w + arrow_w + 10, chip_h - 2)
        self.vtype.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.vtype.setProperty("_caretOk", True)
        from app.widgets.icons import icon_url
        arrow = icon_url("caret-down-dark")
        self.vtype.setStyleSheet(
            f"""
            QComboBox#vtCombo {{
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0px {arrow_w}px 0px 0px;
                margin: 0;
                min-height: {chip_h - 2}px;
                max-height: {chip_h - 2}px;
                font-size: 12px;
                font-weight: 600;
                color: {T.TEXT_PRIMARY};
            }}
            QComboBox#vtCombo:focus {{
                border: none;
                background: transparent;
            }}
            QComboBox#vtCombo QLineEdit {{
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
                min-height: {chip_h - 4}px;
                max-height: {chip_h - 4}px;
                font-size: 12px;
                font-weight: 600;
                color: {T.TEXT_PRIMARY};
                selection-background-color: transparent;
                selection-color: {T.TEXT_PRIMARY};
            }}
            QComboBox#vtCombo::drop-down {{
                subcontrol-origin: border;
                subcontrol-position: center right;
                width: {arrow_w}px;
                border: none;
                background: transparent;
            }}
            QComboBox#vtCombo::down-arrow {{
                image: url("{arrow}");
                width: 12px;
                height: 12px;
            }}
            QComboBox#vtCombo QAbstractItemView {{
                background: {T.SURFACE};
                border: 1px solid {T.BORDER};
                selection-background-color: {T.ACCENT_SOFT};
                selection-color: {T.TEXT_PRIMARY};
                outline: 0;
                padding: 2px;
            }}
            """
        )
        vtl.addWidget(self.vtype, 0, Qt.AlignVCenter)
        lay.addWidget(vt_wrap, 0, Qt.AlignVCenter)
        return bar

    # ── Header fields ────────────────────────────────────────
    def _header_card(self) -> QFrame:
        box = S.card()
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(8)

        if self.is_sales:
            self._build_sales_header(lay)
        else:
            self._build_purchase_header(lay)
        return box

    def _build_purchase_header(self, lay: QVBoxLayout):
        # Match sales density — compact header, not a tall form block
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(8)
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.party = QComboBox()
        self.party.setEditable(False)  # select from list (dropdown)
        parties = [p for p in D.PARTIES if self._party_matches(p)]
        for p in parties:
            self.party.addItem(p["name"])
        for i in range(self.party.count()):
            if "polycab" in self.party.itemText(i).lower():
                self.party.setCurrentIndex(i)
                break
        self.party.currentTextChanged.connect(self._on_party_changed)
        row1.addWidget(S.labeled_input("Customer / Party Name", self.party), 6)

        from app.services import vouchers as vouchers_svc
        self.doc_no = QLineEdit(vouchers_svc.next_doc_no("purchase"))
        row1.addWidget(S.labeled_input("Invoice No", self.doc_no), 3)

        self.doc_date = QDateEdit(QDate(2026, 9, 20))
        self.doc_date.setCalendarPopup(True)
        self.doc_date.setDisplayFormat("dd-MM-yyyy")
        row1.addWidget(S.labeled_input("Invoice Date", self.doc_date), 3)
        lay.addLayout(row1)

        self.balance_lbl = QLabel()
        self.balance_lbl.setVisible(False)
        self._on_party_changed(self.party.currentText())

    def _build_sales_header(self, lay: QVBoxLayout):
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        from app.services import vouchers as vouchers_svc
        self.doc_no = QLineEdit(vouchers_svc.next_doc_no("sale"))
        row1.addWidget(S.labeled_input("Invoice No", self.doc_no), 1)

        self.doc_date = QDateEdit(QDate(2026, 9, 20))
        self.doc_date.setCalendarPopup(True)
        self.doc_date.setDisplayFormat("dd-MM-yyyy")
        row1.addWidget(S.labeled_input("Date", self.doc_date), 1)

        # Party: dropdown by default; "+ New" swaps to a free-text input
        self.party_stack = QWidget()
        self.party_stack.setStyleSheet("background: transparent;")
        psl = QVBoxLayout(self.party_stack)
        psl.setContentsMargins(0, 0, 0, 0)
        psl.setSpacing(4)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        cap = QLabel("Customer / Party Name")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        top.addWidget(cap)
        top.addStretch()
        self.new_party_link = QLabel("+ New [Alt+C]")
        self.new_party_link.setCursor(QCursor(Qt.PointingHandCursor))
        self.new_party_link.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        self.new_party_link.mousePressEvent = (
            lambda e: self._toggle_new_party() if e.button() == Qt.LeftButton else None
        )
        top.addWidget(self.new_party_link)
        psl.addLayout(top)

        self.party = QComboBox()
        self.party.setEditable(False)
        parties = [p for p in D.PARTIES if self._party_matches(p)]
        for p in parties:
            self.party.addItem(p["name"])
        for i in range(self.party.count()):
            if "balaji" in self.party.itemText(i).lower():
                self.party.setCurrentIndex(i)
                break
        self.party.currentTextChanged.connect(self._on_party_changed)
        from app.widgets.icons import combo_dropdown_qss
        self.party.setStyleSheet(
            f"""
            QComboBox {{
                background: {T.INPUT_BG}; border: none; border-radius: {S.R}px;
                padding: 8px 28px 8px 10px; min-height: 20px; font-size: 13px;
                font-weight: 600; color: {T.TEXT_PRIMARY};
            }}
            {combo_dropdown_qss(width=24, background=T.INPUT_BG)}
            """
        )
        self.party_input = QLineEdit()
        self.party_input.setPlaceholderText("Enter new customer / party name…")
        self.party_input.setVisible(False)
        self.party_input.setStyleSheet(
            f"QLineEdit {{ background: {T.INPUT_BG}; border: none; border-radius: {S.R}px; "
            f"padding: 8px 10px; min-height: 20px; font-size: 13px; font-weight: 600; "
            f"color: {T.TEXT_PRIMARY}; }}"
        )
        psl.addWidget(self.party)
        psl.addWidget(self.party_input)
        row1.addWidget(self.party_stack, 3)

        self.vehicle = QLineEdit()
        self.vehicle.setPlaceholderText("TS09 UB 4421")
        row1.addWidget(S.labeled_input("Vehicle No.", self.vehicle), 1)
        lay.addLayout(row1)

        # Contact / Alias as editable inputs (Stitch)
        meta = QHBoxLayout()
        meta.setSpacing(10)
        self.contact_phone = QLineEdit("+91 98765 43210")
        meta.addWidget(S.labeled_input("Contact / Phone", self.contact_phone), 2)
        self.alias_name = QLineEdit("Balaji Electricals")
        meta.addWidget(S.labeled_input("Manual Name / Alias", self.alias_name), 2)
        badge_wrap = QWidget()
        badge_wrap.setStyleSheet("background: transparent;")
        bwl = QVBoxLayout(badge_wrap)
        bwl.setContentsMargins(0, 0, 0, 0)
        bwl.setSpacing(4)
        pcap = QLabel("Party Type")
        pcap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bwl.addWidget(pcap)
        bwl.addWidget(S.pill("Regular B2B GSTIN", "success"), 0, Qt.AlignLeft)
        meta.addWidget(badge_wrap, 1)
        lay.addLayout(meta)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.pay_mode = QComboBox()
        self.pay_mode.addItems(
            ["Online Payment", "Cash Immediately", "UPI / Instant NEFT", "Cheque / PDC"]
        )
        row2.addWidget(S.labeled_input("Payment Option", self.pay_mode), 1)

        self.validity = QComboBox()
        self.validity.addItems(
            ["30 Days (Credit)", "Immediate / Net 0", "15 Days", "45 Days", "60 Days"]
        )
        row2.addWidget(S.labeled_input("Payment Validity", self.validity), 1)

        self.gstin = QLineEdit("36ABCDE1234F1Z5")
        row2.addWidget(S.labeled_input("Party GSTIN & State", self.gstin), 2)

        self.balance_lbl = QLabel()
        self._on_party_changed(self.party.currentText())
        bal_wrap = QWidget()
        bal_wrap.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(bal_wrap)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(4)
        bcap = QLabel("Financial Status")
        bcap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bl.addWidget(bcap)
        bl.addWidget(self.balance_lbl)
        row2.addWidget(bal_wrap, 1)
        lay.addLayout(row2)

    def _toggle_new_party(self):
        """Alt+C / + New — swap party dropdown ↔ free-text input."""
        self._party_new_mode = not self._party_new_mode
        self.party.setVisible(not self._party_new_mode)
        self.party_input.setVisible(self._party_new_mode)
        if self._party_new_mode:
            self.new_party_link.setText("Select existing")
            self.party_input.clear()
            self.party_input.setFocus()
        else:
            self.new_party_link.setText("+ New [Alt+C]")
            self.party.setFocus()

    def _party_matches(self, p):
        if self.is_sales:
            return p["type"] in ("Customer", "Both")
        return p["type"] in ("Supplier", "Both")

    def _on_party_changed(self, name):
        bal = self._party_balances.get(name, 0.0)
        if not hasattr(self, "balance_lbl"):
            return
        if bal > 0:
            self.balance_lbl.setText(f"Bal: {format_inr_indian(bal)} Dr")
            self.balance_lbl.setStyleSheet(
                f"color: {T.DANGER}; background: {T.DANGER_BG}; border: 1px solid #fecaca; "
                f"border-radius: {S.R}px; padding: 6px 10px; font-weight: 700; font-size: 12px;"
            )
        elif bal < 0:
            self.balance_lbl.setText(f"Bal: {format_inr_indian(abs(bal))} Cr")
            self.balance_lbl.setStyleSheet(
                f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: 1px solid #bbf7d0; "
                f"border-radius: {S.R}px; padding: 6px 10px; font-weight: 700; font-size: 12px;"
            )
        else:
            self.balance_lbl.setText("Bal: ₹ 0.00")
            self.balance_lbl.setStyleSheet(
                f"color: {S.SECONDARY}; background: {T.INPUT_BG}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; padding: 6px 10px; font-weight: 600; font-size: 12px;"
            )
        if hasattr(self, "prev_title"):
            self._reload_prev_details()

    # ── Addresses (sales) — type first, then 1 or 2 boxes ────
    def _address_section(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wrap.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self._addr_lay = QVBoxLayout(wrap)
        self._addr_lay.setContentsMargins(0, 0, 0, 0)
        self._addr_lay.setSpacing(8)

        type_row = QHBoxLayout()
        type_row.setSpacing(10)
        self.addr_type = QComboBox()
        self.addr_type.addItems([
            "Same Billing & Shipping (Single Address)",
            "Separate Delivery Address",
        ])
        self.addr_type.currentIndexChanged.connect(self._on_addr_type_changed)
        type_row.addWidget(S.labeled_input("Address Type", self.addr_type), 2)
        type_row.addStretch(3)
        self._addr_lay.addLayout(type_row)

        self._addr_boxes = QWidget()
        self._addr_boxes.setStyleSheet("background: transparent;")
        self._addr_boxes_lay = QHBoxLayout(self._addr_boxes)
        self._addr_boxes_lay.setContentsMargins(0, 0, 0, 0)
        self._addr_boxes_lay.setSpacing(10)

        self._buyer_card = self._addr_card(
            "Buyer Address (Billing)",
            "GST Registered Place",
            "Shop #14-2-89, M.G. Road, Ranigunj, Secunderabad, Telangana - 500003",
            editable=True,
        )
        self._delivery_card = self._addr_card(
            "Delivery / Consignee Address (Shipping)",
            "Ship To",
            "Shop #14-2-89, M.G. Road, Ranigunj, Secunderabad, Telangana - 500003",
            editable=True,
        )
        self._addr_boxes_lay.addWidget(self._buyer_card, 1)
        self._addr_boxes_lay.addWidget(self._delivery_card, 1)
        self._delivery_card.setVisible(False)
        self._addr_lay.addWidget(self._addr_boxes)
        return wrap

    def _on_addr_type_changed(self, idx: int):
        # 0 = single, 1 = separate delivery
        self._delivery_card.setVisible(idx == 1)

    def _addr_card(self, title: str, tag: str, body: str, editable: bool = False) -> QFrame:
        box = S.card()
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(4)
        top = QHBoxLayout()
        ttl = QLabel(title)
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        top.addWidget(ttl)
        top.addStretch()
        top.addWidget(S.pill(tag, "neutral"))
        lay.addLayout(top)
        row = QHBoxLayout()
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap("pin_drop", size=16, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        row.addWidget(ic)
        if editable:
            txt = QTextEdit()
            txt.setPlainText(body)
            txt.setFixedHeight(44)
            txt.setStyleSheet(
                f"QTextEdit {{ background: {T.INPUT_BG}; border: none; border-radius: {S.R}px; "
                f"padding: 4px 6px; font-size: 12px; color: {T.TEXT_PRIMARY}; }}"
            )
        else:
            txt = QLabel(body)
            txt.setWordWrap(True)
            txt.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 12px; border: none; background: transparent;"
            )
        row.addWidget(txt, stretch=1)
        lay.addLayout(row)
        return box

    # ── Fast line bar ────────────────────────────────────────
    def _fast_bar(self) -> QFrame:
        box = S.card()
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        self.item_search = QComboBox()
        self.item_search.setEditable(True)
        self.item_search.setInsertPolicy(QComboBox.NoInsert)
        self.item_search.addItem("")
        for p in D.PRODUCTS:
            self.item_search.addItem(f"{p['sku']} — {p['name']}", p)
        self.item_search.setMinimumWidth(220)
        self.item_search.currentIndexChanged.connect(self._on_item_picked)
        lay.addWidget(S.labeled_input("Item Name", self.item_search), 3)

        self.qty = QDoubleSpinBox()
        self.qty.setRange(0.001, 999999)
        self.qty.setDecimals(3)
        self.qty.setValue(1)
        lay.addWidget(S.labeled_input("Qty", self.qty), 1)

        self.unit = QComboBox()
        self.unit.addItems(["ROL", "NOS", "Pcs", "Coil", "Mtr", "Box"])
        lay.addWidget(S.labeled_input("Unit", self.unit), 1)

        self.unit_scale = QLineEdit()
        self.unit_scale.setPlaceholderText("e.g. 90m")
        lay.addWidget(S.labeled_input("Scale of Unit", self.unit_scale), 1)

        self.rate = QDoubleSpinBox()
        self.rate.setRange(0, 9999999)
        self.rate.setDecimals(2)
        lay.addWidget(S.labeled_input("Rate (₹)", self.rate), 1)

        self.disc = QDoubleSpinBox()
        self.disc.setRange(0, 100)
        self.disc.setDecimals(2)
        self.disc_field = S.labeled_input("Disc %", self.disc)
        lay.addWidget(self.disc_field, 1)

        self.gst = QDoubleSpinBox()
        self.gst.setRange(0, 28)
        self.gst.setDecimals(1)
        self.gst.setValue(18)
        self.gst_field = S.labeled_input("GST %", self.gst)
        lay.addWidget(self.gst_field, 1)

        self.btn_add = S.action_btn(
            "Add", shortcut="Enter", icon="add", kind="primary", on_click=self._add_line
        )
        spacer = QWidget()
        spacer.setFixedHeight(18)
        spacer.setStyleSheet("background: transparent;")
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(4)
        wl.addWidget(spacer)
        wl.addWidget(self.btn_add)
        lay.addWidget(wrap)
        return box

    def _on_item_picked(self, idx):
        data = self.item_search.itemData(idx)
        if not data:
            return
        key = "sale_rate" if self.is_sales else "purchase_rate"
        self.rate.setValue(float(data.get(key, data.get("rate", 0))))
        self.gst.setValue(float(data.get("gst", 18)))
        unit = str(data.get("unit", "NOS"))
        idx_u = self.unit.findText(unit)
        if idx_u < 0:
            # try case-insensitive / partial
            for i in range(self.unit.count()):
                if unit.lower() in self.unit.itemText(i).lower() or self.unit.itemText(i).lower() in unit.lower():
                    idx_u = i
                    break
        if idx_u >= 0:
            self.unit.setCurrentIndex(idx_u)
        else:
            self.unit.addItem(unit)
            self.unit.setCurrentText(unit)
        # Common wire scale hint
        if "sq" in data.get("name", "").lower() or unit.upper() in ("ROL", "COIL"):
            self.unit_scale.setText("90m")
        else:
            self.unit_scale.setText("1")
        self.qty.setFocus()
        self.qty.selectAll()

    # ── Items table ──────────────────────────────────────────
    def _items_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.grid = QTableWidget(0, len(GRID_COLS))
        self.grid.setHorizontalHeaderLabels(GRID_COLS)
        self.grid.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
        )
        self.grid.setSelectionBehavior(QAbstractItemView.SelectRows)
        hdr = self.grid.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed)
        self.grid.setColumnWidth(0, 44)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        # Wide enough for full amounts (avoid "61,000...." elision)
        for c, w in ((2, 100), (3, 120), (4, 80), (5, 80), (6, 140)):
            hdr.setSectionResizeMode(c, QHeaderView.Fixed)
            self.grid.setColumnWidth(c, w)
        hdr.setSectionResizeMode(7, QHeaderView.Fixed)
        self.grid.setColumnWidth(7, 64)
        S.apply_table_style(self.grid)
        self.grid.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.grid.itemChanged.connect(self._on_cell_changed)
        # Show at least ~5–6 product rows comfortably
        row_h = T.GRID_ROW_H
        min_rows = 6
        self.grid.setMinimumHeight(T.TABLE_HEADER_H + row_h * min_rows + 8)
        lay.addWidget(self.grid, stretch=1)

        foot = QFrame()
        foot.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(T.TABLE_PAD_X, 8, T.TABLE_PAD_X, 8)
        self.items_lbl = QLabel("Total Items: 0")
        self.qty_lbl = QLabel("Total Quantity: 0 Units")
        for lbl in (self.items_lbl, self.qty_lbl):
            lbl.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 12px; font-weight: 600; "
                f"border: none; background: transparent;"
            )
        fl.addWidget(self.items_lbl)
        fl.addWidget(QLabel("  |  "))
        fl.addWidget(self.qty_lbl)
        fl.addStretch()
        tip = QLabel(
            "Shortcuts: F9 Save & Print"
            if self.is_sales
            else "Navigation: Up/Down Arrow · Del to remove"
        )
        tip.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        fl.addWidget(tip)
        lay.addWidget(foot)
        return box

    def _seed_demo_lines(self):
        """Preload Stitch demo rows so the screen matches the mockup."""
        if self.is_sales:
            demo = [
                ("Polycab 2.5 sq mm Flame Retardant Wire (Red)", 10, "ROL", 1450, 0, 18),
                ("Havells 16A Modular Switch 1-Way (Crabtree Athena)", 100, "NOS", 85, 0, 18),
                ("Philips 20W LED Batten Tube Light 6500K Cool Day White", 30, "NOS", 240, 0, 18),
                ("Finolex 1.5 sq mm 90m Copper Wire (Blue) Heavy Duty", 15, "ROL", 1120, 0, 18),
            ]
        else:
            demo = [
                ("Polycab 2.5 sq mm FR Red", 50, "Coil", 1220, 0, 18),
                ("Havells 16A Modular Switch Crabtree", 200, "Pcs", 68, 0, 18),
                ("Finolex 1.5 sq mm Blue FR", 30, "Coil", 940, 0, 18),
            ]
        for name, qty, unit, rate, disc, gst in demo:
            self._append_row(name, qty, unit, rate, disc, gst)

    def _append_row(self, name, qty, unit, rate, disc, gst):
        r = self.grid.rowCount()
        self.grid.insertRow(r)
        amount = qty * rate * (1 - disc / 100)
        vals = [
            str(r + 1),
            name,
            f"{qty:g} {unit}",
            f"{rate:,.2f}",
            f"{disc:.1f}",
            f"{gst:.1f}%",
            f"{amount:,.2f}",
            "",
        ]
        self.grid.blockSignals(True)
        for c, v in enumerate(vals):
            if c == 7:
                continue
            it = QTableWidgetItem(v)
            if c == 0:
                it.setTextAlignment(Qt.AlignCenter)
                it.setFlags(Qt.ItemIsEnabled)
            elif c in (2, 3, 4, 5, 6):
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if c == 5:
                it.setForeground(QBrush(QColor(S.PRIMARY)))
            if c == 6:
                it.setForeground(QBrush(QColor(S.PRIMARY)))
                f = it.font()
                f.setBold(True)
                it.setFont(f)
            if c == 1:
                f = it.font()
                f.setBold(True)
                it.setFont(f)
            self.grid.setItem(r, c, it)
        self.grid.blockSignals(False)

        del_btn = QLabel()
        del_btn.setAlignment(Qt.AlignCenter)
        del_btn.setCursor(QCursor(Qt.PointingHandCursor))
        del_btn.setPixmap(icon_pixmap("delete", size=16, color=T.DANGER))
        del_btn.setStyleSheet("background: transparent; border: none;")
        del_btn.mousePressEvent = (
            lambda e, row=r: self._delete_row(row) if e.button() == Qt.LeftButton else None
        )
        self.grid.setCellWidget(r, 7, del_btn)

    def _delete_row(self, row: int):
        if 0 <= row < self.grid.rowCount():
            self.grid.removeRow(row)
            # renumber
            for r in range(self.grid.rowCount()):
                it = self.grid.item(r, 0)
                if it:
                    it.setText(str(r + 1))
            self._recalc()

    def _add_line(self):
        idx = self.item_search.currentIndex()
        data = self.item_search.itemData(idx)
        if not data:
            toast(self, "Select an item first. [F2]")
            self.item_search.setFocus()
            return
        self._append_row(
            data["name"],
            self.qty.value(),
            self.unit.currentText() or data.get("unit", "NOS"),
            self.rate.value(),
            0.0 if self.is_estimate else self.disc.value(),
            0.0 if self.is_estimate else self.gst.value(),
        )
        self._recalc()
        self.item_search.setCurrentIndex(0)
        self.qty.setValue(1)
        self.disc.setValue(0)
        self.unit_scale.clear()
        self.item_search.setFocus()

    def _on_cell_changed(self, item: QTableWidgetItem):
        if item.column() in (2, 3, 4, 5):
            self._recalc()

    # ── Bottom: previous + totals ────────────────────────────
    def _bottom_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wrap.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self._prev_card(), stretch=3)
        right = QVBoxLayout()
        right.setSpacing(8)
        right.setContentsMargins(0, 0, 0, 0)
        right.setAlignment(Qt.AlignTop)
        right.addWidget(self._totals_card())
        lay.addLayout(right, stretch=2)
        return wrap

    def _prev_card(self) -> QFrame:
        box = S.card()
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QFrame()
        head.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; "
            f"border-top-left-radius: {S.CR}px; border-top-right-radius: {S.CR}px; }}"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(10, 6, 10, 6)
        hl.setSpacing(6)
        head.setFixedHeight(34)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap("history", size=14, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        hl.addWidget(ic)
        self.prev_title = QLabel(self._prev_title_text())
        self.prev_title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        hl.addWidget(self.prev_title, stretch=1)
        view_all = QFrame()
        view_all.setCursor(QCursor(Qt.PointingHandCursor))
        view_all.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_HIGH}; }}"
        )
        va = QHBoxLayout(view_all)
        va.setContentsMargins(8, 3, 8, 3)
        va.setSpacing(4)
        va_ic = QLabel()
        va_ic.setFixedSize(12, 12)
        va_ic.setPixmap(icon_pixmap("open_in_new", size=12, color=S.PRIMARY))
        va_ic.setStyleSheet("background: transparent; border: none;")
        va.addWidget(va_ic)
        va_txt = QLabel("View All (Alt+H)")
        va_txt.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        va.addWidget(va_txt)
        view_all.mousePressEvent = (
            lambda e: self._open_history() if e.button() == Qt.LeftButton else None
        )
        hl.addWidget(view_all)
        lay.addWidget(head)

        cols = self._prev_col_headers()
        self.prev_table = QTableWidget(0, len(cols))
        self.prev_table.setHorizontalHeaderLabels(cols)
        self.prev_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.prev_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.prev_table.setFocusPolicy(Qt.NoFocus)
        self.prev_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for c, w in ((0, 120), (1, 100), (3, 110), (4, 64), (5, 64), (6, 130)):
            self.prev_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.Fixed)
            self.prev_table.setColumnWidth(c, w)
        S.apply_table_style(self.prev_table)
        self.prev_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.prev_table.verticalHeader().setDefaultSectionSize(30)
        self.prev_table.horizontalHeader().setFixedHeight(28)
        lay.addWidget(self.prev_table)
        self._reload_prev_details()
        return box

    def _prev_title_text(self) -> str:
        party = ""
        if hasattr(self, "party"):
            party = self.party.currentText()
        if not self.is_sales:
            return f"Previous Purchase Details (Supplier: {party or 'Polycab India Ltd'})"
        kind = self._voucher_kind()
        who = party or "Balaji Electricals & Hardware"
        if kind == "estimate":
            return f"Previous Estimate Details (Customer: {who})"
        if kind == "return":
            return f"Previous Sales Return Details (Customer: {who})"
        return f"Previous Sales Details (Customer: {who})"

    def _prev_col_headers(self) -> list:
        kind = self._voucher_kind() if self.is_sales else "purchase"
        if kind == "estimate":
            return ["Est. No.", "Date", "Item Name", "Last Rate (₹)", "Qty", "Unit", "Net Amount"]
        if kind == "return":
            return ["SR No.", "Date", "Item Name", "Last Rate (₹)", "Qty", "Unit", "Net Amount"]
        if kind == "purchase" or kind == "purchase_return":
            return ["Pur. No.", "Date", "Item Name", "Last Rate (₹)", "Qty", "Unit", "Net Amount"]
        return ["Inv. No.", "Date", "Item Name", "Last Rate (₹)", "Qty", "Unit", "Net Amount"]

    def _prev_rows(self) -> list:
        if not self.is_sales:
            return list(D.PREV_PURCHASES)
        kind = self._voucher_kind()
        if kind == "estimate":
            return list(D.PREV_ESTIMATES)
        if kind == "return":
            return list(D.PREV_SALES_RETURNS)
        return list(D.PREV_SALES)

    def _reload_prev_details(self):
        if not hasattr(self, "prev_table"):
            return
        if hasattr(self, "prev_title"):
            self.prev_title.setText(self._prev_title_text())
        cols = self._prev_col_headers()
        self.prev_table.setHorizontalHeaderLabels(cols)
        rows = self._prev_rows()
        self.prev_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [
                row["inv"], row["date"], row["item"],
                f"{row['rate']:,.2f}", f"{row['qty']:g}", row["unit"],
                format_inr_indian(row["amount"]),
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                if c == 0:
                    it.setForeground(QBrush(QColor(S.PRIMARY)))
                if c in (3, 4, 6):
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.prev_table.setItem(r, c, it)
        body_h = 28 + 30 * max(len(rows), 1) + 4
        self.prev_table.setFixedHeight(min(body_h, 160))

    def _totals_card(self) -> QFrame:
        """Compact totals + remarks in one card (Stitch: no huge empty gap)."""
        box = S.card()
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(6)

        self.lbl_gross = QLabel("₹ 0.00")
        self.lbl_gst = QLabel("₹ 0.00")
        self.lbl_net = QLabel("₹ 0.00")

        self.lbl_gross_cap = QLabel("Gross Taxable:" if self.is_sales else "Subtotal:")
        self.lbl_gst_cap = QLabel("Total GST (18%):" if self.is_sales else "GST (18%):")
        self.lbl_net_cap = QLabel("Net Payable:" if self.is_sales else "Net Total:")

        def _add_total_row(cap: QLabel, widget: QLabel, emphasis: bool) -> QWidget:
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent;")
            row = QHBoxLayout(row_w)
            row.setContentsMargins(0, 2 if emphasis else 0, 0, 2 if emphasis else 0)
            row.setSpacing(12)
            cap.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: {'13px' if emphasis else '12px'}; "
                f"font-weight: {'700' if emphasis else '600'}; "
                f"border: none; background: transparent;"
            )
            row.addWidget(cap)
            row.addStretch()
            widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            widget.setMinimumWidth(140)
            widget.setStyleSheet(
                f"color: {S.PRIMARY if emphasis else T.TEXT_PRIMARY}; "
                f"font-size: {'18px' if emphasis else '13px'}; font-weight: 700; "
                f"border: none; background: transparent; padding-right: 4px;"
            )
            row.addWidget(widget)
            return row_w

        lay.addWidget(_add_total_row(self.lbl_gross_cap, self.lbl_gross, False))
        self._gst_row = _add_total_row(self.lbl_gst_cap, self.lbl_gst, False)
        lay.addWidget(self._gst_row)
        lay.addWidget(_add_total_row(self.lbl_net_cap, self.lbl_net, True))

        if self.is_sales:
            # Divider then remarks — same card, tight spacing (no collapsed gap)
            div = QFrame()
            div.setFixedHeight(1)
            div.setStyleSheet(f"background: {T.BORDER}; border: none;")
            lay.addSpacing(4)
            lay.addWidget(div)
            lay.addSpacing(4)
            cap = QLabel("REMARKS / NARRATION")
            cap.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
                f"letter-spacing: 0.3px; border: none; background: transparent;"
            )
            lay.addWidget(cap)
            self.remarks = QTextEdit()
            self.remarks.setPlaceholderText("Optional narration for this invoice…")
            self.remarks.setFixedHeight(52)
            self.remarks.setStyleSheet(
                f"QTextEdit {{ background: {T.INPUT_BG}; border: none; border-radius: {S.R}px; "
                f"padding: 8px; font-size: 12px; }}"
            )
            lay.addWidget(self.remarks)
        return box

    def _remarks(self) -> QFrame:
        # Kept for compatibility; remarks now live inside _totals_card for sales.
        return QFrame()

    def _actions(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addStretch()
        lay.addWidget(
            S.action_btn("Save & Print", shortcut="F9", icon="print", kind="primary",
                         on_click=lambda: self._save("print"))
        )
        lay.addWidget(
            S.action_btn("New Entry", shortcut="F10", icon="add_circle", kind="secondary",
                         on_click=lambda: self._save("new"))
        )
        lay.addWidget(
            S.action_btn("Clear", shortcut="Esc", icon="close", kind="danger",
                         on_click=self._cancel)
        )
        return wrap

    def _open_history(self):
        from app.screens.history_modal import PartyHistoryDialog

        if getattr(self, "_party_new_mode", False) and hasattr(self, "party_input"):
            party_name = self.party_input.text().strip() or self.party.currentText()
        else:
            party_name = self.party.currentText()
        hist_mode = self.mode
        if self.is_sales:
            kind = self._voucher_kind()
            if kind == "estimate":
                hist_mode = "estimate"
            elif kind == "return":
                hist_mode = "sales_return"
        dlg = PartyHistoryDialog(
            mode=hist_mode,
            party_name=party_name,
            parent=self.window(),
        )
        if dlg.exec() and dlg.selected_rate is not None:
            self.rate.setValue(float(dlg.selected_rate))
            toast(self, f"Applied rate {format_inr_indian(dlg.selected_rate)}")
            self.qty.setFocus()

    def _on_voucher_type_changed(self, *_):
        """Toggle Estimate UI: hide Disc/GST, net without tax, swap previous details."""
        if not self.is_sales:
            return
        est = self.is_estimate
        if hasattr(self, "disc_field"):
            self.disc_field.setVisible(not est)
        if hasattr(self, "gst_field"):
            self.gst_field.setVisible(not est)
        if hasattr(self, "grid"):
            self.grid.setColumnHidden(4, est)  # Disc %
            self.grid.setColumnHidden(5, est)  # GST %
        if hasattr(self, "_gst_row"):
            self._gst_row.setVisible(not est)
        if hasattr(self, "lbl_gross_cap"):
            self.lbl_gross_cap.setText("Gross Amount:" if est else "Gross Taxable:")
        if hasattr(self, "lbl_net_cap"):
            self.lbl_net_cap.setText("Net Amount:" if est else "Net Payable:")
        # Doc number series by voucher type
        if hasattr(self, "doc_no"):
            kind = self._voucher_kind()
            if kind == "estimate":
                self.doc_no.setText("EST/26-27/0089")
            elif kind == "return":
                self.doc_no.setText("SR/26-27/0043")
            else:
                self.doc_no.setText("SLE/26-27/0840")
        if hasattr(self, "remarks"):
            ph = (
                "Optional narration for this estimate…"
                if est
                else "Optional narration for this invoice…"
            )
            self.remarks.setPlaceholderText(ph)
        self._reload_prev_details()
        self._recalc()

    # ── Calc / save ──────────────────────────────────────────
    def _parse_qty(self, text: str) -> float:
        try:
            return float(str(text).split()[0].replace(",", ""))
        except Exception:
            return 0.0

    def _recalc(self):
        taxable = tax = qty_total = 0.0
        items = 0
        estimate = self.is_estimate
        for r in range(self.grid.rowCount()):
            name = self.grid.item(r, 1)
            if not name or not name.text().strip():
                continue
            items += 1
            qty = self._parse_qty(self.grid.item(r, 2).text() if self.grid.item(r, 2) else "0")
            try:
                rate = float((self.grid.item(r, 3).text() or "0").replace(",", ""))
            except ValueError:
                rate = 0.0
            if estimate:
                disc = 0.0
                gst = 0.0
            else:
                try:
                    disc = float((self.grid.item(r, 4).text() or "0").replace("%", ""))
                except ValueError:
                    disc = 0.0
                try:
                    gst = float((self.grid.item(r, 5).text() or "0").replace("%", ""))
                except ValueError:
                    gst = 0.0
            line = qty * rate * (1 - disc / 100)
            taxable += line
            tax += line * gst / 100
            qty_total += qty
            self.grid.blockSignals(True)
            amt = self.grid.item(r, 6)
            if amt:
                amt.setText(f"{line:,.2f}")
            self.grid.blockSignals(False)

        net = taxable if estimate else (taxable + tax)
        self.lbl_gross.setText(format_inr_indian(taxable))
        self.lbl_gst.setText(format_inr_indian(0.0 if estimate else tax))
        self.lbl_net.setText(format_inr_indian(net))
        self.items_lbl.setText(f"Total Items: {items}")
        unit = "Units"
        self.qty_lbl.setText(f"Total Quantity: {qty_total:g} {unit}")

    def _save(self, kind):
        from app.services import vouchers as vouchers_svc
        from app import session

        party_name = ""
        if hasattr(self, "party") and self.party.isVisible():
            party_name = self.party.currentText().strip()
        elif hasattr(self, "party_input") and self.party_input.isVisible():
            party_name = self.party_input.text().strip()
        party = next((p for p in D.PARTIES if p["name"] == party_name), None)
        if party is None:
            toast(self, "Select a party/ledger before saving.")
            return

        lines = []
        for r in range(self.grid.rowCount()):
            name_item = self.grid.item(r, 1)
            if not name_item:
                continue
            pname = name_item.text().strip()
            prod = next((p for p in D.PRODUCTS if p["name"] == pname), None)
            if prod is None:
                continue
            qty_txt = (self.grid.item(r, 2).text() if self.grid.item(r, 2) else "0").split()[0]
            rate_txt = (self.grid.item(r, 3).text() if self.grid.item(r, 3) else "0").replace(",", "")
            disc_txt = (self.grid.item(r, 4).text() if self.grid.item(r, 4) else "0")
            gst_txt = (self.grid.item(r, 5).text() if self.grid.item(r, 5) else "0").replace("%", "")
            try:
                qty = float(qty_txt or 0)
                rate = float(rate_txt or 0)
                disc = float(disc_txt or 0)
                gst = float(gst_txt or 0)
            except ValueError:
                continue
            lines.append(
                {
                    "product_id": prod["id"],
                    "qty": qty,
                    "unit": prod.get("unit") or "Pcs",
                    "rate": rate,
                    "discount_pct": disc,
                    "gst_pct": gst,
                    "line_amount": qty * rate * (1 - disc / 100),
                }
            )
        if not lines:
            toast(self, "Add at least one product line.")
            return

        vtype = {
            "sales": "sale",
            "return": "sales_return",
            "estimate": "estimate",
            "purchase": "purchase",
            "purchase_return": "purchase_return",
        }.get(self._voucher_kind(), "sale")

        godown_id = None
        if D.GODOWNS:
            godown_id = D.GODOWNS[0]["id"]
        user = session.current_user()
        try:
            saved = vouchers_svc.create_voucher(
                voucher_type=vtype,
                ledger_id=party["id"],
                lines=lines,
                doc_no=self.doc_no.text().strip() or None,
                godown_id=godown_id,
                created_by=user["id"] if user else None,
            )
        except Exception as exc:
            toast(self, f"Save failed: {exc}")
            return
        D.reload()
        self._party_balances = {p["name"]: p["balance"] for p in D.PARTIES}
        toast(self, f"Saved {saved['doc_no']} ({kind}) · {self.lbl_net.text()}")
        if kind == "new":
            self._clear_form()
            self.doc_no.setText(vouchers_svc.next_doc_no(vtype))

    def _cancel(self):
        self._clear_form()
        toast(self, "Entry cleared.")

    def _clear_form(self):
        self.grid.setRowCount(0)
        self._recalc()
        self.item_search.setFocus()

    def _wire_shortcuts(self):
        QShortcut(QKeySequence("F2"), self, activated=lambda: self.item_search.setFocus())
        QShortcut(QKeySequence("F9"), self, activated=lambda: self._save("print"))
        QShortcut(QKeySequence("F10"), self, activated=lambda: self._save("new"))
        QShortcut(QKeySequence("Esc"), self, activated=self._cancel)
        QShortcut(QKeySequence("Return"), self, activated=self._add_line)
        QShortcut(QKeySequence("Alt+H"), self, activated=self._open_history)
        QShortcut(
            QKeySequence("Alt+C"),
            self,
            activated=lambda: self._toggle_new_party() if self.is_sales else None,
        )

    def focus_entry(self):
        self.item_search.setFocus()
