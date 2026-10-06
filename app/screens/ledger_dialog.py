"""Stitch — New / Edit Ledger modal dialog [F3]."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.icons import icon_pixmap
from app.widgets import stitch_ui as S

# Dim scrim over the app while the ledger modal is open (Stitch overlay).
_BACKDROP = "rgba(15, 23, 42, 0.55)"


class LedgerEditDialog(QDialog):
    """Centered modal matching Stitch 'Edit Ledger / New Ledger' screen."""

    def __init__(self, parent=None, party: dict = None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.party = dict(party) if party else {}
        self.is_new = party is None
        self.result_data = None

        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        # Full-window backdrop shell
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._backdrop = QFrame()
        self._backdrop.setObjectName("ledgerBackdrop")
        self._backdrop.setStyleSheet(
            f"QFrame#ledgerBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        self._backdrop.setCursor(QCursor(Qt.ArrowCursor))
        shell = QVBoxLayout(self._backdrop)
        shell.setContentsMargins(24, 24, 24, 24)
        shell.setAlignment(Qt.AlignCenter)

        # White modal card (centered over backdrop)
        self._card = QFrame()
        self._card.setObjectName("ledgerModalCard")
        self._card.setFixedWidth(720)
        self._card.setMaximumHeight(720)
        self._card.setStyleSheet(
            f"QFrame#ledgerModalCard {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 8px; }}"
        )
        card_lay = QVBoxLayout(self._card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        card_lay.addWidget(self._header())

        body_scroll = QScrollArea()
        body_scroll.setWidgetResizable(True)
        body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body_scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        body_host = QWidget()
        body_host.setStyleSheet(f"background: {T.SURFACE}; border: none;")
        body = QVBoxLayout(body_host)
        body.setContentsMargins(16, 14, 16, 14)
        body.setSpacing(12)
        body.addWidget(self._section_basic())
        body.addWidget(self._section_gst())
        body.addWidget(self._section_finance())
        body_scroll.setWidget(body_host)
        card_lay.addWidget(body_scroll, stretch=1)
        card_lay.addWidget(self._footer())

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(self._backdrop)

        # Click dimmed area (not the card) closes the dialog
        self._backdrop.mousePressEvent = self._on_backdrop_press

        self._load()
        QShortcut(QKeySequence("Esc"), self, activated=self.reject)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)

    def showEvent(self, event):
        """Cover the parent window so the backdrop dims the whole app chrome."""
        parent = self.parentWidget()
        win = parent.window() if parent is not None else None
        if win is not None:
            top_left = win.mapToGlobal(win.rect().topLeft())
            self.setGeometry(top_left.x(), top_left.y(), win.width(), win.height())
        else:
            screen = self.screen()
            if screen is not None:
                self.setGeometry(screen.availableGeometry())
        super().showEvent(event)

    def _on_backdrop_press(self, event):
        if event.button() != Qt.LeftButton:
            return
        # Only dismiss when the press is outside the modal card
        if not self._card.geometry().contains(event.position().toPoint()):
            self.reject()

    def _header(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; "
            f"border-top-left-radius: 8px; border-top-right-radius: 8px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 12, 12, 12)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(36, 36)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            f"background: {T.ACCENT_SOFT}; border-radius: 4px; border: none;"
        )
        ic.setPixmap(icon_pixmap("person_add", size=20, color=S.PRIMARY))

        title_name = self.party.get("name", "New Party") if not self.is_new else "New Ledger"
        if self.is_new:
            title_txt = "New Ledger — Create Account [F3]"
        else:
            title_txt = f"Edit Ledger — {title_name} [F3]"
        col = QVBoxLayout()
        col.setSpacing(2)
        ttl = QLabel(title_txt)
        ttl.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        sub = QLabel("Create customer or supplier account with GST and opening balance")
        sub.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        col.addWidget(ttl)
        col.addWidget(sub)

        close = QLabel()
        close.setFixedSize(28, 28)
        close.setAlignment(Qt.AlignCenter)
        close.setCursor(QCursor(Qt.PointingHandCursor))
        close.setPixmap(icon_pixmap("close", size=18, color=S.SECONDARY))
        close.setStyleSheet(
            f"background: {S.HEADER_GREY}; border-radius: 4px; border: none;"
        )
        close.mousePressEvent = lambda e: self.reject()

        lay.addWidget(ic)
        lay.addLayout(col, stretch=1)
        lay.addWidget(close, 0, Qt.AlignTop)
        return box

    def _section_shell(self, title: str, icon: str) -> tuple[QFrame, QVBoxLayout]:
        box = S.card()
        outer = QVBoxLayout(box)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(S.section_head(title, icon))
        body_w = QWidget()
        body_w.setStyleSheet("background: transparent;")
        body = QVBoxLayout(body_w)
        body.setContentsMargins(12, 12, 12, 12)
        body.setSpacing(10)
        outer.addWidget(body_w)
        return box, body

    def _row(self, *widgets) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        for w in widgets:
            lay.addWidget(w, stretch=1)
        return wrap

    def _section_basic(self) -> QFrame:
        box, body = self._section_shell("1. Basic Account Information", "badge")
        self.name = QLineEdit()
        self.group = QComboBox()
        self.group.addItems([
            "Sundry Debtors (Customers / Wholesale)",
            "Sundry Creditors (Suppliers)",
            "Cash-in-Hand",
            "Bank Accounts",
        ])
        self.contact = QLineEdit()
        self.mobile = QLineEdit()

        group_wrap = QWidget()
        group_wrap.setStyleSheet("background: transparent;")
        gl = QVBoxLayout(group_wrap)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(4)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        cap = QLabel("UNDER GROUP / ACCOUNT TYPE")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        star = QLabel("*")
        star.setStyleSheet(
            f"color: {S.ERROR}; font-weight: 700; border: none; background: transparent;"
        )
        new_grp = QLabel("+ New Group [F2]")
        new_grp.setCursor(QCursor(Qt.PointingHandCursor))
        new_grp.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 10px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        top.addWidget(cap)
        top.addWidget(star)
        top.addStretch()
        top.addWidget(new_grp)
        gl.addLayout(top)
        from app.widgets.icons import combo_dropdown_qss

        self.group.setStyleSheet(
            f"""
            QComboBox {{
                background: {S.INPUT_BG}; border: none; border-radius: 4px;
                padding: 8px 28px 8px 10px; min-height: 20px;
                font-size: 13px; font-weight: 600;
            }}
            {combo_dropdown_qss(width=24, background="transparent")}
            """
        )
        gl.addWidget(self.group)

        body.addWidget(
            self._row(
                S.labeled_input("ACCOUNT / BUSINESS NAME", self.name, required=True),
                group_wrap,
            )
        )
        body.addWidget(
            self._row(
                S.labeled_input("CONTACT PERSON / PROPRIETOR", self.contact),
                S.labeled_input("MOBILE / WHATSAPP NUMBER", self.mobile, required=True),
            )
        )
        return box

    def _section_gst(self) -> QFrame:
        box, body = self._section_shell("2. GST & Registered Address", "location_on")
        self.gstin = QLineEdit()
        self.state = QComboBox()
        self.state.addItems([
            "33 — Tamil Nadu", "36 — Telangana", "29 — Karnataka",
            "27 — Maharashtra", "09 — Uttar Pradesh",
        ])
        self.address = QLineEdit()
        body.addWidget(
            self._row(
                S.labeled_input("GSTIN (15-DIGIT)", self.gstin),
                S.labeled_input("STATE & POS CODE", self.state),
            )
        )
        body.addWidget(
            S.labeled_input("BILLING ADDRESS / PREMISES & CITY", self.address)
        )
        return box

    def _section_finance(self) -> QFrame:
        box, body = self._section_shell(
            "3. Financial Balances & Credit Terms", "account_balance"
        )
        self.opening = QDoubleSpinBox()
        self.opening.setRange(0, 99_999_999)
        self.opening.setDecimals(2)
        self.opening.setGroupSeparatorShown(True)
        self.credit_limit = QDoubleSpinBox()
        self.credit_limit.setRange(0, 99_999_999)
        self.credit_limit.setDecimals(2)
        self.credit_limit.setGroupSeparatorShown(True)
        self.credit_days = QSpinBox()
        self.credit_days.setRange(0, 365)

        # Opening + Dr/Cr toggle
        open_wrap = QWidget()
        open_wrap.setStyleSheet("background: transparent;")
        ol = QVBoxLayout(open_wrap)
        ol.setContentsMargins(0, 0, 0, 0)
        ol.setSpacing(4)
        cap = QLabel("OPENING BALANCE (₹)")
        cap.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        ol.addWidget(cap)
        row = QHBoxLayout()
        row.setSpacing(6)
        self.opening.setStyleSheet(
            f"QDoubleSpinBox {{ background: {S.INPUT_BG}; border: none; border-radius: 4px; "
            f"padding: 8px 10px; min-height: 20px; font-size: 13px; font-weight: 600; }}"
        )
        row.addWidget(self.opening, stretch=1)
        self._dr_cr = "Dr"
        self.btn_dr = self._toggle_chip("Dr", True)
        self.btn_cr = self._toggle_chip("Cr", False)
        self.btn_dr.mousePressEvent = lambda e: self._set_dr_cr("Dr")
        self.btn_cr.mousePressEvent = lambda e: self._set_dr_cr("Cr")
        row.addWidget(self.btn_dr)
        row.addWidget(self.btn_cr)
        ol.addLayout(row)

        body.addWidget(
            self._row(
                open_wrap,
                S.labeled_input("CREDIT LIMIT (₹)", self.credit_limit),
                S.labeled_input("CREDIT PERIOD [DAYS]", self.credit_days),
            )
        )
        return box

    def _toggle_chip(self, text: str, active: bool) -> QFrame:
        chip = QFrame()
        chip.setFixedSize(36, 34)
        chip.setCursor(QCursor(Qt.PointingHandCursor))
        self._style_toggle(chip, text, active)
        return chip

    def _style_toggle(self, chip: QFrame, text: str, active: bool):
        if active and text == "Dr":
            chip.setStyleSheet(
                f"QFrame {{ background: {T.DANGER_BG}; border: 1px solid #fecaca; "
                f"border-radius: 4px; }}"
            )
            color = S.ERROR
        elif active:
            chip.setStyleSheet(
                f"QFrame {{ background: {T.ACCENT_SOFT}; border: 1px solid #bfdbfe; "
                f"border-radius: 4px; }}"
            )
            color = S.PRIMARY
        else:
            chip.setStyleSheet(
                f"QFrame {{ background: {S.HEADER_GREY}; border: 1px solid {T.BORDER}; "
                f"border-radius: 4px; }}"
            )
            color = S.SECONDARY
        # rebuild label
        if chip.layout() is None:
            lay = QHBoxLayout(chip)
            lay.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setObjectName("toggleLbl")
            lay.addWidget(lbl)
        lbl = chip.findChild(QLabel, "toggleLbl")
        if lbl:
            lbl.setText(text)
            lbl.setStyleSheet(
                f"color: {color}; font-size: 12px; font-weight: 700; "
                f"border: none; background: transparent;"
            )

    def _set_dr_cr(self, side: str):
        self._dr_cr = side
        self._style_toggle(self.btn_dr, "Dr", side == "Dr")
        self._style_toggle(self.btn_cr, "Cr", side == "Cr")

    def _footer(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {S.HEADER_GREY}; border: none; "
            f"border-top: 1px solid {T.BORDER}; border-bottom-left-radius: 8px; "
            f"border-bottom-right-radius: 8px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)
        tip = QLabel("Esc Cancel / Close    ·    Ctrl+S Save Ledger")
        tip.setStyleSheet(
            f"color: {S.SECONDARY}; font-size: 10px; border: none; background: transparent;"
        )
        lay.addWidget(tip)
        lay.addStretch()
        cancel = S.action_btn("Cancel", "Esc", kind="secondary", on_click=self.reject)
        save = S.action_btn(
            "Save Ledger", "Ctrl+S", icon="check_circle", kind="primary", on_click=self._save
        )
        lay.addWidget(cancel)
        lay.addWidget(save)
        return box

    def _load(self):
        p = self.party
        self.name.setText(p.get("name", ""))
        self.contact.setText(p.get("contact_person", ""))
        self.mobile.setText(p.get("phone", ""))
        self.gstin.setText(p.get("gstin", ""))
        self.address.setText(
            f"{p.get('address', '')}, {p.get('city', '')}".strip(", ")
        )
        self.opening.setValue(float(p.get("opening_balance", p.get("balance", 0)) or 0))
        self.credit_limit.setValue(float(p.get("credit_limit", 0) or 0))
        self.credit_days.setValue(int(p.get("credit_days", 30) or 30))
        bt = p.get("balance_type", "Dr")
        self._set_dr_cr(bt if bt in ("Dr", "Cr") else "Dr")
        g = p.get("group", "Sundry Debtors")
        if "Creditor" in g or p.get("type") == "Supplier":
            self.group.setCurrentIndex(1)
        else:
            self.group.setCurrentIndex(0)
        state = p.get("state_code", "33 — Tamil Nadu")
        idx = self.state.findText(state)
        if idx >= 0:
            self.state.setCurrentIndex(idx)

    def _save(self):
        name = self.name.text().strip()
        if not name:
            self.name.setFocus()
            return
        addr = self.address.text().strip()
        city = ""
        if "," in addr:
            parts = [x.strip() for x in addr.rsplit(",", 1)]
            address, city = parts[0], parts[1]
        else:
            address = addr
        gtxt = self.group.currentText()
        ptype = "Supplier" if "Creditor" in gtxt else "Customer"
        group = "Sundry Creditors" if ptype == "Supplier" else "Sundry Debtors"
        self.result_data = {
            **self.party,
            "name": name,
            "short_name": name[:28],
            "type": ptype,
            "group": group,
            "contact_person": self.contact.text().strip(),
            "phone": self.mobile.text().strip(),
            "gstin": self.gstin.text().strip(),
            "state_code": self.state.currentText(),
            "address": address,
            "city": city or self.party.get("city", ""),
            "opening_balance": self.opening.value(),
            "balance": self.opening.value(),
            "balance_type": self._dr_cr,
            "credit_limit": self.credit_limit.value(),
            "credit_days": self.credit_days.value(),
            "active": True,
            "whatsapp": True,
        }
        self.accept()
