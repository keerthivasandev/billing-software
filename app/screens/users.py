"""4.2 Users & Terminal Access — Stitch pixel-faithful."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.screens.users_dialogs import NewUserDialog, ResetPasswordDialog
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import toast
from app.widgets.icons import combo_dropdown_qss, icon_pixmap

_SEC_CONTAINER = "#e2e5ed"
_ON_SEC = "#434654"


class UsersScreen(QWidget):
    """Nav key ``users`` — 4.2 Users & Terminal Access."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.users = [dict(u) for u in D.USERS]
        self._filter = "all"
        self._selected = 0
        self._cards = []
        self._priv_checks = {}
        self.setStyleSheet(f"background: {T.BG_CANVAS};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        body = QWidget()
        body.setStyleSheet(f"background: {T.BG_CANVAS};")
        self.root = QVBoxLayout(body)
        self.root.setContentsMargins(16, 12, 16, 12)
        self.root.setSpacing(10)
        scroll.setWidget(body)
        outer.addWidget(scroll)

        self.root.addWidget(self._summary_row())
        split = QHBoxLayout()
        split.setSpacing(10)
        split.addWidget(self._directory_panel(), stretch=5)
        split.addWidget(self._profile_panel(), stretch=7)
        self.root.addLayout(split, stretch=1)
        self.root.addWidget(self._hotkey_bar())

        QShortcut(QKeySequence("F3"), self, activated=self._add_user)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._reset_password)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search.setFocus())
        QShortcut(QKeySequence("Delete"), self, activated=self._toggle_active)
        QShortcut(QKeySequence("F5"), self, activated=lambda: toast(self, "Mesh refreshed."))
        QShortcut(QKeySequence("Esc"), self, activated=lambda: toast(self, "Back to Settings"))

        self._reload_directory()
        if self.users:
            self._select(0)

    # ── Summary metrics ──────────────────────────────────────
    def _summary_row(self) -> QFrame:
        row = QFrame()
        row.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # User Accounts & Status
        c1 = S.card()
        l1 = QVBoxLayout(c1)
        l1.setContentsMargins(12, 10, 12, 10)
        l1.setSpacing(4)
        h1 = QHBoxLayout()
        t1 = QLabel("USER ACCOUNTS & STATUS")
        t1.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        h1.addWidget(t1)
        h1.addStretch()
        i1 = QLabel()
        i1.setFixedSize(16, 16)
        i1.setPixmap(icon_pixmap("group", size=16, color=S.PRIMARY))
        i1.setStyleSheet("background: transparent; border: none;")
        h1.addWidget(i1)
        l1.addLayout(h1)
        self.total_users_lbl = QLabel(f"{len(self.users)} Users")
        self.total_users_lbl.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 18px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        l1.addWidget(self.total_users_lbl)
        f1 = QLabel("Unlimited Accounts Supported")
        f1.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border-top: 1px solid {T.BORDER}; padding-top: 4px; background: transparent;"
        )
        l1.addWidget(f1)
        lay.addWidget(c1, stretch=1)

        # Role Matrix
        c2 = S.card()
        l2 = QVBoxLayout(c2)
        l2.setContentsMargins(12, 10, 12, 10)
        l2.setSpacing(4)
        h2 = QHBoxLayout()
        t2 = QLabel("PRE-DEFINED ROLE MATRIX")
        t2.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        h2.addWidget(t2)
        h2.addStretch()
        i2 = QLabel()
        i2.setFixedSize(16, 16)
        i2.setPixmap(icon_pixmap("shield_person", size=16, color=T.TEXT_SECONDARY))
        i2.setStyleSheet("background: transparent; border: none;")
        h2.addWidget(i2)
        l2.addLayout(h2)
        chips = QHBoxLayout()
        chips.setSpacing(6)
        self.role_admin = self._chip("Admin: 1", "primary")
        self.role_clerk = self._chip("Billing Clerk: 2", "secondary")
        self.role_godown = self._chip("Godown: 0", "neutral")
        chips.addWidget(self.role_admin)
        chips.addWidget(self.role_clerk)
        chips.addWidget(self.role_godown)
        chips.addStretch()
        l2.addLayout(chips)
        f2 = QLabel("3 System Roles Configured")
        f2.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border-top: 1px solid {T.BORDER}; padding-top: 4px; background: transparent;"
        )
        l2.addWidget(f2)
        lay.addWidget(c2, stretch=1)

        # Quick Provisioning
        c3 = S.card()
        l3 = QVBoxLayout(c3)
        l3.setContentsMargins(12, 10, 12, 10)
        l3.setSpacing(6)
        h3 = QHBoxLayout()
        t3 = QLabel("QUICK PROVISIONING")
        t3.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        h3.addWidget(t3)
        h3.addStretch()
        i3 = QLabel()
        i3.setFixedSize(16, 16)
        i3.setPixmap(icon_pixmap("person_add", size=16, color=S.PRIMARY))
        i3.setStyleSheet("background: transparent; border: none;")
        h3.addWidget(i3)
        l3.addLayout(h3)

        add_btn = QFrame()
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        abl = QHBoxLayout(add_btn)
        abl.setContentsMargins(10, 0, 10, 0)
        abl.setSpacing(6)
        aic = QLabel()
        aic.setFixedSize(14, 14)
        aic.setPixmap(icon_pixmap("add_circle", size=14, color="white"))
        aic.setStyleSheet("background: transparent; border: none;")
        abl.addWidget(aic)
        atxt = QLabel("+ Add New User")
        atxt.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 600; "
            "border: none; background: transparent;"
        )
        abl.addWidget(atxt)
        kbd = QLabel("F3")
        kbd.setStyleSheet(
            f"color: white; background: {T.ACCENT_HOVER}; border: none; "
            f"border-radius: 2px; padding: 1px 5px; font-size: 10px; "
            f"font-family: Consolas, monospace; font-weight: 700;"
        )
        abl.addWidget(kbd)
        abl.addStretch()
        add_btn.mousePressEvent = (
            lambda e: self._add_user() if e.button() == Qt.LeftButton else None
        )
        l3.addWidget(add_btn)

        foot = QHBoxLayout()
        fl = QLabel("Unlimited User Access")
        fl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; border: none; background: transparent;"
        )
        foot.addWidget(fl)
        foot.addStretch()
        ent = QLabel("Enterprise V1")
        ent.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        foot.addWidget(ent)
        sep = QFrame()
        sep.setStyleSheet(f"border-top: 1px solid {T.BORDER}; background: transparent;")
        sep.setFixedHeight(1)
        l3.addWidget(sep)
        l3.addLayout(foot)
        lay.addWidget(c3, stretch=1)

        self._refresh_summary()
        return row

    def _chip(self, text: str, kind: str) -> QLabel:
        lbl = QLabel(text)
        if kind == "primary":
            style = f"color: {S.PRIMARY}; background: {T.PRIMARY_FIXED};"
        elif kind == "secondary":
            style = f"color: {_ON_SEC}; background: {_SEC_CONTAINER};"
        else:
            style = f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER};"
        lbl.setStyleSheet(
            f"{style} border: none; border-radius: {S.R}px; padding: 2px 6px; "
            f"font-size: 11px; font-weight: 700; font-family: Consolas, monospace;"
        )
        return lbl

    def _refresh_summary(self):
        n = len(self.users)
        self.total_users_lbl.setText(f"{n} Users")
        admin = sum(1 for u in self.users if u.get("role", "") == "Admin")
        clerk = sum(1 for u in self.users if "Billing" in u.get("role", ""))
        # Design chip is "Godown" (station role), not Inventory Manager count
        godown = sum(1 for u in self.users if u.get("role", "") == "Godown")
        self.role_admin.setText(f"Admin: {admin}")
        self.role_clerk.setText(f"Billing Clerk: {clerk}")
        self.role_godown.setText(f"Godown: {godown}")

    # ── Directory (left) ─────────────────────────────────────
    def _directory_panel(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        head = QHBoxLayout()
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap("manage_accounts", size=16, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        title_row.addWidget(ic)
        ttl = QLabel("User Directory & Terminals")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(ttl)
        head.addLayout(title_row)
        head.addStretch()
        self.ops_badge = QLabel("3 Operators")
        self.ops_badge.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER}; "
            f"border: none; border-radius: {S.R}px; padding: 2px 6px; "
            f"font-size: 11px; font-weight: 600; font-family: Consolas, monospace;"
        )
        head.addWidget(self.ops_badge)
        lay.addLayout(head)

        # Filter tabs
        tabs = QHBoxLayout()
        tabs.setSpacing(6)
        self._tab_btns = {}
        for key, label in (("all", "All Users"), ("active", "Active"), ("disabled", "Disabled")):
            btn = QLabel()
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setProperty("tab_key", key)
            btn.mousePressEvent = (
                lambda e, k=key: self._set_filter(k) if e.button() == Qt.LeftButton else None
            )
            self._tab_btns[key] = btn
            tabs.addWidget(btn)
        tabs.addStretch()
        lay.addLayout(tabs)
        self._paint_tabs()

        # Search
        sh = T.INPUT_H
        search_wrap = QFrame()
        search_wrap.setFixedHeight(sh)
        search_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_wrap.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        sw = QHBoxLayout(search_wrap)
        sw.setContentsMargins(8, 0, 6, 0)
        sw.setSpacing(6)
        sw.setAlignment(Qt.AlignVCenter)
        sic = QLabel()
        sic.setFixedSize(16, 16)
        sic.setAlignment(Qt.AlignCenter)
        sic.setPixmap(icon_pixmap("search", size=16, color=T.TEXT_SECONDARY))
        sic.setStyleSheet("background: transparent; border: none;")
        sw.addWidget(sic, 0, Qt.AlignVCenter)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by operator name, ID or mobile...")
        self.search.setFrame(False)
        self.search.setFixedHeight(sh - 2)
        self.search.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.search.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; outline: none;
                padding: 0px; margin: 0px; min-height: 0px; max-height: {sh - 2}px;
                color: {T.TEXT_PRIMARY}; font-size: 12px;
            }}
            """
        )
        self.search.textChanged.connect(lambda _: self._reload_directory())
        sw.addWidget(self.search, stretch=1, alignment=Qt.AlignVCenter)
        kbd = QLabel("Ctrl+F")
        kbd.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE}; "
            f"border: 1px solid {T.BORDER}; border-radius: 2px; padding: 1px 4px; "
            f"font-size: 10px; font-family: Consolas, monospace;"
        )
        sw.addWidget(kbd, 0, Qt.AlignVCenter)
        lay.addWidget(search_wrap)

        self.list_host = QVBoxLayout()
        self.list_host.setSpacing(6)
        self.list_host.setContentsMargins(0, 0, 0, 0)
        list_wrap = QWidget()
        list_wrap.setStyleSheet("background: transparent;")
        list_wrap.setLayout(self.list_host)
        lay.addWidget(list_wrap, stretch=1)

        self.showing_lbl = QLabel("Showing 0 of 0 User Records")
        self.showing_lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-family: Consolas, monospace; "
            f"border-top: 1px solid {T.BORDER}; padding-top: 6px; background: transparent;"
        )
        lay.addWidget(self.showing_lbl)
        return box

    def _paint_tabs(self):
        active_n = sum(1 for u in self.users if u.get("active"))
        disabled_n = len(self.users) - active_n
        labels = {
            "all": f"All Users ({len(self.users)})",
            "active": f"Active ({active_n})",
            "disabled": f"Disabled ({disabled_n})",
        }
        for key, btn in self._tab_btns.items():
            btn.setText(labels[key])
            if key == self._filter:
                btn.setStyleSheet(
                    f"color: white; background: {S.PRIMARY}; border: none; "
                    f"border-radius: {S.R}px; padding: 3px 8px; "
                    f"font-size: 11px; font-weight: 700;"
                )
            else:
                btn.setStyleSheet(
                    f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER}; "
                    f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; "
                    f"padding: 3px 8px; font-size: 11px; font-weight: 500;"
                )

    def _set_filter(self, key: str):
        self._filter = key
        self._paint_tabs()
        self._reload_directory()

    def _filtered(self) -> list[tuple[int, dict]]:
        q = self.search.text().strip().lower()
        out = []
        for i, u in enumerate(self.users):
            if self._filter == "active" and not u.get("active"):
                continue
            if self._filter == "disabled" and u.get("active"):
                continue
            hay = " ".join([
                u.get("username", ""),
                u.get("name", ""),
                u.get("mobile", ""),
                u.get("role", ""),
            ]).lower()
            if q and q not in hay:
                continue
            out.append((i, u))
        return out

    def _reload_directory(self):
        while self.list_host.count():
            item = self.list_host.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._cards = []
        rows = self._filtered()
        for idx, u in rows:
            card = self._user_card(idx, u)
            self.list_host.addWidget(card)
            self._cards.append((idx, card))
        self.list_host.addStretch()
        self.ops_badge.setText(f"{len(self.users)} Operators")
        self.showing_lbl.setText(f"Showing {len(rows)} of {len(self.users)} User Records")
        self._paint_tabs()
        self._refresh_summary()

    def _user_card(self, idx: int, u: dict) -> QFrame:
        selected = idx == self._selected
        active = bool(u.get("active"))
        card = QFrame()
        card.setCursor(QCursor(Qt.PointingHandCursor))
        if selected:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
                f"border: 1px solid {S.PRIMARY}; border-radius: {S.R}px; }}"
            )
        else:
            card.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_LOW}; }}"
            )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        left = QHBoxLayout()
        left.setSpacing(8)

        av_bg = S.PRIMARY if selected else (
            T.PRIMARY_FIXED if active else T.SURFACE_CONTAINER
        )
        av_fg = "white" if selected else (S.PRIMARY if active else T.TEXT_SECONDARY)
        av = QLabel(u.get("initials", "?"))
        av.setFixedSize(28, 28)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(
            f"background: {av_bg}; color: {av_fg}; border: none; "
            f"border-radius: 14px; font-size: 11px; font-weight: 700;"
        )
        left.addWidget(av)

        meta = QVBoxLayout()
        meta.setContentsMargins(0, 0, 0, 0)
        meta.setSpacing(1)
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        un_color = T.TEXT_PRIMARY if active else T.TEXT_SECONDARY
        un = QLabel(u.get("username", ""))
        un.setStyleSheet(
            f"color: {un_color}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        name_row.addWidget(un)
        status = QLabel("Active" if active else "Inactive")
        if active:
            status.setStyleSheet(
                f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
            )
        else:
            status.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
            )
        name_row.addWidget(status)
        name_row.addStretch()
        meta.addLayout(name_row)
        nm = QLabel(u.get("name", ""))
        nm.setStyleSheet(
            f"color: {un_color}; font-size: 11px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        meta.addWidget(nm)
        left.addLayout(meta)
        top.addLayout(left, stretch=1)

        role = u.get("role_label", u.get("role", ""))
        role_pill = QLabel(role)
        if "Admin" in role:
            rp = f"color: {S.PRIMARY}; background: {T.PRIMARY_FIXED};"
        elif "Billing" in role:
            rp = f"color: {_ON_SEC}; background: {_SEC_CONTAINER};"
        else:
            rp = f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER};"
        role_pill.setStyleSheet(
            f"{rp} border: none; border-radius: {S.R}px; padding: 2px 6px; "
            f"font-size: 10px; font-weight: 700; font-family: Consolas, monospace;"
        )
        top.addWidget(role_pill, 0, Qt.AlignTop)
        lay.addLayout(top)

        foot = QHBoxLayout()
        term_row = QHBoxLayout()
        term_row.setSpacing(4)
        tic = QLabel()
        tic.setFixedSize(12, 12)
        tic_color = T.SUCCESS if active and selected else (
            S.PRIMARY if active else T.TEXT_SECONDARY
        )
        tic.setPixmap(icon_pixmap(u.get("terminal_icon", "desktop_windows"), size=12, color=tic_color))
        tic.setStyleSheet("background: transparent; border: none;")
        term_row.addWidget(tic)
        term = QLabel(u.get("terminal_short", u.get("terminal", "")))
        term.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        term_row.addWidget(term)
        foot.addLayout(term_row)
        foot.addStretch()
        login = QLabel(u.get("last_login", ""))
        login.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        foot.addWidget(login)
        sep = QFrame()
        sep.setStyleSheet(f"border-top: 1px solid {T.BORDER}; background: transparent;")
        sep.setFixedHeight(1)
        lay.addWidget(sep)
        lay.addLayout(foot)

        card.mousePressEvent = (
            lambda e, i=idx: self._select(i) if e.button() == Qt.LeftButton else None
        )
        return card

    def _select(self, idx: int):
        if idx < 0 or idx >= len(self.users):
            return
        self._selected = idx
        self._reload_directory()
        self._load_profile()

    # ── Profile panel (right) ────────────────────────────────
    def _profile_panel(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        # Header + actions
        head = QHBoxLayout()
        head.setSpacing(8)
        left = QHBoxLayout()
        left.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap("badge", size=16, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        ttl = QLabel("Operator Profile & Access Rights:")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        left.addWidget(ttl)
        self.profile_user = QLabel("")
        self.profile_user.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 12px; font-weight: 700; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        left.addWidget(self.profile_user)
        self.profile_status = QLabel("Active")
        self.profile_status.setStyleSheet(
            f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: none; "
            f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
        )
        left.addWidget(self.profile_status)
        left.addStretch()
        head.addLayout(left, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(self._action_btn(
            "Reset Password", "lock_reset", "Ctrl+R", "secondary", self._reset_password,
        ))
        self.status_toggle = self._action_btn(
            "Deactivate", "person_off", "", "danger", self._toggle_active,
        )
        actions.addWidget(self.status_toggle)
        actions.addWidget(self._action_btn(
            "Delete User", "delete", "", "danger", self._delete_user,
        ))
        actions.addWidget(self._action_btn(
            "Save Changes", "save", "Ctrl+S", "primary", self._save,
        ))
        head.addLayout(actions)
        lay.addLayout(head)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {T.BORDER}; border: none;")
        lay.addWidget(sep)

        # Form grid 2×3
        form = QWidget()
        form.setStyleSheet("background: transparent;")
        grid = QVBoxLayout(form)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        r1 = QHBoxLayout()
        r1.setSpacing(10)
        self.f_username = QLineEdit()
        self.f_username.setReadOnly(True)
        r1.addWidget(self._field(
            "Username (Login ID)", "account_circle", self.f_username,
            mono=True, readonly=True, trailing="[LOCKED]",
        ))
        self.f_name = QLineEdit()
        r1.addWidget(self._field("Full Legal Name", "person", self.f_name))
        grid.addLayout(r1)

        r2 = QHBoxLayout()
        r2.setSpacing(10)
        self.f_mobile = QLineEdit()
        r2.addWidget(self._field(
            "Registered Mobile (SMS Bill Alerts)", "call", self.f_mobile, mono=True,
        ))
        self.f_role = QComboBox()
        self.f_role.addItems(D.USER_ROLES)
        r2.addWidget(self._field("Pre-defined Role Profile", "security", self.f_role))
        grid.addLayout(r2)

        r3 = QHBoxLayout()
        r3.setSpacing(10)
        self.f_terminal = QComboBox()
        self.f_terminal.addItems(D.USER_TERMINALS)
        r3.addWidget(self._field("Workstation Binding", "desktop_windows", self.f_terminal))
        self.f_status = QComboBox()
        self.f_status.addItems([
            "Active (Authorized to Login)",
            "Disabled / Deactivated",
        ])
        r3.addWidget(self._field("Account Status", "toggle_on", self.f_status, success=True))
        grid.addLayout(r3)
        lay.addWidget(form)

        # Privilege matrix
        priv = QFrame()
        priv.setStyleSheet("background: transparent; border: none;")
        pl = QVBoxLayout(priv)
        pl.setContentsMargins(0, 4, 0, 0)
        pl.setSpacing(8)
        ph = QHBoxLayout()
        ph_left = QHBoxLayout()
        ph_left.setSpacing(4)
        pic = QLabel()
        pic.setFixedSize(12, 12)
        pic.setPixmap(icon_pixmap("checklist", size=12, color=S.PRIMARY))
        pic.setStyleSheet("background: transparent; border: none;")
        ph_left.addWidget(pic)
        pt = QLabel("PRE-DEFINED ROLE PRIVILEGE MATRIX")
        pt.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        ph_left.addWidget(pt)
        ph.addLayout(ph_left)
        ph.addStretch()
        defaults = QLabel("Role Defaults Applied")
        defaults.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        ph.addWidget(defaults)
        pl.addLayout(ph)

        matrix = QWidget()
        ml = QVBoxLayout(matrix)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(6)
        row = None
        self._priv_checks = {}
        for i, (key, title, sub, locked) in enumerate(D.USER_PRIVILEGES):
            if i % 2 == 0:
                row = QHBoxLayout()
                row.setSpacing(8)
                ml.addLayout(row)
            cell = self._priv_cell(key, title, sub, locked)
            row.addWidget(cell)
        if len(D.USER_PRIVILEGES) % 2:
            row.addStretch()
        pl.addWidget(matrix)
        lay.addWidget(priv)
        lay.addStretch()
        return box

    def _action_btn(self, label, icon, shortcut, kind, on_click) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(28)
        if kind == "primary":
            btn.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
            )
            fg, ic = "white", "white"
            kbd_bg = T.ACCENT_HOVER
        elif kind == "danger":
            btn.setStyleSheet(
                f"QFrame {{ background: transparent; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.DANGER_BG}; }}"
            )
            fg, ic = T.DANGER, T.DANGER
            kbd_bg = T.SURFACE
        elif kind == "success":
            btn.setStyleSheet(
                f"QFrame {{ background: transparent; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.SUCCESS_BG}; }}"
            )
            fg, ic = T.SUCCESS_FG, T.SUCCESS_FG
            kbd_bg = T.SURFACE
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
                f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
            )
            fg, ic = T.TEXT_PRIMARY, S.PRIMARY
            kbd_bg = T.SURFACE
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(4)
        il = QLabel()
        il.setFixedSize(12, 12)
        il.setPixmap(icon_pixmap(icon, size=12, color=ic))
        il.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(il)
        txt = QLabel(label)
        txt.setStyleSheet(
            f"color: {fg}; font-size: 11px; font-weight: {'700' if kind == 'primary' else '600'}; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(txt)
        if shortcut:
            k = QLabel(shortcut)
            if kind == "primary":
                k.setStyleSheet(
                    f"color: white; background: {kbd_bg}; border: none; "
                    f"border-radius: 2px; padding: 0 4px; font-size: 9px; "
                    f"font-family: Consolas, monospace;"
                )
            else:
                k.setStyleSheet(
                    f"color: {T.TEXT_SECONDARY}; background: {kbd_bg}; "
                    f"border: 1px solid {T.BORDER}; border-radius: 2px; padding: 0 4px; "
                    f"font-size: 9px; font-family: Consolas, monospace;"
                )
            lay.addWidget(k)
        btn.mousePressEvent = (
            lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
        )
        # Keep child refs so toggle button can be repainted in place
        btn._ic_lbl = il
        btn._txt_lbl = txt
        return btn

    def _refresh_status_toggle(self, active: bool):
        """Show Deactivate when active, Activate when inactive."""
        btn = getattr(self, "status_toggle", None)
        if btn is None:
            return
        if active:
            label, icon, kind = "Deactivate", "person_off", "danger"
            fg, ic = T.DANGER, T.DANGER
            hover = T.DANGER_BG
        else:
            label, icon, kind = "Activate", "how_to_reg", "success"
            fg, ic = T.SUCCESS_FG, T.SUCCESS_FG
            hover = T.SUCCESS_BG
        btn.setStyleSheet(
            f"QFrame {{ background: transparent; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {hover}; }}"
        )
        btn._ic_lbl.setPixmap(icon_pixmap(icon, size=12, color=ic))
        btn._txt_lbl.setText(label)
        btn._txt_lbl.setStyleSheet(
            f"color: {fg}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        btn.setProperty("toggle_kind", kind)

    def _field(
        self, label, icon, widget, *, mono=False, readonly=False,
        trailing="", success=False,
    ) -> QWidget:
        h = T.INPUT_H  # match global input rhythm; border lives on wrap
        box = QWidget()
        box.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        cap = QLabel(label)
        cap.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        top.addWidget(cap)
        top.addStretch()
        if trailing:
            tr = QLabel(trailing)
            tr.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
                f"font-family: Consolas, monospace; border: none; background: transparent;"
            )
            top.addWidget(tr)
        lay.addLayout(top)

        wrap = QFrame()
        wrap.setFixedHeight(h)
        wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bg = T.SURFACE_CONTAINER if readonly else T.SURFACE_CONTAINER_LOW
        wrap.setStyleSheet(
            f"QFrame {{ background: {bg}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        wl = QHBoxLayout(wrap)
        wl.setContentsMargins(8, 0, 6, 0)
        wl.setSpacing(6)
        wl.setAlignment(Qt.AlignVCenter)

        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setAlignment(Qt.AlignCenter)
        ic.setPixmap(icon_pixmap(icon, size=16, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        wl.addWidget(ic, 0, Qt.AlignVCenter)

        fg = T.TEXT_SECONDARY if readonly else (T.SUCCESS_FG if success else T.TEXT_PRIMARY)
        weight = "700" if success else ("500" if mono else "600")
        family = "Consolas, 'Courier New', monospace" if mono else "inherit"
        inner_h = h - 2  # inside 1px border
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
                QComboBox:focus {{
                    background: transparent; border: none;
                }}
                {combo_dropdown_qss(width=20, background="transparent")}
                """
            )
        else:
            widget.setStyleSheet(
                f"background: transparent; border: none; padding: 0px; "
                f"min-height: 0px; max-height: {inner_h}px; color: {fg}; "
                f"font-size: 12px; font-weight: {weight}; font-family: {family};"
            )
        wl.addWidget(widget, stretch=1, alignment=Qt.AlignVCenter)
        lay.addWidget(wrap)
        return box

    def _priv_cell(self, key, title, sub, locked) -> QFrame:
        cell = QFrame()
        if locked:
            cell.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
            )
            cell.setCursor(QCursor(Qt.ForbiddenCursor))
        else:
            cell.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; "
                f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; }}"
            )
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignVCenter)
        cb = QCheckBox()
        cb.setEnabled(not locked)
        cb.setStyleSheet("background: transparent; border: none;")
        self._priv_checks[key] = cb
        lay.addWidget(cb, 0, Qt.AlignVCenter)
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(4)
        tl = QLabel(title)
        tl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY if locked else T.TEXT_PRIMARY}; "
            f"font-size: 12px; font-weight: 600; border: none; background: transparent;"
        )
        title_row.addWidget(tl)
        if locked:
            lk = QLabel()
            lk.setFixedSize(12, 12)
            lk.setPixmap(icon_pixmap("lock", size=12, color=T.TEXT_SECONDARY))
            lk.setStyleSheet("background: transparent; border: none;")
            title_row.addWidget(lk)
        title_row.addStretch()
        col.addLayout(title_row)
        sl = QLabel(sub)
        sl.setWordWrap(True)
        sl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
            f"{'font-family: Consolas, monospace;' if locked else ''}"
            f"border: none; background: transparent;"
        )
        col.addWidget(sl)
        lay.addLayout(col, stretch=1)
        return cell

    def _load_profile(self):
        if not self.users:
            return
        u = self.users[self._selected]
        active = bool(u.get("active"))
        self.profile_user.setText(u.get("username", ""))
        self.profile_status.setText("Active" if active else "Inactive")
        if active:
            self.profile_status.setStyleSheet(
                f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
            )
        else:
            self.profile_status.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 700;"
            )
        self.f_username.setText(u.get("username", ""))
        self.f_name.setText(u.get("name", ""))
        self.f_mobile.setText(u.get("mobile", ""))
        role_full = u.get("role_full", "")
        idx = self.f_role.findText(role_full)
        if idx < 0:
            # fuzzy match by role short name
            for i in range(self.f_role.count()):
                if u.get("role", "") in self.f_role.itemText(i):
                    idx = i
                    break
        if idx >= 0:
            self.f_role.setCurrentIndex(idx)
        term = u.get("terminal", "")
        tidx = self.f_terminal.findText(term)
        if tidx >= 0:
            self.f_terminal.setCurrentIndex(tidx)
        self.f_status.setCurrentIndex(0 if active else 1)
        # Re-tint status combo to match active/disabled state
        status_fg = T.SUCCESS_FG if active else T.DANGER
        self.f_status.setStyleSheet(
            f"""
            QComboBox {{
                background: transparent; border: none; outline: none;
                padding: 0px; margin: 0px;
                min-height: 0px; max-height: {T.INPUT_H - 2}px;
                color: {status_fg}; font-size: 12px; font-weight: 700;
            }}
            QComboBox:focus {{ background: transparent; border: none; }}
            {combo_dropdown_qss(width=20, background="transparent")}
            """
        )
        self._refresh_status_toggle(active)
        privs = set(u.get("privileges", []))
        for key, cb in self._priv_checks.items():
            locked = next((p[3] for p in D.USER_PRIVILEGES if p[0] == key), False)
            if locked:
                cb.setChecked(False)
            else:
                cb.setChecked(key in privs)

    # ── Hotkey bar ───────────────────────────────────────────
    def _hotkey_bar(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)

        left = QHBoxLayout()
        left.setSpacing(12)
        title = QHBoxLayout()
        title.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(12, 12)
        ic.setPixmap(icon_pixmap("keyboard", size=12, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        title.addWidget(ic)
        tl = QLabel("HOTKEYS:")
        tl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title.addWidget(tl)
        left.addLayout(title)
        for key, label in (
            ("F3", "Add User"),
            ("F4", "Edit Selected"),
            ("Ctrl+S", "Save Changes"),
            ("Ctrl+R", "Reset Password"),
            ("Del", "Deactivate"),
            ("F5", "Refresh Mesh"),
            ("Esc", "Back / Exit"),
        ):
            item = QHBoxLayout()
            item.setSpacing(4)
            k = QLabel(key)
            k.setStyleSheet(
                f"color: {T.TEXT_PRIMARY}; background: {T.SURFACE_CONTAINER}; "
                f"border: 1px solid {T.BORDER}; border-radius: {S.R}px; padding: 2px 6px; "
                f"font-size: 11px; font-weight: 700; font-family: Consolas, monospace;"
            )
            item.addWidget(k)
            lb = QLabel(label)
            lb.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
                f"border: none; background: transparent;"
            )
            item.addWidget(lb)
            left.addLayout(item)
        lay.addLayout(left)
        lay.addStretch()

        right = QHBoxLayout()
        right.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(f"background: {S.PRIMARY}; border: none; border-radius: 3px;")
        right.addWidget(dot)
        sess = QLabel("Sri Lakshmi Electricals ERP v4.8 • Authorized Session: RAMESH-T1")
        sess.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        right.addWidget(sess)
        lay.addLayout(right)
        return box

    # ── Actions ──────────────────────────────────────────────
    def _current(self) -> dict | None:
        if 0 <= self._selected < len(self.users):
            return self.users[self._selected]
        return None

    def _add_user(self):
        dlg = NewUserDialog(self.window())
        if dlg.exec() != NewUserDialog.Accepted or not dlg.result_user:
            return
        self.users.append(dlg.result_user)
        D.USERS[:] = [dict(u) for u in self.users]
        self._selected = len(self.users) - 1
        self._reload_directory()
        self._load_profile()
        toast(self, f"Operator {dlg.result_user['username']} activated.")

    def _reset_password(self):
        u = self._current()
        if not u:
            return
        dlg = ResetPasswordDialog(u, self.window())
        if dlg.exec() == ResetPasswordDialog.Accepted:
            toast(self, f"Password updated for {u['username']}.")

    def _toggle_active(self):
        u = self._current()
        if not u:
            return
        u["active"] = not bool(u.get("active"))
        self._reload_directory()
        self._load_profile()
        state = "activated" if u["active"] else "deactivated"
        toast(self, f"{u['username']} {state}.")

    def _delete_user(self):
        u = self._current()
        if not u:
            return
        name = u["username"]
        del self.users[self._selected]
        D.USERS[:] = [dict(x) for x in self.users]
        self._selected = min(self._selected, max(0, len(self.users) - 1))
        self._reload_directory()
        if self.users:
            self._load_profile()
        toast(self, f"{name} deleted.")

    def _save(self):
        u = self._current()
        if not u:
            return
        u["name"] = self.f_name.text().strip() or u["name"]
        u["mobile"] = self.f_mobile.text().strip() or u["mobile"]
        role_full = self.f_role.currentText()
        u["role_full"] = role_full
        role_short = role_full.split("(")[0].strip()
        u["role"] = role_short
        if role_short.startswith("Inventory"):
            u["role_label"] = "Inventory Mgr"
        else:
            u["role_label"] = role_short
        u["terminal"] = self.f_terminal.currentText()
        u["terminal_short"] = u["terminal"].replace(" (Main Counter)", "").replace(
            " (Back Office)", ""
        ).replace(" (Stationary)", "")
        u["active"] = self.f_status.currentIndex() == 0
        privs = [k for k, cb in self._priv_checks.items() if cb.isChecked() and cb.isEnabled()]
        # Keep admin-locked keys if already admin
        if "Admin" in role_full:
            for locked_key in ("master", "fy", "delete"):
                if locked_key not in privs:
                    privs.append(locked_key)
        u["privileges"] = privs
        D.USERS[:] = [dict(x) for x in self.users]
        self._reload_directory()
        self._load_profile()
        toast(self, "User permissions saved.")
