from contextlib import contextmanager
from qtpy.QtCore import Qt, QAbstractTableModel, QModelIndex
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from napari_imc.imc_controller import IMCController


class ChannelTableModel(QAbstractTableModel):
    check_column = 0
    label_column = 1

    def __init__(self, controller: 'IMCController', parent=None):
        super(ChannelTableModel, self).__init__(parent)
        self._controller = controller

    def rowCount(self, parent: Optional[QModelIndex] = None, *args, **kwargs) -> int:
        return len(self._controller.channels)

    def columnCount(self, parent: Optional[QModelIndex] = None, *args, **kwargs) -> int:
        return 2

    def data(self, index: QModelIndex, role: Optional[int] = None) -> Any:
        if index.isValid():
            channel = self._controller.channels[index.row()]
            if index.column() == self.check_column and role == Qt.CheckStateRole:
                return Qt.Checked if channel.is_shown else Qt.Unchecked
            if index.column() == self.label_column and role == Qt.DisplayRole:
                return channel.label
        return None

    def setData(self, index: QModelIndex, value: Any, role: Optional[int] = None) -> bool:
        if index.isValid() and index.column() == self.check_column and role == Qt.CheckStateRole:
            # channel is set to shown/hidden in dataChanged event handler
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return super(ChannelTableModel, self).setData(index, value, role=role)

    def flags(self, index: QModelIndex) -> int:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = super(ChannelTableModel, self).flags(index)
        if index.column() == self.check_column:
            flags |= Qt.ItemIsUserCheckable
        return flags

    def headerData(self, section: int, orientation: int, role: Optional[int] = None) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == self.check_column:
                return ''
            if section == self.label_column:
                return 'Channel'
        return None

    @contextmanager
    def append_channels(self, n: int):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + n - 1)
        yield
        self.endInsertRows()

    @contextmanager
    def remove_channel(self, index: int):
        self.beginRemoveRows(QModelIndex(), index, index)
        yield
        self.endRemoveRows()
