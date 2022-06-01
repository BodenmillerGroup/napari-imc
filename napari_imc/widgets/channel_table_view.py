from typing import Optional

from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QTableView, QWidget


class ChannelTableView(QTableView):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(ChannelTableView, self).__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setShowGrid(False)

    def rowsInserted(self, parent: QModelIndex, first: int, last: int):
        super(ChannelTableView, self).rowsInserted(parent, first, last)
        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)
