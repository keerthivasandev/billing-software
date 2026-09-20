"""License Activation dialog — offline RSA + hardware fingerprint stub."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QTextEdit, QVBoxLayout, QApplication,
)

from app.data import sample_data as D
from app.styles import tokens as T
from app.widgets.helpers import field_label, make_button, mono_font


class LicenseActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Activation")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setMinimumHeight(320)
        self._activated = D.LICENSE_STATUS == "Activated"
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("License Activation")
        title.setStyleSheet(f"font-size: {T.FONT_SIZE_TITLE}pt; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "Activate using your offline license key. Machine ID is bound to this PC "
            "(hardware fingerprint)."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {T.TEXT_SECONDARY}; font-size: {T.FONT_SIZE_SHORTCUT}pt;")
        root.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(8)

        machine_row = QHBoxLayout()
        self.machine_id = QLineEdit(D.MACHINE_ID)
        self.machine_id.setReadOnly(True)
        self.machine_id.setFont(mono_font(T.FONT_SIZE_LABEL))
        btn_copy = make_button("Copy")
        btn_copy.setMaximumWidth(80)
        btn_copy.clicked.connect(self._copy_machine_id)
        machine_row.addWidget(self.machine_id)
        machine_row.addWidget(btn_copy)

        self.license_key = QTextEdit()
        self.license_key.setPlaceholderText("Paste license key here…")
        self.license_key.setFixedHeight(80)
        self.license_key.setFont(mono_font(T.FONT_SIZE_SHORTCUT))

        self.status = QLabel(D.LICENSE_STATUS)
        self._update_status_style()

        form.addRow(field_label("Machine ID"), machine_row)
        form.addRow(field_label("License Key"), self.license_key)
        form.addRow(field_label("Status"), self.status)
        root.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch()
        btn_close = make_button("Close", "ghost")
        btn_activate = make_button("Activate", "primary")
        btn_close.clicked.connect(self.reject)
        btn_activate.clicked.connect(self._activate)
        actions.addWidget(btn_close)
        actions.addWidget(btn_activate)
        root.addLayout(actions)

    def _update_status_style(self):
        color = T.SUCCESS if self._activated else T.DANGER
        text = "Activated" if self._activated else "Not Activated"
        self.status.setText(text)
        self.status.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _copy_machine_id(self):
        QApplication.clipboard().setText(self.machine_id.text())
        QMessageBox.information(self, "Copied", "Machine ID copied to clipboard.")

    def _activate(self):
        key = self.license_key.toPlainText().strip()
        if not key or len(key) < 8:
            QMessageBox.warning(self, "Invalid Key", "Enter a valid License Key.")
            return
        # Stub: accept any key >= 8 chars for demo
        self._activated = True
        self._update_status_style()
        QMessageBox.information(self, "Activated", "License activated successfully.")
        self.accept()
