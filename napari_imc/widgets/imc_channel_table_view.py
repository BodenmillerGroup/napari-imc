from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QTableView


class IMCChannelTableView(QTableView):
    def __init__(self, parent=None):
        super(IMCChannelTableView, self).__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setShowGrid(False)

    def rowsInserted(self, parent: QModelIndex, first: int, last: int):
        super(IMCChannelTableView, self).rowsInserted(parent, first, last)
        model = self.model()
        for column in range(model.columnCount()):
            self.resizeColumnToContents(column)
