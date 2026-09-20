"""Master — Company Details."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit, QFrame, QHBoxLayout, QLineEdit, QScrollArea, QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.widgets.fields import field_row, icon_field, section_card
from app.widgets.helpers import make_button, page_title, toast


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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body_host = QWidget()
        body = QVBoxLayout(body_host)
        body.setContentsMargins(0, 0, 4, 0)
        body.setSpacing(12)

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

        # Company Information
        info, info_body = section_card("Company Information", "building")
        info_body.addWidget(
            icon_field("Business Legal Name", self.legal, icon="building", show_edit=True)
        )
        info_body.addWidget(icon_field("GSTIN", self.gstin, icon="file-text"))
        body.addWidget(info)

        # Contact & Address
        contact, contact_body = section_card("Contact & Address", "map-pin")
        contact_body.addWidget(
            field_row(
                icon_field("Phone", self.phone, icon="phone"),
                icon_field("Address", self.address, icon="map-pin"),
            )
        )
        contact_body.addWidget(icon_field("City", self.city, icon="home"))
        body.addWidget(contact)

        # Bank Details
        bank, bank_body = section_card("Bank Details", "wallet")
        bank_body.addWidget(
            field_row(
                icon_field("Bank Name", self.bank, icon="wallet"),
                icon_field("A/c Number", self.ac_no, icon="file-text"),
            )
        )
        bank_body.addWidget(
            field_row(
                icon_field("IFSC", self.ifsc, icon="safety"),
                icon_field("A/c Valid From", self.valid_from, icon="calendar"),
            )
        )
        bank_body.addWidget(icon_field("A/c Valid To", self.valid_to, icon="calendar"))
        body.addWidget(bank)

        body.addStretch()
        scroll.setWidget(body_host)
        root.addWidget(scroll, stretch=1)
