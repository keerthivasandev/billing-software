"""First-Time Administrator Setup — Stitch 49fc6a84ce2c407c80f9989b78865362."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import toast
from app.widgets.icons import icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.55)"
_CARD_R = 8  # Stitch rounded on this screen


class AdminSetupDialog(QDialog):
    """Blocking first-time root administrator creation gate (Step 2 of 2)."""

    CARD_W = 560

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Administrator Account Setup")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")
        self.result_admin = None
        self._pwd_visible = False
        self._confirm_visible = False
        self._build()

        QShortcut(QKeySequence("F9"), self, activated=self._save)
        QShortcut(QKeySequence("Return"), self, activated=self._save)
        QShortcut(QKeySequence("Enter"), self, activated=self._save)
        QShortcut(QKeySequence("Esc"), self, activated=self.reject)
        QShortcut(QKeySequence("Alt+F4"), self, activated=self.reject)

    def showEvent(self, event):
        parent = self.parentWidget()
        win = parent.window() if parent is not None else None
        if win is not None:
            top_left = win.mapToGlobal(win.rect().topLeft())
            self.setGeometry(top_left.x(), top_left.y(), win.width(), win.height())
        else:
            screen = self.screen()
            if screen:
                self.setGeometry(screen.availableGeometry())
        super().showEvent(event)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        backdrop = QFrame()
        backdrop.setObjectName("adminBackdrop")
        backdrop.setStyleSheet(
            f"QFrame#adminBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(backdrop)
        shell.setContentsMargins(24, 24, 24, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("adminCard")
        self._card.setFixedWidth(self.CARD_W)
        self._card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        self._card.setStyleSheet(
            f"QFrame#adminCard {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {_CARD_R}px; }}"
        )
        card = QVBoxLayout(self._card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)

        card.addWidget(self._title_bar())

        body = QVBoxLayout()
        body.setContentsMargins(16, 16, 16, 16)  # p-margin
        body.setSpacing(12)
        body.addWidget(self._header())
        body.addWidget(self._credentials_panel())
        body.addWidget(self._recovery_panel())
        body.addWidget(self._privileges_banner())
        body.addWidget(self._footer())
        card.addLayout(body)

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(backdrop)

    # ── Title bar ────────────────────────────────────────────
    def _title_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-top-left-radius: {_CARD_R}px; border-top-right-radius: {_CARD_R}px; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(8)

        left = QHBoxLayout()
        left.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap("admin_panel_settings", size=16, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        title = QLabel("Administrator Account Setup (First-Time Initialization)")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        left.addWidget(title)
        lay.addLayout(left, stretch=1)

        for icon, enabled in (
            ("minimize", False),
            ("crop_square", False),
            ("close", True),
        ):
            btn = QFrame()
            btn.setFixedSize(24, 24)
            if enabled:
                btn.setCursor(QCursor(Qt.PointingHandCursor))
                btn.setStyleSheet(
                    f"QFrame {{ background: transparent; border: none; border-radius: {S.R}px; }}"
                    f"QFrame:hover {{ background: {T.DANGER}; }}"
                )
            else:
                btn.setStyleSheet("QFrame { background: transparent; border: none; }")
            bl = QHBoxLayout(btn)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setAlignment(Qt.AlignCenter)
            bic = QLabel()
            bic.setFixedSize(14, 14)
            color = T.TEXT_SECONDARY if enabled else "#94a3b8"
            bic.setPixmap(icon_pixmap(icon, size=14, color=color))
            bic.setStyleSheet("background: transparent; border: none;")
            bl.addWidget(bic)
            if enabled:
                def _enter(e, i=bic, n=icon):
                    i.setPixmap(icon_pixmap(n, size=14, color="#ffffff"))

                def _leave(e, i=bic, n=icon):
                    i.setPixmap(icon_pixmap(n, size=14, color=T.TEXT_SECONDARY))

                btn.enterEvent = _enter
                btn.leaveEvent = _leave
                btn.mousePressEvent = (
                    lambda e: self.reject() if e.button() == Qt.LeftButton else None
                )
            lay.addWidget(btn)
        return bar

    # ── Header / identity ────────────────────────────────────
    def _header(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 8)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignHCenter)

        # Logo stack: shield_person + bolt badge
        logo_wrap = QWidget()
        logo_wrap.setFixedSize(56, 56)
        logo_wrap.setStyleSheet("background: transparent;")
        logo = QFrame(logo_wrap)
        logo.setGeometry(4, 0, 48, 48)
        logo.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: 12px; }}"
        )
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setAlignment(Qt.AlignCenter)
        shield = QLabel()
        shield.setFixedSize(28, 28)
        shield.setPixmap(icon_pixmap("shield_person", size=28, color=S.PRIMARY))
        shield.setStyleSheet("background: transparent; border: none;")
        ll.addWidget(shield)

        bolt_badge = QFrame(logo_wrap)
        bolt_badge.setGeometry(34, 34, 20, 20)
        bolt_badge.setStyleSheet(
            f"QFrame {{ background: {T.PRIMARY_CONTAINER}; border: none; "
            f"border-radius: 10px; }}"
        )
        bl = QHBoxLayout(bolt_badge)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setAlignment(Qt.AlignCenter)
        bolt = QLabel()
        bolt.setFixedSize(13, 13)
        bolt.setPixmap(icon_pixmap("bolt", size=13, color="#ffffff"))
        bolt.setStyleSheet("background: transparent; border: none;")
        bl.addWidget(bolt)
        lay.addWidget(logo_wrap, 0, Qt.AlignHCenter)

        # Root badge
        badge = QFrame()
        badge.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        bgl = QHBoxLayout(badge)
        bgl.setContentsMargins(10, 2, 10, 2)
        bgl.setSpacing(4)
        bic = QLabel()
        bic.setFixedSize(13, 13)
        bic.setPixmap(icon_pixmap("verified_user", size=13, color=S.PRIMARY))
        bic.setStyleSheet("background: transparent; border: none;")
        bgl.addWidget(bic)
        bt = QLabel("ROOT SUPERUSER SETUP — OFFLINE SAFE")
        bt.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        bgl.addWidget(bt)
        lay.addSpacing(6)
        lay.addWidget(badge, 0, Qt.AlignHCenter)

        company = QLabel("Sri Lakshmi Electricals")
        company.setAlignment(Qt.AlignCenter)
        company.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(company)

        edition = QLabel("Wholesale Billing & ERP System v4.8.2")
        edition.setAlignment(Qt.AlignCenter)
        edition.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(edition)

        step = QFrame()
        step.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_HIGH}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        sl = QHBoxLayout(step)
        sl.setContentsMargins(8, 2, 8, 2)
        sl.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(f"background: {S.PRIMARY}; border: none; border-radius: 3px;")
        sl.addWidget(dot)
        st = QLabel("Step 2 of 2 — First-Time Installation")
        st.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        sl.addWidget(st)
        lay.addSpacing(8)
        lay.addWidget(step, 0, Qt.AlignHCenter)

        desc = QLabel(
            "License activated successfully. Configure the primary administrative "
            "root account to supervise store ledgers, fiscal closing, and operator roles."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setMaximumWidth(440)
        desc.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent; margin-top: 6px;"
        )
        lay.addWidget(desc, 0, Qt.AlignHCenter)
        return wrap

    # ── Mandatory credentials ────────────────────────────────
    def _credentials_panel(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        head = QHBoxLayout()
        left = QHBoxLayout()
        left.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap("lock", size=14, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        ttl = QLabel("MANDATORY SUPERUSER CREDENTIALS")
        ttl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        left.addWidget(ttl)
        head.addLayout(left)
        head.addStretch()
        req = QLabel("* Required inputs")
        req.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        head.addWidget(req)
        lay.addLayout(head)

        # Full name
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("e.g. K. Lakshmi Narayan (Managing Partner)")
        lay.addWidget(self._labeled_field(
            "Full Name", "Owner / Partner Name", "badge", self.full_name, required=True,
        ))

        # Username
        self.username = QLineEdit("admin")
        self.username.setPlaceholderText("e.g. admin or lakshmi_root")
        user_field = self._icon_field(
            "alternate_email", self.username, mono=True, trailing="AUTH_ROOT",
        )
        user_wrap = self._labeled_field(
            "Username (Master Login ID)", "Case-insensitive", None, None,
            required=True, field_widget=user_field,
            hint="Permanent root handle used during system startup and emergency audits.",
        )
        lay.addWidget(user_wrap)

        # Password row
        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(10)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("••••••••••••")
        self.password.textChanged.connect(self._check_password)
        pwd_field = self._icon_field(
            "key", self.password, mono=True, eye=True, eye_attr="_pwd_visible",
        )
        pwd_col = self._labeled_field(
            "Master Password", "", None, None, required=True, field_widget=pwd_field,
        )
        self.pwd_hint = self._hint_row("info", "Min. 8 characters", S.PRIMARY)
        pwd_col.layout().addWidget(self.pwd_hint)
        pwd_row.addWidget(pwd_col)

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        self.confirm.setPlaceholderText("••••••••••••")
        self.confirm.textChanged.connect(self._check_password)
        conf_field = self._icon_field(
            "lock_reset", self.confirm, mono=True, eye=True, eye_attr="_confirm_visible",
        )
        conf_col = self._labeled_field(
            "Confirm Password", "", None, None, required=True, field_widget=conf_field,
        )
        self.match_hint = self._hint_row("pending", "Repeat password", T.TEXT_SECONDARY)
        conf_col.layout().addWidget(self.match_hint)
        pwd_row.addWidget(conf_col)
        lay.addLayout(pwd_row)
        return box

    # ── Optional recovery ────────────────────────────────────
    def _recovery_panel(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        head = QHBoxLayout()
        left = QHBoxLayout()
        left.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap("contact_phone", size=14, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        ttl = QLabel("OPTIONAL RECOVERY & EMERGENCY ALERTS")
        ttl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.5px; border: none; background: transparent;"
        )
        left.addWidget(ttl)
        head.addLayout(left)
        head.addStretch()
        rec = QLabel("Recommended")
        rec.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        head.addWidget(rec)
        lay.addLayout(head)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("+91 98480 23411")
        mob_field = self._icon_field("call", self.mobile, mono=True)
        mob_col = self._labeled_field(
            "Mobile Number", "", None, None, field_widget=mob_field,
            hint="For critical ledger OTP recovery", hint_size=10,
        )
        row.addWidget(mob_col)

        self.email = QLineEdit()
        self.email.setPlaceholderText("owner@srilakshmielectricals.com")
        em_field = self._icon_field("alternate_email", self.email, mono=True)
        em_col = self._labeled_field(
            "Email Address", "", None, None, field_widget=em_field,
            hint="Automated daily DB backup digests", hint_size=10,
        )
        row.addWidget(em_col)
        lay.addLayout(row)
        return box

    # ── Privileges banner ────────────────────────────────────
    def _privileges_banner(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)
        ic = QLabel()
        ic.setFixedSize(20, 20)
        ic.setPixmap(icon_pixmap("policy", size=20, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, 0, Qt.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(2)
        ttl = QLabel("Unrestricted Super Administrator Privileges")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        col.addWidget(ttl)
        body = QLabel(
            "This account is granted full authority over fiscal books, GSTIN master "
            "settings, invoice revisions, and subordinate staff terminals. Keep these "
            "credentials confidential."
        )
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        col.addWidget(body)
        lay.addLayout(col, stretch=1)
        return box

    # ── Footer ───────────────────────────────────────────────
    def _footer(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(8)

        cancel = QFrame()
        cancel.setCursor(QCursor(Qt.PointingHandCursor))
        cancel.setFixedHeight(32)
        cancel.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        cl = QHBoxLayout(cancel)
        cl.setContentsMargins(8, 0, 8, 0)
        cl.setSpacing(4)
        ct = QLabel("Cancel")
        ct.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        cl.addWidget(ct)
        ck = QLabel("[Esc]")
        ck.setStyleSheet(
            f"color: {T.TEXT_MUTED}; font-size: 10px; "
            f"border: none; background: transparent;"
        )
        cl.addWidget(ck)
        cancel.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(cancel)
        lay.addStretch()

        save = QFrame()
        save.setCursor(QCursor(Qt.PointingHandCursor))
        save.setFixedHeight(32)
        save.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        sl = QHBoxLayout(save)
        sl.setContentsMargins(16, 0, 12, 0)
        sl.setSpacing(8)
        sic = QLabel()
        sic.setFixedSize(18, 18)
        sic.setPixmap(icon_pixmap("how_to_reg", size=18, color="#ffffff"))
        sic.setStyleSheet("background: transparent; border: none;")
        sl.addWidget(sic)
        st = QLabel("Save & Continue to Login")
        st.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 600; "
            "border: none; background: transparent;"
        )
        sl.addWidget(st)
        sl.addWidget(S.kbd("F9 / ↵", on_primary=True))
        save.mousePressEvent = (
            lambda e: self._save() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(save)
        return wrap

    # ── Field helpers ────────────────────────────────────────
    def _labeled_field(
        self, label: str, trailing: str, icon: str | None, edit: QLineEdit | None,
        *, required: bool = False, field_widget: QWidget = None, hint: str = "",
        hint_size: int = 11,
    ) -> QWidget:
        box = QWidget()
        box.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(4)
        cap = QLabel(label + (" *" if required else ""))
        # color the asterisk via rich text if required
        if required:
            cap.setText(f'{label} <span style="color:{T.DANGER}">*</span>')
            cap.setTextFormat(Qt.RichText)
        cap.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        row.addWidget(cap)
        row.addStretch()
        if trailing:
            tr = QLabel(trailing)
            tr.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 400; "
                f"border: none; background: transparent;"
            )
            row.addWidget(tr)
        lay.addLayout(row)

        if field_widget is not None:
            lay.addWidget(field_widget)
        elif edit is not None and icon:
            lay.addWidget(self._icon_field(icon, edit))

        if hint:
            h = QLabel(hint)
            h.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: {hint_size}px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(h)
        return box

    def _icon_field(
        self, icon: str, widget: QLineEdit, *, mono: bool = False,
        trailing: str = "", eye: bool = False, eye_attr: str = "",
    ) -> QFrame:
        wrap = QFrame()
        wrap.setFixedHeight(T.INPUT_H)
        wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(10, 0, 6, 0)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignVCenter)

        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap(icon, size=18, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        family = "Consolas, monospace" if mono else "inherit"
        widget.setFrame(False)
        widget.setFixedHeight(T.INPUT_H - 4)
        widget.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; padding: 0px;
                color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 500;
                font-family: {family};
            }}
            """
        )
        lay.addWidget(widget, stretch=1)

        if trailing:
            chip = QLabel(trailing)
            chip.setStyleSheet(
                f"color: {T.TEXT_PRIMARY}; background: {T.SURFACE_CONTAINER}; "
                f"border: none; border-radius: {S.R}px; padding: 2px 6px; "
                f"font-size: 10px; font-weight: 600;"
            )
            lay.addWidget(chip)

        if eye:
            eye_btn = QLabel()
            eye_btn.setFixedSize(16, 16)
            eye_btn.setCursor(QCursor(Qt.PointingHandCursor))
            eye_btn.setPixmap(icon_pixmap("visibility", size=16, color=T.TEXT_SECONDARY))
            eye_btn.setStyleSheet("background: transparent; border: none;")

            def _toggle(e, w=widget, btn=eye_btn, attr=eye_attr):
                if e.button() != Qt.LeftButton:
                    return
                visible = getattr(self, attr, False)
                visible = not visible
                setattr(self, attr, visible)
                w.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
                btn.setPixmap(icon_pixmap(
                    "visibility_off" if visible else "visibility",
                    size=16, color=T.TEXT_SECONDARY,
                ))

            eye_btn.mousePressEvent = _toggle
            lay.addWidget(eye_btn)

        return wrap

    def _hint_row(self, icon: str, text: str, color: str) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(12, 12)
        ic.setObjectName("hintIcon")
        ic.setPixmap(icon_pixmap(icon, size=12, color=color))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        lbl = QLabel(text)
        lbl.setObjectName("hintText")
        lbl.setStyleSheet(
            f"color: {color}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        lay.addStretch()
        wrap._ic = ic
        wrap._lbl = lbl
        return wrap

    def _set_hint(self, row: QWidget, icon: str, text: str, color: str, bold: bool = False):
        row._ic.setPixmap(icon_pixmap(icon, size=12, color=color))
        weight = "600" if bold else "400"
        row._lbl.setText(text)
        row._lbl.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: {weight}; "
            f"border: none; background: transparent;"
        )

    def _check_password(self):
        p1 = self.password.text()
        p2 = self.confirm.text()
        if len(p1) >= 8:
            self._set_hint(self.pwd_hint, "check_circle", "Min. 8 characters", S.PRIMARY)
        else:
            self._set_hint(self.pwd_hint, "info", "Min. 8 characters", S.PRIMARY)

        if not p2:
            self._set_hint(self.match_hint, "pending", "Repeat password", T.TEXT_SECONDARY)
        elif p1 == p2 and len(p1) >= 8:
            self._set_hint(self.match_hint, "check_circle", "Passwords match", S.PRIMARY, True)
        elif p1 != p2:
            self._set_hint(self.match_hint, "cancel", "Passwords do not match", T.DANGER)
        else:
            self._set_hint(self.match_hint, "warning", "Minimum 8 characters", T.DANGER)

    # ── Actions ──────────────────────────────────────────────
    def _save(self):
        name = self.full_name.text().strip()
        user = self.username.text().strip()
        p1 = self.password.text()
        p2 = self.confirm.text()

        if not name:
            toast(self, "Enter the administrator full name.")
            self.full_name.setFocus()
            return
        if not user:
            toast(self, "Enter a master login username.")
            self.username.setFocus()
            return
        if len(p1) < 8:
            toast(self, "Master password must contain at least 8 characters.")
            self.password.setFocus()
            return
        if p1 != p2:
            toast(self, "Passwords do not match. Please verify and re-enter.")
            self.confirm.setFocus()
            return

        from app.services import users as users_svc

        try:
            self.result_admin = users_svc.create_admin(
                full_name=name,
                username=user.lower(),
                password=p1,
                mobile=self.mobile.text().strip() or "",
                email=self.email.text().strip() or "",
            )
        except Exception as exc:
            toast(self, f"Could not create admin: {exc}")
            return
        D.reload()
        toast(self, "Root administrator created successfully.")
        self.accept()
