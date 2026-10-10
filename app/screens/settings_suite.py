"""Settings — A/c Year Management (Users lives in users.py; A/c Log in ac_log_customer)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFrame, QLabel, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.screens.ac_log_customer import AuditTrailScreen  # noqa: F401 — re-export
from app.screens.users import UsersScreen  # noqa: F401 — re-export
from app.styles import tokens as T
from app.widgets.helpers import (
    card_frame, field_label, make_button, page_title, toast,
)


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
