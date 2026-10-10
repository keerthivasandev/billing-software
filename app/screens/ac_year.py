"""4.3 / 4.4 A/c Year Management — Stitch pixel-faithful (screen 11775185290169561132)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QRadioButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets import stitch_ui as S
from app.widgets.helpers import toast
from app.widgets.icons import icon_pixmap

# Stitch amber / emerald tokens from screen HTML
_AMBER_50 = "#fffbeb"
_AMBER_100 = "#fef3c7"
_AMBER_200 = "#fde68a"
_AMBER_600 = "#d97706"
_AMBER_700 = "#b45309"
_AMBER_800 = "#92400e"
_AMBER_900 = "#78350f"
_AMBER_950 = "#451a03"
_BLUE_100 = "#dbeafe"
_EMERALD_100 = "#d1fae5"
_EMERALD_200 = "#a7f3d0"
_EMERALD_700 = "#047857"
_EMERALD_800 = "#065f46"


class AccountYearManagementScreen(QWidget):
    """Nav key ``ac_year`` — Stitch 4.3 Change + 4.4 Create & Initialize."""

    def __init__(self, on_fy_change=None, parent=None):
        super().__init__(parent)
        self.on_fy_change = on_fy_change
        self.active = dict(D.AC_YEAR_ACTIVE)
        self.partitions = [dict(p) for p in D.AC_YEAR_PARTITIONS]
        self._selected = 0
        self._row_frames = []
        self._radios = []
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
        root = QVBoxLayout(body)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)  # gap-3
        scroll.setWidget(body)
        outer.addWidget(scroll)

        root.addWidget(self._guard_banner())
        root.addWidget(self._active_card())

        split = QHBoxLayout()
        split.setSpacing(12)
        split.addWidget(self._change_panel(), stretch=1)
        split.addWidget(self._create_panel(), stretch=1)
        root.addLayout(split, stretch=1)
        root.addWidget(self._hotkey_bar())

        QShortcut(QKeySequence("Return"), self, activated=self._switch)
        QShortcut(QKeySequence("Enter"), self, activated=self._switch)
        QShortcut(QKeySequence("F9"), self, activated=self._create)
        QShortcut(QKeySequence("F5"), self, activated=lambda: toast(self, "Year registry refreshed."))
        QShortcut(QKeySequence("Esc"), self, activated=lambda: toast(self, "Return to Dashboard"))

    # ══════════════════════════════════════════════════════════
    # OPERATIONAL GUARD ALERT BANNER
    # ══════════════════════════════════════════════════════════
    def _guard_banner(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {_AMBER_50}; border: 1px solid {_AMBER_200}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(box)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(20, 20)
        ic.setPixmap(icon_pixmap("shield_lock", size=20, color=_AMBER_600))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, 0, Qt.AlignTop)

        mid = QVBoxLayout()
        mid.setSpacing(2)
        mid.setContentsMargins(0, 0, 0, 0)
        pills = QHBoxLayout()
        pills.setSpacing(8)
        pills.addWidget(self._mono_pill("OPERATIONAL GUARD", _AMBER_200, _AMBER_950))
        pills.addWidget(self._mono_pill("STRICT AUDIT ISOLATION", _BLUE_100, S.PRIMARY))
        title = QLabel("Multi-Year Accounting Partition Enforced")
        title.setStyleSheet(
            f"color: {_AMBER_950}; font-size: 11px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        pills.addWidget(title)
        pills.addStretch()
        mid.addLayout(pills)
        body = QLabel(
            "Changing / creating an A/c year strictly filters Purchase, Sales, and Daybook "
            "to the selected year. Prior years stay archived & locked for audit and do not "
            "appear in active entry grids."
        )
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: {_AMBER_900}; font-size: 11px; border: none; background: transparent;"
        )
        mid.addWidget(body)
        lay.addLayout(mid, stretch=1)

        barrier = QFrame()
        barrier.setStyleSheet(
            f"QFrame {{ background: {_AMBER_100}; border: 1px solid {_AMBER_200}; "
            f"border-radius: {S.R}px; }}"
        )
        bl = QHBoxLayout(barrier)
        bl.setContentsMargins(8, 4, 8, 4)
        bl.setSpacing(6)
        bic = QLabel()
        bic.setFixedSize(12, 12)
        bic.setPixmap(icon_pixmap("lock", size=12, color=_AMBER_700))
        bic.setStyleSheet("background: transparent; border: none;")
        bl.addWidget(bic)
        bt = QLabel("Voucher Alteration Barrier Active")
        bt.setStyleSheet(
            f"color: {_AMBER_800}; font-size: 11px; font-weight: 600; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        bl.addWidget(bt)
        lay.addWidget(barrier, 0, Qt.AlignVCenter)
        return box

    def _mono_pill(self, text: str, bg: str, fg: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {fg}; background: {bg}; border: none; border-radius: {S.R}px; "
            f"padding: 1px 6px; font-size: 9px; font-weight: 700; "
            f"font-family: Consolas, monospace; letter-spacing: 0.5px;"
        )
        return lbl

    # ══════════════════════════════════════════════════════════
    # ACTIVE OPERATIONAL YEAR HEADER CARD
    # ══════════════════════════════════════════════════════════
    def _active_card(self) -> QFrame:
        box = S.card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)

        left = QHBoxLayout()
        left.setSpacing(12)

        # 40×40 primary tile: calendar + ACTIVE
        tile = QFrame()
        tile.setFixedSize(40, 40)
        tile.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
        )
        tl = QVBoxLayout(tile)
        tl.setContentsMargins(0, 4, 0, 2)
        tl.setSpacing(0)
        tl.setAlignment(Qt.AlignCenter)
        tic = QLabel()
        tic.setFixedSize(16, 16)
        tic.setAlignment(Qt.AlignCenter)
        tic.setPixmap(icon_pixmap("calendar_month", size=16, color="white"))
        tic.setStyleSheet("background: transparent; border: none;")
        tl.addWidget(tic, 0, Qt.AlignHCenter)
        tact = QLabel("ACTIVE")
        tact.setAlignment(Qt.AlignCenter)
        tact.setStyleSheet(
            "color: white; font-size: 8px; font-weight: 700; "
            "font-family: Consolas, monospace; letter-spacing: 0.4px; "
            "border: none; background: transparent;"
        )
        tl.addWidget(tact)
        left.addWidget(tile)

        meta = QVBoxLayout()
        meta.setSpacing(2)
        meta.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        self.active_title = QLabel()
        self._set_active_title(self.active["code"])
        title_row.addWidget(self.active_title)
        live = QFrame()
        live.setStyleSheet(
            f"QFrame {{ background: {T.SUCCESS_BG}; border: 1px solid {_EMERALD_200}; "
            f"border-radius: {S.R}px; }}"
        )
        ll = QHBoxLayout(live)
        ll.setContentsMargins(8, 2, 8, 2)
        ll.setSpacing(4)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            f"background: {T.SUCCESS}; border: none; border-radius: 3px;"
        )
        ll.addWidget(dot, 0, Qt.AlignVCenter)
        lt = QLabel("Live Session (Read/Write)")
        lt.setStyleSheet(
            f"color: {T.SUCCESS_FG}; font-size: 10px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        ll.addWidget(lt)
        title_row.addWidget(live)
        title_row.addStretch()
        meta.addLayout(title_row)

        self.active_sub = QLabel()
        self._set_active_sub()
        meta.addWidget(self.active_sub)
        left.addLayout(meta)
        lay.addLayout(left, stretch=1)

        # KPI chips
        chips = QHBoxLayout()
        chips.setSpacing(8)
        self.kpi_entries = self._kpi_chip("Current Entries", "1,482 Vouchers", S.PRIMARY)
        self.kpi_db = self._kpi_chip("Database State", "Read/Write (Live)", _EMERALD_700)
        self.kpi_sync = self._kpi_chip("Sync Latency", "0 ms (Instant)", T.TEXT_SECONDARY)
        chips.addWidget(self.kpi_entries)
        chips.addWidget(self.kpi_db)
        chips.addWidget(self.kpi_sync)
        lay.addLayout(chips)
        return box

    def _set_active_title(self, code: str):
        self.active_title.setText(f"Active Operational Year:  {code}")
        self.active_title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 15px; font-weight: 700; "
            f"border: none; background: transparent;"
        )

    def _set_active_sub(self):
        self.active_sub.setText(
            f"Period: {self.active['period']}   ·   Partition: {self.active['partition']}"
        )
        self.active_sub.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )

    def _kpi_chip(self, label: str, value: str, value_color: str) -> QFrame:
        chip = QFrame()
        chip.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        lay = QVBoxLayout(chip)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(1)
        cap = QLabel(label.upper())
        cap.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 9px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        lay.addWidget(cap)
        val = QLabel(value)
        val.setObjectName("kpiVal")
        val.setStyleSheet(
            f"color: {value_color}; font-size: 12px; font-weight: 700; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        lay.addWidget(val)
        chip._val = val
        return chip

    # ══════════════════════════════════════════════════════════
    # LEFT: 4.3 CHANGE ACTIVE ACCOUNTING YEAR
    # ══════════════════════════════════════════════════════════
    def _panel_header(self, icon: str, title: str, badge: str, *, badge_primary=False) -> QFrame:
        """Stitch pb-2 border-b — compact header, no extra spacer line."""
        head = QFrame()
        head.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        head.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        lay = QHBoxLayout(head)
        lay.setContentsMargins(0, 0, 0, 8)  # pb-2
        lay.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap(icon, size=16, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        ttl = QLabel(title)
        ttl.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        lay.addWidget(ttl)
        lay.addStretch(1)
        pill = QLabel(badge)
        if badge_primary:
            pill.setStyleSheet(
                f"color: {S.PRIMARY}; background: {T.PRIMARY_FIXED}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 700; "
                f"font-family: Consolas, monospace;"
            )
        else:
            pill.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 6px; font-size: 10px; font-weight: 600; "
                f"font-family: Consolas, monospace;"
            )
        lay.addWidget(pill)
        return head

    def _change_panel(self) -> QFrame:
        box = S.card()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 12, 12, 12)  # p-3
        lay.setSpacing(10)  # gap-2.5
        lay.setAlignment(Qt.AlignTop)

        # Top content block (no stretch — prevents balloon gaps)
        top = QVBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(10)
        top.setAlignment(Qt.AlignTop)

        top.addWidget(self._panel_header(
            "published_with_changes",
            "4.3 CHANGE ACTIVE ACCOUNTING YEAR",
            "3 Partitions Available",
        ))

        desc = QLabel(
            "Switch working session partition. This reloads your current counter register, "
            "sales ledger, and daily stock tally to the target fiscal period."
        )
        desc.setWordWrap(True)
        desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        desc.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        top.addWidget(desc)

        # Radio table — fixed height rows, no vertical expand
        table = QFrame()
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        table.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        tl = QVBoxLayout(table)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)
        tl.addWidget(self._table_header())
        self._radio_group = QButtonGroup(self)
        self._row_host = QVBoxLayout()
        self._row_host.setContentsMargins(0, 0, 0, 0)
        self._row_host.setSpacing(0)
        for i, p in enumerate(self.partitions):
            row = self._table_row(i, p)
            self._row_host.addWidget(row)
            self._row_frames.append(row)
        tl.addLayout(self._row_host)
        top.addWidget(table)

        # Session metadata
        meta = QFrame()
        meta.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        meta.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        ml = QVBoxLayout(meta)
        ml.setContentsMargins(10, 8, 10, 8)
        ml.setSpacing(4)
        for label, value, color in (
            ("Target Schema Binding:", self.active["schema"], T.TEXT_PRIMARY),
            ("Pending Audit Backups:", "0 (Sync Current)", T.SUCCESS_FG),
            ("Active Workstation:", self.active["terminal"], T.TEXT_PRIMARY),
        ):
            r = QHBoxLayout()
            a = QLabel(label)
            a.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 11px; "
                f"border: none; background: transparent;"
            )
            r.addWidget(a)
            r.addStretch()
            b = QLabel(value)
            b.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: 700; "
                f"font-family: Consolas, monospace; border: none; background: transparent;"
            )
            r.addWidget(b)
            ml.addLayout(r)
        top.addWidget(meta)

        # Partition warning
        note = QFrame()
        note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        note.setStyleSheet(
            f"QFrame {{ background: {_AMBER_50}; border: 1px solid {_AMBER_200}; "
            f"border-radius: {S.R}px; }}"
        )
        nl = QHBoxLayout(note)
        nl.setContentsMargins(10, 8, 10, 8)
        nl.setSpacing(6)
        nic = QLabel()
        nic.setFixedSize(12, 12)
        nic.setPixmap(icon_pixmap("info", size=12, color=_AMBER_700))
        nic.setStyleSheet("background: transparent; border: none;")
        nl.addWidget(nic, 0, Qt.AlignTop)
        ntxt = QLabel(
            "Note: Switching into archived years automatically puts POS billing into "
            "Audit Read-Only Mode. Live billing at counter T-01 is paused until "
            "FY 2026–27 is restored."
        )
        ntxt.setWordWrap(True)
        ntxt.setStyleSheet(
            f"color: {_AMBER_900}; font-size: 11px; border: none; background: transparent;"
        )
        nl.addWidget(ntxt, stretch=1)
        top.addWidget(note)

        lay.addLayout(top)
        lay.addStretch(1)  # only gap sits above footer (justify-between)

        # Actions — pt-2 border-t
        actions_wrap = QFrame()
        actions_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        actions_wrap.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        actions = QHBoxLayout(actions_wrap)
        actions.setContentsMargins(0, 8, 0, 0)
        actions.setSpacing(8)
        actions.addWidget(self._secondary_btn("Re-check Partition", "sync", self._recheck))
        actions.addStretch()
        actions.addWidget(
            self._primary_btn("Switch Active A/c Year", "check_circle", "Enter", self._switch)
        )
        lay.addWidget(actions_wrap)
        return box

    # Column widths — dense like Stitch table (Select w-8)
    _COL_SELECT = 36
    _COL_VOUCHERS = 64
    _COL_ACCESS = 118

    def _table_header(self) -> QFrame:
        hdr = QFrame()
        hdr.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hdr.setStyleSheet(
            f"QFrame {{ background: {T.HEADER_BAND}; border: none; "
            f"border-bottom: 1px solid {T.BORDER}; "
            f"border-top-left-radius: {S.R}px; border-top-right-radius: {S.R}px; }}"
        )
        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(10, 6, 10, 6)  # py-2 px-2.5
        lay.setSpacing(8)
        th = (
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.3px; border: none; background: transparent;"
        )
        sel = QLabel("SELECT")
        sel.setFixedWidth(self._COL_SELECT)
        sel.setAlignment(Qt.AlignCenter)
        sel.setStyleSheet(th)
        lay.addWidget(sel)
        fy = QLabel("FINANCIAL YEAR & STATUS")
        fy.setStyleSheet(th)
        lay.addWidget(fy, 5)
        period = QLabel("FISCAL PERIOD")
        period.setStyleSheet(th)
        lay.addWidget(period, 4)
        vouch = QLabel("VOUCHERS")
        vouch.setFixedWidth(self._COL_VOUCHERS)
        vouch.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vouch.setStyleSheet(th)
        lay.addWidget(vouch)
        access = QLabel("ACCESS")
        access.setFixedWidth(self._COL_ACCESS)
        access.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        access.setStyleSheet(th)
        lay.addWidget(access)
        return hdr

    def _table_row(self, idx: int, p: dict) -> QFrame:
        selected = idx == self._selected
        row = QFrame()
        row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row.setCursor(QCursor(Qt.PointingHandCursor))
        if selected:
            row.setStyleSheet(
                f"QFrame {{ background: {T.ACCENT_SOFT}; border: none; "
                f"border-bottom: 1px solid {T.BORDER}; }}"
            )
        else:
            row.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE}; border: none; "
                f"border-bottom: 1px solid {T.BORDER}; }}"
                f"QFrame:hover {{ background: {T.SURFACE_CONTAINER_LOW}; }}"
            )
        lay = QHBoxLayout(row)
        lay.setContentsMargins(10, 6, 10, 6)  # py-2 compact
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignVCenter)

        # Select
        rb_wrap = QWidget()
        rb_wrap.setFixedWidth(self._COL_SELECT)
        rb_wrap.setStyleSheet("background: transparent;")
        rbl = QHBoxLayout(rb_wrap)
        rbl.setContentsMargins(0, 0, 0, 0)
        rbl.setAlignment(Qt.AlignCenter)
        rb = QRadioButton()
        rb.setChecked(selected)
        rb.setStyleSheet(
            f"""
            QRadioButton {{ background: transparent; border: none; spacing: 0; }}
            QRadioButton::indicator {{
                width: 14px; height: 14px;
                border: 2px solid {S.PRIMARY if selected else T.BORDER_STRONG};
                border-radius: 7px; background: {T.SURFACE};
            }}
            QRadioButton::indicator:checked {{
                background: {S.PRIMARY};
                border: 2px solid {S.PRIMARY};
            }}
            """
        )
        rb.toggled.connect(lambda on, i=idx: on and self._select_year(i))
        self._radio_group.addButton(rb, idx)
        self._radios.append(rb)
        rbl.addWidget(rb, 0, Qt.AlignCenter)
        lay.addWidget(rb_wrap, 0, Qt.AlignVCenter)

        # FY + status + partition
        fy_wrap = QWidget()
        fy_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fy_wrap.setStyleSheet("background: transparent;")
        fyl = QVBoxLayout(fy_wrap)
        fyl.setContentsMargins(0, 0, 0, 0)
        fyl.setSpacing(1)
        top = QHBoxLayout()
        top.setSpacing(6)
        code_color = S.PRIMARY if selected else T.TEXT_PRIMARY
        code = QLabel(p["code"])
        code.setStyleSheet(
            f"color: {code_color}; font-size: 12px; font-weight: 700; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        top.addWidget(code)
        st = QLabel(p["status"].upper())
        if p["status"] == "Current":
            st.setStyleSheet(
                f"color: {T.SUCCESS_FG}; background: {T.SUCCESS_BG}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 5px; font-size: 9px; font-weight: 700;"
            )
        else:
            st.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; background: {T.SURFACE_CONTAINER}; border: none; "
                f"border-radius: {S.R}px; padding: 1px 5px; font-size: 9px; font-weight: 700;"
            )
        top.addWidget(st)
        top.addStretch()
        fyl.addLayout(top)
        part = QLabel(p["partition"])
        part.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        fyl.addWidget(part)
        lay.addWidget(fy_wrap, 5)

        # Period
        period_color = T.TEXT_PRIMARY if selected else T.TEXT_SECONDARY
        period = QLabel(p["period"])
        period.setStyleSheet(
            f"color: {period_color}; font-size: 11px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(period, 4)

        # Vouchers (right)
        vouch = QLabel(f"{p['vouchers']:,}")
        vouch.setFixedWidth(self._COL_VOUCHERS)
        vouch.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vouch.setStyleSheet(
            f"color: {period_color}; font-size: 12px; font-weight: 700; "
            f"font-family: Consolas, monospace; border: none; background: transparent;"
        )
        lay.addWidget(vouch)

        # Access (right)
        access_wrap = QWidget()
        access_wrap.setFixedWidth(self._COL_ACCESS)
        access_wrap.setStyleSheet("background: transparent;")
        al = QHBoxLayout(access_wrap)
        al.setContentsMargins(0, 0, 0, 0)
        al.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if p.get("locked"):
            chip = QFrame()
            chip.setStyleSheet(
                f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: none; "
                f"border-radius: {S.R}px; }}"
            )
            cl = QHBoxLayout(chip)
            cl.setContentsMargins(6, 2, 6, 2)
            cl.setSpacing(3)
            lic = QLabel()
            lic.setFixedSize(11, 11)
            lic.setPixmap(icon_pixmap("lock", size=11, color=T.TEXT_SECONDARY))
            lic.setStyleSheet("background: transparent; border: none;")
            cl.addWidget(lic)
            at = QLabel(p["access"])
            at.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-weight: 600; "
                f"font-family: Consolas, monospace; border: none; background: transparent;"
            )
            cl.addWidget(at)
            al.addWidget(chip)
        else:
            at = QLabel(p["access"])
            at.setStyleSheet(
                f"color: {_EMERALD_800}; background: {_EMERALD_100}; border: none; "
                f"border-radius: {S.R}px; padding: 2px 6px; font-size: 10px; font-weight: 700; "
                f"font-family: Consolas, monospace;"
            )
            al.addWidget(at)
        lay.addWidget(access_wrap)

        row.mousePressEvent = (
            lambda e, i=idx: self._select_year(i) if e.button() == Qt.LeftButton else None
        )
        return row

    def _select_year(self, idx: int):
        if idx < 0 or idx >= len(self.partitions):
            return
        self._selected = idx
        # rebuild table body
        while self._row_host.count():
            item = self._row_host.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._row_frames.clear()
        self._radios.clear()
        # clear old radios from group
        for b in self._radio_group.buttons():
            self._radio_group.removeButton(b)
        for i, p in enumerate(self.partitions):
            row = self._table_row(i, p)
            self._row_host.addWidget(row)
            self._row_frames.append(row)

    # ══════════════════════════════════════════════════════════
    # RIGHT: 4.4 CREATE & INITIALIZE
    # ══════════════════════════════════════════════════════════
    def _create_panel(self) -> QFrame:
        box = S.card()
        outer = QVBoxLayout(box)
        outer.setContentsMargins(12, 12, 12, 12)  # p-3
        outer.setSpacing(10)  # gap-2.5
        outer.setAlignment(Qt.AlignTop)

        # Packed content — Fixed/Maximum height so stretch cannot inflate gaps
        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(10)
        content.setAlignment(Qt.AlignTop)

        content.addWidget(self._panel_header(
            "calendar_add_on",
            "4.4 CREATE & INITIALIZE NEW A/C YEAR",
            "Annual Rollover",
            badge_primary=True,
        ))

        desc = QLabel(
            "Initialize the next financial year partition. Balances, stock quantities, "
            "and ledgers will be verified and transferred seamlessly without mutative downtime."
        )
        desc.setWordWrap(True)
        desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        desc.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        content.addWidget(desc)

        # Section 1 — grey container p-2.5 gap-2
        sec1 = QFrame()
        sec1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sec1.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        s1 = QVBoxLayout(sec1)
        s1.setContentsMargins(10, 10, 10, 10)
        s1.setSpacing(8)
        s1.addWidget(self._sec_label("edit_calendar", "Section 1: New Financial Year Target Definition"))
        g1 = QHBoxLayout()
        g1.setSpacing(8)
        self.fy_code = QLineEdit(D.AC_YEAR_NEW["code"])
        g1.addWidget(self._field("Financial Year Code", self.fy_code, primary=True))
        self.fy_period = QLineEdit(D.AC_YEAR_NEW["period"])
        self.fy_period.setReadOnly(True)
        g1.addWidget(self._field("Effective Period", self.fy_period, readonly=True))
        s1.addLayout(g1)
        g2 = QHBoxLayout()
        g2.setSpacing(8)
        self.sales_prefix = QLineEdit(D.AC_YEAR_NEW["sales_prefix"])
        g2.addWidget(self._field(
            "Sales Inv Series Prefix", self.sales_prefix, hint="Start Sequence: #0001",
        ))
        self.pur_prefix = QLineEdit(D.AC_YEAR_NEW["purchase_prefix"])
        g2.addWidget(self._field(
            "Purchase Voucher Prefix", self.pur_prefix, hint="Start Sequence: #0001",
        ))
        s1.addLayout(g2)
        content.addWidget(sec1)

        # Section 2 — gap-1.5 between rule cards (6px)
        sec2 = QVBoxLayout()
        sec2.setContentsMargins(0, 0, 0, 0)
        sec2.setSpacing(6)
        sec2.addWidget(self._sec_label(
            "fact_check", "Section 2: Carry Forward & Schema Integrity Rules",
        ))
        for title, sub in (
            (
                "Party Ledger Closing Balances",
                "Carry forward Dr/Cr net balances into new opening balance ledgers across 412 wholesale parties",
            ),
            (
                "Product Stock Quantities & Valuation",
                "Compute closing batch inventory across all 3 Godowns as opening stock without altering stock history",
            ),
            (
                "Lock Previous Financial Year (FY 2026–27)",
                "Protect older vouchers against backdated alterations or deletions post rollover",
            ),
        ):
            sec2.addWidget(self._rule_row(title, sub))
        content.addLayout(sec2)

        # Section 3
        sec3 = QFrame()
        sec3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sec3.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        s3 = QVBoxLayout(sec3)
        s3.setContentsMargins(10, 10, 10, 10)
        s3.setSpacing(6)
        s3.addWidget(self._sec_label(
            "admin_panel_settings", "Section 3: Supervisor Authorization Gate (Mandatory)",
        ))
        auth = QHBoxLayout()
        auth.setSpacing(8)
        field = QFrame()
        field.setFixedHeight(28)
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        field.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
        )
        fl = QHBoxLayout(field)
        fl.setContentsMargins(8, 0, 6, 0)
        fl.setSpacing(6)
        fl.setAlignment(Qt.AlignVCenter)
        kic = QLabel()
        kic.setFixedSize(14, 14)
        kic.setPixmap(icon_pixmap("key", size=14, color=T.TEXT_SECONDARY))
        kic.setStyleSheet("background: transparent; border: none;")
        fl.addWidget(kic, 0, Qt.AlignVCenter)
        self.admin_pwd = QLineEdit()
        self.admin_pwd.setEchoMode(QLineEdit.Password)
        self.admin_pwd.setPlaceholderText("Enter Master Admin password to authorize rollover...")
        self.admin_pwd.setFrame(False)
        self.admin_pwd.setFixedHeight(26)
        self.admin_pwd.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.admin_pwd.setStyleSheet(
            f"""
            QLineEdit {{
                background: transparent; border: none; padding: 0px; margin: 0px;
                min-height: 0px; max-height: 26px;
                color: {T.TEXT_PRIMARY}; font-size: 12px;
                font-family: Consolas, monospace;
            }}
            """
        )
        fl.addWidget(self.admin_pwd, stretch=1)
        auth.addWidget(field, stretch=1)
        auth_badge = QLabel("Admin Auth")
        auth_badge.setStyleSheet(
            f"color: {S.PRIMARY}; background: {T.ACCENT_SOFT}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; padding: 4px 8px; font-size: 10px; font-weight: 700; "
            f"font-family: Consolas, monospace;"
        )
        auth.addWidget(auth_badge, 0, Qt.AlignVCenter)
        s3.addLayout(auth)
        content.addWidget(sec3)

        outer.addLayout(content)
        outer.addStretch(1)  # single justify-between spacer before footer

        foot_wrap = QFrame()
        foot_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        foot_wrap.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        foot = QHBoxLayout(foot_wrap)
        foot.setContentsMargins(0, 8, 0, 0)
        foot.setSpacing(8)
        note = QLabel("Note: Creates new ledger schema without mutating current entries.")
        note.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        foot.addWidget(note, stretch=1)
        foot.addWidget(
            self._primary_btn(
                "Create & Initialize FY 2027–28", "add_task", "F9", self._create,
            )
        )
        outer.addWidget(foot_wrap)
        return box

    def _sec_label(self, icon: str, text: str) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        ic = QLabel()
        ic.setFixedSize(12, 12)
        ic.setPixmap(icon_pixmap(icon, size=12, color=S.PRIMARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        lab = QLabel(text.upper() if not text.startswith("Section") else text)
        # Design uses mixed: "Section 1: ..." with uppercase tracking on the span
        lab.setText(text)
        lab.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        lay.addWidget(lab)
        lay.addStretch()
        return wrap

    def _field(
        self, label: str, widget: QLineEdit, *, readonly=False, primary=False, hint="",
    ) -> QWidget:
        box = QWidget()
        box.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        cap = QLabel(label)
        cap.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(cap)
        h = 28
        bg = T.SURFACE_CONTAINER if readonly else T.SURFACE
        fg = S.PRIMARY if primary else (T.TEXT_PRIMARY if not readonly else T.TEXT_PRIMARY)
        weight = "700" if primary else "600"
        widget.setFixedHeight(h)
        widget.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        widget.setStyleSheet(
            f"""
            QLineEdit {{
                background: {bg}; border: 1px solid {T.BORDER}; border-radius: {S.R}px;
                padding: 0 8px; margin: 0px;
                min-height: 0px; max-height: {h}px;
                color: {fg}; font-size: 12px; font-weight: {weight};
                font-family: Consolas, monospace;
            }}
            QLineEdit:focus {{
                border: 1px solid {S.PRIMARY}; background: {T.SURFACE};
            }}
            """
        )
        lay.addWidget(widget)
        if hint:
            ht = QLabel(hint)
            ht.setStyleSheet(
                f"color: {T.TEXT_SECONDARY}; font-size: 9px; font-family: Consolas, monospace; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(ht)
        return box

    def _rule_row(self, title: str, sub: str) -> QFrame:
        cell = QFrame()
        cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cell.setCursor(QCursor(Qt.PointingHandCursor))
        cell.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(8, 8, 8, 8)  # p-2
        lay.setSpacing(8)
        cb = QCheckBox()
        cb.setChecked(True)
        cb.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(cb, 0, Qt.AlignTop)
        col = QVBoxLayout()
        col.setSpacing(2)
        col.setContentsMargins(0, 0, 0, 0)
        t = QLabel(title)
        t.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        col.addWidget(t)
        s = QLabel(sub)
        s.setWordWrap(True)
        s.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 10px; "
            f"border: none; background: transparent;"
        )
        col.addWidget(s)
        lay.addLayout(col, stretch=1)
        # click row toggles checkbox
        cell.mousePressEvent = (
            lambda e, c=cb: c.toggle() if e.button() == Qt.LeftButton else None
        )
        return cell

    # ══════════════════════════════════════════════════════════
    # HOTKEYS + BUTTONS
    # ══════════════════════════════════════════════════════════
    def _secondary_btn(self, label: str, icon: str, on_click) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(32)
        btn.setStyleSheet(
            f"QFrame {{ background: {T.SURFACE_CONTAINER_LOW}; border: 1px solid {T.BORDER}; "
            f"border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.SURFACE_CONTAINER}; }}"
        )
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap(icon, size=14, color=T.TEXT_SECONDARY))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        txt = QLabel(label)
        txt.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(txt)
        btn.mousePressEvent = (
            lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
        )
        return btn

    def _primary_btn(self, label: str, icon: str, shortcut: str, on_click) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(32)
        btn.setStyleSheet(
            f"QFrame {{ background: {S.PRIMARY}; border: none; border-radius: {S.R}px; }}"
            f"QFrame:hover {{ background: {T.ACCENT_HOVER}; }}"
        )
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(14, 0, 12, 0)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(14, 14)
        ic.setPixmap(icon_pixmap(icon, size=14, color="white"))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)
        txt = QLabel(label)
        txt.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        lay.addWidget(txt)
        kbd = QLabel(shortcut)
        kbd.setStyleSheet(
            f"color: white; background: {T.ACCENT_HOVER}; border: none; "
            f"border-radius: 2px; padding: 1px 5px; font-size: 10px; "
            f"font-family: Consolas, monospace; font-weight: 700;"
        )
        lay.addWidget(kbd)
        btn.mousePressEvent = (
            lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
        )
        return btn

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
            ("Enter", "Switch Selected Year"),
            ("F9", "Execute Year Rollover"),
            ("F5", "Refresh Year Registry"),
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
        foot = QLabel("PostgreSQL Enterprise Storage: 3 Partition Schemas Active (82.4 MB)")
        foot.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 11px; font-family: Consolas, monospace; "
            f"border: none; background: transparent;"
        )
        right.addWidget(foot)
        lay.addLayout(right)
        return box

    # ── Actions ──────────────────────────────────────────────
    def _recheck(self):
        toast(self, "Partition checksum verified.")

    def _switch(self):
        p = self.partitions[self._selected]
        year = p["code"]
        D.FINANCIAL_YEAR = year
        self.active["code"] = year
        self.active["period"] = p["period"].replace(" – ", " to ").replace(" –", " to")
        self.active["partition"] = p["partition"]
        self.active["vouchers"] = p["vouchers"]
        self._set_active_title(year)
        self._set_active_sub()
        self.kpi_entries._val.setText(f"{p['vouchers']:,} Vouchers")
        if callable(self.on_fy_change):
            self.on_fy_change(year)
        mode = "Audit Read-Only" if p.get("locked") else "Live"
        toast(self, f"Switched to {year} ({mode}).")

    def _create(self):
        if not self.admin_pwd.text().strip():
            toast(self, "Admin password required to authorize rollover.")
            return
        code = self.fy_code.text().strip() or D.AC_YEAR_NEW["code"]
        toast(self, f"Create & Initialize {code} queued (demo).")
