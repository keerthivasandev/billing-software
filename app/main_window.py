"""Application shell: dark nav rail, top bar, breadcrumb, content stack."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenu,
    QMessageBox, QPushButton, QScrollArea, QShortcut, QStackedWidget,
    QToolButton, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.screens.dashboard import DashboardScreen
from app.screens.license_dialog import LicenseActivationDialog
from app.screens.party_master import PartyMasterScreen
from app.screens.product_master import ProductMasterScreen
from app.screens.reports import ReportsScreen
from app.screens.transaction_entry import TransactionEntryScreen
from app.styles import tokens as T


NAV_ITEMS = [
    ("dashboard", "Dashboard", "Dashboard", None),
    ("sep_masters", "MASTERS", None, "section"),
    ("parties", "Parties (Customers & Suppliers)", "Masters > Parties (Customers & Suppliers)", "masters"),
    ("products", "Products", "Masters > Products", "masters"),
    ("item_groups", "Item Group / Category", "Masters > Item Group / Category", "masters"),
    ("warehouses", "Warehouse / Location", "Masters > Warehouse / Location", "masters"),
    ("firm", "Firm", "Masters > Firm", "masters"),
    ("sep_txn", "TRANSACTIONS", None, "section"),
    ("opening_stock", "Opening Stock", "Transactions > Opening Stock", "txn"),
    ("purchase", "Purchase", "Transactions > Purchase", "txn"),
    ("sales", "Sales Invoice", "Transactions > Sales Invoice", "txn"),
    ("purchase_return", "Purchase Return", "Transactions > Purchase Return", "txn"),
    ("sales_return", "Sales Return", "Transactions > Sales Return", "txn"),
    ("payment_out", "Payment Out", "Transactions > Payment Out", "txn"),
    ("receipt_in", "Receipt In", "Transactions > Receipt In", "txn"),
    ("journal", "Journal Entry", "Transactions > Journal Entry", "txn"),
    ("billwise_pay", "Bill-wise Settlement (Payments)", "Transactions > Bill-wise Settlement (Payments)", "txn"),
    ("billwise_rcpt", "Bill-wise Settlement (Receipts)", "Transactions > Bill-wise Settlement (Receipts)", "txn"),
    ("estimate", "Quotation / Estimate", "Transactions > Quotation / Estimate", "txn"),
    ("sep_reports", "REPORTS", None, "section"),
    ("reports_ar_ap", "Payables & Receivables Summary", "Reports > Payables & Receivables Summary", "reports"),
    ("reports_stock", "Stock History by Item", "Reports > Stock History by Item", "reports"),
    ("reports_daybook", "Daily Transaction Log", "Reports > Daily Transaction Log", "reports"),
    ("reports_trial", "Trial Balance", "Reports > Trial Balance", "reports"),
    ("sep_settings", "SETTINGS / TOOLS", None, "section"),
    ("fy_settings", "Financial Year Settings", "Settings > Financial Year Settings", "settings"),
    ("users", "User & Role Permissions", "Settings > User & Role Permissions", "settings"),
    ("backup", "Backup & Restore", "Settings > Backup & Restore", "settings"),
    ("license", "License Activation", "Settings > License Activation", "settings"),
]

# Short labels for collapsed rail
NAV_SHORT = {
    "dashboard": "DB",
    "parties": "PT",
    "products": "PR",
    "item_groups": "IG",
    "warehouses": "WH",
    "firm": "FM",
    "opening_stock": "OS",
    "purchase": "PU",
    "sales": "SA",
    "purchase_return": "PR",
    "sales_return": "SR",
    "payment_out": "PO",
    "receipt_in": "RI",
    "journal": "JE",
    "billwise_pay": "BP",
    "billwise_rcpt": "BR",
    "estimate": "QT",
    "reports_ar_ap": "AR",
    "reports_stock": "ST",
    "reports_daybook": "DY",
    "reports_trial": "TB",
    "fy_settings": "FY",
    "users": "UR",
    "backup": "BK",
    "license": "LC",
}


class PlaceholderScreen(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; }}"
        )
        bl = QVBoxLayout(box)
        bl.setContentsMargins(20, 20, 20, 20)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-size: {T.FONT_SIZE_TITLE}pt; font-weight: bold;")
        hint = QLabel(
            "This screen is scaffolded and ready for business logic.\n"
            "Final Windows .exe will use the same layout and Fusion theme."
        )
        hint.setStyleSheet(f"color: {T.TEXT_SECONDARY};")
        hint.setWordWrap(True)
        bl.addWidget(lbl)
        bl.addWidget(hint)
        bl.addStretch()
        lay.addWidget(box)
        lay.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{D.COMPANY_NAME} — Wholesale Billing & Inventory")
        self.resize(1366, 768)
        self.setMinimumSize(1280, 720)
        self.nav_expanded = True
        self._nav_buttons = {}
        self._nav_labels = {}
        self._section_labels = []
        self._screen_keys = {}

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
            f"  {D.COMPANY_NAME}  |  {D.FINANCIAL_YEAR}  |  Ready  |  "
            f"F5 New Entry   F9 Save & Print   F10 Save & New   Esc Cancel"
        )

    def _build_nav(self) -> QFrame:
        rail = QFrame()
        rail.setObjectName("navRail")
        rail.setFixedWidth(T.NAV_EXPANDED)
        self._nav_rail = rail

        outer = QVBoxLayout(rail)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Brand header
        header = QWidget()
        hl = QVBoxLayout(header)
        hl.setContentsMargins(10, 12, 10, 4)
        hl.setSpacing(2)
        top = QHBoxLayout()
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setObjectName("navToggle")
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

        # Scrollable nav items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        body = QWidget()
        body.setStyleSheet(f"background-color: {T.NAV_BG};")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(4, 4, 4, 8)
        lay.setSpacing(1)

        for key, label, crumb, kind in NAV_ITEMS:
            if kind == "section":
                sec = QLabel(label)
                sec.setProperty("class", "navSection")
                sec.setStyleSheet(
                    f"color: #7A8799; font-size: {T.FONT_SIZE_SHORTCUT}pt; font-weight: bold; "
                    "padding: 12px 10px 4px 10px;"
                )
                sec.setObjectName(f"sec_{key}")
                self._section_labels.append(sec)
                lay.addWidget(sec)
                continue

            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("class", "navItem")
            btn.setStyleSheet("")  # use global QSS .navItem
            # Ensure class selector works — PyQt needs polish
            btn.setStyleSheet(
                f"QPushButton {{ background: transparent; border: none; "
                f"border-left: 3px solid transparent; text-align: left; "
                f"padding: 5px 8px; color: {T.NAV_TEXT}; min-height: 22px; "
                f"font-size: {T.FONT_SIZE_NAV}pt; }}"
                f"QPushButton:hover {{ background-color: {T.NAV_HOVER}; color: {T.NAV_TEXT_ACTIVE}; }}"
                f"QPushButton:checked {{ background-color: {T.NAV_ACTIVE}; color: {T.NAV_TEXT_ACTIVE}; "
                f"font-weight: bold; border-left: 3px solid {T.ACCENT}; }}"
            )
            btn.clicked.connect(lambda checked, k=key: self.navigate(k))
            self._nav_buttons[key] = btn
            self._nav_labels[key] = label
            lay.addWidget(btn)

        lay.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)
        return rail

    def _build_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(40)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(8)

        company = QLabel(D.COMPANY_NAME)
        company.setObjectName("companyTitle")

        fy = QLabel(D.FINANCIAL_YEAR)
        fy.setObjectName("fyBadge")

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search party, item, invoice…  (Enter)")
        self.search.setFixedWidth(260)
        self.search.returnPressed.connect(self._do_search)

        user = QLabel(f"{D.CURRENT_USER}  ·  {D.CURRENT_ROLE}")
        user.setObjectName("userBadge")

        self.btn_new = QToolButton()
        self.btn_new.setText("+ New")
        self.btn_new.setPopupMode(QToolButton.MenuButtonPopup)
        menu = QMenu(self)
        menu.addAction("New Sale          F5", lambda: self.navigate("sales"))
        menu.addAction("New Purchase", lambda: self.navigate("purchase"))
        menu.addAction("New Payment", lambda: self.navigate("payment_out"))
        self.btn_new.setMenu(menu)
        self.btn_new.clicked.connect(lambda: self.navigate("sales"))

        lay.addWidget(company)
        lay.addWidget(fy)
        lay.addStretch()
        lay.addWidget(self.search)
        lay.addWidget(user)
        lay.addWidget(self.btn_new)
        return bar

    def _build_breadcrumb(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("breadcrumbBar")
        bar.setFixedHeight(26)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 14, 0)
        self.breadcrumb = QLabel("Dashboard")
        self.breadcrumb.setObjectName("breadcrumbLabel")
        self.breadcrumb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt;"
        )
        lay.addWidget(self.breadcrumb)
        lay.addStretch()
        return bar

    def _register_screens(self):
        screens = {
            "dashboard": DashboardScreen(),
            "sales": TransactionEntryScreen(mode="sales"),
            "purchase": TransactionEntryScreen(mode="purchase"),
            "parties": PartyMasterScreen(),
            "products": ProductMasterScreen(),
            "reports_ar_ap": ReportsScreen(),
        }
        for key, widget in screens.items():
            idx = self.stack.addWidget(widget)
            self._screen_keys[key] = idx

        for key, label, crumb, kind in NAV_ITEMS:
            if kind == "section" or key in self._screen_keys or key == "license":
                continue
            idx = self.stack.addWidget(PlaceholderScreen(label))
            self._screen_keys[key] = idx

    def navigate(self, key: str):
        if key == "license":
            dlg = LicenseActivationDialog(self)
            dlg.exec_()
            return

        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)

        crumb = next((c for k, _, c, _ in NAV_ITEMS if k == key), key)
        if crumb:
            self.breadcrumb.setText(crumb)

        if key in self._screen_keys:
            self.stack.setCurrentIndex(self._screen_keys[key])
            widget = self.stack.currentWidget()
            if hasattr(widget, "focus_entry"):
                widget.focus_entry()

    def _toggle_nav(self):
        self.nav_expanded = not self.nav_expanded
        width = T.NAV_EXPANDED if self.nav_expanded else T.NAV_COLLAPSED
        self._nav_rail.setFixedWidth(width)
        self._nav_brand.setVisible(self.nav_expanded)
        self._nav_sub.setVisible(self.nav_expanded)
        for sec in self._section_labels:
            sec.setVisible(self.nav_expanded)
        for key, btn in self._nav_buttons.items():
            label = self._nav_labels[key]
            if self.nav_expanded:
                btn.setText(label)
                btn.setToolTip("")
            else:
                btn.setText(NAV_SHORT.get(key, label[:2].upper()))
                btn.setToolTip(label)

    def _do_search(self):
        q = self.search.text().strip()
        if not q:
            return
        QMessageBox.information(self, "Search", f"Search for: {q}\n(Connect to index later.)")

    def _wire_global_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.navigate("sales"))
