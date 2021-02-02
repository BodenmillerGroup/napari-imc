from qtpy.QtCore import Qt, QModelIndex, QObject, QPoint, Signal
from qtpy.QtWidgets import QMenu, QStyle, QTreeView, QWidget
from typing import Optional

from napari_imc.models import IMCFileModel


class IMCFileTreeView(QTreeView):
    class Events(QObject):
        imc_file_closed = Signal(IMCFileModel)

    def __init__(self, parent: Optional[QWidget] = None):
        super(IMCFileTreeView, self).__init__(parent)
        self.events = IMCFileTreeView.Events(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # noinspection PyUnresolvedReferences
        @self.customContextMenuRequested.connect
        def on_custom_context_menu_requested(pos: QPoint):
            index: QModelIndex = self.indexAt(pos)
            if index.isValid():
                item = index.internalPointer()
                if isinstance(item, IMCFileModel):
                    menu = QMenu()
                    close_action_icon = self.window().style().standardIcon(QStyle.SP_DialogCloseButton, widget=self)
                    close_action = menu.addAction(close_action_icon, 'Close')
                    if menu.exec(self.mapToGlobal(pos)) == close_action:
                        self.events.imc_file_closed.emit(item)

    def rowsInserted(self, parent: QModelIndex, first: int, last: int):
        super(IMCFileTreeView, self).rowsInserted(parent, first, last)
        for row in range(first, last + 1):
            index = self.model().index(row, 0, parent)
            self.expandRecursively(index)
            self.setFirstColumnSpanned(row, parent, True)
            for child_row in range(self.model().rowCount(index)):
                self.setFirstColumnSpanned(child_row, index, True)
        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)
