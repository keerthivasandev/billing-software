"""4. Product Master (Catalog & Rates) — Stitch-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap
from app.widgets import stitch_ui as S

# Filter chips shown in Stitch left panel
_FILTER_TABS = [
    ("all", "All"),
    ("Wires & Cables", "Wires & Cables"),
    ("Switches & Sockets", "Switchgear"),
    ("Lighting", "Lighting"),
    ("Conduit & Fittings", "Conduits"),
]

_UNITS = [
    "Roll (ROL)", "Numbers (NOS)", "Meter (MTR)", "Bundle (BDL)",
    "Packet (PKT)", "Coil", "Pcs", "Box", "Kg",
]


def _unit_short(unit: str) -> str:
    u = (unit or "Pcs").upper()
    mapping = {
        "ROLL (ROL)": "ROL", "ROL": "ROL", "COIL": "ROL",
        "NUMBERS (NOS)": "NOS", "NOS": "NOS", "PCS": "NOS",
        "METER (MTR)": "MTR", "MTR": "MTR", "MTR.": "MTR",
        "BUNDLE (BDL)": "BDL", "BDL": "BDL",
        "PACKET (PKT)": "PKT", "PKT": "PKT",
        "BOX": "BOX", "KG": "KG",
    }
    return mapping.get(u, u[:3])


class ProductMasterScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.products = [dict(p) for p in D.PRODUCTS]
        self._filter = "all"
        self._selected_id = self.products[0]["id"] if self.products else None
        self._editing = False

        self.setObjectName("productRoot")
        self.setStyleSheet(f"QWidget#productRoot {{ background: {T.BG_CANVAS}; }}")

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

        body.addWidget(self._metrics_ribbon())
        body.addWidget(self._workspace(), stretch=1)
        body.addWidget(self._footer())

        scroll.setWidget(host)
        root.addWidget(scroll)

        QShortcut(QKeySequence("F3"), self, activated=self._new_product)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())

        self._rebuild_list()
        self._load_detail()
        self._set_editing(True)  # Stitch form fields stay editable; Save commits

    # ── Metrics ribbon ───────────────────────────────────────
    def _metrics_ribbon(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(16)

        # Master Catalog
        cat = QHBoxLayout()
        cat.setSpacing(8)
        ic1 = QLabel()
        ic1.setFixedSize(32, 32)
        ic1.setAlignment(Qt.AlignCenter)
        ic1.setStyleSheet(
            f"background: {S.SURFACE_GREY}; border-radius: 6px; border: none;"
        )
        ic1.setPixmap(icon_pixmap("inventory_2", size=18, color=S.PRIMARY))
        c1 = QVBoxLayout()
        c1.setSpacing(0)
        l1 = QLabel("MASTER CATALOG")
        l1.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 9px; font-weight: 700; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        self.count_val = QLabel(str(len(self.products)))
        self.count_val.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        items_lbl = QLabel("Items")
        items_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        row_c = QHBoxLayout()
        row_c.setSpacing(4)
        row_c.addWidget(self.count_val)
        row_c.addWidget(items_lbl)
        c1.addWidget(l1)
        c1.addLayout(row_c)
        cat.addWidget(ic1)
        cat.addLayout(c1)

        sep = QFrame()
        sep.setFixedSize(1, 32)
        sep.setStyleSheet(f"background: {T.BORDER}; border: none;")

        # Valuation
        val = QHBoxLayout()
        val.setSpacing(8)
        ic2 = QLabel()
        ic2.setFixedSize(32, 32)
        ic2.setAlignment(Qt.AlignCenter)
        ic2.setStyleSheet(
            f"background: {S.HEADER_GREY}; border-radius: 6px; border: none;"
        )
        ic2.setPixmap(icon_pixmap("payments", size=16, color=S.SECONDARY))
        c2 = QVBoxLayout()
        c2.setSpacing(0)
        l2 = QLabel("CURRENT VALUATION")
        l2.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 9px; font-weight: 700; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        self.val_lbl = QLabel(format_inr_indian(self._valuation()))
        self.val_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 14px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        c2.addWidget(l2)
        c2.addWidget(self.val_lbl)
        val.addWidget(ic2)
        val.addLayout(c2)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(
            S.action_btn("New Product", "F3", "add_circle", "primary", self._new_product)
        )
        actions.addWidget(
            S.action_btn("Save", "Ctrl+S", "save", "secondary", self._save)
        )

        lay.addLayout(cat)
        lay.addWidget(sep)
        lay.addLayout(val)
        lay.addStretch(1)
        lay.addLayout(actions)
        return box

    def _valuation(self) -> float:
        return sum(
            float(p.get("stock", 0)) * float(p.get("purchase_rate", 0))
            for p in self.products
        )

    def _refresh_metrics(self):
        self.count_val.setText(str(len(self.products)))
        self.val_lbl.setText(format_inr_indian(self._valuation()))

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

    def _left_panel(self) -> QFrame:
        box = S.card()
        box.setMinimumWidth(280)
        box.setMaximumWidth(380)
        outer = QVBoxLayout(box)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Grey header band: search + tabs
        head = QFrame()
        head.setObjectName("prodListHead")
        head.setStyleSheet(
            f"QFrame#prodListHead {{ background: {S.HEADER_GREY}; border: none; "
            f"border-top-left-radius: {T.CARD_RADIUS}px; "
            f"border-top-right-radius: {T.CARD_RADIUS}px; }}"
        )
        hl = QVBoxLayout(head)
        hl.setContentsMargins(10, 10, 10, 8)
        hl.setSpacing(8)

        search_box = QFrame()
        search_box.setFixedHeight(32)
        search_box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; border-radius: 6px; }}"
        )
        sw = QHBoxLayout(search_box)
        sw.setContentsMargins(8, 0, 6, 0)
        sw.setSpacing(6)
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setPixmap(icon_pixmap("search", size=16, color=S.SECONDARY))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search products by name or code...")
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; font-size: 12px; "
            f"color: {T.TEXT_PRIMARY}; }}"
        )
        self.search.textChanged.connect(self._rebuild_list)
        sw.addWidget(sic)
        sw.addWidget(self.search, stretch=1)
        sw.addWidget(S.kbd("Ctrl+F"))
        hl.addWidget(search_box)

        tabs = QHBoxLayout()
        tabs.setSpacing(4)
        self._tab_btns = {}
        for key, label in _FILTER_TABS:
            b = QFrame()
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setFixedHeight(24)
            b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            bl = QHBoxLayout(b)
            bl.setContentsMargins(8, 0, 8, 0)
            lbl = QLabel(label)
            lbl.setObjectName("tabLbl")
            bl.addWidget(lbl)
            b.mousePressEvent = lambda e, k=key: self._set_filter(k)
            self._tab_btns[key] = b
            tabs.addWidget(b)
        tabs.addStretch()
        hl.addLayout(tabs)
        self._style_tabs()
        outer.addWidget(head)

        # List
        self.list_host = QVBoxLayout()
        self.list_host.setSpacing(0)
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
        outer.addWidget(list_scroll, stretch=1)

        self.showing_lbl = QLabel()
        self.showing_lbl.setAlignment(Qt.AlignCenter)
        self.showing_lbl.setStyleSheet(
            f"background: {S.HEADER_GREY}; color: {S.SECONDARY}; font-size: 10px; "
            f"padding: 6px; border: none; "
            f"border-bottom-left-radius: {T.CARD_RADIUS}px; "
            f"border-bottom-right-radius: {T.CARD_RADIUS}px;"
        )
        outer.addWidget(self.showing_lbl)
        return box

    def _style_tabs(self):
        for key, b in self._tab_btns.items():
            active = key == self._filter
            lbl = b.findChild(QLabel, "tabLbl")
            if active:
                b.setStyleSheet(
                    f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: 4px; }}"
                )
                if lbl:
                    lbl.setStyleSheet(
                        "color: white; font-size: 10px; font-weight: 700; "
                        "border: none; background: transparent;"
                    )
            else:
                b.setStyleSheet(
                    f"QFrame {{ background: {S.SURFACE_GREY}; border: none; border-radius: 4px; }}"
                )
                if lbl:
                    lbl.setStyleSheet(
                        f"color: {S.SECONDARY}; font-size: 10px; font-weight: 600; "
                        f"border: none; background: transparent;"
                    )

    def _set_filter(self, key: str):
        self._filter = key
        self._style_tabs()
        self._rebuild_list()

    def _filtered(self):
        q = self.search.text().strip().lower()
        rows = self.products
        if self._filter != "all":
            rows = [p for p in rows if p.get("group") == self._filter]
        if q:
            rows = [
                p for p in rows
                if q in p.get("name", "").lower()
                or q in p.get("sku", "").lower()
                or q in p.get("hsn", "").lower()
            ]
        return rows

    def _rebuild_list(self):
        while self.list_host.count():
            item = self.list_host.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        rows = self._filtered()
        for p in rows:
            self.list_host.addWidget(self._product_card(p))
        self.list_host.addStretch(1)
        self.showing_lbl.setText(
            f"Showing {len(rows)} of {len(self.products)} products"
        )
        # Update All tab count label
        all_btn = self._tab_btns.get("all")
        if all_btn:
            lbl = all_btn.findChild(QLabel, "tabLbl")
            if lbl and self._filter == "all":
                lbl.setText(f"All ({len(self.products)})")
            elif lbl:
                # keep short when not active
                pass

    def _product_card(self, p: dict) -> QFrame:
        selected = p["id"] == self._selected_id
        card = QFrame()
        card.setCursor(QCursor(Qt.PointingHandCursor))
        if selected:
            card.setStyleSheet(
                f"QFrame {{ background: rgba(243,244,246,0.9); border: none; "
                f"border-bottom: 1px solid {T.BORDER}; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: none; "
                f"border-bottom: 1px solid {T.BORDER}; }}"
                f"QFrame:hover {{ background: {S.HEADER_GREY}; }}"
            )
        lay = QHBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        if selected:
            bar = QFrame()
            bar.setFixedWidth(3)
            bar.setStyleSheet(
                f"background: {S.PRIMARY}; border: none; border-radius: 1px;"
            )
            lay.addWidget(bar)

        col = QVBoxLayout()
        col.setSpacing(3)
        top = QHBoxLayout()
        name = QLabel(p.get("name", ""))
        name.setWordWrap(True)
        name.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        rate = QLabel(format_inr_indian(p.get("sale_rate", 0)))
        rate_color = S.PRIMARY if selected else T.TEXT_PRIMARY
        rate.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {rate_color}; "
            f"border: none; background: transparent;"
        )
        top.addWidget(name, stretch=1)
        top.addWidget(rate)
        col.addLayout(top)

        bot = QHBoxLayout()
        grp = QLabel(f"Group: {p.get('group', '—')}")
        grp.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        unit = _unit_short(p.get("unit", "Pcs"))
        stock = QLabel(f"Stock: {int(p.get('stock', 0))} {unit}")
        stock.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bot.addWidget(grp)
        bot.addStretch()
        bot.addWidget(stock)
        col.addLayout(bot)
        lay.addLayout(col, stretch=1)

        card.mousePressEvent = lambda e, pid=p["id"]: self._select(pid)
        return card

    def _select(self, pid: int):
        self._selected_id = pid
        self._rebuild_list()
        self._load_detail()
        self._set_editing(True)

    def _current(self) -> dict | None:
        for p in self.products:
            if p["id"] == self._selected_id:
                return p
        return None

    # ── Right detail ─────────────────────────────────────────
    def _right_panel(self) -> QFrame:
        box = S.card()
        outer = QVBoxLayout(box)
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(12)

        # Header
        head = QHBoxLayout()
        head.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(20, 20)
        ic.setPixmap(icon_pixmap("edit_document", size=18, color=S.PRIMARY))
        ttl = QLabel("Product Details")
        ttl.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.sku_badge = S.pill("SKU #—", "neutral")
        head.addWidget(ic)
        head.addWidget(ttl)
        head.addStretch()
        head.addWidget(self.sku_badge)
        outer.addLayout(head)

        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {T.BORDER}; border: none;")
        outer.addWidget(line)

        # Form fields
        self.name = QLineEdit()
        self.group = QComboBox()
        self.group.addItems(list(D.ITEM_GROUPS))
        self.unit = QComboBox()
        self.unit.setEditable(True)
        self.unit.addItems(_UNITS)
        self.hsn = QLineEdit()
        self.stock = QDoubleSpinBox()
        self.stock.setRange(0, 9_999_999)
        self.stock.setDecimals(0)
        self.purchase_rate = QDoubleSpinBox()
        self.purchase_rate.setRange(0, 9_999_999)
        self.purchase_rate.setDecimals(2)
        self.purchase_rate.setGroupSeparatorShown(True)
        self.sale_rate = QDoubleSpinBox()
        self.sale_rate.setRange(0, 9_999_999)
        self.sale_rate.setDecimals(2)
        self.sale_rate.setGroupSeparatorShown(True)

        # Product name full width with required hint
        name_wrap = QWidget()
        name_wrap.setStyleSheet("background: transparent;")
        nl = QVBoxLayout(name_wrap)
        nl.setContentsMargins(0, 0, 0, 0)
        nl.setSpacing(4)
        ntop = QHBoxLayout()
        ncap = QLabel("PRODUCT NAME")
        ncap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        nreq = QLabel("*Required")
        nreq.setStyleSheet(
            f"color: {S.ERROR}; font-size: 9px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        ntop.addWidget(ncap)
        ntop.addStretch()
        ntop.addWidget(nreq)
        nl.addLayout(ntop)
        self.name.setStyleSheet(
            f"QLineEdit {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 6px; padding: 8px 10px; font-size: 13px; font-weight: 600; "
            f"color: {T.TEXT_PRIMARY}; }}"
        )
        nl.addWidget(self.name)
        outer.addWidget(name_wrap)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(S.labeled_input("Product Group", self.group), 1)
        row1.addWidget(S.labeled_input("Unit of Sale", self.unit), 1)
        outer.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        row2.addWidget(S.labeled_input("HSN Code", self.hsn), 1)
        stock_wrap = QWidget()
        stock_wrap.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(stock_wrap)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(4)
        scap = QLabel("Current Stock")
        scap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        sl.addWidget(scap)
        srow = QHBoxLayout()
        srow.setSpacing(6)
        self.stock.setStyleSheet(
            f"QDoubleSpinBox {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; "
            f"padding: 8px 10px; min-height: 20px; font-size: 13px; font-weight: 700; }}"
        )
        self.stock_unit_lbl = QLabel("NOS")
        self.stock_unit_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        srow.addWidget(self.stock, stretch=1)
        srow.addWidget(self.stock_unit_lbl)
        sl.addLayout(srow)
        row2.addWidget(stock_wrap, 1)
        outer.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(10)
        row3.addWidget(S.labeled_input("Purchase Rate (₹)", self.purchase_rate), 1)
        # Sale rate emphasized (primary label + bold)
        sale_wrap = QWidget()
        sale_wrap.setStyleSheet("background: transparent;")
        sal = QVBoxLayout(sale_wrap)
        sal.setContentsMargins(0, 0, 0, 0)
        sal.setSpacing(4)
        scap2 = QLabel("SALE RATE (₹)")
        scap2.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        sal.addWidget(scap2)
        self.sale_rate.setStyleSheet(
            f"QDoubleSpinBox {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; padding: 8px 10px; min-height: 22px; font-size: 14px; "
            f"font-weight: 700; color: {S.PRIMARY}; }}"
        )
        sal.addWidget(self.sale_rate)
        row3.addWidget(sale_wrap, 1)
        outer.addLayout(row3)

        # Status + actions
        foot = QHBoxLayout()
        foot.setSpacing(8)
        status = QHBoxLayout()
        status.setSpacing(6)
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {T.SUCCESS}; border-radius: 4px; border: none;")
        self.status_lbl = QLabel("Status: In Stock & Active")
        self.status_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        status.addWidget(dot)
        status.addWidget(self.status_lbl)
        foot.addLayout(status)
        foot.addStretch()
        foot.addWidget(
            S.action_btn("New Product", "F3", "add_circle", "secondary", self._new_product)
        )
        foot.addWidget(
            S.action_btn("Save", "Ctrl+S", "save", "primary", self._save)
        )
        outer.addLayout(foot)
        outer.addStretch(1)
        return box

    def _load_detail(self):
        p = self._current()
        if not p:
            return
        self.sku_badge.setText(f"SKU #{p.get('sku', '—')}")
        self.name.setText(p.get("name", ""))
        grp = p.get("group", D.ITEM_GROUPS[0])
        idx = self.group.findText(grp)
        self.group.setCurrentIndex(idx if idx >= 0 else 0)
        unit = p.get("unit", "Pcs")
        # Prefer matching Stitch-style unit labels
        uidx = self.unit.findText(unit, Qt.MatchContains)
        if uidx >= 0:
            self.unit.setCurrentIndex(uidx)
        else:
            self.unit.setEditText(unit)
        self.hsn.setText(p.get("hsn", ""))
        self.stock.setValue(float(p.get("stock", 0)))
        self.stock_unit_lbl.setText(_unit_short(unit))
        self.purchase_rate.setValue(float(p.get("purchase_rate", 0)))
        self.sale_rate.setValue(float(p.get("sale_rate", p.get("rate", 0))))
        low = float(p.get("stock", 0)) <= float(p.get("min_stock", 0))
        if low:
            self.status_lbl.setText("Status: Low Stock — Reorder")
        else:
            self.status_lbl.setText("Status: In Stock & Active")

    def _fields(self):
        return [
            self.name, self.group, self.unit, self.hsn,
            self.stock, self.purchase_rate, self.sale_rate,
        ]

    def _set_editing(self, enabled: bool):
        self._editing = enabled
        for w in self._fields():
            if isinstance(w, (QLineEdit, QDoubleSpinBox)):
                w.setReadOnly(not enabled)
            elif isinstance(w, QComboBox):
                w.setEnabled(enabled)
            w.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
            if not isinstance(w, QComboBox):
                w.setFocusPolicy(Qt.StrongFocus if enabled else Qt.NoFocus)

    def _new_product(self):
        nid = max((p["id"] for p in self.products), default=0) + 1
        p = {
            "id": nid,
            "sku": f"NEW-{nid:04d}",
            "name": "",
            "group": D.ITEM_GROUPS[0],
            "hsn": "",
            "unit": "Pcs",
            "sale_rate": 0.0,
            "purchase_rate": 0.0,
            "rate": 0.0,
            "gst": 18,
            "stock": 0,
            "warehouse": D.WAREHOUSES[0] if D.WAREHOUSES else "",
            "min_stock": 0,
            "opening_qty": 0,
        }
        self.products.append(p)
        self._selected_id = nid
        self._refresh_metrics()
        self._rebuild_list()
        self._load_detail()
        self._set_editing(True)
        self.name.setFocus()
        self.name.setPlaceholderText("Enter new product description...")
        toast(self, "New product — fill details and Save (Ctrl+S).")

    def _save(self):
        p = self._current()
        if not p:
            return
        name = self.name.text().strip()
        if not name:
            self._set_editing(True)
            self.name.setFocus()
            toast(self, "Product name is required.")
            return
        p["name"] = name
        p["group"] = self.group.currentText()
        p["unit"] = self.unit.currentText()
        p["hsn"] = self.hsn.text().strip()
        p["stock"] = self.stock.value()
        p["purchase_rate"] = self.purchase_rate.value()
        p["sale_rate"] = self.sale_rate.value()
        p["rate"] = p["sale_rate"]
        self._refresh_metrics()
        self._rebuild_list()
        self._load_detail()
        self._set_editing(True)
        toast(self, f"Saved: {p['name']}")

    def _footer(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(8)
        for key, label in (
            ("F3", "New Product"),
            ("Ctrl+S", "Save Product"),
            ("Ctrl+F", "Search List"),
            ("Esc", "Back to Dashboard"),
        ):
            lay.addWidget(S.kbd(key))
            t = QLabel(label)
            t.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 10px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(t)
            lay.addSpacing(6)
        lay.addStretch()
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {S.PRIMARY}; border-radius: 4px; border: none;")
        st = QLabel("Sri Lakshmi Electricals · Simple Master v1")
        st.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(dot)
        lay.addWidget(st)
        return box
