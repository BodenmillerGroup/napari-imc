from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QTableView


class ChannelTableView(QTableView):
    def __init__(self, parent=None):
        super(ChannelTableView, self).__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setShowGrid(False)

    def rowsInserted(self, parent: QModelIndex, first: int, last: int):
        super(ChannelTableView, self).rowsInserted(parent, first, last)
        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)
