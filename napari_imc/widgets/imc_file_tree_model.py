from contextlib import contextmanager
from qtpy.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from typing import Any, Optional, TYPE_CHECKING

from napari_imc.models.base import IMCFileTreeItem

if TYPE_CHECKING:
    from napari_imc.imc_controller import IMCController


class IMCFileTreeModel(QAbstractItemModel):
    CHECK_COLUMN = 0
    ID_COLUMN = 1
    DESCRIPTION_COLUMN = 2

    def __init__(self, controller: 'IMCController', parent: Optional[QObject] = None):
        super(IMCFileTreeModel, self).__init__(parent)
        self._controller = controller

    def index(self, row: int, column: int, parent: QModelIndex = None, **kwargs) -> QModelIndex:
        if self.hasIndex(row, column, parent=parent):
            if parent is not None and parent.isValid():
                parent_item: IMCFileTreeItem = parent.internalPointer()
            else:
                parent_item = self._controller
            if 0 <= row < len(parent_item.imc_file_tree_children):
                child_item: IMCFileTreeItem = parent_item.imc_file_tree_children[row]
                if 0 <= column < len(child_item.imc_file_tree_data):
                    return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex = None, **kwargs) -> QModelIndex:
        if index is not None and index.isValid():
            parent_item: IMCFileTreeItem = index.internalPointer().imc_file_tree_parent
            if parent_item is not None and parent_item.imc_file_tree_parent is not None:
                parent_row = parent_item.imc_file_tree_parent.imc_file_tree_children.index(parent_item)
                return self.createIndex(parent_row, 0, parent_item)
        return QModelIndex()

    def rowCount(self, parent: Optional[QModelIndex] = None, **kwargs) -> int:
        if parent is not None and parent.isValid():
            parent_item: IMCFileTreeItem = parent.internalPointer()
        else:
            parent_item = self._controller
        return len(parent_item.imc_file_tree_children)

    def columnCount(self, parent: Optional[QModelIndex] = None, **kwargs) -> int:
        return 3

    def data(self, index: QModelIndex, role: Optional[int] = None) -> Any:
        if index.isValid():
            item: IMCFileTreeItem = index.internalPointer()
            if role == Qt.DisplayRole and (index.column() != self.CHECK_COLUMN or not item.imc_file_tree_is_checkable):
                return item.imc_file_tree_data[index.column()]
            if role == Qt.CheckStateRole and (index.column() == self.CHECK_COLUMN and item.imc_file_tree_is_checkable):
                return Qt.Checked if item.imc_file_tree_is_checked else Qt.Unchecked
        return None

    def setData(self, index: QModelIndex, value: Any, role: Optional[int] = None) -> bool:
        if index.isValid() and role == Qt.CheckStateRole and index.column() == self.CHECK_COLUMN:
            item: IMCFileTreeItem = index.internalPointer()
            if item.imc_file_tree_is_checkable:
                # imc_file_acquisition is set to loaded/unloaded in dataChanged event handler
                # imc_file_panorama is set to shown/hidden in dataChanged event handler
                # noinspection PyUnresolvedReferences
                self.dataChanged.emit(index, index, [Qt.CheckStateRole])
                return True
        return super(IMCFileTreeModel, self).setData(index, value, role=role)

    def flags(self, index: QModelIndex) -> int:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = super(IMCFileTreeModel, self).flags(index)
        item: IMCFileTreeItem = index.internalPointer()
        if index.column() == self.CHECK_COLUMN and item.imc_file_tree_is_checkable:
            flags |= Qt.ItemIsUserCheckable
        return flags

    def headerData(self, section: int, orientation: int, role: Optional[int] = None) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == self.CHECK_COLUMN:
                return ''
            if section == self.ID_COLUMN:
                return 'ID'
            if section == self.DESCRIPTION_COLUMN:
                return 'Description'
        return None

    @contextmanager
    def append_imc_file(self):
        self.beginInsertRows(self.createIndex(0, 0, self._controller), self.rowCount(), self.rowCount())
        yield
        self.endInsertRows()

    @contextmanager
    def remove_imc_file(self, index: int):
        self.beginRemoveRows(self.createIndex(0, 0, self._controller), index, index)
        yield
        self.endRemoveRows()
