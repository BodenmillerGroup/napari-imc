from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QTableView, QWidget
from typing import Optional


class ChannelTableView(QTableView):
    def __init__(self, parent: Optional[QWidget] = None):
        super(ChannelTableView, self).__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setShowGrid(False)

    def rowsInserted(self, parent: QModelIndex, first: int, last: int):
        super(ChannelTableView, self).rowsInserted(parent, first, last)
        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)
