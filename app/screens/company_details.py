"""Master — Company Details."""

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QDateEdit, QFormLayout, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.widgets.helpers import card_frame, field_label, make_button, page_title, toast


class CompanyDetailsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        c = D.COMPANY
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        bar = QHBoxLayout()
        bar.addWidget(page_title("1.1 Company Details"))
        bar.addStretch()
        save = make_button("Save Company", "primary")
        save.clicked.connect(lambda: toast(self, "Company details saved."))
        bar.addWidget(save)
        root.addLayout(bar)

        box = card_frame()
        fl = QFormLayout(box)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(10)
        fl.setLabelAlignment(Qt.AlignRight)

        self.legal = QLineEdit(c["legal_name"])
        self.address = QLineEdit(c["address"])
        self.city = QLineEdit(c["city"])
        self.phone = QLineEdit(c["phone"])
        self.gstin = QLineEdit(c["gstin"])
        self.bank = QLineEdit(c["bank_name"])
        self.ac_no = QLineEdit(c["account_no"])
        self.ifsc = QLineEdit(c["ifsc"])
        self.valid_from = QDateEdit(QDate.fromString(c["valid_from"], "yyyy-MM-dd"))
        self.valid_from.setCalendarPopup(True)
        self.valid_from.setDisplayFormat("dd-MM-yyyy")
        self.valid_to = QDateEdit(QDate.fromString(c["valid_to"], "yyyy-MM-dd"))
        self.valid_to.setCalendarPopup(True)
        self.valid_to.setDisplayFormat("dd-MM-yyyy")

        for label, w in (
            ("Business Legal Name", self.legal),
            ("Address", self.address),
            ("City", self.city),
            ("Phone", self.phone),
            ("GSTIN", self.gstin),
            ("Bank Name", self.bank),
            ("A/c Number", self.ac_no),
            ("IFSC", self.ifsc),
            ("A/c Valid From", self.valid_from),
            ("A/c Valid To", self.valid_to),
        ):
            fl.addRow(field_label(label), w)

        root.addWidget(box)
        root.addStretch()
