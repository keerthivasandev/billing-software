"""Stitch — 4.2 Users: Provision New Operator + Reset Operator Password modals."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.icons import combo_dropdown_qss, icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.40)"
def _icon_field(
    icon: str,
    widget: QWidget,
    *,
    mono: bool = False,
    readonly: bool = False,
) -> QFrame:
    h = T.INPUT_H
    inner_h = h - 2
    wrap = QFrame()
    wrap.setFixedHeight(h)
    wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    bg = T.SURFACE_CONTAINER if readonly else T.SURFACE_CONTAINER_LOW
    fg = T.TEXT_SECONDARY if readonly else T.TEXT_PRIMARY
    wrap.setStyleSheet(
        f"QFrame {{ background: {bg}; border: 1px solid {T.BORDER}; "
        f"border-radius: {S.R}px; }}"
    )
    lay = QHBoxLayout(wrap)
    lay.setContentsMargins(8, 0, 6, 0)
    lay.setSpacing(6)
    lay.setAlignment(Qt.AlignVCenter)

    ic = QLabel()
    ic.setFixedSize(16, 16)
    ic.setAlignment(Qt.AlignCenter)
    ic.setPixmap(icon_pixmap(icon, size=16, color=T.TEXT_SECONDARY))
    ic.setStyleSheet("background: transparent; border: none;")
    lay.addWidget(ic, 0, Qt.AlignVCenter)

    weight = "500" if mono else "600"
    family = "Consolas, 'Courier New', monospace" if mono else "inherit"
    widget.setFixedHeight(inner_h)
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    if isinstance(widget, QLineEdit):
        widget.setFrame(False)
        widget.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        widget.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; outline: none;
                padding: 0px; margin: 0px;
                min-height: 0px; max-height: {inner_h}px;
                color: {fg}; font-size: 12px; font-weight: {weight};
                font-family: {family};
                selection-background-color: {S.PRIMARY}; selection-color: white;
            }}
            """
        )
    elif isinstance(widget, QComboBox):
        widget.setStyleSheet(
            f"""
            QComboBox {{
                background: transparent; border: none; outline: none;
                padding: 0px; margin: 0px;
                min-height: 0px; max-height: {inner_h}px;
                color: {fg}; font-size: 12px; font-weight: {weight};
                font-family: {family};
            }}
            QComboBox:focus {{ background: transparent; border: none; }}
            {combo_dropdown_qss(width=20, background="transparent")}
            """
        )
    else:
        widget.setStyleSheet(
            f"background: transparent; border: none; padding: 0px; "
            f"min-height: 0px; max-height: {inner_h}px; color: {fg}; "
            f"font-size: 12px; font-weight: {weight}; font-family: {family};"
        )
    lay.addWidget(widget, stretch=1, alignment=Qt.AlignVCenter)
    return wrap


def _labeled(label: str, field: QWidget, required: bool = False, trailing: str = "") -> QWidget:
    box = QWidget()
    box.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(4)
    cap = QLabel(label)
    cap.setStyleSheet(
        f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; "
        f"border: none; background: transparent;"
    )
    row.addWidget(cap)
    if required:
        star = QLabel("*")
        star.setStyleSheet(
            f"color: {T.DANGER}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        row.addWidget(star)
    row.addStretch()
    if trailing:
        tr = QLabel(trailing)
        tr.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        row.addWidget(tr)
    lay.addLayout(row)
    lay.addWidget(field)
    return box


def _ghost_btn(text: str, on_click) -> QFrame:
    btn = QFrame()
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFixedHeight(32)
    btn.setStyleSheet(
        f"QFrame {{ background: transparent; border: 1px solid {T.BORDER}; "
        f"border-radius: {S.R}px; }}"
        f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
    )
    lay = QHBoxLayout(btn)
    lay.setContentsMargins(12, 0, 12, 0)
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; "
        f"border: none; background: transparent;"
    )
    lay.addWidget(lbl)
    btn.mousePressEvent = (
        lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
    )
    return btn


def _primary_btn(text: str, icon: str, on_click) -> QFrame:
    btn = QFrame()
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFixedHeight(32)
    btn.setStyleSheet(
        f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
        f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
    )
    lay = QHBoxLayout(btn)
    lay.setContentsMargins(14, 0, 14, 0)
    lay.setSpacing(6)
    ic = QLabel()
    ic.setFixedSize(14, 14)
    ic.setPixmap(icon_pixmap(icon, size=14, color="white"))
    ic.setStyleSheet("background: transparent; border: none;")
    lay.addWidget(ic)
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "color: white; font-size: 12px; font-weight: 700; "
        "border: none; background: transparent;"
    )
    lay.addWidget(lbl)
    btn.mousePressEvent = (
        lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
    )
    return btn


