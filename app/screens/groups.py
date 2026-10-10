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
        self._page = 1

        self.setObjectName("groupRoot")
        self.setStyleSheet(f"QWidget#groupRoot {{ background: {T.BG_CANVAS}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(self._page_header())
        root.addWidget(self._workspace(), stretch=1)
        root.addWidget(self._footer())

        QShortcut(QKeySequence("F3"), self, activated=self._new_group)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())
        QShortcut(QKeySequence("Delete"), self, activated=self._delete)

        self._rebuild_list()
        self._load_detail()

    # ── data helpers ─────────────────────────────────────────
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

    def _count_for(self, key: str) -> int:
        return {
            "product": len(self.product_groups),
            "ledger": len(self.ledger_groups),
            "godown": len(self.godown_groups),
        }[key]

    def _current(self) -> dict | None:
        for g in self._records():
            if g["id"] == self._selected_id:
                return g
        return None

    # ── Header ───────────────────────────────────────────────
    def _page_header(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(16)

        # Icon chip — primary filled (Stitch primary-container)
        ic = QLabel()
        ic.setFixedSize(36, 36)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {S.PRIMARY}; border-radius: 4px; border: none;"
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
        badge = QLabel("Master Setup · 3")
        badge.setStyleSheet(
            f"color: {S.SECONDARY}; background: {S.HEADER_GREY}; border: none; "
            f"border-radius: 3px; padding: 2px 6px; font-size: 9px; font-weight: 700;"
        )
        title_row.addWidget(ttl)
        title_row.addWidget(badge)
        title_row.addStretch()
        sub = QLabel("Categorize catalog items, ledger accounts, and warehouse godowns")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        col.addLayout(title_row)
        col.addWidget(sub)

        lay.addWidget(ic)
        lay.addLayout(col, stretch=1)
        lay.addWidget(self._mode_tabs())
        return box

    def _mode_tabs(self) -> QFrame:
        """Segmented control matching Stitch surface-container-low tray."""
        wrap = QFrame()
        wrap.setStyleSheet(
            f"QFrame {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(4)
        self._tab_btns = {}
        for key, title, icon, _ in _MODES:
            b = QFrame()
            b.setObjectName(f"tab_{key}")
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setFixedHeight(32)
            bl = QHBoxLayout(b)
            bl.setContentsMargins(12, 0, 10, 0)
            bl.setSpacing(6)
            i = QLabel()
            i.setFixedSize(16, 16)
            i.setObjectName("tabIcon")
            i.setStyleSheet("background: transparent; border: none;")
            bl.addWidget(i)
            lbl = QLabel(title)
            lbl.setObjectName("tabLbl")
            bl.addWidget(lbl)
            cnt = QLabel(str(self._count_for(key)))
            cnt.setObjectName("tabCnt")
            cnt.setAlignment(Qt.AlignCenter)
            bl.addWidget(cnt)
            b.mousePressEvent = lambda e, k=key: self._switch_mode(k)
            self._tab_btns[key] = (b, icon)
            lay.addWidget(b)
        self._style_tabs()
        return wrap

    def _style_tabs(self):
        for key, (b, icon) in self._tab_btns.items():
            active = key == self._mode
            lbl = b.findChild(QLabel, "tabLbl")
            cnt = b.findChild(QLabel, "tabCnt")
            ic = b.findChild(QLabel, "tabIcon")
            cnt.setText(str(self._count_for(key)))
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
                        f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; border: none; "
                        f"border-radius: 3px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
                    )
                if ic:
                    ic.setPixmap(icon_pixmap(icon, size=14, color=S.PRIMARY))
            else:
                b.setStyleSheet(
                    "QFrame { background: transparent; border: none; border-radius: 4px; }"
                )
                if lbl:
                    lbl.setStyleSheet(
                        f"color: {S.SECONDARY}; font-size: 12px; font-weight: 500; "
                        f"border: none; background: transparent;"
                    )
                if cnt:
                    cnt.setStyleSheet(
                        f"color: {S.SECONDARY}; background: {S.SURFACE_GREY}; border: none; "
                        f"border-radius: 3px; padding: 1px 6px; font-size: 10px; font-weight: 600;"
                    )
                if ic:
                    ic.setPixmap(icon_pixmap(icon, size=14, color=S.SECONDARY))

    def _switch_mode(self, key: str):
        if key == self._mode:
            return
        self._mode = key
        self._page = 1
        rows = self._records()
        self._selected_id = rows[0]["id"] if rows else None
        self._style_tabs()
        self.list_title.setText(self._mode_meta()[0])
        self._rebuild_list()
        self._load_detail()

    # ── Workspace ────────────────────────────────────────────
    def _workspace(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(self._left_panel())
        lay.addWidget(self._right_panel(), stretch=1)
        return wrap

    def _btn(self, label: str, icon: str, kind: str, on_click) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(30)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if kind == "primary":
            btn.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: 4px; }}"
                f"QFrame:hover {{ background: #1d4ed8; }}"
            )
            fg, ic = "#ffffff", "#ffffff"
        elif kind == "danger":
            # Stitch: bg-surface-container text-error
            btn.setStyleSheet(
                f"QFrame {{ background: {S.HEADER_GREY}; border: none; border-radius: 4px; }}"
                f"QFrame:hover {{ background: {T.DANGER_BG}; }}"
            )
            fg, ic = S.ERROR, S.ERROR
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
                f"QFrame:hover {{ background: {S.SURFACE_GREY}; }}"
            )
            fg, ic = T.TEXT_PRIMARY, S.PRIMARY
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(5)
        if icon:
            il = QLabel()
            il.setFixedSize(14, 14)
            il.setStyleSheet("background: transparent; border: none;")
            il.setPixmap(icon_pixmap(icon, size=14, color=ic))
            lay.addWidget(il)
        txt = QLabel(label)
        txt.setStyleSheet(
            f"color: {fg}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(txt)
        if on_click is not None:
            btn.mousePressEvent = (
                lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
            )
        return btn

    # ── Left directory ───────────────────────────────────────
    def _left_panel(self) -> QFrame:
        box = S.card()
        box.setFixedWidth(300)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Title row with bottom border
        head = QFrame()
        head.setStyleSheet(
            f"background: transparent; border: none; border-bottom: 1px solid {T.BORDER};"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(0, 0, 0, 8)
        hl.setSpacing(6)
        self.list_title = QLabel("Product Groups")
        self.list_title.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.active_pill = QLabel("0 Active")
        self.active_pill.setStyleSheet(
            f"color: {S.SECONDARY}; background: {S.HEADER_GREY}; border: none; "
            f"border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: 600;"
        )
        hl.addWidget(self.list_title)
        hl.addWidget(self.active_pill)
        hl.addStretch()
        # Icon is Material `add` (+); label omits extra "+" to avoid "++ New"
        hl.addWidget(self._btn("New [F3]", "add", "primary", self._new_group))
        lay.addWidget(head)

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
        sic.setStyleSheet("background: transparent; border: none;")
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

        # Scrollable list
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
        list_scroll.setStyleSheet(
            f"QScrollArea {{ background: transparent; border: none; }}"
        )
        list_scroll.setWidget(list_wrap)
        lay.addWidget(list_scroll, stretch=1)

        # Mapped footer
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
        for g in self._filtered():
            self.list_host.addWidget(self._group_card(g))
        self.list_host.addStretch(1)

        active = sum(1 for g in self._records() if g.get("active", True))
        self.active_pill.setText(f"{active} Active")
        total = sum(int(g.get("item_count", 0)) for g in self._records())
        unit = (
            "SKUs" if self._mode == "product"
            else ("Accounts" if self._mode == "ledger" else "Locations")
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
                f"QFrame:hover {{ background: {S.HEADER_GREY}; }}"
            )
        lay = QHBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        left = QVBoxLayout()
        left.setSpacing(2)
        name = QLabel(g["name"])
        name.setStyleSheet(
            f"color: {S.PRIMARY if selected else T.TEXT_PRIMARY}; "
            f"font-size: 12px; font-weight: {'700' if selected else '600'}; "
            f"border: none; background: transparent;"
        )
        parent = g.get("parent", "")
        root_lbl = "Root Group" if "Root" in parent or not parent else parent
        meta = QLabel(f"GST: {g.get('gst', 0)}% · {root_lbl}")
        meta.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        left.addWidget(name)
        left.addWidget(meta)

        count_n = int(g.get("item_count", 0))
        count = QLabel(f"{count_n} SKUs" if self._mode == "product" else str(count_n))
        if selected:
            count.setStyleSheet(
                f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; border: none; "
                f"border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 700;"
            )
        else:
            count.setStyleSheet(
                f"color: {S.SECONDARY}; background: {S.HEADER_GREY}; border: none; "
                f"border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600;"
            )
        lay.addLayout(left, stretch=1)
        lay.addWidget(count, 0, Qt.AlignVCenter)
        card.mousePressEvent = lambda e, gid=g["id"]: self._select(gid)
        return card

    def _select(self, gid: int):
        self._selected_id = gid
        self._page = 1
        self._rebuild_list()
        self._load_detail()

    # ── Right detail ─────────────────────────────────────────
    def _right_panel(self) -> QFrame:
        box = S.card()
        outer = QVBoxLayout(box)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)

        # Detail header
        head = QFrame()
        head.setStyleSheet(
            f"background: transparent; border: none; border-bottom: 1px solid {T.BORDER};"
        )
        hl = QHBoxLayout(head)
        hl.setContentsMargins(0, 0, 0, 10)
        hl.setSpacing(10)

        ic_wrap = QLabel()
        ic_wrap.setFixedSize(32, 32)
        ic_wrap.setAlignment(Qt.AlignCenter)
        ic_wrap.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: 4px; border: none;"
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
        active = QLabel("Active Group")
        active.setStyleSheet(
            f"color: #047857; background: {T.SUCCESS_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 600;"
        )
        tr.addWidget(self.detail_title)
        tr.addWidget(active)
        tr.addStretch()
        sub = QLabel("Group configuration, parent hierarchy, and tax rate")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        title_col.addLayout(tr)
        title_col.addWidget(sub)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self._btn("Delete", "delete", "danger", self._delete))
        actions.addWidget(self._btn("Save [Ctrl+S]", "save", "primary", self._save))

        hl.addWidget(ic_wrap)
        hl.addLayout(title_col, stretch=1)
        hl.addLayout(actions)
        outer.addWidget(head)

        # Form band
        form = QFrame()
        form.setStyleSheet(
            f"QFrame {{ background: {S.INPUT_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
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
        for w in (self.name, self.gtype, self.parent, self.gst, self.notes):
            self._style_field(w)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(self._field("Group Name", self.name), 1)
        row1.addWidget(self._field("Group Type", self.gtype), 1)
        row1.addWidget(self._field("Parent Group", self.parent), 1)
        row1.addWidget(self._field("Default GST Rate (%)", self.gst), 1)
        fl.addLayout(row1)
        fl.addWidget(self._field("Description / Internal Notes", self.notes))
        outer.addWidget(form)

        # Items header
        items_head = QHBoxLayout()
        items_head.setSpacing(8)
        it = QLabel("Items Assigned to this Group")
        it.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        self.items_badge = QLabel("0 Items")
        self.items_badge.setStyleSheet(
            f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; border: none; "
            f"border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
        items_head.addWidget(it)
        items_head.addWidget(self.items_badge)
        items_head.addStretch()
        items_head.addWidget(
            self._btn(
                "+ Add Item to Group", "add_circle", "secondary",
                lambda: toast(self, "Open product/ledger picker…"),
            )
        )
        outer.addLayout(items_head)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Item Code", "Item Name", "Unit (UOM)", "Selling Rate (₹)", "Actions"]
        )
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 64)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        S.apply_table_style(self.table)
        outer.addWidget(self.table)

        # Pagination — fixed horizontal strip (widget, not bare layout)
        pager = QFrame()
        pager.setStyleSheet("background: transparent; border: none;")
        pager.setFixedHeight(28)
        pl = QHBoxLayout(pager)
        pl.setContentsMargins(0, 4, 0, 0)
        pl.setSpacing(4)
        self.page_info = QLabel("Showing 0 of 0 items")
        self.page_info.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        pl.addWidget(self.page_info)
        pl.addStretch()
        self._pager_row = QHBoxLayout()
        self._pager_row.setSpacing(4)
        self._pager_row.setContentsMargins(0, 0, 0, 0)
        pl.addLayout(self._pager_row)
        outer.addWidget(pager)

        outer.addStretch(1)
        return box

    def _style_field(self, widget: QWidget):
        widget.setFixedHeight(32)
        from app.widgets.icons import combo_dropdown_qss

        widget.setStyleSheet(
            f"""
            QLineEdit, QComboBox {{
                background: {T.SURFACE}; border: 1px solid {T.BORDER}; border-radius: 4px;
                padding: 4px 10px; font-size: 12px; font-weight: 600;
                color: {T.TEXT_PRIMARY};
                selection-background-color: {S.PRIMARY}; selection-color: white;
            }}
            QComboBox {{
                padding-right: 26px;
            }}
            {combo_dropdown_qss(width=22, background="transparent")}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {S.PRIMARY};
            }}
            """
        )

    def _field(self, label: str, widget: QWidget) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        cap = QLabel(label)
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(cap)
        lay.addWidget(widget)
        return wrap

    def _assigned_items(self, g: dict) -> list:
        preview = getattr(D, "GROUP_ITEMS_PREVIEW", {}).get(g.get("id"))
        if preview:
            return [dict(x) for x in preview]
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
            name = g.get("name", "")
            return [
                {
                    "code": p.get("code", f"PTY-{p['id']}"),
                    "name": p["name"],
                    "unit": p.get("type", "Ledger"),
                    "rate": abs(float(p.get("balance", 0))),
                }
                for p in D.PARTIES
                if (
                    ("Debtor" in name and p.get("type") in ("Customer", "Both"))
                    or ("Creditor" in name and p.get("type") == "Supplier")
                )
            ][:8]
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
        _, icon, type_label = self._mode_meta()
        self.detail_icon.setPixmap(icon_pixmap(icon, size=18, color=S.PRIMARY))
        if not g:
            self.detail_title.setText("—")
            self.table.setRowCount(0)
            self.table.setFixedHeight(40)
            self.page_info.setText("Showing 0 of 0 items")
            self.items_badge.setText("0 Items")
            self._render_pager(1)
            return

        self.detail_title.setText(g["name"])
        self.name.setText(g.get("name", ""))
        idx = self.gtype.findText(type_label)
        self.gtype.setCurrentIndex(idx if idx >= 0 else 0)
        parent = g.get("parent", _PARENT_OPTIONS[0])
        pidx = self.parent.findText(parent)
        self.parent.setCurrentIndex(pidx if pidx >= 0 else 0)
        gst = int(g.get("gst", 18))
        self.gst.setCurrentIndex({0: 0, 5: 1, 12: 2, 18: 3, 28: 4}.get(gst, 3))
        self.notes.setText(g.get("notes", ""))

        items = self._assigned_items(g)
        total_count = int(g.get("item_count", len(items)))
        self.items_badge.setText(f"{total_count} Items")

        self.table.setRowCount(len(items))
        for r, row in enumerate(items):
            code = QTableWidgetItem(row["code"])
            code.setForeground(Qt.GlobalColor.blue)
            f = code.font()
            f.setBold(True)
            code.setFont(f)
            self.table.setItem(r, 0, code)

            self.table.setItem(r, 1, QTableWidgetItem(row["name"]))

            unit = QTableWidgetItem(str(row["unit"]))
            unit.setForeground(Qt.GlobalColor.darkGray)
            self.table.setItem(r, 2, unit)

            if self._mode == "godown":
                rate_txt = f"{row['rate']:.0f} items"
            else:
                rate_txt = format_inr_indian(row["rate"]).replace("₹ ", "₹")
            rate = QTableWidgetItem(rate_txt)
            rate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            f = rate.font()
            f.setBold(True)
            rate.setFont(f)
            self.table.setItem(r, 3, rate)

            act = QLabel()
            act.setAlignment(Qt.AlignCenter)
            act.setPixmap(icon_pixmap("close", size=14, color=S.SECONDARY))
            act.setCursor(QCursor(Qt.PointingHandCursor))
            act.setToolTip("Remove from group")
            self.table.setCellWidget(r, 4, act)

        rows_h = max(len(items), 1)
        self.table.setFixedHeight(T.TABLE_HEADER_H + rows_h * T.GRID_ROW_H + 4)
        shown = len(items)
        self.page_info.setText(f"Showing {shown} of {total_count} items")
        pages = max(1, min(3, (max(total_count, 1) + 49) // 50)) if total_count else 1
        self._render_pager(pages)

        total = sum(int(x.get("item_count", 0)) for x in self._records())
        unit = (
            "SKUs" if self._mode == "product"
            else ("Accounts" if self._mode == "ledger" else "Locations")
        )
        self.mapped_lbl.setText(f"{total} {unit}")

    def _render_pager(self, pages: int):
        while self._pager_row.count():
            item = self._pager_row.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._pager_row.addWidget(self._page_chip("Prev", False))
        for i in range(1, pages + 1):
            self._pager_row.addWidget(self._page_chip(str(i), i == self._page))
        self._pager_row.addWidget(self._page_chip("Next", False))

    def _page_chip(self, text: str, active: bool) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFixedHeight(22)
        lbl.setMinimumWidth(28 if text.isdigit() else 40)
        lbl.setCursor(QCursor(Qt.PointingHandCursor))
        if active:
            lbl.setStyleSheet(
                f"background: {S.PRIMARY}; color: white; border: none; "
                f"border-radius: 3px; padding: 2px 8px; font-size: 11px; font-weight: 700;"
            )
        else:
            lbl.setStyleSheet(
                f"background: {S.HEADER_GREY}; color: {S.SECONDARY}; border: none; "
                f"border-radius: 3px; padding: 2px 8px; font-size: 11px; font-weight: 600;"
            )
        if text.isdigit():
            lbl.mousePressEvent = lambda e, p=int(text): self._set_page(p)
        return lbl

    def _set_page(self, page: int):
        self._page = page
        self._load_detail()

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
        lay.setSpacing(6)
        for key, label in (
            ("F3", "New Group"),
            ("Ctrl+S", "Save Group"),
            ("Ctrl+F", "Filter Groups"),
            ("Esc", "Back to Dashboard"),
        ):
            lay.addWidget(S.kbd(key))
            t = QLabel(label)
            t.setStyleSheet(
                f"color: {S.SECONDARY}; font-size: 11px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(t)
            lay.addSpacing(10)
        lay.addStretch()
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"background: {T.SUCCESS}; border-radius: 4px; border: none;"
        )
        tip = QLabel("Sri Lakshmi Electricals ERP · V1 Group Master")
        tip.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(dot)
        lay.addSpacing(6)
        lay.addWidget(tip)
        return box
