"""Settings — Audit Trail, Users, A/c Year Management."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QFormLayout, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import (
    card_frame, field_label, make_button, page_title, toast, ui_font,
)


class AuditTrailScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        root.addWidget(page_title("4.1 Audit Trail / Operator Logs"))

        self.table = QTableWidget(len(D.AUDIT_LOG), 4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "User", "Module", "Action"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        S.apply_table_style(self.table)
        for r, row in enumerate(D.AUDIT_LOG):
            for c, key in enumerate(("ts", "user", "module", "action")):
                it = QTableWidgetItem(row[key])
                it.setFont(ui_font(T.FONT_SIZE_GRID))
                self.table.setItem(r, c, it)
        root.addWidget(self.table, stretch=1)


class UsersScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.users = [dict(u) for u in D.USERS]
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        bar = QHBoxLayout()
        bar.addWidget(page_title("4.2 User Management"))
        bar.addStretch()
        save = make_button("Save User", "primary")
        save.clicked.connect(self._save)
        bar.addWidget(save)
        root.addLayout(bar)

        split = QHBoxLayout()
        left = card_frame()
        left.setFixedWidth(240)
        ll = QVBoxLayout(left)
        self.list = QListWidget()
        self.list.setSpacing(2)
        self.list.setUniformItemSizes(True)
        self.list.currentRowChanged.connect(self._load)
        ll.addWidget(self.list)
        split.addWidget(left)

        right = card_frame()
        fl = QFormLayout(right)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(8)
        fl.setLabelAlignment(Qt.AlignRight)
        self.name = QLineEdit()
        self.username = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["Admin", "Billing Clerk", "Inventory Manager"])
        self.active = QCheckBox("Active")
        fl.addRow(field_label("Display Name"), self.name)
        fl.addRow(field_label("Username"), self.username)
        fl.addRow(field_label("Role"), self.role)
        fl.addRow(QLabel(""), self.active)
        split.addWidget(right, stretch=1)
        root.addLayout(split, stretch=1)
        self._refresh()
        if self.list.count():
            self.list.setCurrentRow(0)

    def _refresh(self):
        self.list.clear()
        for u in self.users:
            status = "" if u["active"] else " (inactive)"
            self.list.addItem(QListWidgetItem(f"{u['name']} · {u['role']}{status}"))

    def _load(self, row: int):
        if row < 0:
            return
        u = self.users[row]
        self.name.setText(u["name"])
        self.username.setText(u["username"])
        self.role.setCurrentText(u["role"])
        self.active.setChecked(u["active"])

    def _save(self):
        row = self.list.currentRow()
        if row < 0:
            return
        u = self.users[row]
        u.update({
            "name": self.name.text().strip() or u["name"],
            "username": self.username.text().strip() or u["username"],
            "role": self.role.currentText(),
            "active": self.active.isChecked(),
        })
        self._refresh()
        self.list.setCurrentRow(row)
        toast(self, "User permissions saved.")


class AccountYearManagementScreen(QWidget):
    """4.3 A/c Year Management — switch active year + create/rollover new year."""

    def __init__(self, on_fy_change=None, parent=None):
        super().__init__(parent)
        self.on_fy_change = on_fy_change
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        root.addWidget(page_title("4.3 A/c Year Management"))

        # —— Switch active year ——
        switch_box = card_frame()
        sl = QVBoxLayout(switch_box)
        sl.setContentsMargins(16, 16, 16, 16)
        sl.setSpacing(10)
        switch_hdr = QLabel("Change active A/c year")
        switch_hdr.setStyleSheet(
            f"font-weight: 600; font-size: {T.FONT_SIZE_UI}pt; color: {T.TEXT_PRIMARY};"
        )
        sl.addWidget(switch_hdr)
        sl.addWidget(field_label("Active Financial Year"))
        self.fy = QComboBox()
        self.fy.addItems(D.FISCAL_YEARS)
        self.fy.setCurrentText(D.FINANCIAL_YEAR)
        sl.addWidget(self.fy)
        apply = make_button("Switch Year", "primary")
        apply.clicked.connect(self._switch)
        sl.addWidget(apply, alignment=Qt.AlignLeft)
        root.addWidget(switch_box)

        notice = QFrame()
        notice.setStyleSheet(
            f"QFrame {{ background: {T.DANGER_BG}; border: 1px solid #fecaca; "
            f"border-left: 4px solid {T.DANGER}; border-radius: {T.CARD_RADIUS}px; }}"
        )
        nl = QVBoxLayout(notice)
        nl.setContentsMargins(14, 12, 14, 12)
        title = QLabel("Critical A/c Year Impact Notice")
        title.setStyleSheet(
            f"color: {T.DANGER}; font-weight: bold; font-size: {T.FONT_SIZE_UI}pt; "
            f"border: none; background: transparent;"
        )
        body = QLabel(
            "Changing the active financial year locks and isolates prior-year transactions. "
            "Reports and edits for the previous year remain available only in read-only "
            "archive mode. Closing balances carry forward only via Create / Rollover below."
        )
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; border: none; background: transparent; "
            f"font-size: {T.FONT_SIZE_LABEL}pt;"
        )
        nl.addWidget(title)
        nl.addWidget(body)
        root.addWidget(notice)

        # —— Create / rollover ——
        roll_notice = QFrame()
        roll_notice.setStyleSheet(
            f"QFrame {{ background: {T.WARNING_BG}; border: 1px solid #fde68a; "
            f"border-left: 4px solid {T.WARNING}; border-radius: {T.CARD_RADIUS}px; }}"
        )
        rnl = QVBoxLayout(roll_notice)
        rnl.setContentsMargins(14, 12, 14, 12)
        rt = QLabel("Create / Rollover new year")
        rt.setStyleSheet(
            f"color: {T.WARNING}; font-weight: bold; border: none; background: transparent;"
        )
        rb = QLabel(
            "Rollover will carry closing balances forward as opening balances for the new year. "
            "All prior-year vouchers become locked. This action cannot be undone from the UI."
        )
        rb.setWordWrap(True)
        rb.setStyleSheet("border: none; background: transparent;")
        rnl.addWidget(rt)
        rnl.addWidget(rb)
        root.addWidget(roll_notice)

        roll_box = card_frame()
        rl = QVBoxLayout(roll_box)
        rl.setContentsMargins(16, 16, 16, 16)
        rl.setSpacing(10)
        self.current_lbl = QLabel(f"Current year:  {D.FINANCIAL_YEAR}")
        rl.addWidget(self.current_lbl)
        self.next_fy = QComboBox()
        self.next_fy.addItems(["FY 2027–28", "FY 2028–29"])
        rl.addWidget(field_label("New Year"))
        rl.addWidget(self.next_fy)
        go = make_button("Run Rollover Wizard", "primary")
        go.clicked.connect(self._run_rollover)
        rl.addWidget(go, alignment=Qt.AlignLeft)
        root.addWidget(roll_box)
        root.addStretch()

    def _switch(self):
        year = self.fy.currentText()
        D.FINANCIAL_YEAR = year
        self.current_lbl.setText(f"Current year:  {year}")
        if callable(self.on_fy_change):
            self.on_fy_change(year)
        toast(self, f"Active year switched to {year}.")

    def _run_rollover(self):
        toast(self, f"Rollover to {self.next_fy.currentText()} queued (demo).")