class _UsersModalBase(QDialog):
    """Frameless centered modal with dimmed backdrop."""

    CARD_W = 512

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._backdrop = QFrame()
        self._backdrop.setObjectName("usersModalBackdrop")
        self._backdrop.setStyleSheet(
            f"QFrame#usersModalBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(self._backdrop)
        shell.setContentsMargins(28, 24, 28, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("usersModalCard")
        self._card.setFixedWidth(self.CARD_W)
        self._card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        self._card.setStyleSheet(
            f"QFrame#usersModalCard {{ background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 8px; }}"
        )
        self._card_lay = QVBoxLayout(self._card)
        self._card_lay.setContentsMargins(0, 0, 0, 0)
        self._card_lay.setSpacing(0)

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(self._backdrop)
        self._backdrop.mousePressEvent = self._on_backdrop
        QShortcut(QKeySequence("Esc"), self, activated=self.reject)

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

    def _on_backdrop(self, e):
        if e.button() != Qt.LeftButton:
            return
        if not self._card.geometry().contains(e.position().toPoint()):
            self.reject()

    def _header(self, icon: str, title: str, badge: str = "") -> QFrame:
        box = QFrame()
        box.setFixedHeight(44)
        box.setStyleSheet(
            f"QFrame {{ background: {T.HEADER_BAND}; border: none; "
            f"border-top-left-radius: 8px; border-top-right-radius: 8px; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(8)

        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap(icon, size=16, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        ttl = QLabel(title)
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(ttl)

        if badge:
            pill = QLabel(badge)
            pill.setStyleSheet(
                f"color: {S.PRIMARY}; background: {T.PRIMARY_FIXED}; "
                f"border: none; border-radius: {S.R}px; padding: 1px 6px; "
                f"font-size: 10px; font-weight: 700; font-family: Consolas, monospace;"
            )
            lay.addWidget(pill)

        lay.addStretch()

        close = QLabel()
        close.setFixedSize(22, 22)
        close.setCursor(QCursor(Qt.PointingHandCursor))
        close.setAlignment(Qt.AlignCenter)
        close.setPixmap(icon_pixmap("close", size=14, color=T.TEXT_SECONDARY))
        close.setStyleSheet("background: transparent; border: none;")
        close.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(close)
        return box


class NewUserDialog(_UsersModalBase):
    """Provision New Operator Account [F3]."""

    CARD_W = 512

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_user = None

        self._card_lay.addWidget(
            self._header("person_add", "Provision New Operator Account", "Enterprise")
        )

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 16, 16, 16)
        bl.setSpacing(12)

        grid = QWidget()
        gl = QVBoxLayout(grid)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(12)
        self.username = QLineEdit()
        self.username.setPlaceholderText("e.g. prakash_sales")
        row1.addWidget(_labeled(
            "Login Username",
            _icon_field("account_circle", self.username, mono=True),
            required=True,
        ))
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("e.g. Prakash Rao")
        row1.addWidget(_labeled(
            "Full Legal Name",
            _icon_field("person", self.full_name),
            required=True,
        ))
        gl.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("••••••••")
        row2.addWidget(_labeled(
            "New Password",
            _icon_field("key", self.password, mono=True),
            required=True,
        ))
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        self.confirm.setPlaceholderText("••••••••")
        row2.addWidget(_labeled(
            "Confirm Password",
            _icon_field("lock", self.confirm, mono=True),
            required=True,
        ))
        gl.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(12)
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("+91 90000 00000")
        row3.addWidget(_labeled(
            "Registered Mobile (SMS OTP/Alerts)",
            _icon_field("call", self.mobile, mono=True),
        ))
        self.role = QComboBox()
        self.role.addItems([
            "Billing Clerk (POS Counter & Invoicing)",
            "Admin (Full System Access)",
            "Inventory Manager (Godown Inward/Stock)",
            "Audit & Accounts Read-Only",
        ])
        row3.addWidget(_labeled(
            "Operator Role Profile",
            _icon_field("security", self.role),
        ))
        gl.addLayout(row3)

        self.terminal = QComboBox()
        self.terminal.addItems([
            "Floating / Any Authorized Terminal",
            "Terminal-01 (Main Counter)",
            "Terminal-02 (Back Office)",
            "Godown Desk (Stationary)",
        ])
        gl.addWidget(_labeled(
            "Workstation Binding",
            _icon_field("desktop_windows", self.terminal),
        ))
        bl.addWidget(grid)

        info = QFrame()
        info.setStyleSheet(
            f"QFrame {{ background: {T.ACCENT_SOFT}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        il = QHBoxLayout(info)
        il.setContentsMargins(10, 8, 10, 8)
        il.setSpacing(8)
        iic = QLabel()
        iic.setFixedSize(14, 14)
        iic.setPixmap(icon_pixmap("info", size=14, color=S.PRIMARY))
        iic.setStyleSheet("background: transparent; border: none;")
        il.addWidget(iic, 0, Qt.AlignTop)
        itxt = QLabel(
            "Hardware node locking will bind credentials upon first login. "
            "Accounts are provisioned instantly with zero seat restrictions."
        )
        itxt.setWordWrap(True)
        itxt.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        il.addWidget(itxt, stretch=1)
        bl.addWidget(info)

        foot = QHBoxLayout()
        foot.setContentsMargins(0, 4, 0, 0)
        foot.setSpacing(8)
        foot.addStretch()
        foot.addWidget(_ghost_btn("Cancel [Esc]", self.reject))
        foot.addWidget(_primary_btn("Save & Activate [F3]", "check_circle", self._save))
        bl.addLayout(foot)

        self._card_lay.addWidget(body)
        QShortcut(QKeySequence("F3"), self, activated=self._save)
        self.username.setFocus()

    def _save(self):
        user = self.username.text().strip()
        name = self.full_name.text().strip()
        pwd = self.password.text()
        if not user or not name or not pwd:
            return
        if pwd != self.confirm.text():
            return
        role_full = self.role.currentText()
        role_short = role_full.split("(")[0].strip()
        if role_short.startswith("Inventory"):
            role_label = "Inventory Mgr"
        elif role_short.startswith("Audit"):
            role_label = "Audit"
        else:
            role_label = role_short
        term = self.terminal.currentText()
        initials = "".join(p[0] for p in name.split()[:2]).upper() or "NU"
        self.result_user = {
            "id": max((u["id"] for u in D.USERS), default=0) + 1,
            "initials": initials,
            "username": user,
            "name": name,
            "role": role_short,
            "role_label": role_label,
            "role_full": role_full,
            "terminal": term,
            "terminal_short": term.replace(" (Main Counter)", "").replace(
                " (Back Office)", ""
            ).replace(" (Stationary)", ""),
            "terminal_icon": "desktop_windows",
            "mobile": self.mobile.text().strip() or "+91 90000 00000",
            "last_login": "Login: —",
            "active": True,
            "privileges": ["sales", "purchase", "cash"]
            if "Admin" not in role_full
            else ["sales", "purchase", "cash", "master", "fy", "delete"],
        }
        self.accept()


class ResetPasswordDialog(_UsersModalBase):
    """Reset Operator Password [Ctrl+R]."""

    CARD_W = 448

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.password_value = ""

        self._card_lay.addWidget(self._header("lock_reset", "Reset Operator Password"))

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 16, 16, 16)
        bl.setSpacing(12)

        # Operator identity strip
        strip = QFrame()
        strip.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        sl = QHBoxLayout(strip)
        sl.setContentsMargins(10, 8, 10, 8)
        sl.setSpacing(8)

        av = QLabel(user.get("initials", "?"))
        av.setFixedSize(28, 28)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(
            f"background: {S.PRIMARY}; color: white; border: none; "
            f"border-radius: 14px; font-size: 11px; font-weight: 700;"
        )
        sl.addWidget(av)

        meta = QVBoxLayout()
        meta.setContentsMargins(0, 0, 0, 0)
        meta.setSpacing(1)
        un = QLabel(user.get("username", ""))
        un.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        meta.addWidget(un)
        sub = QLabel(f"{user.get('name', '')} · {user.get('role_label', user.get('role', ''))}")
        sub.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        meta.addWidget(sub)
        sl.addLayout(meta, stretch=1)

        term_badge = QLabel(
            user.get("terminal_short", user.get("terminal", "")).split(" ")[0]
            if user.get("terminal_short") or user.get("terminal")
            else "—"
        )
        # Prefer Terminal-01 style short badge
        raw = user.get("terminal_short", "") or user.get("terminal", "")
        if "T-01" in raw or "Terminal-01" in raw:
            term_badge.setText("Terminal-01")
        elif "T-02" in raw or "Terminal-02" in raw:
            term_badge.setText("Terminal-02")
        elif "Godown" in raw:
            term_badge.setText("Godown")
        else:
            term_badge.setText(raw.split("(")[0].strip() or "—")
        term_badge.setStyleSheet(
            f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: none; "
            f"border-radius: {S.R}px; padding: 2px 6px; font-size: 10px; font-weight: 700;"
        )
        sl.addWidget(term_badge, 0, Qt.AlignTop)
        bl.addWidget(strip)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Enter new password")
        bl.addWidget(_labeled(
            "New Password",
            _icon_field("key", self.password, mono=True),
        ))

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        self.confirm.setPlaceholderText("Re-enter password to verify")
        bl.addWidget(_labeled(
            "Confirm New Password",
            _icon_field("lock", self.confirm, mono=True),
        ))

        force = QFrame()
        force.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        fl = QHBoxLayout(force)
        fl.setContentsMargins(8, 6, 8, 6)
        fl.setSpacing(8)
        self.force_change = QCheckBox("Force password change upon next workstation login")
        self.force_change.setChecked(True)
        self.force_change.setStyleSheet(
            f"QCheckBox {{ color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 500; "
            f"border: none; background: transparent; }}"
        )
        fl.addWidget(self.force_change)
        bl.addWidget(force)

        foot = QHBoxLayout()
        foot.setContentsMargins(0, 4, 0, 0)
        foot.setSpacing(8)
        foot.addStretch()
        foot.addWidget(_ghost_btn("Cancel [Esc]", self.reject))
        foot.addWidget(_primary_btn("Update Password", "lock", self._save))
        bl.addLayout(foot)

        self._card_lay.addWidget(body)
        self.password.setFocus()

    def _save(self):
        pwd = self.password.text()
        if not pwd or pwd != self.confirm.text():
            return
        self.password_value = pwd
        self.accept()
