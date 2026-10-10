"""Application shell — Stitch Design System Implementation layout."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import make_button, toast
from app.widgets.icons import icon_pixmap, icon_size, nav_icon, qicon


# Accordion groups aligned to Stitch sidebar labels
# (group_key, title, [(nav_key, label, shortcut, crumb), ...])
NAV_GROUPS = [
    ("masters", "1. MASTER SETUP", [
        ("company", "1. Company Details", "", "Master Setup / Company Details"),
        ("parties", "2. Ledger", "", "Master Setup / Ledger"),
        ("groups", "3. Group", "", "Master Setup / Group"),
        ("products", "4. Product", "", "Master Setup / Product"),
        ("godowns", "5. Godown", "", "Master Setup / Godown"),
    ]),
    ("operations", "2. ENTRY", [
        ("purchase", "2.1 Purchase", "F3", "Operations / Purchase Entry"),
        ("sales", "2.2 Sales", "F2", "Operations / Sales & Distribution"),
        ("cash_flow", "2.3 Cash Flow", "", "Operations / Cash Flow"),
        ("billwise", "2.4 Billwise Settlement", "", "Operations / Billwise Settlement"),
    ]),
    ("reports", "3. REPORTS", [
        ("reports_ar_ap", "Stock Summary", "", "Reports / Stock Summary"),
        ("registers", "Daybook & Registers", "", "Reports / Daybook & Registers"),
        ("ledger_stmt", "Ledger Statement", "", "Reports / Ledger Statement"),
        ("export_tools", "Export Tools", "", "Reports / Export Tools"),
    ]),
    ("settings", "4. SETTINGS / A/C YEAR", [
        ("audit_trail", "4.1 A/c Log Customer", "", "Settings / A/c Log"),
        ("users", "4.2 Users", "", "Settings / Users"),
        ("ac_year", "4.3 A/c Year Management", "", "Settings / A/c Year Management"),
        ("license", "License & Activation", "", "Settings / License & Activation"),
    ]),
]

NAV_SHORT = {
    "dashboard": "Home",
    "company": "Co",
    "parties": "Ld",
    "groups": "Gr",
    "products": "Pr",
    "godowns": "Gd",
    "purchase": "Pu",
    "sales": "Sa",
    "cash_flow": "Cf",
    "billwise": "Bw",
    "ledger_stmt": "Ls",
    "registers": "Rg",
    "reports_ar_ap": "St",
    "export_tools": "Ex",
    "audit_trail": "Au",
    "users": "Ur",
    "ac_year": "FY",
    "license": "Lc",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{D.COMPANY_NAME} — {D.COMPANY_TAGLINE}")
        self.resize(1366, 768)
        self.setMinimumSize(1280, 720)
        self.nav_expanded = True
        self._nav_buttons = {}
        self._nav_labels = {}
        self._nav_shortcuts = {}
        self._group_headers = {}
        self._group_bodies = {}
        self._group_open = {k: True for k, _, _ in NAV_GROUPS}
        self._screen_keys = {}
        self._crumb_map = {
            "dashboard": "Operations / Sales & Distribution",
        }
        for _, _, items in NAV_GROUPS:
            for key, _, _, crumb in items:
                self._crumb_map[key] = crumb

        self._build_ui()
        self._wire_global_shortcuts()
        self.navigate("dashboard")

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralRoot")
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.nav = self._build_nav()
        outer.addWidget(self.nav)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        right.addWidget(self._build_top_bar())
        right.addWidget(self._build_breadcrumb())
        self.stack = QStackedWidget()
        right.addWidget(self.stack, stretch=1)
        outer.addLayout(right, stretch=1)

        self._register_screens()
        self.statusBar().hide()

    def _nav_btn_style(self, child=False, collapsed=False, active=False) -> str:
        if collapsed:
            return (
                f"QPushButton {{ background: transparent; border: none; "
                f"border-left: 3px solid transparent; text-align: center; "
                f"padding: 10px 2px; color: {T.NAV_TEXT_ACTIVE}; min-height: 36px; }}"
                f"QPushButton:hover {{ background-color: {T.NAV_HOVER}; }}"
                f"QPushButton:checked {{ background-color: {T.NAV_ACTIVE}; "
                f"border-left: 3px solid {T.NAV_ACTIVE_INDICATOR}; }}"
            )
        pad = "6px 8px 6px 10px" if child else "6px 8px"
        checked_bg = T.NAV_ACTIVE
        return (
            f"QPushButton {{ background: transparent; border: none; "
            f"border-left: 3px solid transparent; border-radius: 4px; "
            f"text-align: left; padding: {pad}; color: {T.NAV_TEXT}; "
            f"min-height: 26px; font-size: {T.FONT_SIZE_NAV}pt; }}"
            f"QPushButton:hover {{ background-color: rgba(148,163,184,0.12); "
            f"color: {T.NAV_TEXT_ACTIVE}; }}"
            f"QPushButton:checked {{ background-color: {checked_bg}; "
            f"color: {T.NAV_TEXT_ACTIVE}; font-weight: bold; "
            f"border-left: 3px solid {T.NAV_ACTIVE_INDICATOR}; }}"
        )

    def _shortcut_chip(self, text: str, on_dark=True) -> QLabel:
        chip = QLabel(text)
        chip.setAlignment(Qt.AlignCenter)
        if on_dark:
            chip.setStyleSheet(
                f"color: {T.NAV_TEXT_ACTIVE}; background: rgba(148,163,184,0.18); "
                f"border-radius: 3px; padding: 1px 5px; "
                f"font-size: {T.FONT_SIZE_MICRO}pt; font-weight: bold;"
            )
        else:
            chip.setStyleSheet(
                f"color: {T.TEXT_MUTED}; background: {T.HEADER_BAND}; "
                f"border: 1px solid {T.BORDER_STRONG}; border-radius: 3px; "
                f"padding: 1px 5px; font-size: {T.FONT_SIZE_MICRO}pt; font-weight: bold;"
            )
        return chip

    def _build_nav(self) -> QFrame:
        rail = QFrame()
        rail.setObjectName("navRail")
        rail.setFixedWidth(T.NAV_EXPANDED)
        self._nav_rail = rail

        outer = QVBoxLayout(rail)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Brand header (Stitch h-11)
        header = QFrame()
        header.setFixedHeight(44)
        header.setStyleSheet(
            f"QFrame {{ background: {T.NAV_BG}; border: none; "
            f"border-bottom: 1px solid rgba(148,163,184,0.12); }}"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 8, 0)
        hl.setSpacing(8)
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand_col.setContentsMargins(0, 0, 0, 0)
        brand = QLabel(D.COMPANY_NAME)
        brand.setObjectName("navBrand")
        brand.setStyleSheet(
            f"color: {T.NAV_TEXT_ACTIVE}; font-size: {T.FONT_SIZE_TITLE}pt; "
            f"font-weight: bold; border: none; background: transparent;"
        )
        self._nav_brand = brand
        sub = QLabel(D.COMPANY_TAGLINE.upper())
        sub.setObjectName("navBrandSub")
        sub.setStyleSheet(
            f"color: {T.NAV_TEXT}; font-size: {T.FONT_SIZE_MICRO}pt; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        self._nav_sub = sub
        brand_col.addWidget(brand)
        brand_col.addWidget(sub)
        hl.addLayout(brand_col, stretch=1)
        self.btn_toggle = QPushButton()
        self.btn_toggle.setObjectName("navToggle")
        self.btn_toggle.setIcon(qicon("menu", size=16))
        self.btn_toggle.setIconSize(icon_size(16))
        self.btn_toggle.setFixedSize(28, 28)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setToolTip("Collapse / Expand menu")
        self.btn_toggle.clicked.connect(self._toggle_nav)
        hl.addWidget(self.btn_toggle)
        outer.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        body = QWidget()
        body.setStyleSheet(f"background-color: {T.NAV_BG};")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(10)

        # Home / Dashboard
        dash_wrap = QWidget()
        dash_row = QHBoxLayout(dash_wrap)
        dash_row.setContentsMargins(0, 0, 0, 0)
        dash_row.setSpacing(4)
        dash = QPushButton("  Home / Dashboard")
        dash.setCheckable(True)
        dash.setCursor(Qt.PointingHandCursor)
        dash.setIcon(nav_icon("dashboard", 16))
        dash.setIconSize(icon_size(16))
        dash.setStyleSheet(self._nav_btn_style(False))
        dash.clicked.connect(lambda: self.navigate("dashboard"))
        self._nav_buttons["dashboard"] = dash
        self._nav_labels["dashboard"] = "Home / Dashboard"
        self._nav_shortcuts["dashboard"] = "F10"
        dash_row.addWidget(dash, stretch=1)
        f10 = self._shortcut_chip("F10")
        self._dash_chip = f10
        dash_row.addWidget(f10)
        lay.addWidget(dash_wrap)

        for gkey, gtitle, items in NAV_GROUPS:
            group_wrap = QWidget()
            gl = QVBoxLayout(group_wrap)
            gl.setContentsMargins(0, 4, 0, 0)
            gl.setSpacing(2)

            header_btn = QPushButton(f"  {gtitle}")
            header_btn.setCursor(Qt.PointingHandCursor)
            header_btn.setIcon(qicon("caret-down", 12))
            header_btn.setIconSize(icon_size(12))
            header_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; border: none; text-align: left; "
                f"padding: 4px 8px; color: {T.NAV_GROUP_TEXT}; font-weight: 600; "
                f"font-size: {T.FONT_SIZE_MICRO}pt; letter-spacing: 0.6px; }}"
                f"QPushButton:hover {{ color: {T.NAV_TEXT_ACTIVE}; }}"
            )
            header_btn.clicked.connect(lambda checked=False, k=gkey: self._toggle_group(k))
            self._group_headers[gkey] = header_btn
            self._group_open[gkey] = True
            gl.addWidget(header_btn)

            children = QFrame()
            children.setStyleSheet(
                f"QFrame {{ background: transparent; border: none; "
                f"border-left: 1px solid rgba(148,163,184,0.15); margin-left: 10px; }}"
            )
            cl = QVBoxLayout(children)
            cl.setContentsMargins(6, 0, 0, 0)
            cl.setSpacing(1)
            for key, label, shortcut, _crumb in items:
                row = QWidget()
                rl = QHBoxLayout(row)
                rl.setContentsMargins(0, 0, 0, 0)
                rl.setSpacing(2)
                btn = QPushButton(f"  {label}")
                btn.setCheckable(True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setIcon(nav_icon(key, 14))
                btn.setIconSize(icon_size(14))
                btn.setStyleSheet(self._nav_btn_style(True))
                btn.clicked.connect(lambda checked=False, k=key: self.navigate(k))
                self._nav_buttons[key] = btn
                self._nav_labels[key] = label
                self._nav_shortcuts[key] = shortcut
                rl.addWidget(btn, stretch=1)
                if shortcut:
                    chip = self._shortcut_chip(shortcut)
                    chip.setObjectName(f"navChip_{key}")
                    rl.addWidget(chip)
                cl.addWidget(row)
            self._group_bodies[gkey] = children
            gl.addWidget(children)
            lay.addWidget(group_wrap)

        lay.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)

        # Footer — POS mode + Exit
        footer = QFrame()
        footer.setStyleSheet(
            f"QFrame {{ background: {T.NAV_BG}; border: none; "
            f"border-top: 1px solid rgba(148,163,184,0.12); }}"
        )
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(8, 8, 8, 10)
        fl.setSpacing(6)
        pos = QLabel("POS Mode: Wholesale")
        pos.setStyleSheet(
            f"color: {T.NAV_TEXT}; font-size: {T.FONT_SIZE_MICRO}pt; "
            f"background: rgba(148,163,184,0.08); border-radius: 4px; padding: 4px 8px;"
        )
        self._nav_pos = pos
        fl.addWidget(pos)
        exit_btn = QPushButton("  6. Exit")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.setIcon(qicon("safety", size=14, color="#ef4444"))
        exit_btn.setIconSize(icon_size(14))
        exit_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; text-align: left; "
            f"padding: 6px 8px; color: {T.DANGER}; border-radius: 4px; "
            f"font-size: {T.FONT_SIZE_NAV}pt; }}"
            f"QPushButton:hover {{ background: {T.DANGER_BG}; }}"
        )
        exit_btn.clicked.connect(self.close)
        self._nav_exit = exit_btn
        exit_row = QHBoxLayout()
        exit_row.setContentsMargins(0, 0, 0, 0)
        exit_row.addWidget(exit_btn, stretch=1)
        exit_row.addWidget(self._shortcut_chip("Alt+F4"))
        fl.addLayout(exit_row)
        outer.addWidget(footer)
        return rail

    def _toggle_group(self, gkey: str):
        open_ = not self._group_open.get(gkey, True)
        self._group_open[gkey] = open_
        body = self._group_bodies[gkey]
        body.setVisible(open_ and self.nav_expanded)
        title = next(t for k, t, _ in NAV_GROUPS if k == gkey)
        header = self._group_headers[gkey]
        header.setText(f"  {title}")
        header.setIcon(qicon("caret-down" if open_ else "caret-right", 12))
        header.setIconSize(icon_size(12))

    def _build_top_bar(self) -> QFrame:
        """Stitch header row 1: company + badges | search | user + logout + avatar."""
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(T.HEADER_ZONE_H)
        lay = QHBoxLayout(bar)
        # Vertical inset so chips/search don't stretch edge-to-edge (Stitch h-11 / h-7 gap)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(16)
        lay.setAlignment(Qt.AlignVCenter)

        # Left: company + FY + GST (compact Stitch badges)
        left = QHBoxLayout()
        left.setSpacing(12)
        left.setContentsMargins(0, 0, 0, 0)
        left.setAlignment(Qt.AlignVCenter)

        company = QLabel(D.COMPANY_NAME)
        company.setObjectName("companyTitle")
        company.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        company.setStyleSheet(
            f"font-size: 11pt; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"letter-spacing: -0.2px; border: none; background: transparent;"
        )
        self._company_label = company

        self.fy_badge = QLabel(D.FINANCIAL_YEAR)
        self.fy_badge.setObjectName("fyBadge")
        self.fy_badge.setCursor(Qt.PointingHandCursor)
        self.fy_badge.setToolTip("Click to change fiscal year")
        self.fy_badge.setFixedHeight(22)
        self.fy_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fy_badge.mousePressEvent = lambda e: self.navigate("ac_year")
        self.fy_badge.setStyleSheet(
            f"color: {T.PRIMARY_CONTAINER}; background: {T.ACCENT_SOFT}; "
            f"border: 1px solid {T.BORDER}; border-radius: 4px; "
            f"padding: 0 6px; font-size: 8pt; font-weight: 600;"
        )

        gst = QLabel("GST: Registered")
        gst.setObjectName("gstBadge")
        gst.setFixedHeight(22)
        gst.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        gst.setStyleSheet(
            f"color: #047857; background: {T.SUCCESS_BG}; "
            f"border: 1px solid {T.BORDER}; border-radius: 4px; "
            f"padding: 0 6px; font-size: 8pt; font-weight: 600;"
        )

        left.addWidget(company, 0, Qt.AlignVCenter)
        left.addWidget(self.fy_badge, 0, Qt.AlignVCenter)
        left.addWidget(gst, 0, Qt.AlignVCenter)

        # Center: search box with Material search icon + Ctrl+K inside (Stitch)
        search_box = QFrame()
        search_box.setObjectName("globalSearchBox")
        search_box.setFixedHeight(28)
        search_box.setMinimumWidth(280)
        search_box.setMaximumWidth(448)  # max-w-md
        search_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_box.setStyleSheet(
            f"QFrame#globalSearchBox {{ background: #f3f4f6; "
            f"border: 1px solid {T.BORDER_STRONG}; border-radius: 4px; }}"
        )
        sw = QHBoxLayout(search_box)
        sw.setContentsMargins(8, 0, 6, 0)
        sw.setSpacing(6)

        search_ic = QLabel()
        search_ic.setFixedSize(16, 16)
        search_ic.setPixmap(icon_pixmap("search", size=16, color=T.TEXT_SECONDARY))
        search_ic.setStyleSheet("background: transparent; border: none;")

        self.search = QLineEdit()
        self.search.setObjectName("globalSearch")
        self.search.setPlaceholderText("Global search (Invoice, Party, Item, Ledger)...")
        self.search.setFixedHeight(24)
        self.search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search.setStyleSheet(
            f"QLineEdit#globalSearch {{ background: transparent; border: none; "
            f"padding: 0 2px; font-size: 9pt; color: {T.TEXT_PRIMARY}; }}"
            f"QLineEdit#globalSearch:focus {{ border: none; background: transparent; }}"
        )
        self.search.textChanged.connect(self._live_search)
        self.search.returnPressed.connect(self._do_search)
        self.search.focusInEvent = self._search_focus_in
        self.search.focusOutEvent = self._search_focus_out

        kbd = QLabel("Ctrl+K")
        kbd.setFixedHeight(18)
        kbd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        kbd.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 3px; padding: 0 5px; "
            f"font-size: {T.FONT_SIZE_MICRO}pt; font-weight: 700;"
        )
        self._search_kbd = kbd
        self._search_box = search_box

        sw.addWidget(search_ic, 0, Qt.AlignVCenter)
        sw.addWidget(self.search, stretch=1)
        sw.addWidget(kbd, 0, Qt.AlignVCenter)

        # Right: user chip + Logout (logout icon) + person avatar
        right = QHBoxLayout()
        right.setSpacing(8)
        right.setContentsMargins(0, 0, 0, 0)
        right.setAlignment(Qt.AlignVCenter)

        user_chip = QFrame()
        user_chip.setFixedHeight(28)
        user_chip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        user_chip.setStyleSheet(
            f"QFrame {{ background: #f3f4f6; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
        )
        ul = QHBoxLayout(user_chip)
        ul.setContentsMargins(8, 0, 8, 0)
        ul.setSpacing(8)

        # Stitch: h-2 w-2 green ping + solid core
        status_wrap = QFrame()
        status_wrap.setFixedSize(8, 8)
        status_wrap.setStyleSheet("background: transparent; border: none;")
        glow = QFrame(status_wrap)
        glow.setGeometry(0, 0, 8, 8)
        glow.setStyleSheet(
            "background: rgba(16, 185, 129, 0.45); border-radius: 4px; border: none;"
        )
        dot = QFrame(status_wrap)
        dot.setGeometry(1, 1, 6, 6)
        dot.setStyleSheet(
            f"background: {T.SUCCESS}; border-radius: 3px; border: none;"
        )
        self._online_dot = status_wrap

        uname = QLabel(D.CURRENT_USER)
        uname.setStyleSheet(
            f"font-weight: 600; color: {T.TEXT_PRIMARY}; border: none; "
            f"background: transparent; font-size: 9pt;"
        )
        urole = QLabel(f"· {D.CURRENT_ROLE}")
        urole.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; border: none; background: transparent; "
            f"font-size: 8pt;"
        )
        ul.addWidget(status_wrap, 0, Qt.AlignVCenter)
        ul.addWidget(uname, 0, Qt.AlignVCenter)
        ul.addWidget(urole, 0, Qt.AlignVCenter)

        logout = QFrame()
        logout.setCursor(Qt.PointingHandCursor)
        logout.setFixedHeight(28)
        logout.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        logout.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: 4px; }}"
            f"QFrame:hover {{ background: {T.DANGER_BG}; }}"
        )
        lo = QHBoxLayout(logout)
        lo.setContentsMargins(10, 0, 10, 0)
        lo.setSpacing(4)
        lo_ic = QLabel()
        lo_ic.setFixedSize(14, 14)
        lo_ic.setPixmap(icon_pixmap("logout", size=14, color=T.DANGER))
        lo_ic.setStyleSheet("background: transparent; border: none;")
        lo_txt = QLabel("Logout")
        lo_txt.setStyleSheet(
            f"color: {T.DANGER}; font-size: 9pt; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lo.addWidget(lo_ic, 0, Qt.AlignVCenter)
        lo.addWidget(lo_txt, 0, Qt.AlignVCenter)
        logout.mousePressEvent = (
            lambda e: toast(self, "Logout — login gate coming next.")
        )

        avatar = QLabel()
        avatar.setFixedSize(28, 28)
        avatar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background: {T.PRIMARY_CONTAINER}; border-radius: 14px; border: none;"
        )
        avatar.setPixmap(icon_pixmap("person", size=16, color="#ffffff"))

        right.addWidget(user_chip, 0, Qt.AlignVCenter)
        right.addWidget(logout, 0, Qt.AlignVCenter)
        right.addWidget(avatar, 0, Qt.AlignVCenter)

        # Left cluster | search (capped width) | stretch | right cluster (far right)
        lay.addLayout(left, 0)
        lay.addWidget(search_box, 0, Qt.AlignVCenter)
        lay.addStretch(1)
        lay.addLayout(right, 0)
        return bar

    def _search_focus_in(self, event):
        QLineEdit.focusInEvent(self.search, event)
        self._search_box.setStyleSheet(
            f"QFrame#globalSearchBox {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.FOCUS_BORDER}; border-radius: 4px; }}"
        )

    def _search_focus_out(self, event):
        QLineEdit.focusOutEvent(self.search, event)
        self._search_box.setStyleSheet(
            f"QFrame#globalSearchBox {{ background: #f3f4f6; "
            f"border: 1px solid {T.BORDER_STRONG}; border-radius: 4px; }}"
        )

    def _build_breadcrumb(self) -> QFrame:
        """Stitch header row 2: desktop_windows + terminal breadcrumb | server/sync."""
        bar = QFrame()
        bar.setObjectName("breadcrumbBar")
        bar.setFixedHeight(T.BREADCRUMB_H)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(6)

        term_ic = QLabel()
        term_ic.setFixedSize(14, 14)
        term_ic.setPixmap(icon_pixmap("desktop_windows", size=14, color=T.TEXT_SECONDARY))
        term_ic.setStyleSheet("background: transparent; border: none;")

        left = QLabel(f"{D.TERMINAL_NAME}")
        left.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 8pt; "
            f"border: none; background: transparent;"
        )
        sep = QLabel("/")
        sep.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 8pt; "
            f"border: none; background: transparent;"
        )
        self.breadcrumb = QLabel("Operations / Sales & Distribution")
        self.breadcrumb.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 8pt; font-weight: 600; "
            f"border: none; background: transparent;"
        )

        right = QLabel(f"Server: 192.168.1.104 (Connected)    Sync: Instant")
        # Prefer sample_data status strings when present
        server = getattr(D, "SERVER_STATUS", "Server: 192.168.1.104 (Connected)")
        sync = getattr(D, "SYNC_STATUS", "Sync: Instant")
        right.setText(f"{server}    {sync}")
        right.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 8pt; "
            f"border: none; background: transparent;"
        )

        lay.addWidget(term_ic)
        lay.addWidget(left)
        lay.addWidget(sep)
        lay.addWidget(self.breadcrumb)
        lay.addStretch()
        lay.addWidget(right)
        return bar

    def _register_screens(self):
        self._ensure_screen("dashboard")

    def _create_screen(self, key: str) -> QWidget:
        if key == "dashboard":
            from app.screens.dashboard import DashboardScreen
            return DashboardScreen(navigate_cb=self.navigate)
        if key == "company":
            from app.screens.company_details import CompanyDetailsScreen
            return CompanyDetailsScreen()
        if key == "parties":
            from app.screens.party_master import PartyMasterScreen
            return PartyMasterScreen()
        if key == "groups":
            from app.screens.groups import GroupsScreen
            return GroupsScreen()
        if key == "products":
            from app.screens.product_master import ProductMasterScreen
            return ProductMasterScreen()
        if key == "godowns":
            from app.screens.godowns import GodownsScreen
            return GodownsScreen()
        if key == "purchase":
            from app.screens.transaction_entry import TransactionEntryScreen
            return TransactionEntryScreen(mode="purchase")
        if key == "sales":
            from app.screens.transaction_entry import TransactionEntryScreen
            return TransactionEntryScreen(mode="sales")
        if key == "cash_flow":
            from app.screens.cash_flow import CashFlowScreen
            return CashFlowScreen()
        if key == "billwise":
            from app.screens.billwise import BillwiseScreen
            return BillwiseScreen(mode="receipt")
        if key == "ledger_stmt":
            from app.screens.reports_suite import LedgerStatementScreen
            return LedgerStatementScreen()
        if key == "registers":
            from app.screens.reports_suite import RegistersScreen
            return RegistersScreen()
        if key == "reports_ar_ap":
            from app.screens.reports import ReportsScreen
            return ReportsScreen()
        if key == "export_tools":
            from app.screens.reports_suite import ExportToolsScreen
            return ExportToolsScreen()
        if key == "audit_trail":
            from app.screens.settings_suite import AuditTrailScreen
            return AuditTrailScreen()
        if key == "users":
            from app.screens.settings_suite import UsersScreen
            return UsersScreen()
        if key == "ac_year":
            from app.screens.settings_suite import AccountYearManagementScreen
            return AccountYearManagementScreen(on_fy_change=self._on_fy_change)
        raise KeyError(f"Unknown screen: {key}")

    def _ensure_screen(self, key: str):
        if key in self._screen_keys:
            return
        widget = self._create_screen(key)
        idx = self.stack.addWidget(widget)
        self._screen_keys[key] = idx

    def navigate(self, key: str):
        if key == "license":
            from app.screens.license_dialog import LicenseActivationDialog
            dlg = LicenseActivationDialog(self)
            dlg.exec()
            return

        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)

        for gkey, _, items in NAV_GROUPS:
            if any(k == key for k, _, _, _ in items):
                if not self._group_open.get(gkey, True):
                    self._toggle_group(gkey)
                break

        self.breadcrumb.setText(self._crumb_map.get(key, key))
        self._ensure_screen(key)
        self.stack.setCurrentIndex(self._screen_keys[key])
        widget = self.stack.currentWidget()
        if hasattr(widget, "focus_entry"):
            widget.focus_entry()

    def _on_fy_change(self, year: str):
        self.fy_badge.setText(year)
        toast(self, f"Fiscal year switched to {year}")

    def _toggle_nav(self):
        self.nav_expanded = not self.nav_expanded
        width = T.NAV_EXPANDED if self.nav_expanded else T.NAV_COLLAPSED
        self._nav_rail.setFixedWidth(width)
        self._nav_brand.setVisible(self.nav_expanded)
        self._nav_sub.setVisible(self.nav_expanded)
        self._nav_pos.setVisible(self.nav_expanded)
        self._dash_chip.setVisible(self.nav_expanded)
        for gkey, header in self._group_headers.items():
            header.setVisible(self.nav_expanded)
            self._group_bodies[gkey].setVisible(
                self.nav_expanded and self._group_open.get(gkey, True)
            )
        for key, btn in self._nav_buttons.items():
            label = self._nav_labels[key]
            child = key != "dashboard"
            btn.setIcon(nav_icon(key, 20 if not self.nav_expanded else 14))
            btn.setIconSize(icon_size(20 if not self.nav_expanded else 14))
            if self.nav_expanded:
                btn.setText(f"  {label}")
                btn.setToolTip("")
                btn.setStyleSheet(self._nav_btn_style(child=child, collapsed=False))
            else:
                btn.setText("")
                btn.setToolTip(label)
                btn.setStyleSheet(self._nav_btn_style(child=False, collapsed=True))

    def _live_search(self, text: str):
        q = text.strip().lower()
        if len(q) < 2:
            return
        hits = []
        for p in D.PARTIES:
            if q in p["name"].lower():
                hits.append(f"Party: {p['name']}")
        for p in D.PRODUCTS:
            if q in p["name"].lower() or q in p["sku"].lower():
                hits.append(f"Item: {p['name']}")
        for t in D.RECENT_TXNS:
            if q in t["doc"].lower() or q in t["party"].lower():
                hits.append(f"Invoice: {t['doc']}")
        if hits:
            toast(self, "  ·  ".join(hits[:3]), 1800)

    def _do_search(self):
        q = self.search.text().strip()
        if not q:
            return
        ql = q.lower()
        for p in D.PARTIES:
            if ql in p["name"].lower():
                self.navigate("parties")
                toast(self, f"Opened parties — matched {p['name']}")
                return
        for p in D.PRODUCTS:
            if ql in p["name"].lower() or ql in p["sku"].lower():
                self.navigate("products")
                toast(self, f"Opened catalog — matched {p['name']}")
                return
        for t in D.RECENT_TXNS:
            if ql in t["doc"].lower():
                self.navigate("sales" if t["type"] == "Sale" else "purchase")
                toast(self, f"Opened {t['doc']}")
                return
        toast(self, f"No match for “{q}”")

    def _wire_global_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+K"), self, activated=self._focus_search)
        QShortcut(QKeySequence("/"), self, activated=self._focus_search_slash)
        QShortcut(QKeySequence("F1"), self, activated=lambda: self.navigate("cash_flow"))
        QShortcut(QKeySequence("F2"), self, activated=lambda: self.navigate("sales"))
        QShortcut(QKeySequence("F3"), self, activated=lambda: self.navigate("purchase"))
        QShortcut(QKeySequence("F4"), self, activated=self._on_f4)
        QShortcut(QKeySequence("F6"), self, activated=lambda: self.navigate("cash_flow"))
        QShortcut(QKeySequence("F10"), self, activated=lambda: self.navigate("dashboard"))
        QShortcut(QKeySequence("Alt+1"), self, activated=lambda: self._open_group("masters"))
        QShortcut(QKeySequence("Alt+2"), self, activated=lambda: self.navigate("sales"))
        QShortcut(QKeySequence("Alt+3"), self, activated=lambda: self.navigate("purchase"))
        QShortcut(QKeySequence("Alt+4"), self, activated=lambda: self.navigate("cash_flow"))
        QShortcut(QKeySequence("Esc"), self, activated=self._esc)

    def _on_f4(self):
        """F4: Party Lookup on Billwise; otherwise open Ledger master."""
        widget = self.stack.currentWidget()
        if widget is not None and hasattr(widget, "_open_party_lookup"):
            widget._open_party_lookup()
            return
        self.navigate("parties")

    def _focus_search(self):
        self.search.setFocus()
        self.search.selectAll()

    def _focus_search_slash(self):
        w = self.focusWidget()
        if isinstance(w, QLineEdit) and w is not self.search:
            return
        self._focus_search()

    def _open_group(self, gkey: str):
        if not self._group_open.get(gkey, True):
            self._toggle_group(gkey)
        items = next(items for k, _, items in NAV_GROUPS if k == gkey)
        if items:
            self.navigate(items[0][0])

    def _esc(self):
        if self.search.hasFocus():
            self.search.clear()
            self.search.clearFocus()
            return
        toast(self, "Ready")
