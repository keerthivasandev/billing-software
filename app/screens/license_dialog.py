"""License Activation Dialog (First-Time Setup) — Stitch 65c6e8cb6fdb45fbb6eddafb6b1fd7c8."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import toast
from app.widgets.icons import icon_pixmap

_BACKDROP = "rgba(15, 23, 42, 0.55)"
_CARD_R = 12  # Stitch rounded-xl
_MAX_CHARS = 256
_MACHINE_ID = "SLE-WIN11-HYD01-984F-A41C-2026"
_TERMINAL = "POS-HYD-01"


class LicenseActivationDialog(QDialog):
    """Blocking first-time offline license activation gate."""

    CARD_W = 530

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Software License Activation")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")
        self._activated = D.LICENSE_STATUS == "Activated"
        self._drag_pos = None
        self._build()

        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._copy_machine_id)
        QShortcut(QKeySequence("F3"), self, activated=self._browse_lic)
        QShortcut(QKeySequence("F9"), self, activated=self._activate)
        QShortcut(QKeySequence("Return"), self, activated=self._activate)
        QShortcut(QKeySequence("Enter"), self, activated=self._activate)
        QShortcut(QKeySequence("Alt+F4"), self, activated=self.reject)
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

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        backdrop = QFrame()
        backdrop.setObjectName("licBackdrop")
        backdrop.setStyleSheet(
            f"QFrame#licBackdrop {{ background: {_BACKDROP}; border: none; }}"
        )
        shell = QVBoxLayout(backdrop)
        shell.setContentsMargins(24, 24, 24, 24)
        shell.setAlignment(Qt.AlignCenter)

        self._card = QFrame()
        self._card.setObjectName("licCard")
        self._card.setFixedWidth(self.CARD_W)
        self._card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        self._card.setStyleSheet(
            f"QFrame#licCard {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {_CARD_R}px; }}"
        )
        card = QVBoxLayout(self._card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)

        card.addWidget(self._title_bar())
        body = QVBoxLayout()
        body.setContentsMargins(20, 20, 20, 20)  # p-5
        body.setSpacing(16)  # gap-4
        body.addWidget(self._brand_header())
        body.addWidget(self._step1())
        body.addWidget(self._step2())
        body.addWidget(self._status_bar())
        body.addWidget(self._footer())
        card.addLayout(body)

        shell.addWidget(self._card, 0, Qt.AlignCenter)
        root.addWidget(backdrop)

    # ── Title bar ────────────────────────────────────────────
    def _title_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(40)
        bar.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_HIGH}; border: none; "
            f"border-top-left-radius: {_CARD_R}px; border-top-right-radius: {_CARD_R}px; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 10, 0)
        lay.setSpacing(8)

        left = QHBoxLayout()
        left.setSpacing(8)
        ic = QLabel()
        ic.setFixedSize(18, 18)
        ic.setPixmap(icon_pixmap("admin_panel_settings", size=18, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        left.addWidget(ic)
        title = QLabel("Sri Lakshmi Electricals — Software License Activation")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        left.addWidget(title)
        lay.addLayout(left, stretch=1)

        for icon, enabled, handler in (
            ("remove", False, None),
            ("check_box_outline_blank", False, None),
            ("close", True, self.reject),
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
                    "QFrame { background: transparent; border: none; }"
                )
            bl = QHBoxLayout(btn)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setAlignment(Qt.AlignCenter)
            bic = QLabel()
            bic.setFixedSize(16, 16)
            color = T.TEXT_SECONDARY if enabled else "#94a3b8"
            bic.setPixmap(icon_pixmap(icon, size=16, color=color))
            bic.setStyleSheet("background: transparent; border: none;")
            bic.setObjectName("winBtnIcon")
            bl.addWidget(bic)
            if enabled and handler:
                def _hover_enter(e, b=btn, i=bic, n=icon):
                    i.setPixmap(icon_pixmap(n, size=16, color="#ffffff"))

                def _hover_leave(e, b=btn, i=bic, n=icon):
                    i.setPixmap(icon_pixmap(n, size=16, color=T.TEXT_SECONDARY))

                btn.enterEvent = _hover_enter
                btn.leaveEvent = _hover_leave
                btn.mousePressEvent = (
                    lambda e, cb=handler: cb() if e.button() == Qt.LeftButton else None
                )
            lay.addWidget(btn)

        # drag support on title bar
        bar.mousePressEvent = self._title_press
        bar.mouseMoveEvent = self._title_move
        return bar

    def _title_press(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self._card.mapToGlobal(
                self._card.rect().topLeft()
            )

    def _title_move(self, e):
        if e.buttons() & Qt.LeftButton and self._drag_pos is not None:
            # card is centered in fullscreen dialog — skip free drag for gate
            pass

    # ── Brand header ─────────────────────────────────────────
    def _brand_header(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 8)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignHCenter)

        logo = QFrame()
        logo.setFixedSize(56, 56)
        logo.setStyleSheet(
            f"QFrame {{ background: {T.PRIMARY_CONTAINER}; border: none; "
            f"border-radius: {_CARD_R}px; }}"
        )
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setAlignment(Qt.AlignCenter)
        bolt = QLabel()
        bolt.setFixedSize(32, 32)
        bolt.setPixmap(icon_pixmap("electric_bolt", size=32, color="#ffffff"))
        bolt.setStyleSheet("background: transparent; border: none;")
        ll.addWidget(bolt)
        lay.addWidget(logo, 0, Qt.AlignHCenter)

        company = QLabel("Sri Lakshmi Electricals")
        company.setAlignment(Qt.AlignCenter)
        company.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; "
            f"border: none; background: transparent; margin-top: 8px;"
        )
        lay.addWidget(company)

        edition = QLabel("Wholesale Billing & ERP System v4.8.2")
        edition.setAlignment(Qt.AlignCenter)
        edition.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(edition)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setAlignment(Qt.AlignCenter)
        h2 = QLabel("Activate License")
        h2.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 14px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(h2)
        badge = QFrame()
        badge.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: {S.R}px; }}"
        )
        bl = QHBoxLayout(badge)
        bl.setContentsMargins(8, 2, 8, 2)
        bl.setSpacing(4)
        bic = QLabel()
        bic.setFixedSize(13, 13)
        bic.setPixmap(icon_pixmap("verified_user", size=13, color=S.PRIMARY))
        bic.setStyleSheet("background: transparent; border: none;")
        bl.addWidget(bic)
        bt = QLabel("Offline — No Internet Required")
        bt.setStyleSheet(
            f"color: {S.PRIMARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bl.addWidget(bt)
        title_row.addWidget(badge)
        lay.addSpacing(10)
        lay.addLayout(title_row)

        desc = QLabel(
            "This terminal requires an offline machine-bound commercial activation key "
            "before its initial wholesale registry launch."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setMaximumWidth(420)
        desc.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent; margin-top: 4px;"
        )
        lay.addWidget(desc, 0, Qt.AlignHCenter)
        return wrap

    # ── Step 1 ───────────────────────────────────────────────
    def _step1(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.CR}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 14, 14, 14)  # p-3.5
        lay.setSpacing(8)

        head = QHBoxLayout()
        head.addWidget(self._step_label(1, "Copy Machine Hardware ID"))
        head.addStretch()
        term = QLabel(f"Terminal: {_TERMINAL}")
        term.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        head.addWidget(term)
        lay.addLayout(head)

        hint = QLabel(
            "Share this unique hardware fingerprint with Sri Lakshmi Support "
            "or your regional ERP distributor."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(hint)

        row = QHBoxLayout()
        row.setSpacing(8)
        field = QFrame()
        field.setFixedHeight(32)
        field.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        fl = QHBoxLayout(field)
        fl.setContentsMargins(10, 0, 8, 0)
        fl.setSpacing(6)
        fic = QLabel()
        fic.setFixedSize(16, 16)
        fic.setPixmap(icon_pixmap("fingerprint", size=16, color=T.TEXT_SECONDARY))
        fic.setStyleSheet("background: transparent; border: none;")
        fl.addWidget(fic)
        self.machine_id = QLineEdit(_MACHINE_ID)
        self.machine_id.setReadOnly(True)
        self.machine_id.setFrame(False)
        self.machine_id.setFixedHeight(28)
        self.machine_id.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; padding: 0px;
                color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600;
                font-family: Consolas, monospace;
            }}
            """
        )
        fl.addWidget(self.machine_id, stretch=1)
        row.addWidget(field, stretch=1)

        copy_btn = self._chip_btn(
            "Copy ID", "content_copy", "Ctrl+C", on_click=self._copy_machine_id,
            icon_primary=True,
        )
        row.addWidget(copy_btn)
        lay.addLayout(row)
        return box

    # ── Step 2 ───────────────────────────────────────────────
    def _step2(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: none; "
            f"border-radius: {S.CR}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)

        head = QHBoxLayout()
        head.addWidget(self._step_label(2, "Load or Paste License Credentials"))
        head.addStretch()
        enc = QLabel("Encrypted Payload")
        enc.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        head.addWidget(enc)
        lay.addLayout(head)

        browse = QFrame()
        browse.setCursor(QCursor(Qt.PointingHandCursor))
        browse.setFixedHeight(36)
        browse.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        bl = QHBoxLayout(browse)
        bl.setContentsMargins(12, 0, 12, 0)
        bl.setSpacing(8)
        bl.setAlignment(Qt.AlignCenter)
        bic = QLabel()
        bic.setFixedSize(18, 18)
        bic.setPixmap(icon_pixmap("drive_folder_upload", size=18, color=S.PRIMARY))
        bic.setStyleSheet("background: transparent; border: none;")
        bl.addWidget(bic)
        bt = QLabel("Browse .lic File…")
        bt.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        bl.addWidget(bt)
        bl.addWidget(S.kbd("F3"))
        browse.mousePressEvent = (
            lambda e: self._browse_lic() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(browse)

        # OR divider
        div = QHBoxLayout()
        div.setSpacing(8)
        line_l = QFrame()
        line_l.setFixedHeight(1)
        line_l.setStyleSheet(f"background: {T.BORDER_STRONG}; border: none;")
        div.addWidget(line_l, stretch=1)
        or_lbl = QLabel("OR PASTE CRYPTOGRAPHIC PAYLOAD")
        or_lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-weight: 600; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        div.addWidget(or_lbl)
        line_r = QFrame()
        line_r.setFixedHeight(1)
        line_r.setStyleSheet(f"background: {T.BORDER_STRONG}; border: none;")
        div.addWidget(line_r, stretch=1)
        lay.addLayout(div)

        self.license_key = QTextEdit()
        self.license_key.setPlaceholderText(
            "Paste encrypted key string (e.g. SLE26-WHLS8-9421A-BK77X-0989Z) "
            "or raw cryptographic .lic payload here..."
        )
        self.license_key.setFixedHeight(72)
        self.license_key.setStyleSheet(
            f"""
            QTextEdit {{
                background: {T.SURFACE}; border: 1px solid {T.BORDER};
                border-radius: {S.R}px; padding: 8px;
                color: {T.TEXT_PRIMARY}; font-size: 11px;
                font-family: Consolas, monospace;
            }}
            QTextEdit:focus {{ border: 1px solid {S.PRIMARY}; }}
            """
        )
        self.license_key.textChanged.connect(self._on_key_changed)
        lay.addWidget(self.license_key)

        meta = QHBoxLayout()
        self.validation_hint = QLabel("Awaiting 64-char signature")
        self.validation_hint.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        meta.addWidget(self.validation_hint)
        meta.addStretch()
        self.char_counter = QLabel(f"0 / {_MAX_CHARS} chars")
        self.char_counter.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        meta.addWidget(self.char_counter)
        lay.addLayout(meta)
        return box

    # ── Status strip ─────────────────────────────────────────
    def _status_bar(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
            f"border-radius: {S.CR}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(6)

        top = QHBoxLayout()
        left = QHBoxLayout()
        left.setSpacing(8)
        self._state_dot = QLabel()
        self._state_dot.setFixedSize(10, 10)
        self._state_dot.setStyleSheet(
            f"background: {T.DANGER}; border: none; border-radius: 5px;"
        )
        left.addWidget(self._state_dot)
        st_lbl = QLabel("Activation State:")
        st_lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        left.addWidget(st_lbl)
        self.status_pill = QLabel("Not Activated")
        self.status_pill.setStyleSheet(
            f"color: {T.DANGER_FG}; background: {T.DANGER_BG}; border: none; "
            f"border-radius: {S.R}px; padding: 2px 8px; font-size: 11px; font-weight: 600;"
        )
        left.addWidget(self.status_pill)
        top.addLayout(left)
        top.addStretch()
        self.lock_lbl = QLabel("Hardware Lock: Unmatched")
        self.lock_lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        top.addWidget(self.lock_lbl)
        lay.addLayout(top)

        bot = QHBoxLayout()
        phone = QHBoxLayout()
        phone.setSpacing(4)
        pic = QLabel()
        pic.setFixedSize(13, 13)
        pic.setPixmap(icon_pixmap("phone_in_talk", size=13, color=T.TEXT_SECONDARY))
        pic.setStyleSheet("background: transparent; border: none;")
        phone.addWidget(pic)
        pt = QLabel("Distributor Helpline: +91 98480 23411")
        pt.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        phone.addWidget(pt)
        bot.addLayout(phone)
        bot.addStretch()
        hours = QLabel("09:00 - 20:00 IST")
        hours.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
            f"border: none; background: transparent;"
        )
        bot.addWidget(hours)
        lay.addLayout(bot)

        if self._activated:
            self._set_activated_ui()
        return box

    # ── Footer ───────────────────────────────────────────────
    def _footer(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(8)

        exit_btn = QFrame()
        exit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        exit_btn.setFixedHeight(36)
        exit_btn.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_HIGH}; border: none; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.BORDER_STRONG}; }}"
        )
        el = QHBoxLayout(exit_btn)
        el.setContentsMargins(16, 0, 12, 0)
        el.setSpacing(8)
        et = QLabel("Exit App")
        et.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        el.addWidget(et)
        el.addWidget(S.kbd("Alt+F4"))
        exit_btn.mousePressEvent = (
            lambda e: self.reject() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(exit_btn)
        lay.addStretch()

        act = QFrame()
        act.setCursor(QCursor(Qt.PointingHandCursor))
        act.setFixedHeight(36)
        act.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        al = QHBoxLayout(act)
        al.setContentsMargins(20, 0, 14, 0)
        al.setSpacing(8)
        aic = QLabel()
        aic.setFixedSize(18, 18)
        aic.setPixmap(icon_pixmap("verified", size=18, color="#ffffff"))
        aic.setStyleSheet("background: transparent; border: none;")
        al.addWidget(aic)
        at = QLabel("Activate License")
        at.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 600; "
            "border: none; background: transparent;"
        )
        al.addWidget(at)
        al.addWidget(S.kbd("F9 / Enter", on_primary=True))
        act.mousePressEvent = (
            lambda e: self._activate() if e.button() == Qt.LeftButton else None
        )
        lay.addWidget(act)
        return wrap

    # ── helpers ──────────────────────────────────────────────
    def _step_label(self, n: int, text: str) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        badge = QLabel(str(n))
        badge.setFixedSize(16, 16)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"color: white; background: {S.PRIMARY}; border: none; "
            f"border-radius: 8px; font-size: 10px; font-weight: 700;"
        )
        lay.addWidget(badge)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(lbl)
        return wrap

    def _chip_btn(
        self, label: str, icon: str, shortcut: str, *, on_click=None, icon_primary=False,
    ) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(32)
        btn.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap(
            icon, size=16, color=S.PRIMARY if icon_primary else T.TEXT_SECONDARY,
        ))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        t = QLabel(label)
        t.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(t)
        lay.addWidget(S.kbd(shortcut))
        if on_click:
            btn.mousePressEvent = (
                lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
            )
        return btn

    def _on_key_changed(self):
        text = self.license_key.toPlainText()
        if len(text) > _MAX_CHARS:
            self.license_key.blockSignals(True)
            self.license_key.setPlainText(text[:_MAX_CHARS])
            cursor = self.license_key.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.license_key.setTextCursor(cursor)
            self.license_key.blockSignals(False)
            text = text[:_MAX_CHARS]
        n = len(text.strip())
        self.char_counter.setText(f"{n} / {_MAX_CHARS} chars")
        if n == 0:
            self.validation_hint.setText("Awaiting 64-char signature")
        elif n < 8:
            self.validation_hint.setText("Payload too short")
        else:
            self.validation_hint.setText("Payload ready for validation")

    def _set_activated_ui(self):
        self._state_dot.setStyleSheet(
            f"background: {T.SUCCESS}; border: none; border-radius: 5px;"
        )
        self.status_pill.setText("Activated")
        self.status_pill.setStyleSheet(
            f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: none; "
            f"border-radius: {S.R}px; padding: 2px 8px; font-size: 11px; font-weight: 600;"
        )
        self.lock_lbl.setText("Hardware Lock: Matched")

    def _copy_machine_id(self):
        QApplication.clipboard().setText(self.machine_id.text())
        toast(self, "Machine ID copied to clipboard")

    def _browse_lic(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Browse License File", "",
            "License Files (*.lic *.key);;All Files (*)",
        )
        if not path:
            return
        try:
            text = open(path, encoding="utf-8", errors="ignore").read().strip()
            self.license_key.setPlainText(text[:_MAX_CHARS])
        except OSError:
            self.license_key.setPlainText(path[:_MAX_CHARS])
        toast(self, "License file loaded")

    def _activate(self):
        key = self.license_key.toPlainText().strip()
        if not key or len(key) < 8:
            toast(self, "Enter a valid license key or browse a .lic file.")
            return
        toast(self, "Validating Hardware Lock...")
        self._activated = True
        D.LICENSE_STATUS = "Activated"
        self._set_activated_ui()
        toast(self, "License activated successfully.")
        self.accept()
