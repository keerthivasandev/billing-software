"""License & Activation Management — Stitch pixel-faithful (0c409a033ee84ad5b0982eb007a6cb8c)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import toast
from app.widgets.icons import icon_pixmap


class LicenseActivationScreen(QWidget):
    """Nav key ``license`` — License & System Activation management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lic = dict(D.LICENSE)
        self.setStyleSheet(f"background: {T.BG_CANVAS};")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)  # gap-3
        root.setAlignment(Qt.AlignTop)

        root.addWidget(self._header_ribbon())

        split = QHBoxLayout()
        split.setSpacing(12)  # gap-3
        split.setAlignment(Qt.AlignTop)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(12)
        left.setAlignment(Qt.AlignTop)
        left.addWidget(self._certificate_card())
        left.addWidget(self._hardware_card())
        left_wrap = QWidget()
        left_wrap.setStyleSheet("background: transparent;")
        left_wrap.setLayout(left)
        left_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        split.addWidget(left_wrap, 7)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(12)
        right.setAlignment(Qt.AlignTop)
        right.addWidget(self._upgrade_card())
        right.addWidget(self._support_card())
        right_wrap = QWidget()
        right_wrap.setStyleSheet("background: transparent;")
        right_wrap.setLayout(right)
        right_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        split.addWidget(right_wrap, 5)

        root.addLayout(split)
        root.addStretch(1)
        root.addWidget(self._hotkey_bar())

        QShortcut(QKeySequence("F3"), self, activated=lambda: toast(self, "Checking for updates…"))
        QShortcut(QKeySequence("F4"), self, activated=self._focus_renewal)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._revalidate)
        QShortcut(QKeySequence("F5"), self, activated=self._revalidate)
        QShortcut(QKeySequence("Return"), self, activated=self._apply_key)
        QShortcut(QKeySequence("Enter"), self, activated=self._apply_key)
        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._copy_info)
        QShortcut(QKeySequence("Esc"), self, activated=lambda: toast(self, "Return to Dashboard"))

    # ══════════════════════════════════════════════════════════
    # TOP CONTROL RIBBON
    # ══════════════════════════════════════════════════════════
    def _header_ribbon(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)  # p-3
        lay.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.setContentsMargins(0, 0, 0, 0)

        # Title chip
        chip = QFrame()
        chip.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        cl = QHBoxLayout(chip)
        cl.setContentsMargins(10, 6, 10, 6)
        cl.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap("verified_user", size=18, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        cl.addWidget(ic, 0, Qt.AlignTop)

        mid = QVBoxLayout()
        mid.setContentsMargins(0, 0, 0, 0)
        mid.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title = QLabel("License & System Activation")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(title)
        status = QFrame()
        status.setStyleSheet(
            f"QFrame {{ background: {T.SUCCESS_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        sl = QHBoxLayout(status)
        sl.setContentsMargins(8, 2, 8, 2)
        sl.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(f"background: {T.SUCCESS}; border: none; border-radius: 3px;")
        sl.addWidget(dot)
        st = QLabel(self.lic["status"])
        st.setStyleSheet(
            f"color: {T.SUCCESS_FG}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        sl.addWidget(st)
        title_row.addWidget(status)
        title_row.addStretch()
        mid.addLayout(title_row)

        sub = QLabel(f"{self.lic['entity']}  •  {self.lic['edition']}")
        sub.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        mid.addWidget(sub)
        cl.addLayout(mid, stretch=1)
        row.addWidget(chip, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(self._btn(
            "Renew / Extend", "upgrade", "F4", kind="secondary",
            icon_color=T.SUCCESS_FG, on_click=self._focus_renewal,
        ))
        actions.addWidget(self._btn(
            "Re-validate Node", "lock_reset", "Ctrl+R", kind="primary",
            on_click=self._revalidate,
        ))
        row.addLayout(actions)
        lay.addLayout(row)
        return box

    # ══════════════════════════════════════════════════════════
    # CERTIFICATE DETAILS
    # ══════════════════════════════════════════════════════════
    def _certificate_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignTop)

        lay.addWidget(self._card_title("badge", "Commercial License Certificate Details"))

        # Registered entity
        lay.addWidget(self._kv_row(
            "domain", "Registered Entity:",
            f"{self.lic['entity']} ",
            trailing_muted=self.lic["entity_loc"],
        ))

        # Product key
        key_row = QFrame()
        key_row.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        kr = QHBoxLayout(key_row)
        kr.setContentsMargins(10, 6, 10, 6)
        kr.setSpacing(8)
        left = QHBoxLayout()
        left.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap("vpn_key", size=14, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        lb = QLabel("License Product Key:")
        lb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        left.addWidget(lb)
        kr.addLayout(left)
        kr.addStretch()
        key = QLabel(self.lic["product_key"])
        key.setStyleSheet(
            f"color: {S.PRIMARY}; background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; padding: 2px 8px; font-size: 12px; font-weight: 700; "
            f"font-family: Consolas, monospace;"
        )
        kr.addWidget(key)
        lay.addWidget(key_row)

        # Dates grid
        dates = QHBoxLayout()
        dates.setSpacing(8)
        dates.addWidget(self._date_cell(
            "calendar_today", "Activation Date & Time", self.lic["activated_at"],
        ))
        exp = self._date_cell(
            "event_repeat", "Expiry / Renewal Date", self.lic["expires_at"],
            hint=f"Auto-offline grace period: {self.lic['grace_days']} days",
        )
        dates.addWidget(exp)
        lay.addLayout(dates)

        # Features
        feat_wrap = QFrame()
        feat_wrap.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        fl = QVBoxLayout(feat_wrap)
        fl.setContentsMargins(0, 8, 0, 0)
        fl.setSpacing(8)
        fh = QHBoxLayout()
        fh.setSpacing(6)
        fic = QLabel()
        fic.setFixedSize(12, 12)
        fic.setPixmap(icon_pixmap("checklist", size=12, color=S.PRIMARY))
        fic.setStyleSheet("background: transparent; border: none;")
        fh.addWidget(fic)
        ft = QLabel("FEATURES ENTITLED UNDER CURRENT LICENSE")
        ft.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        fh.addWidget(ft)
        fh.addStretch()
        fl.addLayout(fh)

        grid = QHBoxLayout()
        grid.setSpacing(8)
        col_a = QVBoxLayout()
        col_a.setSpacing(8)
        col_b = QVBoxLayout()
        col_b.setSpacing(8)
        feats = self.lic["features"]
        for i, name in enumerate(feats):
            cell = self._feature_cell(name)
            (col_a if i % 2 == 0 else col_b).addWidget(cell)
        grid.addLayout(col_a)
        grid.addLayout(col_b)
        fl.addLayout(grid)
        lay.addWidget(feat_wrap)
        return box

    # ══════════════════════════════════════════════════════════
    # HARDWARE BINDING
    # ══════════════════════════════════════════════════════════
    def _hardware_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignTop)

        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(self._icon_chip("memory"), 0, Qt.AlignVCenter)
        ttl = QLabel("Hardware Binding & Terminal Lock")
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        head.addWidget(ttl)
        head.addStretch()
        badge = QLabel("Strict Lock Enforced")
        badge.setStyleSheet(
            f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
        head.addWidget(badge)
        head_wrap = QFrame()
        head_wrap.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        hl = QHBoxLayout(head_wrap)
        hl.setContentsMargins(0, 0, 0, 8)
        hl.addLayout(head)
        lay.addWidget(head_wrap)

        sig = QFrame()
        sig.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        sg = QHBoxLayout(sig)
        sg.setContentsMargins(8, 8, 8, 8)
        sg.setSpacing(8)
        col = QVBoxLayout()
        col.setSpacing(2)
        sl = QLabel("Hardware Signature (CPU & Motherboard UUID)")
        sl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        col.addWidget(sl)
        sv = QLabel(self.lic["hw_signature"])
        sv.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        col.addWidget(sv)
        sg.addLayout(col, stretch=1)
        matched = QHBoxLayout()
        matched.setSpacing(4)
        mic = QLabel()
        mic.setFixedSize(14, 14)
        mic.setPixmap(icon_pixmap("check", size=14, color=T.SUCCESS_FG))
        mic.setStyleSheet("background: transparent; border: none;")
        matched.addWidget(mic)
        mt = QLabel("Matched")
        mt.setStyleSheet(
            f"color: {T.SUCCESS_FG}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        matched.addWidget(mt)
        sg.addLayout(matched)
        lay.addWidget(sig)

        grid = QHBoxLayout()
        grid.setSpacing(8)
        grid.addWidget(self._info_tile("IP / Network Binding", self.lic["ip_binding"]))
        grid.addWidget(self._info_tile("Last Verified Timestamp", self.lic["last_verified"]))
        lay.addLayout(grid)
        return box

    # ══════════════════════════════════════════════════════════
    # UPGRADE / APPLY KEY
    # ══════════════════════════════════════════════════════════
    def _upgrade_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignTop)

        lay.addWidget(self._card_title("card_membership", "Extend or Upgrade License"))

        desc = QLabel(
            "To add more terminal seats or extend your annual support subscription, "
            "enter a renewal key or contact Sri Lakshmi ERP Support."
        )
        desc.setWordWrap(True)
        desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        desc.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(desc)

        lab = QLabel("ENTER RENEWAL LICENSE KEY OR PAYLOAD")
        lab.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        lay.addWidget(lab)

        field = QFrame()
        field.setFixedHeight(32)
        field.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        fl = QHBoxLayout(field)
        fl.setContentsMargins(10, 0, 4, 0)
        fl.setSpacing(6)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX-XXXXX")
        self.key_input.setFrame(False)
        self.key_input.setFixedHeight(28)
        self.key_input.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; padding: 0px;
                color: {T.TEXT_PRIMARY}; font-size: 12px;
                font-family: Consolas, monospace;
            }}
            """
        )
        fl.addWidget(self.key_input, stretch=1)
        browse = QFrame()
        browse.setCursor(QCursor(Qt.PointingHandCursor))
        browse.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        bl = QHBoxLayout(browse)
        bl.setContentsMargins(8, 4, 8, 4)
        bl.setSpacing(4)
        bic = QLabel()
        bic.setFixedSize(12, 12)
        bic.setPixmap(icon_pixmap("folder_open", size=12, color=T.TEXT_SECONDARY))
        bic.setStyleSheet("background: transparent; border: none;")
        bl.addWidget(bic)
        bt = QLabel("Browse .lic")
        bt.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        bl.addWidget(bt)
        browse.mousePressEvent = (
            lambda e: self._browse_lic() if e.button() == Qt.LeftButton else None
        )
        fl.addWidget(browse)
        lay.addWidget(field)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        apply_btn = self._btn(
            "Apply License Key", "key", "Enter", kind="primary",
            stretch=True, on_click=self._apply_key,
        )
        actions.addWidget(apply_btn, stretch=1)
        actions.addWidget(self._btn(
            "Request Quote", "request_quote", kind="secondary",
            on_click=lambda: toast(self, "Quote request sent to partner."),
        ))
        lay.addLayout(actions)
        return box

    # ══════════════════════════════════════════════════════════
    # SUPPORT CONTACT
    # ══════════════════════════════════════════════════════════
    def _support_card(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignTop)

        lay.addWidget(self._card_title("support_agent", "Distributor & Vendor Support Contact"))

        partner = QFrame()
        partner.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        pl = QVBoxLayout(partner)
        pl.setContentsMargins(10, 10, 10, 10)
        pl.setSpacing(6)
        pl.addWidget(self._muted("Authorized Partner:"))
        pn = QLabel(self.lic["partner"])
        pn.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        pl.addWidget(pn)
        pa = QLabel(self.lic["partner_address"])
        pa.setWordWrap(True)
        pa.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        pl.addWidget(pa)
        lay.addWidget(partner)

        help_box = QFrame()
        help_box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        hl = QVBoxLayout(help_box)
        hl.setContentsMargins(10, 10, 10, 10)
        hl.setSpacing(4)
        top = QHBoxLayout()
        top.addWidget(self._muted("Direct Helpline:"))
        top.addStretch()
        online = QHBoxLayout()
        online.setSpacing(4)
        od = QLabel()
        od.setFixedSize(6, 6)
        od.setStyleSheet(f"background: {T.SUCCESS}; border: none; border-radius: 3px;")
        online.addWidget(od)
        ot = QLabel("Support Online")
        ot.setStyleSheet(
            f"color: {T.SUCCESS_FG}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        online.addWidget(ot)
        top.addLayout(online)
        hl.addLayout(top)

        phone = QHBoxLayout()
        phone.setSpacing(6)
        pic = QLabel()
        pic.setFixedSize(14, 14)
        pic.setPixmap(icon_pixmap("call", size=14, color=S.PRIMARY))
        pic.setStyleSheet("background: transparent; border: none;")
        phone.addWidget(pic)
        pt = QLabel(self.lic["helpline"])
        pt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        phone.addWidget(pt)
        phone.addStretch()
        hl.addLayout(phone)

        hours = QLabel(self.lic["hours"])
        hours.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
            f"border: none; background: transparent;"
        )
        hl.addWidget(hours)
        lay.addWidget(help_box)
        return box

    # ══════════════════════════════════════════════════════════
    # HOTKEYS
    # ══════════════════════════════════════════════════════════
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
        tl = QLabel("Hotkeys:")
        tl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        title.addWidget(tl)
        left.addLayout(title)
        for key, label in (
            ("F3", "Check Updates"),
            ("F4", "Extend License"),
            ("Ctrl+C", "Copy License Info"),
            ("F5", "Re-verify Node"),
            ("Esc", "Return to Dashboard"),
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
        dot.setStyleSheet(f"background: {T.SUCCESS}; border: none; border-radius: 3px;")
        right.addWidget(dot)
        foot = QLabel(self.lic["footer"])
        foot.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        right.addWidget(foot)
        lay.addLayout(right)
        return box

    # ── helpers ──────────────────────────────────────────────
    def _card_title(self, icon: str, text: str) -> QFrame:
        wrap = QFrame()
        wrap.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 8)
        lay.setSpacing(8)
        lay.addWidget(self._icon_chip(icon))
        ttl = QLabel(text)
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 13px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(ttl)
        lay.addStretch()
        return wrap

    def _icon_chip(self, icon: str) -> QFrame:
        chip = QFrame()
        chip.setFixedSize(24, 24)
        chip.setStyleSheet(
            f"QFrame {{ background: {T.PRIMARY_FIXED}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(chip)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignCenter)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap(icon, size=14, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        return chip

    def _kv_row(self, icon: str, label: str, value: str, trailing_muted: str = "") -> QFrame:
        row = QFrame()
        row.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(row)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)
        left = QHBoxLayout()
        left.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap(icon, size=14, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        lb = QLabel(label)
        lb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        left.addWidget(lb)
        lay.addLayout(left)
        lay.addStretch()
        val = QLabel(value)
        val.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(val)
        if trailing_muted:
            mute = QLabel(trailing_muted)
            mute.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 400; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(mute)
        return row

    def _date_cell(self, icon: str, label: str, value: str, hint: str = "") -> QFrame:
        cell = QFrame()
        cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cell.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QVBoxLayout(cell)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(2)
        top = QHBoxLayout()
        top.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(12, 12)
        ic.setPixmap(icon_pixmap(icon, size=12, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        top.addWidget(ic)
        lb = QLabel(label)
        lb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        top.addWidget(lb)
        top.addStretch()
        lay.addLayout(top)
        val = QLabel(value)
        val.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        lay.addWidget(val)
        if hint:
            h = QLabel(hint)
            h.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(h)
        return cell

    def _feature_cell(self, name: str) -> QFrame:
        cell = QFrame()
        cell.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(12, 12)
        ic.setPixmap(icon_pixmap("check_circle", size=12, color=T.SUCCESS_FG))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        t = QLabel(name)
        t.setWordWrap(True)
        t.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(t, stretch=1)
        return cell

    def _info_tile(self, label: str, value: str) -> QFrame:
        cell = QFrame()
        cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cell.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QVBoxLayout(cell)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(2)
        lb = QLabel(label)
        lb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(lb)
        val = QLabel(value)
        val.setWordWrap(True)
        val.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        lay.addWidget(val)
        return cell

    def _muted(self, text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        return lb

    def _btn(
        self, label: str, icon: str = "", shortcut: str = "", *,
        kind: str = "secondary", icon_color: str = None, stretch: bool = False,
        on_click=None,
    ) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(T.BUTTON_H)
        if stretch:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if kind == "primary":
            btn.setStyleSheet(
                f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
            )
            fg, ic = "white", "white"
            on_pri = True
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
                f"border-radius: {S.R}px; }}"
                f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
            )
            fg, ic = T.TEXT_PRIMARY, (icon_color or T.TEXT_SECONDARY)
            on_pri = False
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(10, 0, 8, 0)
        lay.setSpacing(6)
        if icon:
            ic_lbl = QLabel()
            ic_lbl.setFixedSize(14, 14)
            ic_lbl.setPixmap(icon_pixmap(icon, size=14, color=ic))
            ic_lbl.setStyleSheet("background: transparent; border: none;")
            lay.addWidget(ic_lbl)
        text = QLabel(label)
        text.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(text)
        if shortcut:
            lay.addWidget(S.kbd(shortcut, on_primary=on_pri))
        if on_click is not None:
            btn.mousePressEvent = (
                lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
            )
        return btn

    # ── actions ──────────────────────────────────────────────
    def _focus_renewal(self):
        self.key_input.setFocus()
        toast(self, "Enter renewal license key.")

    def _revalidate(self):
        toast(self, "Node re-validated — hardware match OK.")

    def _browse_lic(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Browse License File", "", "License Files (*.lic);;All Files (*)",
        )
        if path:
            try:
                text = open(path, encoding="utf-8", errors="ignore").read().strip()
                self.key_input.setText(text[:120] if text else path)
            except OSError:
                self.key_input.setText(path)
            toast(self, "License file loaded.")

    def _apply_key(self):
        key = self.key_input.text().strip()
        if not key or len(key) < 8:
            toast(self, "Enter a valid license key or browse a .lic file.")
            return
        toast(self, "License key applied successfully.")

    def _copy_info(self):
        info = (
            f"{self.lic['entity']}\n"
            f"Key: {self.lic['product_key']}\n"
            f"HW: {self.lic['hw_signature']}\n"
            f"Expires: {self.lic['expires_at']}"
        )
        QApplication.clipboard().setText(info)
        toast(self, "License info copied.")
