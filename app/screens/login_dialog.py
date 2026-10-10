"""User Sign In Dialog (Blocking Modal) — Stitch 47e058a45a3e433d83d731ee5371c99c."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import toast
from app.widgets.icons import icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.55)"
_CARD_R = 12  # Stitch rounded-xl
_ERROR_BG = "#fce8e6"  # error-container soft
_ERROR_FG = "#8c1d18"


class LoginDialog(QDialog):
    """Blocking operator sign-in gate before MainWindow."""

    CARD_W = 460

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("User Sign In")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")
        self.result_user = None
        self._pwd_visible = False
        self._build()

        QShortcut(QKeySequence("F9"), self, activated=self._sign_in)
        QShortcut(QKeySequence("Return"), self, activated=self._sign_in)
        QShortcut(QKeySequence("Enter"), self, activated=self._sign_in)
        QShortcut(QKeySequence("Esc"), self, activated=self.reject)
        QShortcut(QKeySequence("F1"), self, activated=lambda: toast(self, "Contact Shift Supervisor / Support."))
        QShortcut(QKeySequence("F3"), self, activated=lambda: toast(self, "Terminal select — coming next."))

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
        self.username.setFocus()
        self.username.selectAll()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        backdrop = QFrame()
        backdrop.setObjectName("loginBackdrop")
        backdrop.setStyleSheet(
            f"QFrame#loginBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(backdrop)
        shell.setContentsMargins(24, 24, 24, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("loginCard")
        self._card.setFixedWidth(self.CARD_W)
        self._card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        self._card.setStyleSheet(
            f"QFrame#loginCard {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {_CARD_R}px; }}"
        )
        card = QVBoxLayout(self._card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)

        card.addWidget(self._title_bar())

        body = QVBoxLayout()
        body.setContentsMargins(20, 20, 20, 16)  # p-space-lg-ish
        body.setSpacing(14)
        body.addWidget(self._brand_header())
        body.addWidget(self._error_banner())
        body.addWidget(self._form())
        card.addLayout(body)

        card.addWidget(self._status_bar())
        card.addWidget(self._hotkey_bar())

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(backdrop)

    # ── Title bar ────────────────────────────────────────────
    def _title_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_HIGH}; border: none; "
            f"border-top-left-radius: {_CARD_R}px; border-top-right-radius: {_CARD_R}px; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(6)

        left = QHBoxLayout()
        left.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(17, 17)
        ic.setPixmap(icon_pixmap("bolt", size=17, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        title = QLabel("Sri Lakshmi Electricals — User Sign In")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        left.addWidget(title)
        lay.addLayout(left, stretch=1)

        for icon, enabled in (
            ("remove", False),
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
                btn.setStyleSheet(
                    "QFrame { background: transparent; border: none; opacity: 0.4; }"
                )
            bl = QHBoxLayout(btn)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setAlignment(Qt.AlignCenter)
            bic = QLabel()
            bic.setFixedSize(15, 15)
            color = T.TEXT_SECONDARY if enabled else "#94a3b8"
            bic.setPixmap(icon_pixmap(icon, size=15, color=color))
            bic.setStyleSheet("background: transparent; border: none;")
            bl.addWidget(bic)
            if enabled:
                def _enter(e, i=bic, n=icon):
                    i.setPixmap(icon_pixmap(n, size=15, color="#ffffff"))

                def _leave(e, i=bic, n=icon):
                    i.setPixmap(icon_pixmap(n, size=15, color=T.TEXT_SECONDARY))

                btn.enterEvent = _enter
                btn.leaveEvent = _leave
                btn.mousePressEvent = (
                    lambda e: self.reject() if e.button() == Qt.LeftButton else None
                )
            lay.addWidget(btn)
        return bar

    # ── Brand ────────────────────────────────────────────────
    def _brand_header(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignHCenter)

        logo_host = QWidget()
        logo_host.setFixedSize(52, 52)
        logo_host.setStyleSheet("background: transparent;")
        logo = QFrame(logo_host)
        logo.setGeometry(2, 4, 48, 48)
        logo.setStyleSheet(
            f"QFrame {{ background: {T.PRIMARY_FIXED}; border: none; "
            f"border-radius: 12px; }}"
        )
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setAlignment(Qt.AlignCenter)
        bolt = QLabel()
        bolt.setFixedSize(28, 28)
        bolt.setPixmap(icon_pixmap("electric_bolt", size=28, color=S.PRIMARY))
        bolt.setStyleSheet("background: transparent; border: none;")
        ll.addWidget(bolt)
        dot = QLabel(logo_host)
        dot.setGeometry(38, 0, 12, 12)
        dot.setStyleSheet(
            f"background: {S.PRIMARY}; border: none; border-radius: 6px;"
        )
        lay.addWidget(logo_host, 0, Qt.AlignHCenter)

        company = QLabel("Sri Lakshmi Electricals")
        company.setAlignment(Qt.AlignCenter)
        company.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(company)

        sub_row = QHBoxLayout()
        sub_row.setSpacing(6)
        sub_row.setAlignment(Qt.AlignCenter)
        sub = QLabel("Wholesale Billing & ERP System")
        sub.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        sub_row.addWidget(sub)
        ver = QLabel("v4.8.2")
        ver.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; background: {T.SURFACE_CONTAINER_HIGH}; "
            f"border: none; border-radius: {S.R}px; padding: 1px 5px; "
            f"font-size: 11px; font-family: Consolas, monospace;"
        )
        sub_row.addWidget(ver)
        lay.addLayout(sub_row)

        badge = QFrame()
        badge.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        bl = QHBoxLayout(badge)
        bl.setContentsMargins(10, 4, 10, 4)
        bl.setSpacing(6)
        bdot = QLabel()
        bdot.setFixedSize(6, 6)
        bdot.setStyleSheet(f"background: {S.PRIMARY}; border: none; border-radius: 3px;")
        bl.addWidget(bdot)
        bt = QLabel("OFFLINE SECURE · LOCAL TERMINAL")
        bt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.6px; border: none; background: transparent;"
        )
        bl.addWidget(bt)
        lay.addSpacing(10)
        lay.addWidget(badge, 0, Qt.AlignHCenter)
        return wrap

    # ── Error banner ─────────────────────────────────────────
    def _error_banner(self) -> QFrame:
        self.error_banner = QFrame()
        self.error_banner.setVisible(False)
        self.error_banner.setStyleSheet(
            f"QFrame {{ background: {_ERROR_BG}; border: none; border-radius: {S.CR}px; }}"
        )
        lay = QHBoxLayout(self.error_banner)
        lay.setContentsMargins(10, 8, 8, 8)
        lay.setSpacing(8)

        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap("error", size=18, color=T.DANGER))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, 0, Qt.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(2)
        t1 = QLabel("Invalid credentials or account is inactive.")
        t1.setStyleSheet(
            f"color: {_ERROR_FG}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        col.addWidget(t1)
        t2 = QLabel("Please check credentials or verify with Shift Supervisor.")
        t2.setStyleSheet(
            f"color: {_ERROR_FG}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        col.addWidget(t2)
        lay.addLayout(col, stretch=1)

        close = QLabel()
        close.setFixedSize(15, 15)
        close.setCursor(QCursor(Qt.PointingHandCursor))
        close.setPixmap(icon_pixmap("close", size=15, color=_ERROR_FG))
        close.setStyleSheet("background: transparent; border: none;")
        close.mousePressEvent = (
            lambda e: self.error_banner.hide() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(close, 0, Qt.AlignTop)
        return self.error_banner

    # ── Form ─────────────────────────────────────────────────
    def _form(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        # Username
        u_head = QHBoxLayout()
        ul = QLabel("Username")
        ul.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        u_head.addWidget(ul)
        u_head.addStretch()
        uh = QLabel("e.g. admin or OP-402")
        uh.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        u_head.addWidget(uh)
        lay.addLayout(u_head)

        self.username = QLineEdit("counter.lead")
        self.username.setPlaceholderText("Enter operator username")
        lay.addWidget(self._icon_field("account_circle", self.username))

        # Password
        p_head = QHBoxLayout()
        pl = QLabel("Password")
        pl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        p_head.addWidget(pl)
        p_head.addStretch()
        self.caps_warn = QFrame()
        self.caps_warn.setVisible(False)
        self.caps_warn.setStyleSheet("background: transparent; border: none;")
        cl = QHBoxLayout(self.caps_warn)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(4)
        cic = QLabel()
        cic.setFixedSize(14, 14)
        cic.setPixmap(icon_pixmap("keyboard_capslock", size=14, color=S.PRIMARY))
        cic.setStyleSheet("background: transparent; border: none;")
        cl.addWidget(cic)
        ct = QLabel("CAPS LOCK ON")
        ct.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        cl.addWidget(ct)
        p_head.addWidget(self.caps_warn)
        lay.addLayout(p_head)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("••••••••")
        self.password.textChanged.connect(self._update_caps)
        lay.addWidget(self._icon_field("lock", self.password, eye=True))

        # Remember + Reset PIN
        opts = QHBoxLayout()
        opts.setSpacing(8)
        self.remember = QCheckBox("Remember on T-01 Main Counter")
        self.remember.setChecked(True)
        self.remember.setStyleSheet(
            f"""
            QCheckBox {{
                spacing: 8px; color: {T.TEXT_PRIMARY}; font-size: 12px;
                background: transparent; border: none;
            }}
            QCheckBox::indicator {{
                width: 16px; height: 16px; border-radius: 3px;
                border: 1px solid {T.BORDER_STRONG}; background: {T.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background: {S.PRIMARY}; border: 1px solid {S.PRIMARY};
            }}
            """
        )
        opts.addWidget(self.remember)
        opts.addStretch()
        reset = QLabel("Reset PIN")
        reset.setCursor(QCursor(Qt.PointingHandCursor))
        reset.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        reset.mousePressEvent = (
            lambda e: toast(self, "PIN reset request sent to supervisor.")
            if e.button() == Qt.LeftButton else None
        )
        opts.addWidget(reset)
        lay.addLayout(opts)

        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self._exit_btn(), stretch=1)
        actions.addWidget(self._sign_in_btn(), stretch=1)
        lay.addLayout(actions)
        return wrap

    def _icon_field(self, icon: str, widget: QLineEdit, *, eye: bool = False) -> QFrame:
        wrap = QFrame()
        wrap.setFixedHeight(36)
        wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.CR}px; }}"
        )
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(10, 0, 8, 0)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignVCenter)

        ic = QLabel()
        ic.setFixedSize(17, 17)
        ic.setPixmap(icon_pixmap(icon, size=17, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        widget.setFrame(False)
        widget.setFixedHeight(32)
        widget.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; padding: 0px;
                color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 500;
                font-family: Consolas, monospace;
            }}
            """
        )
        lay.addWidget(widget, stretch=1)

        if eye:
            eye_btn = QLabel()
            eye_btn.setFixedSize(18, 18)
            eye_btn.setCursor(QCursor(Qt.PointingHandCursor))
            eye_btn.setPixmap(icon_pixmap("visibility", size=18, color=T.TEXT_SECONDARY))
            eye_btn.setStyleSheet("background: transparent; border: none;")

            def _toggle(e, w=widget, btn=eye_btn):
                if e.button() != Qt.LeftButton:
                    return
                self._pwd_visible = not self._pwd_visible
                w.setEchoMode(QLineEdit.Normal if self._pwd_visible else QLineEdit.Password)
                btn.setPixmap(icon_pixmap(
                    "visibility_off" if self._pwd_visible else "visibility",
                    size=18, color=T.TEXT_SECONDARY,
                ))

            eye_btn.mousePressEvent = _toggle
            lay.addWidget(eye_btn)
        return wrap

    def _exit_btn(self) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.CR}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_HIGH}; }}"
        )
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignCenter)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap("power_settings_new", size=16, color=T.DANGER))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        t = QLabel("Exit App")
        t.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(t)
        lay.addWidget(S.kbd("Esc"))
        btn.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        return btn

    def _sign_in_btn(self) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.CR}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignCenter)
        t = QLabel("Sign In")
        t.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 600; "
            "border: none; background: transparent;"
        )
        lay.addWidget(t)
        lay.addWidget(S.kbd("↵ F9", on_primary=True))
        btn.mousePressEvent = (
            lambda e: self._sign_in() if e.button() == Qt.LeftButton else None
        )
        return btn

    # ── Footer bars ──────────────────────────────────────────
    def _status_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        left = QHBoxLayout()
        left.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {S.PRIMARY}; border: none; border-radius: 4px;")
        left.addWidget(dot)
        st = QLabel("POS-HYD-01 · Server Online (Local)")
        st.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        left.addWidget(st)
        lay.addLayout(left)
        lay.addStretch()
        link = QLabel("Terminal Status")
        link.setCursor(QCursor(Qt.PointingHandCursor))
        link.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        link.mousePressEvent = (
            lambda e: toast(self, "Terminal POS-HYD-01 — Online (Local)")
            if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(link)
        return bar

    def _hotkey_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_HIGH}; border: none; "
            f"border-bottom-left-radius: {_CARD_R}px; "
            f"border-bottom-right-radius: {_CARD_R}px; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignCenter)
        for i, (key, label) in enumerate((
            ("Enter", "Sign In"),
            ("Esc", "Exit App"),
            ("F3", "Terminal Select"),
            ("F1", "Support"),
        )):
            if i:
                sep = QLabel("•")
                sep.setStyleSheet(
                    f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
                    f"border: none; background: transparent;"
                )
                lay.addWidget(sep)
            item = QLabel(f"<b style='color:{T.TEXT_PRIMARY}'>{key}:</b> {label}")
            item.setTextFormat(Qt.RichText)
            item.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
                f"font-family: Consolas, monospace; border: none; background: transparent;"
            )
            lay.addWidget(item)
        return bar

    # ── Auth ─────────────────────────────────────────────────
    def _update_caps(self, *_):
        # Qt doesn't expose caps lock portably; hide by default
        mods = QGuiApplication.queryKeyboardModifiers()
        # Best-effort: show when Shift is locked isn't available — keep hidden
        self.caps_warn.setVisible(False)
        _ = mods

    def _sign_in(self):
        user = self.username.text().strip()
        pwd = self.password.text()
        if not user or not pwd:
            self.error_banner.setVisible(True)
            toast(self, "Enter username and password.")
            return

        match = None
        for u in D.USERS:
            if u.get("username", "").lower() == user.lower():
                match = u
                break

        # Demo stub: known active user with any password ≥ 4, or any non-empty pair ≥ 4
        ok = False
        if match is not None:
            ok = bool(match.get("active")) and len(pwd) >= 4
        else:
            ok = len(pwd) >= 4  # allow counter.lead demo login

        if not ok:
            self.error_banner.setVisible(True)
            self.password.clear()
            self.password.setFocus()
            return

        self.error_banner.hide()
        self.result_user = dict(match) if match else {
            "username": user,
            "name": user,
            "role": "Billing Clerk",
            "terminal": "T-01 Main Counter",
            "active": True,
        }
        if self.remember.isChecked():
            # stub: remembered terminal preference
            pass
        toast(self, f"Signed in as {self.result_user.get('name', user)}")
        self.accept()
