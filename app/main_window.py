"""Application shell — Zoho Inventory layout: accordion nav, top bar, stack."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenu, QPushButton,
    QScrollArea, QStackedWidget, QToolButton, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import toast
from app.widgets.icons import icon_size, nav_icon, qicon


# Accordion groups: (group_key, title, [(nav_key, label, crumb), ...])
NAV_GROUPS = [
    ("masters", "1. Master Setup", [
        ("company", "1.1 Company Details", "Master Setup > Company Details"),
        ("parties", "1.2 Ledger Parties", "Master Setup > Ledger Parties"),
        ("groups", "1.3 Group Classifications", "Master Setup > Group Classifications"),
        ("products", "1.4 Product Catalog", "Master Setup > Product Catalog"),
        ("godowns", "1.5 Godowns", "Master Setup > Godowns"),
    ]),
    ("operations", "2. Operations & Entry", [
        ("purchase", "2.1 Purchases", "Operations > Purchases"),
        ("sales", "2.2 Sales Invoices", "Operations > Sales Invoices"),
        ("cash_flow", "2.3 Cash Flow", "Operations > Cash Flow"),
        ("billwise", "2.4 Billwise Settlement", "Operations > Billwise Settlement"),
        ("estimate", "2.5 Estimates / Quotations", "Operations > Estimates"),
    ]),
    ("reports", "3. Reports & Audits", [
        ("ledger_stmt", "3.1 Ledger Statement", "Reports > Ledger Statement"),
        ("registers", "3.2 Sales & Purchase Registers", "Reports > Registers"),
        ("reports_ar_ap", "Payables & Receivables", "Reports > Payables & Receivables"),
        ("export_tools", "3.3 Export Tools", "Reports > Export Tools"),
    ]),
    ("settings", "4. Settings & A/c Year", [
        ("audit_trail", "4.1 Audit Trail", "Settings > Audit Trail"),
        ("users", "4.2 User Management", "Settings > User Management"),
        ("change_fy", "4.3 Change Fiscal Year", "Settings > Change Fiscal Year"),
        ("rollover", "4.4 Create / Rollover New Year", "Settings > Rollover New Year"),
        ("license", "License Activation", "Settings > License Activation"),
    ]),
]

NAV_SHORT = {
    "dashboard": "Home",
    "company": "Co",
    "parties": "Pt",
    "groups": "Gr",
    "products": "Pr",
    "godowns": "Gd",
    "purchase": "Pu",
    "sales": "Sa",
    "cash_flow": "Cf",
    "billwise": "Bw",
    "estimate": "Qt",
    "ledger_stmt": "Ld",
    "registers": "Rg",
    "reports_ar_ap": "AR",
    "export_tools": "Ex",
    "audit_trail": "Au",
    "users": "Ur",
    "change_fy": "FY",
    "rollover": "Ro",
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
        self._group_headers = {}
        self._group_bodies = {}
        self._group_open = {k: True for k, _, _ in NAV_GROUPS}
        self._screen_keys = {}
        self._crumb_map = {"dashboard": "Dashboard / Home"}
        for _, _, items in NAV_GROUPS:
            for key, _, crumb in items:
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
        self.statusBar().showMessage(
            f"  {D.COMPANY_NAME}  |  {D.FINANCIAL_YEAR}  |  "
            f"Ctrl+K Search   Alt+1 Masters   Alt+2 Sales   Alt+3 Purchase   Alt+4 Cash   Esc Close"
        )

    def _nav_btn_style(self, child=False, collapsed=False) -> str:
        if collapsed:
            return (
                f"QPushButton {{ background: transparent; border: none; "
                f"border-left: 3px solid transparent; text-align: center; "
                f"padding: 12px 2px; color: {T.NAV_TEXT_ACTIVE}; min-height: 36px; "
                f"font-size: 10pt; font-weight: bold; }}"
                f"QPushButton:hover {{ background-color: {T.NAV_HOVER}; color: {T.NAV_TEXT_ACTIVE}; }}"
                f"QPushButton:checked {{ background-color: {T.NAV_ACTIVE}; color: {T.NAV_TEXT_ACTIVE}; "
                f"border-left: 3px solid #93c5fd; }}"
            )
        pad = "5px 8px 5px 18px" if child else "6px 8px"
        return (
            f"QPushButton {{ background: transparent; border: none; "
            f"border-left: 3px solid transparent; text-align: left; "
            f"padding: {pad}; color: {T.NAV_TEXT}; min-height: 22px; "
            f"font-size: {T.FONT_SIZE_NAV}pt; }}"
            f"QPushButton:hover {{ background-color: {T.NAV_HOVER}; color: {T.NAV_TEXT_ACTIVE}; }}"
            f"QPushButton:checked {{ background-color: {T.NAV_ACTIVE}; color: {T.NAV_TEXT_ACTIVE}; "
            f"font-weight: bold; border-left: 3px solid #93c5fd; }}"
        )

    def _build_nav(self) -> QFrame:
        rail = QFrame()
        rail.setObjectName("navRail")
        rail.setFixedWidth(T.NAV_EXPANDED)
        self._nav_rail = rail

        outer = QVBoxLayout(rail)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QWidget()
        hl = QVBoxLayout(header)
        hl.setContentsMargins(10, 12, 10, 4)
        hl.setSpacing(2)
        top = QHBoxLayout()
        self.btn_toggle = QPushButton()
        self.btn_toggle.setObjectName("navToggle")
        self.btn_toggle.setIcon(qicon("menu", size=18))
        self.btn_toggle.setIconSize(icon_size(18))
        self.btn_toggle.setToolTip("Collapse / Expand menu")
        self.btn_toggle.clicked.connect(self._toggle_nav)
        brand = QLabel("Wholesale ERP")
        brand.setObjectName("navBrand")
        self._nav_brand = brand
        top.addWidget(self.btn_toggle)
        top.addWidget(brand)
        top.addStretch()
        hl.addLayout(top)
        sub = QLabel("Billing · Stock · GST")
        sub.setObjectName("navBrandSub")
        self._nav_sub = sub
        hl.addWidget(sub)
        outer.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        body = QWidget()
        body.setStyleSheet(f"background-color: {T.NAV_BG};")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(4, 4, 4, 8)
        lay.setSpacing(2)

        # Dashboard direct
        dash = QPushButton("  Dashboard / Home")
        dash.setCheckable(True)
        dash.setCursor(Qt.PointingHandCursor)
        dash.setIcon(nav_icon("dashboard", 18))
        dash.setIconSize(icon_size(18))
        dash.setStyleSheet(self._nav_btn_style(False))
        dash.clicked.connect(lambda: self.navigate("dashboard"))
        self._nav_buttons["dashboard"] = dash
        self._nav_labels["dashboard"] = "Dashboard / Home"
        lay.addWidget(dash)

        for gkey, gtitle, items in NAV_GROUPS:
            header_btn = QPushButton(f"  {gtitle}")
            header_btn.setCursor(Qt.PointingHandCursor)
            header_btn.setIcon(qicon("caret-down", 14))
            header_btn.setIconSize(icon_size(14))
            header_btn.setStyleSheet(
                f"QPushButton {{ background: {T.NAV_HOVER}; border: none; text-align: left; "
                f"padding: 8px 10px; color: {T.NAV_TEXT_ACTIVE}; font-weight: bold; "
                f"font-size: {T.FONT_SIZE_NAV}pt; border-radius: {T.RADIUS}px; }}"
                f"QPushButton:hover {{ background-color: #374151; }}"
            )
            header_btn.clicked.connect(lambda checked=False, k=gkey: self._toggle_group(k))
            self._group_headers[gkey] = header_btn
            self._group_open[gkey] = True
            lay.addWidget(header_btn)

            children = QWidget()
            cl = QVBoxLayout(children)
            cl.setContentsMargins(0, 0, 0, 4)
            cl.setSpacing(1)
            for key, label, _crumb in items:
                btn = QPushButton(f"  {label}")
                btn.setCheckable(True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setIcon(nav_icon(key, 16))
                btn.setIconSize(icon_size(16))
                btn.setStyleSheet(self._nav_btn_style(True))
                btn.clicked.connect(lambda checked=False, k=key: self.navigate(k))
                self._nav_buttons[key] = btn
                self._nav_labels[key] = label
                cl.addWidget(btn)
            self._group_bodies[gkey] = children
            lay.addWidget(children)

        lay.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)
        return rail

    def _toggle_group(self, gkey: str):
        open_ = not self._group_open.get(gkey, True)
        self._group_open[gkey] = open_
        body = self._group_bodies[gkey]
        body.setVisible(open_ and self.nav_expanded)
        title = next(t for k, t, _ in NAV_GROUPS if k == gkey)
        header = self._group_headers[gkey]
        header.setText(f"  {title}")
        header.setIcon(qicon("caret-down" if open_ else "caret-right", 14))
        header.setIconSize(icon_size(14))

    def _build_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(44)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(10)

        company = QLabel(f"{D.COMPANY_NAME} — {D.COMPANY_TAGLINE}")
        company.setObjectName("companyTitle")
        self._company_label = company

        self.fy_badge = QLabel(D.FINANCIAL_YEAR)
        self.fy_badge.setObjectName("fyBadge")
        self.fy_badge.setCursor(Qt.PointingHandCursor)
        self.fy_badge.setToolTip("Click to change fiscal year")
        self.fy_badge.mousePressEvent = lambda e: self.navigate("change_fy")

        self.search = QLineEdit()
        self.search.setObjectName("globalSearch")
        self.search.setPlaceholderText("Search parties, items, invoices…  Ctrl+K  /")
        self.search.setFixedWidth(300)
        self.search.textChanged.connect(self._live_search)
        self.search.returnPressed.connect(self._do_search)

        user = QLabel(f"{D.CURRENT_USER} · {D.CURRENT_ROLE}")
        user.setObjectName("userBadge")

        self.btn_new = QToolButton()
        self.btn_new.setText("+ New Transaction")
        self.btn_new.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.btn_new.setPopupMode(QToolButton.MenuButtonPopup)
        self.btn_new.setMinimumWidth(160)
        self.btn_new.setMinimumHeight(T.BUTTON_H)
        menu = QMenu(self)
        menu.addAction("Sales Invoice", lambda: self.navigate("sales"))
        menu.addAction("Purchase", lambda: self.navigate("purchase"))
        menu.addAction("Cash Entry", lambda: self.navigate("cash_flow"))
        menu.addAction("Quotation", lambda: self.navigate("estimate"))
        self.btn_new.setMenu(menu)
        self.btn_new.clicked.connect(lambda: self.navigate("sales"))

        lay.addWidget(company)
        lay.addWidget(self.fy_badge)
        lay.addStretch()
        lay.addWidget(self.search)
        lay.addSpacing(8)
        lay.addWidget(user)
        lay.addSpacing(10)
        lay.addWidget(self.btn_new)
        return bar

    def _build_breadcrumb(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("breadcrumbBar")
        bar.setFixedHeight(26)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 14, 0)
        self.breadcrumb = QLabel("Dashboard / Home")
        self.breadcrumb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt;"
        )
        lay.addWidget(self.breadcrumb)
        lay.addStretch()
        return bar

    def _register_screens(self):
        # Lazy init: only dashboard at startup (potato-PC friendly).
        self._ensure_screen("dashboard")

    def _create_screen(self, key: str) -> QWidget:
        if key == "dashboard":
            from app.screens.dashboard import DashboardScreen
            return DashboardScreen()
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
        if key == "estimate":
            from app.screens.estimate import EstimateScreen
            return EstimateScreen(navigate_cb=self.navigate)
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
        if key == "change_fy":
            from app.screens.settings_suite import FiscalYearScreen
            return FiscalYearScreen(on_fy_change=self._on_fy_change)
        if key == "rollover":
            from app.screens.settings_suite import RolloverScreen
            return RolloverScreen()
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

        # Ensure parent accordion is open
        for gkey, _, items in NAV_GROUPS:
            if any(k == key for k, _, _ in items):
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
        self.statusBar().showMessage(
            f"  {D.COMPANY_NAME}  |  {year}  |  Fiscal year switched", 4000
        )

    def _toggle_nav(self):
        self.nav_expanded = not self.nav_expanded
        width = T.NAV_EXPANDED if self.nav_expanded else T.NAV_COLLAPSED
        self._nav_rail.setFixedWidth(width)
        self._nav_brand.setVisible(self.nav_expanded)
        self._nav_sub.setVisible(self.nav_expanded)
        for gkey, header in self._group_headers.items():
            header.setVisible(self.nav_expanded)
            self._group_bodies[gkey].setVisible(
                self.nav_expanded and self._group_open.get(gkey, True)
            )
        for key, btn in self._nav_buttons.items():
            label = self._nav_labels[key]
            child = key != "dashboard"
            btn.setIcon(nav_icon(key, 20 if not self.nav_expanded else 16))
            btn.setIconSize(icon_size(20 if not self.nav_expanded else 16))
            if self.nav_expanded:
                btn.setText(f"  {label}")
                btn.setToolTip("")
                btn.setStyleSheet(self._nav_btn_style(child=child, collapsed=False))
            else:
                # Icon-only rail — Ant SVG, no tiny Unicode glyphs
                btn.setText("")
                btn.setToolTip(label)
                btn.setStyleSheet(self._nav_btn_style(child=False, collapsed=True))

    def _live_search(self, text: str):
        q = text.strip().lower()
        if len(q) < 2:
            return
        # Lightweight in-memory filter preview via status bar (no blocking dialog)
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
            self.statusBar().showMessage("  ·  ".join(hits[:4]), 2500)

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
        QShortcut(QKeySequence("Alt+1"), self, activated=lambda: self._open_group("masters"))
        QShortcut(QKeySequence("Alt+2"), self, activated=lambda: self.navigate("sales"))
        QShortcut(QKeySequence("Alt+3"), self, activated=lambda: self.navigate("purchase"))
        QShortcut(QKeySequence("Alt+4"), self, activated=lambda: self.navigate("cash_flow"))
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.navigate("sales"))
        QShortcut(QKeySequence("Esc"), self, activated=self._esc)

    def _focus_search(self):
        self.search.setFocus()
        self.search.selectAll()

    def _focus_search_slash(self):
        # Don't steal typing from focused line edits
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
        # Dismiss search focus / toast; never block with dialogs
        if self.search.hasFocus():
            self.search.clear()
            self.search.clearFocus()
            return
        toast(self, "Ready")
