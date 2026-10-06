"""Icon-field cards — attractive labeled inputs matching ERP palette."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

from app.styles import tokens as T
from app.widgets.icons import combo_dropdown_qss, icon_pixmap

# Darker than TEXT_SECONDARY — gray icons look washed-out at small sizes.
_FIELD_ICON_COLOR = "#374151"
_FIELD_ICON_PX = 22
_SECTION_ICON_PX = 18
_SECTION_ICON_COLOR = T.TEXT_PRIMARY


def _strip_control_chrome(widget: QWidget):
    """Make nested inputs look like bold values inside the field card."""
    widget.setStyleSheet(
        f"""
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
            min-height: 22px;
            max-height: 28px;
            font-size: {T.FONT_SIZE_UI}pt;
            font-weight: 600;
            color: {T.TEXT_PRIMARY};
            selection-background-color: {T.ACCENT};
            selection-color: white;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
        QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {{
            border: none;
            background: transparent;
        }}
        {combo_dropdown_qss(width=20, background="transparent", border_left=f"1px solid {T.BORDER}")}
        QComboBox, QDateEdit {{
            padding-right: 24px;
        }}
        QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
            border: none;
            border-left: 1px solid {T.BORDER};
            width: 18px;
            background: transparent;
        }}
        """
    )


class IconField(QFrame):
    """
    Rounded field card: [icon | label / value]  (+ optional Edit).

    Keeps existing app colors; wraps any input widget as the value row.
    """

    edit_clicked = Signal()

    def __init__(
        self,
        label: str,
        widget: QWidget,
        icon: str = "file-text",
        show_edit: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("iconField")
        self.widget = widget
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            f"""
            QFrame#iconField {{
                background: {T.INPUT_BG};
                border: 1px solid {T.BORDER};
                border-radius: {T.RADIUS}px;
            }}
            QFrame#iconField:hover {{
                border-color: {T.PRIMARY};
                background: {T.SURFACE};
            }}
            QLabel#iconFieldLabel {{
                color: {T.TEXT_SECONDARY};
                font-size: {T.FONT_SIZE_LABEL}pt;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
            QLabel#iconFieldGlyph {{
                background: transparent;
                border: none;
            }}
            QFrame#iconFieldDivider {{
                background: {T.BORDER_STRONG};
                border: none;
                max-width: 1px;
                min-width: 1px;
            }}
            QPushButton#iconFieldEdit {{
                background: {T.BORDER};
                color: {T.TEXT_PRIMARY};
                border: 1px solid {T.BORDER_STRONG};
                border-radius: {T.RADIUS}px;
                padding: 2px 10px;
                min-height: 22px;
                max-height: 24px;
                font-size: {T.FONT_SIZE_LABEL}pt;
                font-weight: 600;
            }}
            QPushButton#iconFieldEdit:hover {{
                background: {T.ACCENT_SOFT};
                border-color: {T.PRIMARY};
                color: {T.PRIMARY};
            }}
            """
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(10)

        glyph = QLabel()
        glyph.setObjectName("iconFieldGlyph")
        glyph.setFixedSize(_FIELD_ICON_PX + 2, _FIELD_ICON_PX + 2)
        glyph.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        glyph.setAutoFillBackground(False)
        glyph.setStyleSheet("background: transparent; border: none;")
        glyph.setPixmap(
            icon_pixmap(icon, size=_FIELD_ICON_PX, color=_FIELD_ICON_COLOR)
        )
        glyph.setAlignment(Qt.AlignCenter)
        row.addWidget(glyph, 0, Qt.AlignVCenter)

        divider = QFrame()
        divider.setObjectName("iconFieldDivider")
        divider.setFrameShape(QFrame.NoFrame)
        divider.setFixedWidth(1)
        divider.setMinimumHeight(28)
        row.addWidget(divider)

        stack = QVBoxLayout()
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(1)
        caption = QLabel(label)
        caption.setObjectName("iconFieldLabel")
        stack.addWidget(caption)
        _strip_control_chrome(widget)
        stack.addWidget(widget)
        row.addLayout(stack, stretch=1)

        if show_edit:
            btn = QPushButton("Edit")
            btn.setObjectName("iconFieldEdit")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(self._on_edit)
            row.addWidget(btn, 0, Qt.AlignVCenter)

    def _on_edit(self):
        self.widget.setFocus()
        if hasattr(self.widget, "selectAll"):
            try:
                self.widget.selectAll()
            except Exception:
                pass
        self.edit_clicked.emit()


def icon_field(
    label: str,
    widget: QWidget,
    icon: str = "file-text",
    show_edit: bool = False,
) -> IconField:
    return IconField(label, widget, icon=icon, show_edit=show_edit)


def section_card(title: str, icon: str = "file-text") -> tuple[QFrame, QVBoxLayout]:
    """Outer section with icon + title header; returns (frame, body_layout)."""
    box = QFrame()
    box.setObjectName("sectionCard")
    box.setStyleSheet(
        f"""
        QFrame#sectionCard {{
            background: {T.SURFACE};
            border: 1px solid {T.BORDER};
            border-radius: {T.CARD_RADIUS}px;
        }}
        QLabel#sectionCardTitle {{
            font-size: {T.FONT_SIZE_UI}pt;
            font-weight: bold;
            color: {T.TEXT_PRIMARY};
            background: transparent;
            border: none;
        }}
        QLabel#sectionCardIcon {{
            background: transparent;
            border: none;
        }}
        """
    )
    outer = QVBoxLayout(box)
    outer.setContentsMargins(14, 12, 14, 14)
    outer.setSpacing(10)

    header = QHBoxLayout()
    header.setSpacing(8)
    ic = QLabel()
    ic.setObjectName("sectionCardIcon")
    ic.setFixedSize(_SECTION_ICON_PX + 2, _SECTION_ICON_PX + 2)
    ic.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    ic.setAutoFillBackground(False)
    ic.setStyleSheet("background: transparent; border: none;")
    ic.setPixmap(
        icon_pixmap(icon, size=_SECTION_ICON_PX, color=_SECTION_ICON_COLOR)
    )
    title_lbl = QLabel(title)
    title_lbl.setObjectName("sectionCardTitle")
    header.addWidget(ic)
    header.addWidget(title_lbl)
    header.addStretch()
    outer.addLayout(header)

    body = QVBoxLayout()
    body.setContentsMargins(0, 0, 0, 0)
    body.setSpacing(8)
    outer.addLayout(body)
    return box, body


def field_row(*fields: QWidget) -> QWidget:
    """Place icon fields side-by-side."""
    wrap = QWidget()
    lay = QHBoxLayout(wrap)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)
    for f in fields:
        lay.addWidget(f, stretch=1)
    return wrap
