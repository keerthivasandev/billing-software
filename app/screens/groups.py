"""Master — Group Classifications (Product / Ledger / Godown)."""

from PyQt5.QtWidgets import (
    QHBoxLayout, QInputDialog, QListWidget, QListWidgetItem, QTabWidget,
    QVBoxLayout, QWidget,
)

from app.data import sample_data as D
from app.widgets.helpers import card_frame, make_button, page_title, toast


class GroupsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        root.addWidget(page_title("1.3 Group Classifications"))

        self.tabs = QTabWidget()
        self.product_list = self._group_tab(list(D.ITEM_GROUPS), "Product Groups")
        self.ledger_list = self._group_tab(list(D.LEDGER_GROUPS), "Ledger Groups")
        self.godown_list = self._group_tab(list(D.GODOWN_GROUPS), "Godown Groups")
        self.tabs.addTab(self.product_list, "Product Groups")
        self.tabs.addTab(self.ledger_list, "Ledger Groups")
        self.tabs.addTab(self.godown_list, "Godown Groups")
        root.addWidget(self.tabs, stretch=1)

    def _group_tab(self, items, title: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        box = card_frame()
        bl = QVBoxLayout(box)
        lst = QListWidget()
        for name in items:
            lst.addItem(QListWidgetItem(name))
        bl.addWidget(lst)
        bar = QHBoxLayout()
        add = make_button("Add Group", "primary")
        rem = make_button("Remove", "destructive")

        def _add():
            text, ok = QInputDialog.getText(self, title, "Group name:")
            if ok and text.strip():
                lst.addItem(text.strip())
                toast(self, f"Added group: {text.strip()}")

        def _rem():
            row = lst.currentRow()
            if row >= 0:
                item = lst.takeItem(row)
                toast(self, f"Removed: {item.text()}")

        add.clicked.connect(_add)
        rem.clicked.connect(_rem)
        bar.addWidget(add)
        bar.addWidget(rem)
        bar.addStretch()
        bl.addLayout(bar)
        lay.addWidget(box)
        return w
