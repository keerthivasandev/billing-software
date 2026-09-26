"""Master — Company Details (Stitch V1 Edited layout)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import toast
from app.widgets.icons import icon_pixmap

_PRIMARY = "#2563eb"
_SECONDARY = "#575e70"
_HEADER_GREY = "#f3f4f6"       # surface-container-low
_SURFACE_GREY = "#edeef0"     # surface-container
_INPUT_BG = "#f3f4f6"


def _card() -> QFrame:
    box = QFrame()
    box.setObjectName("cdCard")
    box.setStyleSheet(
        f"QFrame#cdCard {{ background: {T.SURFACE}; border: 1px solid {T.BORDER}; "
        f"border-radius: {T.CARD_RADIUS}px; }}"
    )
    return box


def _kbd(text: str, on_primary: bool = False) -> QLabel:
    chip = QLabel(text)
    chip.setAlignment(Qt.AlignCenter)
    chip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    if on_primary:
        chip.setStyleSheet(
            "background: rgba(255,255,255,0.22); color: white; "
            "border: 1px solid rgba(255,255,255,0.35); border-radius: 3px; "
            f"padding: 1px 5px; font-size: {T.FONT_SIZE_MICRO}pt; font-weight: 700;"
        )
    else:
        chip.setStyleSheet(
            f"background: {T.SURFACE}; color: {_SECONDARY}; "
            f"border: 1px solid {T.BORDER}; border-radius: 3px; "
            f"padding: 1px 5px; font-size: {T.FONT_SIZE_MICRO}pt; font-weight: 700;"
        )
    return chip


def _pill(text: str, kind: str = "neutral") -> QLabel:
    lbl = QLabel(text)
    lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    if kind == "primary":
        lbl.setStyleSheet(
            f"color: {_PRIMARY}; background: {_SURFACE_GREY}; border: none; "
            f"border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
    else:
        lbl.setStyleSheet(
            f"color: {_SECONDARY}; background: {_SURFACE_GREY}; border: none; "
            f"border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 600;"
        )
    return lbl


def _verified_badge(text: str = "Active / Verified") -> QFrame:
    """Blue-dot badge matching Stitch (not a green success chip)."""
    wrap = QFrame()
    wrap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    wrap.setStyleSheet(
        f"QFrame {{ background: {_SURFACE_GREY}; border: none; border-radius: 4px; }}"
    )
    lay = QHBoxLayout(wrap)
    lay.setContentsMargins(6, 2, 6, 2)
    lay.setSpacing(4)
    dot = QFrame()
    dot.setFixedSize(6, 6)
    dot.setStyleSheet(f"background: {_PRIMARY}; border-radius: 3px; border: none;")
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {_SECONDARY}; font-size: 10px; font-weight: 600; "
        f"border: none; background: transparent;"
    )
    lay.addWidget(dot)
    lay.addWidget(lbl)
    return wrap


def _linked_badge() -> QFrame:
    wrap = QFrame()
    wrap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    wrap.setStyleSheet("QFrame { background: transparent; border: none; }")
    lay = QHBoxLayout(wrap)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(3)
    ic = QLabel()
    ic.setFixedSize(12, 12)
    ic.setPixmap(icon_pixmap("chat", size=12, color=_PRIMARY))
    lbl = QLabel("Linked")
    lbl.setStyleSheet(
        f"color: {_PRIMARY}; font-size: 10px; font-weight: 600; "
        f"border: none; background: transparent;"
    )
    lay.addWidget(ic)
    lay.addWidget(lbl)
    return wrap


def _form_field(
    label: str,
    widget: QWidget,
    trailing: QWidget = None,
    required: bool = False,
    bold_value: bool = False,
) -> QWidget:
    """Label above soft-grey input (Stitch field pattern — no outer border card)."""
    wrap = QWidget()
    wrap.setStyleSheet("background: transparent;")
    wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    lay = QVBoxLayout(wrap)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)

    top = QHBoxLayout()
    top.setContentsMargins(0, 0, 0, 0)
    top.setSpacing(4)
    cap = QLabel(label)
    cap.setStyleSheet(
        f"color: {_SECONDARY}; font-size: 11px; font-weight: 600; "
        f"border: none; background: transparent;"
    )
    top.addWidget(cap)
    if required:
        star = QLabel("*")
        star.setStyleSheet(
            "color: #dc2626; font-size: 12px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        top.addWidget(star)
    top.addStretch()
    if trailing is not None:
        top.addWidget(trailing)
    lay.addLayout(top)

    weight = "700" if bold_value else "600"
    size = "14px" if bold_value else "13px"
    widget.setStyleSheet(
        f"""
        QLineEdit, QTextEdit {{
            background: {_INPUT_BG}; border: none; border-radius: 4px;
            padding: 8px 10px; min-height: 20px;
            font-size: {size}; font-weight: {weight}; color: {T.TEXT_PRIMARY};
            selection-background-color: {_PRIMARY}; selection-color: white;
        }}
        """
    )
    lay.addWidget(widget)
    return wrap


class CompanyDetailsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        c = D.COMPANY
        self._editing = False
        self.setObjectName("companyRoot")
        self.setStyleSheet(f"QWidget#companyRoot {{ background: {T.BG_CANVAS}; }}")
        self.setFocusPolicy(Qt.StrongFocus)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {T.BG_CANVAS}; border: none; }}")

        host = QWidget()
        host.setStyleSheet(f"background: {T.BG_CANVAS};")
        body = QVBoxLayout(host)
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(14)

        body.addWidget(self._page_header())
        body.addWidget(self._status_strip())
        body.addWidget(self._identity_section(c))
        body.addWidget(self._address_section(c))
        body.addWidget(self._bank_section(c))
        body.addWidget(self._footer_bar())
        body.addStretch(1)

        scroll.setWidget(host)
        root.addWidget(scroll)

        # Locked until Edit — no focus, no text selection
        self._set_editing(False)
        QShortcut(QKeySequence("F4"), self, activated=self._enter_edit)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save_changes)

    def _fields(self) -> list:
        return [
            self.trade_name, self.entity_type, self.gstin, self.pan,
            self.state_code, self.fy, self.activity,
            self.address, self.landmark, self.city, self.pincode,
            self.contact_person, self.mobile, self.landline, self.email,
            self.bank, self.beneficiary, self.ac_no, self.ac_type,
            self.ifsc, self.branch, self.upi, self.invoice_note,
        ]

    def _set_editing(self, enabled: bool):
        self._editing = enabled
        for w in self._fields():
            w.setReadOnly(not enabled)
            if enabled:
                w.setFocusPolicy(Qt.StrongFocus)
                w.setCursor(QCursor(Qt.IBeamCursor))
                w.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                if isinstance(w, QTextEdit):
                    w.setTextInteractionFlags(
                        Qt.TextEditorInteraction | Qt.TextSelectableByMouse
                    )
            else:
                w.setFocusPolicy(Qt.NoFocus)
                w.setCursor(QCursor(Qt.ArrowCursor))
                w.clearFocus()
                # No caret / text selection until Edit
                w.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                if isinstance(w, QLineEdit):
                    w.deselect()
                    w.setCursorPosition(0)
                else:
                    cursor = w.textCursor()
                    cursor.clearSelection()
                    w.setTextCursor(cursor)
                    w.setTextInteractionFlags(Qt.NoTextInteraction)

        # Visual: view = grey inputs; edit = white + primary ring
        bg = T.SURFACE if enabled else _INPUT_BG
        border = f"1px solid {_PRIMARY}" if enabled else "none"
        for w in self._fields():
            if isinstance(w, QTextEdit):
                w.setStyleSheet(
                    f"""
                    QTextEdit {{
                        background: {bg}; border: {border}; border-radius: 4px;
                        padding: 8px 10px; font-size: 12px; font-weight: 500;
                        color: {T.TEXT_PRIMARY};
                        selection-background-color: {_PRIMARY}; selection-color: white;
                    }}
                    """
                )
            else:
                weight = "700" if w in (self.trade_name, self.ac_no) else "600"
                size = "14px" if w is self.trade_name else "13px"
                w.setStyleSheet(
                    f"""
                    QLineEdit {{
                        background: {bg}; border: {border}; border-radius: 4px;
                        padding: 8px 10px; min-height: 20px;
                        font-size: {size}; font-weight: {weight}; color: {T.TEXT_PRIMARY};
                        selection-background-color: {_PRIMARY}; selection-color: white;
                    }}
                    """
                )

        if hasattr(self, "_edit_btn"):
            if enabled:
                self._edit_btn.setStyleSheet(
                    f"QFrame {{ background: {_SURFACE_GREY}; border: 1px solid {_PRIMARY}; "
                    f"border-radius: 6px; }}"
                )
            else:
                self._edit_btn.setStyleSheet(
                    f"QFrame {{ background: {_HEADER_GREY}; border: none; border-radius: 6px; }}"
                    f"QFrame:hover {{ background: {_SURFACE_GREY}; }}"
                )

    def _enter_edit(self):
        if self._editing:
            return
        self._set_editing(True)
        self.trade_name.setFocus()
        self.trade_name.selectAll()

    def _save_changes(self):
        if not self._editing:
            return
        self._set_editing(False)
        toast(self, "Company details saved.")

    # ── Page header ──────────────────────────────────────────
    def _page_header(self) -> QFrame:
        box = _card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)

        # domain icon in grey square (Stitch)
        ic_wrap = QLabel()
        ic_wrap.setFixedSize(40, 40)
        ic_wrap.setAlignment(Qt.AlignCenter)
        ic_wrap.setStyleSheet(
            f"background: {_SURFACE_GREY}; border-radius: 8px; border: none;"
        )
        ic_wrap.setPixmap(icon_pixmap("domain", size=22, color=_PRIMARY))

        left = QVBoxLayout()
        left.setSpacing(4)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title = QLabel("1. Company Details Master")
        title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        title_row.addWidget(title)
        title_row.addWidget(_pill("Master Record", "neutral"))
        title_row.addStretch()
        sub = QLabel(
            "Business identity, GSTIN, registered address and banking details "
            "for invoice printing and E-Way bills"
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(
            f"color: {_SECONDARY}; font-size: 12px; "
            f"border: none; background: transparent;"
        )
        left.addLayout(title_row)
        left.addWidget(sub)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        self._edit_btn = self._btn(
            "Edit Details", "F4", "edit", "secondary", on_click=self._enter_edit
        )
        actions.addWidget(self._edit_btn)
        actions.addWidget(
            self._btn("Print Profile", "Ctrl+P", "print", "secondary")
        )
        actions.addWidget(
            self._btn(
                "Save Changes", "Ctrl+S", "save", "primary", on_click=self._save_changes
            )
        )

        lay.addWidget(ic_wrap)
        lay.addLayout(left, stretch=1)
        lay.addLayout(actions)
        return box

    def _btn(
        self, label: str, shortcut: str, icon: str, kind: str, on_click=None
    ) -> QFrame:
        btn = QFrame()
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(34)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if kind == "primary":
            btn.setStyleSheet(
                f"QFrame {{ background: {_PRIMARY}; border: none; border-radius: 6px; }}"
                f"QFrame:hover {{ background: #1d4ed8; }}"
            )
            fg = "white"
            ic_color = "white"
        else:
            btn.setStyleSheet(
                f"QFrame {{ background: {_HEADER_GREY}; border: none; border-radius: 6px; }}"
                f"QFrame:hover {{ background: {_SURFACE_GREY}; }}"
            )
            fg = T.TEXT_PRIMARY
            ic_color = T.TEXT_PRIMARY
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setFixedSize(16, 16)
        ic.setPixmap(icon_pixmap(icon, size=16, color=ic_color))
        text = QLabel(label)
        text.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(ic)
        lay.addWidget(text)
        lay.addWidget(_kbd(shortcut, on_primary=(kind == "primary")))
        if on_click is not None:
            btn.mousePressEvent = lambda e, cb=on_click: cb() if e.button() == Qt.LeftButton else None
        return btn

    # ── Status overview ──────────────────────────────────────
    def _status_strip(self) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        grid = QGridLayout(wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        # Icons match Stitch Material Symbols exactly
        items = [
            ("GST Filing Status", D.COMPANY["gst_filing_status"], "verified"),
            ("Current FY Locked", "2026–27 (Active)", "schedule"),
            ("E-Invoice & E-Way Ready", D.COMPANY["einvoice_status"], "qr_code_2"),
            ("Terminal ID", D.COMPANY["terminal_id"], "terminal"),
        ]
        for i, (title, value, icon) in enumerate(items):
            grid.addWidget(self._status_card(title, value, icon), 0, i)
            grid.setColumnStretch(i, 1)
        return wrap

    def _status_card(self, title: str, value: str, icon: str) -> QFrame:
        """Plain icon + text — no colored icon chip (Stitch)."""
        box = _card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setFixedSize(22, 22)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap(icon, size=20, color=_SECONDARY))

        col = QVBoxLayout()
        col.setSpacing(2)
        ttl = QLabel(title.upper())
        ttl.setStyleSheet(
            f"color: {_SECONDARY}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 0.4px; border: none; background: transparent;"
        )
        val = QLabel(value)
        val.setWordWrap(True)
        val.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 12px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        col.addWidget(ttl)
        col.addWidget(val)
        lay.addWidget(ic)
        lay.addLayout(col, stretch=1)
        return box

    # ── Section shell with grey header band ──────────────────
    def _section_shell(
        self, title: str, icon: str, tag: str = None, tag_plain: bool = False
    ) -> tuple[QFrame, QVBoxLayout]:
        box = _card()
        # Outer layout with no padding — header band edge-to-edge
        outer = QVBoxLayout(box)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        head = QFrame()
        head.setObjectName("cdSectionHead")
        head.setStyleSheet(
            f"QFrame#cdSectionHead {{ background: {_HEADER_GREY}; border: none; "
            f"border-top-left-radius: {T.CARD_RADIUS}px; "
            f"border-top-right-radius: {T.CARD_RADIUS}px; }}"
        )
        head_lay = QHBoxLayout(head)
        head_lay.setContentsMargins(14, 10, 14, 10)
        head_lay.setSpacing(8)

        ic = QLabel()
        ic.setFixedSize(22, 22)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setPixmap(icon_pixmap(icon, size=20, color=_PRIMARY))

        ttl = QLabel(title)
        ttl.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {T.TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        head_lay.addWidget(ic)
        head_lay.addWidget(ttl)
        head_lay.addStretch()
        if tag:
            if tag_plain:
                tag_lbl = QLabel(tag)
                tag_lbl.setStyleSheet(
                    f"color: {_SECONDARY}; font-size: 11px; "
                    f"border: none; background: transparent;"
                )
                head_lay.addWidget(tag_lbl)
            else:
                head_lay.addWidget(_pill(tag, "primary" if "Core" in tag else "neutral"))

        outer.addWidget(head)

        body_wrap = QWidget()
        body_wrap.setStyleSheet("background: transparent;")
        body = QVBoxLayout(body_wrap)
        body.setContentsMargins(14, 14, 14, 14)
        body.setSpacing(12)
        outer.addWidget(body_wrap)
        return box, body

    def _row(self, *fields: QWidget) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        for f in fields:
            lay.addWidget(f, stretch=1)
        return wrap

    # ── 1. Identity (full width — no compliance seal) ────────
    def _identity_section(self, c: dict) -> QFrame:
        section, body = self._section_shell(
            "1. Business Identity & Registration",
            "corporate_fare",
            tag="Core Entity",
        )

        self.trade_name = QLineEdit(c.get("trade_name", c["legal_name"]))
        self.entity_type = QLineEdit(c.get("entity_type", "Proprietorship / Partnership Firm"))
        self.gstin = QLineEdit(c["gstin"])
        self.pan = QLineEdit(c.get("pan", ""))
        self.state_code = QLineEdit(c.get("state_code", ""))
        self.fy = QLineEdit(
            c.get("fy_display", f"{c.get('financial_year', D.FINANCIAL_YEAR)}")
        )
        self.activity = QLineEdit(c.get("business_activity", ""))

        body.addWidget(
            self._row(
                _form_field(
                    "Company / Trade Name",
                    self.trade_name,
                    required=True,
                    bold_value=True,
                ),
                _form_field("Legal Entity / Organization Type", self.entity_type),
            )
        )
        body.addWidget(
            self._row(
                _form_field(
                    "GSTIN (15-Digit Identifier)",
                    self.gstin,
                    required=True,
                    trailing=_verified_badge(),
                ),
                _form_field("Permanent Account Number (PAN)", self.pan),
            )
        )
        body.addWidget(
            self._row(
                _form_field("State & Place of Supply Code", self.state_code),
                _form_field(
                    "Operational Financial Year",
                    self.fy,
                    trailing=_pill(
                        c.get("assessment_year", "Assessment Yr 2027–28"), "primary"
                    ),
                ),
            )
        )
        body.addWidget(
            _form_field("Primary Business Activity & Line of Trade", self.activity)
        )
        return section

    # ── 2. Address ───────────────────────────────────────────
    def _address_section(self, c: dict) -> QFrame:
        section, body = self._section_shell(
            "2. Registered Address & Communication Channels",
            "location_on",
            tag="Dispatch Origin (Place of Dispatch)",
            tag_plain=True,
        )
        self.address = QLineEdit(c["address"])
        self.landmark = QLineEdit(c.get("landmark", ""))
        self.city = QLineEdit(c.get("city_display", c.get("district", c["city"])))
        self.pincode = QLineEdit(c.get("pincode", ""))
        self.contact_person = QLineEdit(c.get("contact_person", ""))
        self.mobile = QLineEdit(c.get("mobile", c["phone"]))
        self.landline = QLineEdit(c.get("landline", c["phone"]))
        self.email = QLineEdit(c.get("email", ""))

        body.addWidget(_form_field("Shop / Principal Godown Address", self.address))
        body.addWidget(
            self._row(
                _form_field("Landmark / Sub-Area", self.landmark),
                _form_field("City & Revenue District", self.city),
                _form_field("Postal Code (PIN)", self.pincode),
            )
        )
        body.addWidget(
            self._row(
                _form_field("Primary Contact Person", self.contact_person),
                _form_field(
                    "Mobile & WhatsApp",
                    self.mobile,
                    trailing=_linked_badge(),
                ),
            )
        )
        body.addWidget(
            self._row(
                _form_field("Landline Number", self.landline),
                _form_field("Official Billing / Accounts Email", self.email),
            )
        )
        return section

    # ── 3. Bank ──────────────────────────────────────────────
    def _bank_section(self, c: dict) -> QFrame:
        section, body = self._section_shell(
            "3. Primary Bank Details (Printed on Invoices & Quotations)",
            "account_balance",
            tag="Auto-Embed in Voucher Footer",
        )
        self.bank = QLineEdit(c["bank_name"])
        self.beneficiary = QLineEdit(c.get("beneficiary", c["legal_name"]))
        self.ac_no = QLineEdit(c["account_no"])
        self.ac_type = QLineEdit(c.get("account_type", "Current Account"))
        self.ifsc = QLineEdit(c["ifsc"])
        self.branch = QLineEdit(c.get("branch", ""))
        self.upi = QLineEdit(c.get("upi", ""))
        self.invoice_note = QTextEdit()
        self.invoice_note.setPlainText(c.get("invoice_note", ""))
        self.invoice_note.setFixedHeight(64)

        body.addWidget(
            self._row(
                _form_field("Bank Name", self.bank),
                _form_field("Beneficiary Name", self.beneficiary),
            )
        )
        body.addWidget(
            self._row(
                _form_field("Account Number", self.ac_no, bold_value=True),
                _form_field("Account Type", self.ac_type),
            )
        )
        body.addWidget(
            self._row(
                _form_field("IFSC Code (RTGS / NEFT)", self.ifsc),
                _form_field("Branch Name & Locality", self.branch),
            )
        )
        body.addWidget(
            _form_field(
                "Unified Payments Interface (UPI ID / VPA)",
                self.upi,
                trailing=_pill("Dynamic QR", "neutral"),
            )
        )

        note_top = QHBoxLayout()
        note_top.setContentsMargins(0, 0, 0, 0)
        note_lbl = QLabel("Invoice Note / Standard Terms & Conditions")
        note_lbl.setStyleSheet(
            f"color: {_SECONDARY}; font-size: 11px; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        printed = QLabel("Printed on all Tax Invoices")
        printed.setStyleSheet(
            f"color: {_SECONDARY}; font-size: 10px; "
            f"border: none; background: transparent;"
        )
        note_top.addWidget(note_lbl)
        note_top.addStretch()
        note_top.addWidget(printed)
        self.invoice_note.setStyleSheet(
            f"""
            QTextEdit {{
                background: {_INPUT_BG}; border: none; border-radius: 4px;
                padding: 8px 10px; font-size: 12px; font-weight: 500;
                color: {T.TEXT_PRIMARY};
            }}
            """
        )
        note_wrap = QWidget()
        note_wrap.setStyleSheet("background: transparent;")
        note_lay = QVBoxLayout(note_wrap)
        note_lay.setContentsMargins(0, 0, 0, 0)
        note_lay.setSpacing(4)
        note_lay.addLayout(note_top)
        note_lay.addWidget(self.invoice_note)
        body.addWidget(note_wrap)
        return section

    # ── Footer ───────────────────────────────────────────────
    def _footer_bar(self) -> QFrame:
        box = _card()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(10)

        title = QLabel("Keyboard Shortcuts:")
        title.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 10px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(title)
        for key, label in (
            ("F4", "Edit"),
            ("Ctrl+S", "Save"),
            ("Ctrl+P", "Print Voucher Profile"),
            ("Esc", "Back to Dashboard"),
        ):
            lay.addWidget(_kbd(key))
            text = QLabel(label)
            text.setStyleSheet(
                f"color: {_SECONDARY}; font-size: 10px; "
                f"border: none; background: transparent;"
            )
            lay.addWidget(text)
            lay.addSpacing(6)

        lay.addStretch()
        # Stitch uses primary blue pulse (not green)
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {_PRIMARY}; border-radius: 4px; border: none;")
        status_k = QLabel("System Status:")
        status_k.setStyleSheet(
            f"color: {T.TEXT_PRIMARY}; font-size: 10px; font-weight: 700; "
            f"border: none; background: transparent;"
        )
        status = QLabel("Database Synced (Terminal-01 Local Engine)")
        status.setStyleSheet(
            f"color: {_SECONDARY}; font-size: 10px; "
            f"border: none; background: transparent;"
        )
        lay.addWidget(dot)
        lay.addWidget(status_k)
        lay.addWidget(status)
        return box
