from qtpy.QtCore import QModelIndex
from qtpy.QtWidgets import QTreeView


class IMCFileTreeView(QTreeView):
    def __init__(self, parent=None):
        super(IMCFileTreeView, self).__init__(parent)

    def rowsInserted(self, parent: QModelIndex, first: int, last: int):
        super(IMCFileTreeView, self).rowsInserted(parent, first, last)
        model = self.model()
        for row in range(first, last + 1):
            index = model.index(row, 0, parent)
            self.expandRecursively(index)
            self.setFirstColumnSpanned(row, parent, True)
            for child_row in range(model.rowCount(index)):
                self.setFirstColumnSpanned(child_row, index, True)
        for column in range(model.columnCount()):
            self.resizeColumnToContents(column)
