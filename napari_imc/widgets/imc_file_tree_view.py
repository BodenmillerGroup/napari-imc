from typing import Optional

from qtpy.QtCore import QModelIndex, QObject, QPoint, Qt, Signal
from qtpy.QtWidgets import QMenu, QStyle, QTreeView, QWidget

from ..models import IMCFileModel


class IMCFileTreeView(QTreeView):
    class Events(QObject):
        imc_file_closed = Signal(IMCFileModel)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(IMCFileTreeView, self).__init__(parent)
        self.events = IMCFileTreeView.Events(self)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        @self.customContextMenuRequested.connect
        def on_custom_context_menu_requested(pos: QPoint):
            index: QModelIndex = self.indexAt(pos)
            if index.isValid():
                item = index.internalPointer()
                if isinstance(item, IMCFileModel):
                    menu = QMenu()
                    style = self.window().style()
                    close_action_icon = style.standardIcon(
                        QStyle.StandardPixmap.SP_DialogCloseButton, widget=self
                    )
                    close_action = menu.addAction(close_action_icon, "Close")
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
