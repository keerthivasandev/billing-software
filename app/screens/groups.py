"""3. Group Master (Product, Ledger & Godown Groups) — Stitch-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import format_inr_indian, toast
from app.widgets.icons import icon_pixmap
from app.widgets import stitch_ui as S

_MODES = (
    ("product", "Product Groups", "category", "Product Group"),
    ("ledger", "Common Ledger Groups", "account_balance", "Common (Ledger Group)"),
    ("godown", "Godown Groups", "warehouse", "Godown Group"),
)

_GST_OPTIONS = ["0% (Exempt)", "5%", "12%", "18% (Standard)", "28%"]
_PARENT_OPTIONS = [
    "Primary / Top-Level [Root]",
    "Domestic Electricals",
    "Industrial Supplies",
]


class GroupsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.product_groups = [dict(g) for g in D.PRODUCT_GROUP_RECORDS]
        self.ledger_groups = [dict(g) for g in D.LEDGER_GROUP_RECORDS]
        self.godown_groups = [dict(g) for g in D.GODOWN_GROUP_RECORDS]
        self._mode = "product"
        self._selected_id = self.product_groups[0]["id"] if self.product_groups else None

        self.setObjectName("groupRoot")
        self.setStyleSheet(f"QWidget#groupRoot {{ background: {T.BG_CANVAS}; }}")

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

        QShortcut(QKeySequence("F3"), self, activated=self._new_group)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())
        QShortcut(QKeySequence("Delete"), self, activated=self._delete)

        self._rebuild_list()
        self._load_detail()

    def _records(self) -> list:
        if self._mode == "ledger":
            return self.ledger_groups
        if self._mode == "godown":
            return self.godown_groups
        return self.product_groups

    def _mode_meta(self):
        for key, title, icon, type_label in _MODES:
            if key == self._mode:
                return title, icon, type_label
        return "Product Groups", "category", "Product Group"

    def _count_label(self, key: str) -> str:
        n = {
            "product": len(self.product_groups),
            "ledger": len(self.ledger_groups),
            "godown": len(self.godown_groups),
        }[key]
        return str(n)

    # ── Header + tabs ────────────────────────────────────────
    def _page_header(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(16)

        ic = QLabel()
        ic.setFixedSize(36, 36)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {S.PRIMARY}; border-radius: 6px; border: none;"
        )
        ic.setPixmap(icon_pixmap("folder_copy", size=20, color="#ffffff"))

        col = QVBoxLayout()
        col.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        ttl = QLabel("Group Master")
        ttl.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        title_row.addWidget(S.pill("Master Setup · 3", "neutral"))
        title_row.addStretch()
        sub = QLabel("Categorize catalog items, ledger accounts, and warehouse godowns")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        col.addLayout(title_row)
        col.addWidget(sub)

        # Tab switcher
        tabs_wrap = QFrame()
        tabs_wrap.setStyleSheet(
            f"QFrame {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; "
            f"border-radius: 6px; }}"
        )
        tabs = QHBoxLayout(tabs_wrap)
        tabs.setContentsMargins(4, 4, 4, 4)
        tabs.setSpacing(4)
        self._tab_btns = {}
        for key, title, icon, _ in _MODES:
            b = QFrame()
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setFixedHeight(32)
            b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            bl = QHBoxLayout(b)
            bl.setContentsMargins(10, 0, 8, 0)
            bl.setSpacing(6)
            i = QLabel()
            i.setFixedSize(16, 16)
            i.setObjectName("tabIcon")
            bl.addWidget(i)
            lbl = QLabel(title)
            lbl.setObjectName("tabLbl")
            bl.addWidget(lbl)
            cnt = QLabel(self._count_label(key))
            cnt.setObjectName("tabCnt")
            cnt.setAlignment(Qt.AlignCenter)
            bl.addWidget(cnt)
            b.mousePressEvent = lambda e, k=key: self._switch_mode(k)
            self._tab_btns[key] = (b, icon)
            tabs.addWidget(b)

        lay.addWidget(ic)
        lay.addLayout(col, stretch=1)
        lay.addWidget(tabs_wrap)
        self._style_tabs()
        return box

    def _style_tabs(self):
        for key, (b, icon) in self._tab_btns.items():
            active = key == self._mode
            lbl = b.findChild(QLabel, "tabLbl")
            cnt = b.findChild(QLabel, "tabCnt")
            ic = b.findChild(QLabel, "tabIcon")
            cnt.setText(self._count_label(key))
            if active:
                b.setStyleSheet(
                    f"QFrame {{ background: {T.SURFACE}; border: none; border-radius: 4px; }}"
                )
                if lbl:
                    lbl.setStyleSheet(
                        f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
                        f"border: none; background: transparent;"
                    )
                if cnt:
                    cnt.setStyleSheet(
                        f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; "
                        f"border-radius: 3px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
                    )
                if ic:
                    ic.setPixmap(icon_pixmap(icon, size=14, color=S.PRIMARY))
            else:
                b.setStyleSheet(
                    "QFrame { background: transparent; border: none; border-radius: 4px; }"
                    f"QFrame:hover {{ background: {S.SURFACE_GREY}; }}"
                )
                if lbl:
                    lbl.setStyleSheet(
                        f"color: {S.SECONDARY}; font-size: 12px; font-weight: 500; "
                        f"border: none; background: transparent;"
                    )
                if cnt:
                    cnt.setStyleSheet(
                        f"color: {S.SECONDARY}; background: {S.SURFACE_GREY}; "
                        f"border-radius: 3px; padding: 1px 6px; font-size: 10px; font-weight: 600;"
                    )
                if ic:
                    ic.setPixmap(icon_pixmap(icon, size=14, color=S.SECONDARY))

    def _switch_mode(self, key: str):
        self._mode = key
        rows = self._records()
        self._selected_id = rows[0]["id"] if rows else None
        self._style_tabs()
        title, _, _ = self._mode_meta()
        self.list_title.setText(title)
        self._rebuild_list()
        self._load_detail()

    # ── Workspace ────────────────────────────────────────────
    def _workspace(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._left_panel(), stretch=3)
        lay.addWidget(self._right_panel(), stretch=9)
        return wrap

    def _left_panel(self) -> QFrame:
        box = S.card()
        box.setMinimumWidth(260)
        box.setMaximumWidth(340)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        head = QHBoxLayout()
        self.list_title = QLabel("Product Groups")
        self.list_title.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.active_pill = S.pill("0 Active", "neutral")
        head.addWidget(self.list_title)
        head.addWidget(self.active_pill)
        head.addStretch()
        head.addWidget(
            S.action_btn("+ New", "F3", "add", "primary", self._new_group)
        )
        lay.addLayout(head)

        # Filter
        search_box = QFrame()
        search_box.setFixedHeight(32)
        search_box.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        sw = QHBoxLayout(search_box)
        sw.setContentsMargins(8, 0, 6, 0)
        sw.setSpacing(6)
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setPixmap(icon_pixmap("filter_list", size=16, color=S.SECONDARY))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter groups (Ctrl+F)...")
        self.search.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; font-size: 12px; "
            f"color: {T.TEXT_PRIMARY}; }}"
        )
        self.search.textChanged.connect(self._rebuild_list)
        sw.addWidget(sic)
        sw.addWidget(self.search, stretch=1)
        sw.addWidget(S.kbd("Ctrl+F"))
        lay.addWidget(search_box)

        self.list_host = QVBoxLayout()
        self.list_host.setSpacing(4)
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
        lay.addWidget(list_scroll, stretch=1)

        mapped = QFrame()
        mapped.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        ml = QHBoxLayout(mapped)
        ml.setContentsMargins(10, 8, 10, 8)
        m1 = QLabel("Total Mapped Items")
        m1.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        self.mapped_lbl = QLabel("0")
        self.mapped_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        ml.addWidget(m1)
        ml.addStretch()
        ml.addWidget(self.mapped_lbl)
        lay.addWidget(mapped)
        return box

    def _filtered(self):
        q = self.search.text().strip().lower()
        rows = self._records()
        if q:
            rows = [g for g in rows if q in g.get("name", "").lower()]
        return rows

    def _rebuild_list(self):
        while self.list_host.count():
            item = self.list_host.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        rows = self._filtered()
        for g in rows:
            self.list_host.addWidget(self._group_card(g))
        self.list_host.addStretch(1)
        active = sum(1 for g in self._records() if g.get("active", True))
        self.active_pill.setText(f"{active} Active")
        total = sum(int(g.get("item_count", 0)) for g in self._records())
        unit = "SKUs" if self._mode == "product" else (
            "Accounts" if self._mode == "ledger" else "Locations"
        )
        self.mapped_lbl.setText(f"{total} {unit}")
        self._style_tabs()

    def _group_card(self, g: dict) -> QFrame:
        selected = g["id"] == self._selected_id
        card = QFrame()
        card.setCursor(QCursor(Qt.PointingHandCursor))
        if selected:
            card.setStyleSheet(
                f"QFrame {{ background: {S.HEADER_GREY}; border: none; "
                f"border-left: 4px solid {S.PRIMARY}; border-radius: 4px; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid transparent; "
                f"border-radius: 4px; }}"
                f"QFrame:hover {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; }}"
            )
        lay = QHBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        left = QVBoxLayout()
        left.setSpacing(2)
        name = QLabel(g["name"])
        name_color = S.PRIMARY if selected else T.TEXT_PRIMARY
        name.setStyleSheet(
            f"color: {name_color}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        meta = QLabel(f"GST: {g.get('gst', 0)}% · Root Group")
        meta.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        left.addWidget(name)
        left.addWidget(meta)

        count = QLabel(str(g.get("item_count", 0)))
        if self._mode == "product":
            count.setText(f"{g.get('item_count', 0)} SKUs")
        elif self._mode == "ledger":
            count.setText(f"{g.get('item_count', 0)}")
        else:
            count.setText(f"{g.get('item_count', 0)}")
        if selected:
            count.setStyleSheet(
                f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; border-radius: 4px; "
                f"padding: 2px 8px; font-size: 11px; font-weight: 700;"
            )
        else:
            count.setStyleSheet(
                f"color: {S.SECONDARY}; background: {S.HEADER_GREY}; border-radius: 4px; "
                f"padding: 2px 8px; font-size: 11px; font-weight: 600;"
            )

        lay.addLayout(left, stretch=1)
        lay.addWidget(count, 0, Qt.AlignVCenter)
        card.mousePressEvent = lambda e, gid=g["id"]: self._select(gid)
        return card

    def _select(self, gid: int):
        self._selected_id = gid
        self._rebuild_list()
        self._load_detail()

    def _current(self) -> dict | None:
        for g in self._records():
            if g["id"] == self._selected_id:
                return g
        return None

    # ── Right detail ─────────────────────────────────────────
    def _right_panel(self) -> QFrame:
        box = S.card()
        outer = QVBoxLayout(box)
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(12)

        # Header
        head = QHBoxLayout()
        ic_wrap = QLabel()
        ic_wrap.setFixedSize(32, 32)
        ic_wrap.setAlignment(Qt.AlignCenter)
        ic_wrap.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: 6px; border: none;"
        )
        self.detail_icon = ic_wrap
        ic_wrap.setPixmap(icon_pixmap("category", size=18, color=S.PRIMARY))

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        tr = QHBoxLayout()
        tr.setSpacing(8)
        self.detail_title = QLabel("—")
        self.detail_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        tr.addWidget(self.detail_title)
        tr.addWidget(S.pill("Active Group", "success"))
        tr.addStretch()
        sub = QLabel("Group configuration, parent hierarchy, and tax rate")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        title_col.addLayout(tr)
        title_col.addWidget(sub)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(
            S.action_btn("Delete", "", "delete", "danger", self._delete)
        )
        actions.addWidget(
            S.action_btn("Save", "Ctrl+S", "save", "primary", self._save)
        )

        head.addWidget(ic_wrap)
        head.addLayout(title_col, stretch=1)
        head.addLayout(actions)
        outer.addLayout(head)

        # Form band
        form = QFrame()
        form.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 6px; }}"
        )
        fl = QVBoxLayout(form)
        fl.setContentsMargins(12, 12, 12, 12)
        fl.setSpacing(10)

        self.name = QLineEdit()
        self.gtype = QComboBox()
        self.gtype.addItems([m[3] for m in _MODES])
        self.parent = QComboBox()
        self.parent.addItems(_PARENT_OPTIONS)
        self.gst = QComboBox()
        self.gst.addItems(_GST_OPTIONS)
        self.notes = QLineEdit()

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(S.labeled_input("Group Name", self.name), 1)
        row1.addWidget(S.labeled_input("Group Type", self.gtype), 1)
        row1.addWidget(S.labeled_input("Parent Group", self.parent), 1)
        row1.addWidget(S.labeled_input("Default GST Rate (%)", self.gst), 1)
        fl.addLayout(row1)
        fl.addWidget(S.labeled_input("Description / Internal Notes", self.notes))
        outer.addWidget(form)

        # Items table
        items_head = QHBoxLayout()
        it = QLabel("Items Assigned to this Group")
        it.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.items_badge = S.pill("0 Items", "primary")
        items_head.addWidget(it)
        items_head.addWidget(self.items_badge)
        items_head.addStretch()
        items_head.addWidget(
            S.action_btn(
                "+ Add Item to Group", "", "add_circle", "secondary",
                lambda: toast(self, "Open product/ledger picker…"),
            )
        )
        outer.addLayout(items_head)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Item Code", "Item Name", "Unit (UOM)", "Selling Rate (₹)", "Actions"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            f"""
            QTableWidget {{ background: {T.SURFACE}; border: 1px solid {T.BORDER};
                border-radius: 4px; }}
            QHeaderView::section {{ background: {S.HEADER_GREY}; color: {S.SECONDARY};
                font-size: 10px; font-weight: 700; padding: 6px 8px; border: none;
                border-bottom: 1px solid {T.BORDER}; text-transform: uppercase; }}
            QTableWidget::item {{ padding: 6px 8px; border-bottom: 1px solid {T.BORDER}; }}
            """
        )
        outer.addWidget(self.table, stretch=1)
        return box

    def _assigned_items(self, g: dict) -> list:
        if self._mode == "product":
            return [
                {
                    "code": p["sku"],
                    "name": p["name"],
                    "unit": p.get("unit", "Pcs"),
                    "rate": p.get("sale_rate", 0),
                }
                for p in D.PRODUCTS
                if p.get("group") == g.get("name")
            ]
        if self._mode == "ledger":
            return [
                {
                    "code": p.get("code", f"PTY-{p['id']}"),
                    "name": p["name"],
                    "unit": p.get("type", "Ledger"),
                    "rate": abs(float(p.get("balance", 0))),
                }
                for p in D.PARTIES
                if p.get("group") == g.get("name")
                or (g.get("name") == "Sundry Debtors" and p.get("type") in ("Customer", "Both"))
                or (g.get("name") == "Sundry Creditors" and p.get("type") == "Supplier")
            ][:8]
        # godown
        return [
            {
                "code": gd.get("code", ""),
                "name": gd["name"],
                "unit": gd.get("location_label", "Location"),
                "rate": float(gd.get("item_count", 0)),
            }
            for gd in D.GODOWNS
        ]

    def _load_detail(self):
        g = self._current()
        title, icon, type_label = self._mode_meta()
        self.detail_icon.setPixmap(icon_pixmap(icon, size=18, color=S.PRIMARY))
        if not g:
            self.detail_title.setText("—")
            self.table.setRowCount(0)
            return

        self.detail_title.setText(g["name"])
        self.name.setText(g.get("name", ""))
        idx = self.gtype.findText(type_label)
        self.gtype.setCurrentIndex(idx if idx >= 0 else 0)
        parent = g.get("parent", _PARENT_OPTIONS[0])
        pidx = self.parent.findText(parent)
        self.parent.setCurrentIndex(pidx if pidx >= 0 else 0)
        gst = int(g.get("gst", 18))
        gst_map = {0: 0, 5: 1, 12: 2, 18: 3, 28: 4}
        self.gst.setCurrentIndex(gst_map.get(gst, 3))
        self.notes.setText(g.get("notes", ""))

        items = self._assigned_items(g)
        # Prefer live count for product groups
        live_count = len(items) if self._mode == "product" else g.get("item_count", len(items))
        self.items_badge.setText(f"{live_count} Items")
        g["item_count"] = live_count

        self.table.setRowCount(len(items))
        for r, row in enumerate(items):
            code = QTableWidgetItem(row["code"])
            code.setForeground(Qt.blue)
            self.table.setItem(r, 0, code)
            self.table.setItem(r, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["unit"])))
            rate_txt = (
                format_inr_indian(row["rate"])
                if self._mode == "product"
                else (format_inr_indian(row["rate"]) if self._mode == "ledger" else f"{row['rate']:.0f} items")
            )
            rate = QTableWidgetItem(rate_txt)
            rate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 3, rate)
            # Close action cell
            act = QLabel()
            act.setAlignment(Qt.AlignCenter)
            act.setPixmap(icon_pixmap("close", size=14, color=S.SECONDARY))
            act.setCursor(QCursor(Qt.PointingHandCursor))
            self.table.setCellWidget(r, 4, act)
        self.table.setFixedHeight(28 + max(len(items), 1) * 34)
        # Refresh left counts without full re-select loop
        total = sum(int(x.get("item_count", 0)) for x in self._records())
        unit = "SKUs" if self._mode == "product" else (
            "Accounts" if self._mode == "ledger" else "Locations"
        )
        self.mapped_lbl.setText(f"{total} {unit}")

    # ── Actions ──────────────────────────────────────────────
    def _new_group(self):
        rows = self._records()
        base = max((g["id"] for g in rows), default=0) + 1
        _, _, type_label = self._mode_meta()
        g = {
            "id": base,
            "name": f"New Group {base}",
            "gst": 18 if self._mode == "product" else 0,
            "parent": _PARENT_OPTIONS[0],
            "kind": self._mode,
            "active": True,
            "notes": "",
            "item_count": 0,
        }
        rows.append(g)
        self._selected_id = g["id"]
        self._rebuild_list()
        self._load_detail()
        self.name.setFocus()
        self.name.selectAll()
        toast(self, f"Created {type_label.lower()} — edit and Save.")

    def _save(self):
        g = self._current()
        if not g:
            return
        name = self.name.text().strip()
        if not name:
            self.name.setFocus()
            toast(self, "Group name is required.")
            return
        g["name"] = name
        g["parent"] = self.parent.currentText()
        g["notes"] = self.notes.text().strip()
        gst_txt = self.gst.currentText()
        try:
            g["gst"] = int(gst_txt.split("%")[0])
        except ValueError:
            g["gst"] = 18
        # Keep flat lists in sync for product/ledger/godown masters
        if self._mode == "product":
            D.ITEM_GROUPS[:] = [x["name"] for x in self.product_groups]
        elif self._mode == "ledger":
            D.LEDGER_GROUPS[:] = [x["name"] for x in self.ledger_groups]
        else:
            D.GODOWN_GROUPS[:] = [x["name"] for x in self.godown_groups]
        self._rebuild_list()
        self._load_detail()
        toast(self, f"Saved group: {name}")

    def _delete(self):
        g = self._current()
        if not g:
            return
        rows = self._records()
        rows[:] = [x for x in rows if x["id"] != g["id"]]
        self._selected_id = rows[0]["id"] if rows else None
        self._rebuild_list()
        self._load_detail()
        toast(self, f"Deleted: {g['name']}")

    def _footer(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(8)
        for key, label in (
            ("F3", "New Group"),
            ("Ctrl+S", "Save Group"),
            ("Ctrl+F", "Filter List"),
            ("Del", "Delete"),
            ("Esc", "Back to Masters"),
        ):
            lay.addWidget(S.kbd(key))
            t = QLabel(label)
            t.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 10px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(t)
            lay.addSpacing(4)
        lay.addStretch()
        tip = QLabel("Switch tabs for Product · Ledger · Godown groups")
        tip.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        lay.addWidget(tip)
        return box
