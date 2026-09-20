"""Settings — Audit Trail, Users, Fiscal Year & Rollover."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QFormLayout, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
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
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(T.GRID_ROW_H)
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


class FiscalYearScreen(QWidget):
    def __init__(self, on_fy_change=None, parent=None):
        super().__init__(parent)
        self.on_fy_change = on_fy_change
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        root.addWidget(page_title("4.3 Change Fiscal Year"))

        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)
        lay.addWidget(field_label("Active Financial Year"))
        self.fy = QComboBox()
        self.fy.addItems(D.FISCAL_YEARS)
        self.fy.setCurrentText(D.FINANCIAL_YEAR)
        lay.addWidget(self.fy)
        apply = make_button("Switch Year", "primary")
        apply.clicked.connect(self._switch)
        lay.addWidget(apply, alignment=Qt.AlignLeft)
        root.addWidget(box)

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
            "archive mode. Closing balances carry forward only via the Rollover wizard."
        )
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; border: none; background: transparent; "
            f"font-size: {T.FONT_SIZE_LABEL}pt;"
        )
        nl.addWidget(title)
        nl.addWidget(body)
        root.addWidget(notice)
        root.addStretch()

    def _switch(self):
        year = self.fy.currentText()
        D.FINANCIAL_YEAR = year
        if callable(self.on_fy_change):
            self.on_fy_change(year)
        toast(self, f"Active year switched to {year}.")


class RolloverScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        root.addWidget(page_title("4.4 Create / Rollover New Year"))

        notice = QFrame()
        notice.setStyleSheet(
            f"QFrame {{ background: {T.WARNING_BG}; border: 1px solid #fde68a; "
            f"border-left: 4px solid {T.WARNING}; border-radius: {T.CARD_RADIUS}px; }}"
        )
        nl = QVBoxLayout(notice)
        nl.setContentsMargins(14, 12, 14, 12)
        t = QLabel("Critical A/c Year Impact Notice")
        t.setStyleSheet(
            f"color: {T.WARNING}; font-weight: bold; border: none; background: transparent;"
        )
        b = QLabel(
            "Rollover will carry closing balances forward as opening balances for the new year. "
            "All prior-year vouchers become locked. This action cannot be undone from the UI."
        )
        b.setWordWrap(True)
        b.setStyleSheet("border: none; background: transparent;")
        nl.addWidget(t)
        nl.addWidget(b)
        root.addWidget(notice)

        box = card_frame()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)
        lay.addWidget(QLabel(f"Current year:  {D.FINANCIAL_YEAR}"))
        self.next_fy = QComboBox()
        # suggest next
        self.next_fy.addItems(["FY 2027–28", "FY 2028–29"])
        lay.addWidget(field_label("New Year"))
        lay.addWidget(self.next_fy)
        go = make_button("Run Rollover Wizard", "primary")
        go.clicked.connect(self._run)
        lay.addWidget(go, alignment=Qt.AlignLeft)
        root.addWidget(box)
        root.addStretch()

    def _run(self):
        toast(self, f"Rollover to {self.next_fy.currentText()} queued (demo).")
