"""5. Godown Master (Storage & Locations) — Stitch-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QScrollArea,
    QSizePolicy, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap
from app.widgets import stitch_ui as S


class GodownsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = [dict(g) for g in D.GODOWNS]
        self._selected_id = self.rows[0]["id"] if self.rows else None
        self._editing = False

        self.setObjectName("godownRoot")
        self.setStyleSheet(f"QWidget#godownRoot {{ background: {T.BG_CANVAS}; }}")

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

        body.addWidget(self._page_header())
        body.addWidget(self._workspace(), stretch=1)
        body.addWidget(self._footer())

        scroll.setWidget(host)
        root.addWidget(scroll)

        QShortcut(QKeySequence("F3"), self, activated=self._new)
        QShortcut(QKeySequence("F4"), self, activated=self._enter_edit)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Delete"), self, activated=self._delete)

        self._rebuild_list()
        self._load_detail()
        self._set_editing(False)

    def _page_header(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(4)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(22, 22)
        ic.setPixmap(icon_pixmap("warehouse", size=20, color=S.PRIMARY))
        ttl = QLabel("5. Godown & Location Master")
        ttl.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ic)
        title_row.addWidget(ttl)
        title_row.addWidget(S.pill("Primary Setup", "primary"))
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
        actions.addWidget(S.action_btn("+ New Godown", "F3", "add_box", "primary", self._new))
        actions.addWidget(S.action_btn("Edit", "F4", "edit", "secondary", self._enter_edit))
        actions.addWidget(S.action_btn("Save", "Ctrl+S", "save", "secondary", self._save))
        actions.addWidget(S.action_btn("Delete", "Del", "delete", "danger", self._delete))

        lay.addLayout(left, stretch=1)
        lay.addLayout(actions)
        return box

    def _workspace(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._left_panel(), stretch=3)
        lay.addWidget(self._right_panel(), stretch=9)
        return wrap

    # ── Left list ────────────────────────────────────────────
    def _left_panel(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        col.setMinimumWidth(260)
        col.setMaximumWidth(340)
        lay = QVBoxLayout(col)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        box = S.card()
        bl = QVBoxLayout(box)
        bl.setContentsMargins(10, 10, 10, 10)
        bl.setSpacing(8)

        head = QHBoxLayout()
        ttl = QLabel("Storage Locations")
        ttl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.units_pill = S.pill(f"{len(self.rows)} units", "neutral")
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
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setPixmap(icon_pixmap("search", size=16, color=S.SECONDARY))
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter code, name, shed...")
        self.filter.setStyleSheet(
            "QLineEdit { background: transparent; border: none; font-size: 12px; }"
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
        bl.addWidget(list_wrap)

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
        lay.addWidget(box)

        # Depot glance
        glance = S.card()
        gl = QVBoxLayout(glance)
        gl.setContentsMargins(10, 10, 10, 10)
        gl.setSpacing(6)
        gt = QLabel("Depot Operations Glance")
        gt.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        gl.addWidget(gt)
        total_items = sum(g.get("item_count", 0) for g in self.rows)
        gl.addWidget(self._glance_row("Current SKUs Mapped", f"{total_items} Items", primary=True))
        gl.addWidget(self._glance_row("Active Dispatch Terminal", "Gate #01 / Guindy"))
        lay.addWidget(glance)
        lay.addStretch(1)
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
            if q and q not in g["name"].lower() and q not in g.get("code", "").lower() \
                    and q not in g.get("location_label", "").lower():
                continue
            self.list_host.addWidget(self._godown_card(g))
        self.units_pill.setText(f"{len(self.rows)} units")
        self.reg_lbl.setText(f"{len(self.rows)} / 10 Allowed")

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
        name_color = S.PRIMARY if selected else T.TEXT_PRIMARY
        name.setStyleSheet(
            f"color: {name_color}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        code = S.pill(g.get("code", ""), "primary" if selected else "neutral")
        top.addWidget(name)
        top.addStretch()
        top.addWidget(code)
        lay.addLayout(top)

        meta = QHBoxLayout()
        meta.setSpacing(4)
        mic = QLabel()
        mic.setFixedSize(14, 14)
        mic.setPixmap(
            icon_pixmap(g.get("icon", "warehouse"), size=13, color=S.SECONDARY)
        )
        mtxt = QLabel(f"{g.get('location_label', '')}  ·  {g.get('item_count', 0)} Items")
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
        self._selected_id = gid
        self._rebuild_list()
        self._load_detail()
        self._set_editing(False)

    def _current(self) -> dict | None:
        for g in self.rows:
            if g["id"] == self._selected_id:
                return g
        return None

    # ── Right detail ─────────────────────────────────────────
    def _right_panel(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        self.right_lay = QVBoxLayout(col)
        self.right_lay.setContentsMargins(0, 0, 0, 0)
        self.right_lay.setSpacing(12)

        # Identification
        id_card = S.card()
        id_outer = QVBoxLayout(id_card)
        id_outer.setContentsMargins(0, 0, 0, 0)
        id_outer.setSpacing(0)
        self.ref_lbl = QLabel("System Ref ID: —")
        self.ref_lbl.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        id_outer.addWidget(S.section_head("Godown Identification", "badge", self.ref_lbl))
        id_body = QWidget()
        id_body.setStyleSheet("background: transparent;")
        idl = QVBoxLayout(id_body)
        idl.setContentsMargins(14, 12, 14, 14)
        idl.setSpacing(10)

        self.name = QLineEdit()
        self.code = QLineEdit()
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        name_f = S.labeled_input("Godown Name", self.name, required=True)
        code_f = S.labeled_input("Godown Code", self.code, required=True)
        # Status toggle
        status_wrap = QWidget()
        status_wrap.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(status_wrap)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(4)
        scap = QLabel("Godown Status")
        scap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        sl.addWidget(scap)
        self.status_chip = QFrame()
        self.status_chip.setFixedHeight(36)
        self.status_chip.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; }}"
        )
        scl = QHBoxLayout(self.status_chip)
        scl.setContentsMargins(10, 0, 10, 0)
        self.status_txt = QLabel("Active Depot")
        self.status_txt.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        tog = QLabel()
        tog.setFixedSize(22, 22)
        tog.setPixmap(icon_pixmap("toggle_on", size=20, color=S.PRIMARY))
        scl.addWidget(self.status_txt)
        scl.addStretch()
        scl.addWidget(tog)
        sl.addWidget(self.status_chip)
        hint = QLabel("Available in sales/purchase dropdown")
        hint.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        sl.addWidget(hint)

        row1.addWidget(name_f, stretch=6)
        row1.addWidget(code_f, stretch=3)
        row1.addWidget(status_wrap, stretch=3)
        idl.addLayout(row1)
        name_hint = QLabel("Name printed on Delivery Challans & Transfer Vouchers")
        name_hint.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        idl.addWidget(name_hint)
        id_outer.addWidget(id_body)
        self.right_lay.addWidget(id_card)

        # Location & contact
        loc_card = S.card()
        loc_outer = QVBoxLayout(loc_card)
        loc_outer.setContentsMargins(0, 0, 0, 0)
        loc_outer.setSpacing(0)
        loc_outer.addWidget(S.section_head("Location & In-Charge Contact", "location_on"))
        loc_body = QWidget()
        loc_body.setStyleSheet("background: transparent;")
        locl = QVBoxLayout(loc_body)
        locl.setContentsMargins(14, 12, 14, 14)
        locl.setSpacing(10)
        self.address = QTextEdit()
        self.address.setFixedHeight(64)
        self.incharge = QLineEdit()
        self.phone = QLineEdit()
        self.alt_phone = QLineEdit()
        locl.addWidget(S.labeled_input("Physical Warehouse Address", self.address))
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        row2.addWidget(S.labeled_input("In-Charge Supervisor Name", self.incharge), 1)
        row2.addWidget(S.labeled_input("Contact Phone", self.phone), 1)
        row2.addWidget(S.labeled_input("Alternate Line", self.alt_phone), 1)
        locl.addLayout(row2)
        loc_outer.addWidget(loc_body)
        self.right_lay.addWidget(loc_card)

        # Stock summary
        stock_card = S.card()
        stock_outer = QVBoxLayout(stock_card)
        stock_outer.setContentsMargins(0, 0, 0, 0)
        stock_outer.setSpacing(0)
        stock_outer.addWidget(S.section_head("Stock Summary in this Godown", "inventory_2"))
        stock_body = QWidget()
        stock_body.setStyleSheet("background: transparent;")
        sbl = QVBoxLayout(stock_body)
        sbl.setContentsMargins(12, 8, 12, 12)
        self.stock_table = QTableWidget(0, 6)
        self.stock_table.setHorizontalHeaderLabels(
            ["ITEM CODE", "PRODUCT DESCRIPTION", "CATEGORY GROUP", "CURRENT QTY", "UNIT", "EST. VALUE (₹)"]
        )
        self.stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.stock_table.verticalHeader().setVisible(False)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stock_table.setSelectionMode(QTableWidget.NoSelection)
        self.stock_table.setFocusPolicy(Qt.NoFocus)
        self.stock_table.setShowGrid(False)
        self.stock_table.setStyleSheet(
            f"""
            QTableWidget {{ background: {T.SURFACE}; border: 1px solid {T.BORDER};
                border-radius: 4px; }}
            QHeaderView::section {{ background: {S.HEADER_GREY}; color: {S.SECONDARY};
                font-size: 10px; font-weight: 700; padding: 6px 8px; border: none;
                border-bottom: 1px solid {T.BORDER}; }}
            QTableWidget::item {{ padding: 6px 8px; border-bottom: 1px solid {T.BORDER}; }}
            """
        )
        sbl.addWidget(self.stock_table)
        self.stock_footer = QLabel()
        self.stock_footer.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent; padding: 4px 2px;"
        )
        sbl.addWidget(self.stock_footer)
        stock_outer.addWidget(stock_body)
        self.right_lay.addWidget(stock_card)
        self.right_lay.addStretch(1)
        return col

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
        self.status_txt.setText("Active Depot" if g.get("active", True) else "Inactive")

        stock = D.GODOWN_STOCK.get(g["id"], [])
        self.stock_table.setRowCount(len(stock))
        total_qty = 0.0
        total_val = 0.0
        for r, row in enumerate(stock):
            code = QTableWidgetItem(row["sku"])
            code.setForeground(Qt.blue)
            self.stock_table.setItem(r, 0, code)
            self.stock_table.setItem(r, 1, QTableWidgetItem(row["name"]))
            self.stock_table.setItem(r, 2, QTableWidgetItem(row["group"]))
            self.stock_table.setItem(r, 3, QTableWidgetItem(f"{row['qty']:,.2f}"))
            self.stock_table.setItem(r, 4, QTableWidgetItem(row["unit"]))
            self.stock_table.setItem(r, 5, QTableWidgetItem(format_inr_indian(row["value"])))
            total_qty += float(row["qty"])
            total_val += float(row["value"])
        self.stock_table.setFixedHeight(28 + max(len(stock), 1) * 32)
        self.stock_footer.setText(
            f"Sampled inventory: {total_qty:,.2f} qty    ·    "
            f"Est. value {format_inr_indian(total_val)}"
        )

    def _fields(self):
        return [self.name, self.code, self.address, self.incharge, self.phone, self.alt_phone]

    def _set_editing(self, enabled: bool):
        self._editing = enabled
        for w in self._fields():
            if hasattr(w, "setReadOnly"):
                w.setReadOnly(not enabled)
            w.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
            w.setFocusPolicy(Qt.StrongFocus if enabled else Qt.NoFocus)

    def _enter_edit(self):
        self._set_editing(True)
        self.name.setFocus()

    def _new(self):
        nid = max((g["id"] for g in self.rows), default=0) + 1
        g = {
            "id": nid,
            "code": f"GDN-{nid:02d}",
            "name": f"New Godown {nid}",
            "ref_id": f"GDN-REC-{10000 + nid}",
            "incharge": "",
            "phone": "",
            "alt_phone": "",
            "address": "",
            "location_label": "New Location",
            "item_count": 0,
            "status": "Active",
            "role_tag": "Storage",
            "active": True,
            "is_default": False,
            "icon": "warehouse",
        }
        self.rows.append(g)
        self._selected_id = nid
        self._rebuild_list()
        self._load_detail()
        self._set_editing(True)
        toast(self, "New godown created — fill details and Save.")

    def _save(self):
        g = self._current()
        if not g:
            return
        g["name"] = self.name.text().strip() or g["name"]
        g["code"] = self.code.text().strip() or g["code"]
        g["address"] = self.address.toPlainText().strip()
        g["incharge"] = self.incharge.text().strip()
        g["phone"] = self.phone.text().strip()
        g["alt_phone"] = self.alt_phone.text().strip()
        self._set_editing(False)
        self._rebuild_list()
        toast(self, "Godown saved.")

    def _delete(self):
        g = self._current()
        if not g:
            return
        self.rows = [x for x in self.rows if x["id"] != g["id"]]
        self._selected_id = self.rows[0]["id"] if self.rows else None
        self._rebuild_list()
        self._load_detail()
        toast(self, f"Deleted: {g['name']}")

    def _footer(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(8)
        tip = QLabel("Keyboard:")
        tip.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 10px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
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
                f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
            )
            lay.addWidget(t)
            lay.addSpacing(4)
        lay.addStretch()
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {S.PRIMARY}; border-radius: 4px; border: none;")
        st = QLabel("Terminal Sync: Verified (Port 8042)")
        st.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        lay.addWidget(dot)
        lay.addWidget(st)
        return box
