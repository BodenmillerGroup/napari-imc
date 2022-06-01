from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Optional

from qtpy.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt

if TYPE_CHECKING:
    from ..imc_controller import IMCController


class ChannelTableModel(QAbstractTableModel):
    CHECK_COLUMN = 0
    LABEL_COLUMN = 1

    def __init__(
        self, controller: "IMCController", parent: Optional[QObject] = None
    ) -> None:
        super(ChannelTableModel, self).__init__(parent)
        self._controller = controller

    def rowCount(self, parent: Optional[QModelIndex] = None, *args, **kwargs) -> int:
        return len(self._controller.channels)

    def columnCount(self, parent: Optional[QModelIndex] = None, *args, **kwargs) -> int:
        return 2

    def data(self, index: QModelIndex, role: Optional[int] = None) -> Any:
        if index.isValid():
            channel = self._controller.channels[index.row()]
            if (
                index.column() == self.CHECK_COLUMN
                and role == Qt.ItemDataRole.CheckStateRole
            ):
                if channel.is_shown:
                    return Qt.CheckState.Checked
                return Qt.CheckState.Unchecked
            if (
                index.column() == self.LABEL_COLUMN
                and role == Qt.ItemDataRole.DisplayRole
            ):
                return channel.label
        return None

    def setData(
        self, index: QModelIndex, value: Any, role: Optional[int] = None
    ) -> bool:
        if (
            index.isValid()
            and index.column() == self.CHECK_COLUMN
            and role == Qt.ItemDataRole.CheckStateRole
        ):
            # channel is set to shown/hidden in dataChanged event handler
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            return True
        return super(ChannelTableModel, self).setData(index, value, role=role)

    def flags(self, index: QModelIndex) -> int:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = super(ChannelTableModel, self).flags(index)
        if index.column() == self.CHECK_COLUMN:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def headerData(
        self, section: int, orientation: int, role: Optional[int] = None
    ) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            if section == self.CHECK_COLUMN:
                return ""
            if section == self.LABEL_COLUMN:
                return "Channel"
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
