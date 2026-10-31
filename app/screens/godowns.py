"""5. Godown Master (Storage & Locations) — Stitch-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QScrollArea,
    QSizePolicy, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import confirm_delete, confirm_save, format_inr_indian, toast
from app.widgets.icons import icon_pixmap
from app.widgets import stitch_ui as S


class GodownsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = [dict(g) for g in D.GODOWNS]
        self._selected_id = self.rows[0]["id"] if self.rows else None
        self._editing = False
        self._draft = None

        self.setObjectName("godownRoot")
        self.setStyleSheet(f"QWidget#godownRoot {{ background: {T.BG_CANVAS}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(self._page_header())
        root.addWidget(self._workspace(), stretch=1)
        root.addWidget(self._footer())

        QShortcut(QKeySequence("F3"), self, activated=self._new)
        QShortcut(QKeySequence("F4"), self, activated=self._enter_edit)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Delete"), self, activated=self._delete)

        self._rebuild_list()
        self._load_detail()
        self._set_editing(False)

    # ── Header ───────────────────────────────────────────────
    def _page_header(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(22, 22)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap("warehouse", size=20, color=S.PRIMARY))
        ttl = QLabel("5. Godown & Location Master")
        ttl.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        badge = QLabel("Primary Setup")
        badge.setStyleSheet(
            f"color: {S.PRIMARY}; background: {S.SURFACE_GREY}; border: none; "
            f"border-radius: 3px; padding: 2px 6px; font-size: 9px; font-weight: 700;"
        )
        title_row.addWidget(ic)
        title_row.addWidget(ttl)
        title_row.addWidget(badge)
        title_row.addStretch()
        sub = QLabel(
            "Manage physical storage warehouses, shop floors and racks for stock inward/outward"
        )
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        left.addLayout(title_row)
        left.addWidget(sub)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(
            S.action_btn("+ New Godown", "F3", "add_box", "primary", self._new)
        )
        actions.addWidget(
            S.action_btn("Edit", "F4", "edit", "secondary", self._enter_edit)
        )
        actions.addWidget(
            S.action_btn("Save", "Ctrl+S", "save", "save", self._save)
        )
        actions.addWidget(
            S.action_btn("Delete", "Del", "delete", "danger", self._delete)
        )

        lay.addLayout(left, stretch=1)
        lay.addLayout(actions)
        return box

    def _workspace(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._left_panel())
        lay.addWidget(self._right_panel(), stretch=1)
        return wrap

    # ── Left list ────────────────────────────────────────────
    def _left_panel(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        col.setFixedWidth(300)
        lay = QVBoxLayout(col)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        box = S.card()
        bl = QVBoxLayout(box)
        bl.setContentsMargins(12, 12, 12, 12)
        bl.setSpacing(8)

        head = QHBoxLayout()
        ttl = QLabel("Storage Locations")
        ttl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.units_pill = QLabel(f"{len(self.rows)} units")
        self.units_pill.setStyleSheet(
            f"color: {S.SECONDARY}; background: {S.HEADER_GREY}; border: none; "
            f"border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: 600;"
        )
        head.addWidget(ttl)
        head.addStretch()
        head.addWidget(self.units_pill)
        bl.addLayout(head)

        search_box = QFrame()
        search_box.setFixedHeight(32)
        search_box.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; }}"
        )
        sw = QHBoxLayout(search_box)
        sw.setContentsMargins(8, 0, 8, 0)
        sw.setSpacing(6)
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setStyleSheet("background: transparent; border: none;")
        sic.setPixmap(icon_pixmap("search", size=16, color=S.SECONDARY))
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter code, name, shed...")
        self.filter.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; font-size: 12px; "
            f"color: {T.TEXT_PRIMARY}; }}"
        )
        self.filter.textChanged.connect(self._rebuild_list)
        sw.addWidget(sic)
        sw.addWidget(self.filter, stretch=1)
        bl.addWidget(search_box)

        self.list_host = QVBoxLayout()
        self.list_host.setSpacing(6)
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
        bl.addWidget(list_scroll, stretch=1)

        reg = QFrame()
        reg.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; }}"
        )
        rl = QHBoxLayout(reg)
        rl.setContentsMargins(10, 8, 10, 8)
        r1 = QLabel("Godowns Registered:")
        r1.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        self.reg_lbl = QLabel(f"{len(self.rows)} / 10 Allowed")
        self.reg_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        rl.addWidget(r1)
        rl.addStretch()
        rl.addWidget(self.reg_lbl)
        bl.addWidget(reg)
        lay.addWidget(box, stretch=1)

        # Depot glance
        glance = S.card()
        gl = QVBoxLayout(glance)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setSpacing(6)
        gt = QLabel("Depot Operations Glance")
        gt.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        gl.addWidget(gt)
        self.glance_skus = self._glance_row("Current SKUs Mapped", "0 Items", primary=True)
        self.glance_term = self._glance_row(
            "Active Dispatch Terminal", "Gate #01 / Ranigunj"
        )
        gl.addWidget(self.glance_skus)
        gl.addWidget(self.glance_term)
        lay.addWidget(glance)
        return col

    def _glance_row(self, k: str, v: str, primary: bool = False) -> QFrame:
        row = QFrame()
        row.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; }}"
        )
        lay = QHBoxLayout(row)
        lay.setContentsMargins(8, 6, 8, 6)
        a = QLabel(k)
        a.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        b = QLabel(v)
        b.setObjectName("glanceVal")
        color = S.PRIMARY if primary else T.TEXT_PRIMARY
        b.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(a)
        lay.addStretch()
        lay.addWidget(b)
        return row

    def _rebuild_list(self):
        while self.list_host.count():
            item = self.list_host.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        q = self.filter.text().strip().lower()
        for g in self.rows:
            hay = f"{g['name']} {g.get('code', '')} {g.get('location_label', '')}".lower()
            if q and q not in hay:
                continue
            self.list_host.addWidget(self._godown_card(g))
        self.list_host.addStretch(1)
        self.units_pill.setText(f"{len(self.rows)} units")
        self.reg_lbl.setText(f"{len(self.rows)} / 10 Allowed")
        total_items = sum(int(g.get("item_count", 0)) for g in self.rows)
        val = self.glance_skus.findChild(QLabel, "glanceVal")
        if val:
            val.setText(f"{total_items} Items")

    def _godown_card(self, g: dict) -> QFrame:
        selected = g["id"] == self._selected_id
        card = QFrame()
        card.setCursor(QCursor(Qt.PointingHandCursor))
        if selected:
            card.setStyleSheet(
                f"QFrame {{ background: {S.SURFACE_GREY}; border: none; border-radius: 4px; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
                f"QFrame:hover {{ background: {S.HEADER_GREY}; }}"
            )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        top = QHBoxLayout()
        name = QLabel(g["name"])
        name.setStyleSheet(
            f"color: {S.PRIMARY if selected else T.TEXT_PRIMARY}; "
            f"font-size: 12px; font-weight: 700; border: none; background: transparent;"
        )
        code = QLabel(g.get("code", ""))
        if selected:
            code.setStyleSheet(
                f"color: {S.PRIMARY}; background: {T.SURFACE}; border: none; "
                f"border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: 700;"
            )
        else:
            code.setStyleSheet(
                f"color: {S.SECONDARY}; background: {S.HEADER_GREY}; border: none; "
                f"border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: 600;"
            )
        top.addWidget(name)
        top.addStretch()
        top.addWidget(code)
        lay.addLayout(top)

        meta = QHBoxLayout()
        meta.setSpacing(4)
        mic = QLabel()
        mic.setFixedSize(14, 14)
        mic.setStyleSheet("background: transparent; border: none;")
        mic.setPixmap(
            icon_pixmap(
                g.get("icon", "warehouse"), size=13,
                color=S.PRIMARY if selected else S.SECONDARY,
            )
        )
        mtxt = QLabel(
            f"{g.get('location_label', '')}  ·  {g.get('item_count', 0)} Items"
        )
        mtxt.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        meta.addWidget(mic)
        meta.addWidget(mtxt)
        meta.addStretch()
        lay.addLayout(meta)

        foot = QHBoxLayout()
        status = QLabel(f"●  {g.get('status', 'Active')}")
        status.setStyleSheet(
            f"color: {S.PRIMARY if selected else S.SECONDARY}; font-size: 10px; "
            f"font-weight: 600; border: none; background: transparent;"
        )
        tag = QLabel(g.get("role_tag", ""))
        tag.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        foot.addWidget(status)
        foot.addStretch()
        foot.addWidget(tag)
        lay.addLayout(foot)

        card.mousePressEvent = lambda e, gid=g["id"]: self._select(gid)
        return card

    def _select(self, gid: int):
        self._draft = None
        self._selected_id = gid
        self._rebuild_list()
        self._load_detail()
        self._set_editing(False)

    # ── Right detail ─────────────────────────────────────────
    def _right_panel(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        self.right_lay = QVBoxLayout(col)
        self.right_lay.setContentsMargins(0, 0, 0, 0)
        self.right_lay.setSpacing(12)

        self.right_lay.addWidget(self._id_card())
        self.right_lay.addWidget(self._loc_card())
        self.right_lay.addWidget(self._stock_card(), stretch=1)
        return col

    def _soft_field(self, widget: QWidget):
        from app.widgets.icons import combo_dropdown_qss

        widget.setStyleSheet(
            f"""
            QLineEdit, QTextEdit, QComboBox {{
                background: {S.INPUT_BG}; border: none; border-radius: 4px;
                padding: 6px 10px; font-size: 12px; font-weight: 600;
                color: {T.TEXT_PRIMARY};
                selection-background-color: {S.PRIMARY}; selection-color: white;
            }}
            QComboBox {{
                padding-right: 28px;
            }}
            {combo_dropdown_qss(width=24, background="transparent")}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                background: {T.SURFACE}; border: 1px solid {S.PRIMARY};
            }}
            """
        )

    def _labeled(
        self, label: str, widget: QWidget, *, required: bool = False, hint: str = ""
    ) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        top = QHBoxLayout()
        top.setSpacing(3)
        cap = QLabel(label)
        cap.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        top.addWidget(cap)
        if required:
            star = QLabel("*")
            star.setStyleSheet(
                f"color: {S.ERROR}; font-size: 12px; font-weight: 700; "
                f"border: none; background: transparent;"
            )
            top.addWidget(star)
        top.addStretch()
        lay.addLayout(top)
        lay.addWidget(widget)
        if hint:
            h = QLabel(hint)
            h.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
            )
            h.setWordWrap(True)
            lay.addWidget(h)
        return wrap

    def _id_card(self) -> QFrame:
        card = S.card()
        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)

        head = QHBoxLayout()
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap("badge", size=18, color=S.PRIMARY))
        ttl = QLabel("Godown Identification")
        ttl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.ref_lbl = QLabel("System Ref ID: —")
        self.ref_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        head.addWidget(ic)
        head.addWidget(ttl)
        head.addStretch()
        head.addWidget(self.ref_lbl)
        outer.addLayout(head)

        self.name = QLineEdit()
        self.code = QLineEdit()
        self._soft_field(self.name)
        self._soft_field(self.code)
        self.name.setFixedHeight(36)
        self.code.setFixedHeight(36)

        # Status dropdown (Active / Inactive) — same pattern as Users
        status_wrap = QWidget()
        status_wrap.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(status_wrap)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(4)
        scap = QLabel("Godown Status")
        scap.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        sl.addWidget(scap)
        from app.widgets.icons import combo_dropdown_qss
        self.status = QComboBox()
        self.status.addItems([
            "Active (Available in sales/purchase)",
            "Inactive (Hidden from vouchers)",
        ])
        self.status.setFixedHeight(36)
        self.status.setStyleSheet(
            f"""
            QComboBox {{
                background: {S.INPUT_BG}; border: none; border-radius: 4px;
                padding: 6px 28px 6px 10px; font-size: 12px; font-weight: 600;
                color: {S.PRIMARY};
            }}
            {combo_dropdown_qss(width=22, background=S.INPUT_BG)}
            """
        )
        sl.addWidget(self.status)
        shint = QLabel("Available in sales/purchase dropdown")
        shint.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        sl.addWidget(shint)

        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(
            self._labeled(
                "Godown Name", self.name, required=True,
                hint="Name printed on Delivery Challans & Transfer Vouchers",
            ),
            stretch=6,
        )
        row.addWidget(
            self._labeled(
                "Godown Code", self.code, required=True,
                hint="Short unique identifier",
            ),
            stretch=3,
        )
        row.addWidget(status_wrap, stretch=3)
        outer.addLayout(row)
        return card

    def _loc_card(self) -> QFrame:
        card = S.card()
        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)

        head = QHBoxLayout()
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap("place", size=18, color=S.PRIMARY))
        ttl = QLabel("Location & In-Charge Contact")
        ttl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.pin_zone = QLabel("")
        self.pin_zone.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        head.addWidget(ic)
        head.addWidget(ttl)
        head.addStretch()
        head.addWidget(self.pin_zone)
        outer.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(12)

        # Address
        self.address = QTextEdit()
        self.address.setFixedHeight(84)
        self._soft_field(self.address)
        body.addWidget(
            self._labeled(
                "Physical Warehouse Address", self.address,
                hint="Used for E-Way bill generation and delivery transit notes",
            ),
            stretch=1,
        )

        # Contact column
        contact = QWidget()
        contact.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(contact)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)

        # In-charge with person icon
        in_wrap = QWidget()
        in_wrap.setStyleSheet("background: transparent;")
        il = QVBoxLayout(in_wrap)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(4)
        icap = QLabel("In-Charge Supervisor Name")
        icap.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        il.addWidget(icap)
        in_box = QFrame()
        in_box.setFixedHeight(36)
        in_box.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; }}"
        )
        ibl = QHBoxLayout(in_box)
        ibl.setContentsMargins(8, 0, 8, 0)
        ibl.setSpacing(6)
        pic = QLabel()
        pic.setFixedSize(16, 16)
        pic.setStyleSheet("background: transparent; border: none;")
        pic.setPixmap(icon_pixmap("person", size=16, color=S.SECONDARY))
        self.incharge = QLineEdit()
        self.incharge.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; font-size: 12px; "
            f"font-weight: 600; color: {T.TEXT_PRIMARY}; }}"
        )
        ibl.addWidget(pic)
        ibl.addWidget(self.incharge, stretch=1)
        il.addWidget(in_box)
        cl.addWidget(in_wrap)

        phones = QHBoxLayout()
        phones.setSpacing(10)
        self.phone = QLineEdit()
        self.alt_phone = QLineEdit()
        self._soft_field(self.phone)
        self._soft_field(self.alt_phone)
        self.phone.setFixedHeight(36)
        self.alt_phone.setFixedHeight(36)
        phones.addWidget(self._labeled("Contact Phone", self.phone), 1)
        phones.addWidget(self._labeled("Alternate Line", self.alt_phone), 1)
        cl.addLayout(phones)
        cl.addStretch()

        body.addWidget(contact, stretch=1)
        outer.addLayout(body)
        return card

    def _stock_card(self) -> QFrame:
        card = S.card()
        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap("inventory_2", size=18, color=S.PRIMARY))
        ttl = QLabel("Stock Summary in this Godown")
        ttl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.live_badge = QLabel("Live Inventory")
        self.live_badge.setStyleSheet(
            f"color: {S.PRIMARY}; background: {S.HEADER_GREY}; border: none; "
            f"border-radius: 3px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
        head.addWidget(ic)
        head.addWidget(ttl)
        head.addWidget(self.live_badge)
        head.addStretch()
        head.addWidget(
            self._mini_btn("Filter Group", "tune", lambda: toast(self, "Filter by group…"))
        )
        head.addWidget(
            self._mini_btn("Export XLS", "download", lambda: toast(self, "Exporting XLS…"))
        )
        outer.addLayout(head)

        self.stock_table = QTableWidget(0, 6)
        self.stock_table.setHorizontalHeaderLabels(
            [
                "Item Code", "Product Description", "Category Group",
                "Current Qty", "Unit", "Est. Value (₹)",
            ]
        )
        hdr = self.stock_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stock_table.setSelectionMode(QTableWidget.NoSelection)
        self.stock_table.setFocusPolicy(Qt.NoFocus)
        self.stock_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        S.apply_table_style(self.stock_table)
        outer.addWidget(self.stock_table, stretch=1)

        # Totals footer strip (Stitch tfoot)
        self.stock_footer = QFrame()
        self.stock_footer.setStyleSheet(
            f"QFrame {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        fl = QHBoxLayout(self.stock_footer)
        fl.setContentsMargins(T.TABLE_PAD_X, T.TABLE_PAD_Y, T.TABLE_PAD_X, T.TABLE_PAD_Y)
        self.stock_total_lbl = QLabel("Total Sampled Inventory in Godown")
        self.stock_total_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        self.stock_qty_lbl = QLabel("0.00")
        self.stock_qty_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.stock_qty_lbl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        dash = QLabel("—")
        dash.setAlignment(Qt.AlignCenter)
        dash.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        self.stock_val_lbl = QLabel("₹ 0.00")
        self.stock_val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.stock_val_lbl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        fl.addWidget(self.stock_total_lbl, stretch=3)
        fl.addWidget(self.stock_qty_lbl, stretch=1)
        fl.addWidget(dash, stretch=0)
        fl.addWidget(self.stock_val_lbl, stretch=1)
        outer.addWidget(self.stock_footer)
        return card

    def _mini_btn(self, label: str, icon: str, on_click) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(26)
        btn.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; }}"
            f"QFrame:hover {{ background: {S.SURFACE_GREY}; }}"
        )
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap(icon, size=14, color=S.SECONDARY))
        txt = QLabel(label)
        txt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(ic)
        lay.addWidget(txt)
        btn.mousePressEvent = (
            lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
        )
        return btn

    def _load_detail(self):
        g = self._current()
        if not g:
            return
        self.ref_lbl.setText(f"System Ref ID: {g.get('ref_id', '—')}")
        self.name.setText(g.get("name", ""))
        self.code.setText(g.get("code", ""))
        self.address.setPlainText(g.get("address", ""))
        self.incharge.setText(g.get("incharge", ""))
        self.phone.setText(g.get("phone", ""))
        self.alt_phone.setText(g.get("alt_phone", ""))
        self.status.setCurrentIndex(0 if g.get("active", True) else 1)
        self.pin_zone.setText(g.get("pin_zone", ""))
        self.live_badge.setText(f"{g.get('code', '')} Live Inventory")

        stock = D.GODOWN_STOCK.get(g["id"], []) if g.get("id") else []
        self.stock_table.setRowCount(len(stock))
        total_qty = 0.0
        total_val = 0.0
        for r, row in enumerate(stock):
            # Alternating row tint via background brush is awkward; keep clean rows
            code = QTableWidgetItem(row["sku"])
            code.setForeground(Qt.GlobalColor.blue)
            f = code.font()
            f.setBold(True)
            code.setFont(f)
            self.stock_table.setItem(r, 0, code)

            self.stock_table.setItem(r, 1, QTableWidgetItem(row["name"]))

            grp = QTableWidgetItem(row["group"])
            grp.setForeground(Qt.GlobalColor.darkGray)
            self.stock_table.setItem(r, 2, grp)

            qty = QTableWidgetItem(f"{row['qty']:,.2f}")
            qty.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            f = qty.font()
            f.setBold(True)
            qty.setFont(f)
            self.stock_table.setItem(r, 3, qty)

            unit = QTableWidgetItem(row["unit"])
            unit.setTextAlignment(Qt.AlignCenter)
            unit.setForeground(Qt.GlobalColor.darkGray)
            self.stock_table.setItem(r, 4, unit)

            val = QTableWidgetItem(f"{row['value']:,.2f}")
            val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.stock_table.setItem(r, 5, val)

            total_qty += float(row["qty"])
            total_val += float(row["value"])

        total_lines = int(g.get("item_count", len(stock)))
        self.stock_total_lbl.setText(
            f"Total Sampled Inventory in Godown ({len(stock)} of {total_lines} lines)"
        )
        self.stock_qty_lbl.setText(f"{total_qty:,.2f}")
        self.stock_val_lbl.setText(format_inr_indian(total_val))

    def _fields(self):
        return [
            self.name, self.code, self.address,
            self.incharge, self.phone, self.alt_phone, self.status,
        ]

    def _set_editing(self, enabled: bool):
        self._editing = enabled
        for w in self._fields():
            if isinstance(w, QComboBox):
                w.setEnabled(enabled)
            elif hasattr(w, "setReadOnly"):
                w.setReadOnly(not enabled)
            w.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
            if not isinstance(w, QComboBox):
                w.setFocusPolicy(Qt.StrongFocus if enabled else Qt.NoFocus)

    def _enter_edit(self):
        if not self._current():
            return
        self._set_editing(True)
        self.name.setFocus()

    def _current(self) -> dict | None:
        if self._draft is not None and self._selected_id is None:
            return self._draft
        for g in self.rows:
            if g["id"] == self._selected_id:
                return g
        return None

    def _new(self):
        n = len(self.rows) + 1
        self._draft = {
            "id": None,
            "code": f"GDN-{n:02d}",
            "name": "",
            "ref_id": "",
            "incharge": "",
            "phone": "",
            "alt_phone": "",
            "address": "",
            "location_label": "New Location",
            "pin_zone": "",
            "item_count": 0,
            "status": "Active",
            "role_tag": "Storage",
            "active": True,
            "is_default": len(self.rows) == 0,
            "_is_new": True,
        }
        self._selected_id = None
        self._rebuild_list()
        self.ref_lbl.setText("System Ref ID: (new)")
        self.name.setText("")
        self.code.setText(self._draft["code"])
        self.address.setPlainText("")
        self.incharge.setText("")
        self.phone.setText("")
        self.alt_phone.setText("")
        self.status.setCurrentIndex(0)
        self.pin_zone.setText("")
        self.live_badge.setText("New Godown")
        self.stock_table.setRowCount(0)
        self._set_editing(True)
        self.name.setFocus()
        toast(self, "New godown — fill details and Save.")

    def _save(self):
        from app.services import godowns as godowns_svc

        if not self._editing:
            toast(self, "Click Edit before saving.")
            return
        g = self._current()
        if not g:
            return
        name = self.name.text().strip()
        if not name:
            toast(self, "Godown name is required.")
            self.name.setFocus()
            return
        if not confirm_save(self, f"godown “{name}”"):
            return
        active = self.status.currentIndex() == 0
        payload = {
            **g,
            "name": name,
            "code": self.code.text().strip() or g.get("code") or "GDN-01",
            "address": self.address.toPlainText().strip(),
            "incharge": self.incharge.text().strip(),
            "phone": self.phone.text().strip(),
            "alt_phone": self.alt_phone.text().strip(),
            "active": active,
            "status": "Active" if active else "Inactive",
            "is_default": g.get("is_default", False),
        }
        try:
            if g.get("_is_new") or g.get("id") is None:
                saved = godowns_svc.create_godown(payload)
                self._draft = None
            else:
                saved = godowns_svc.update_godown(g["id"], payload)
        except Exception as exc:
            toast(self, f"Save failed: {exc}")
            return
        D.reload()
        self.rows = [dict(x) for x in D.GODOWNS]
        self._selected_id = saved["id"] if saved else None
        self._set_editing(False)
        self._rebuild_list()
        self._load_detail()
        toast(self, "Godown saved.")

    def _delete(self):
        from app.services import godowns as godowns_svc

        g = self._current()
        if not g:
            return
        if g.get("_is_new") or g.get("id") is None:
            self._draft = None
            self._selected_id = self.rows[0]["id"] if self.rows else None
            self._rebuild_list()
            self._load_detail()
            self._set_editing(False)
            toast(self, "Draft discarded.")
            return
        name = g["name"]
        if not confirm_delete(self, f"godown “{name}”"):
            return
        godowns_svc.delete_godown(g["id"])
        D.reload()
        self.rows = [dict(x) for x in D.GODOWNS]
        self._selected_id = self.rows[0]["id"] if self.rows else None
        self._rebuild_list()
        self._load_detail()
        self._set_editing(False)
        toast(self, f"Deleted: {name}")

    def _footer(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(8)

        kbd_ic = QLabel()
        kbd_ic.setFixedSize(16, 16)
        kbd_ic.setStyleSheet("background: transparent; border: none;")
        kbd_ic.setPixmap(icon_pixmap("keyboard", size=15, color=S.SECONDARY))
        tip = QLabel("KEYBOARD ACCELERATORS:")
        tip.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(kbd_ic)
        lay.addWidget(tip)
        for key, label in (
            ("F3", "New Godown"),
            ("F4", "Edit Record"),
            ("Ctrl+S", "Save Changes"),
            ("Del", "Delete"),
            ("Esc", "Back to Masters"),
        ):
            lay.addWidget(S.kbd(key))
            t = QLabel(label)
            t.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
            )
            lay.addWidget(t)
            lay.addSpacing(6)
        lay.addStretch()
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {S.PRIMARY}; border-radius: 4px; border: none;")
        st = QLabel("Terminal Sync: Verified (Port 8042)")
        st.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        lay.addWidget(dot)
        lay.addWidget(st)
        return box
