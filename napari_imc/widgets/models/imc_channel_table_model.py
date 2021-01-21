from imctools.data import Acquisition, Channel
from pathlib import Path
from qtpy.QtCore import Qt, QAbstractTableModel, QModelIndex
from typing import Any, List, Optional, Tuple


class IMCChannelTableModel(QAbstractTableModel):
    class Item:
        def __init__(self, channel_label: str):
            self.channel_label = channel_label
            self.shown_acquisitions: List[Tuple[Path, int]] = []
            self.checked = False

        @property
        def data(self):
            return [self.checked, self.channel_label]

    check_column = 0
    label_column = 1
    section_headers = ['', 'Channel']

    def __init__(self, parent=None):
        super(IMCChannelTableModel, self).__init__(parent)
        self.items: List[IMCChannelTableModel.Item] = []

    def add_acquisition(self, path: Path, acquisition: Acquisition) -> List[Channel]:
        new_items = []
        acquisition_channels_to_show = []
        for channel in acquisition.channels.values():
            item = next((item for item in self.items if item.channel_label == channel.label), None)
            if item is None:
                item = IMCChannelTableModel.Item(channel.label)
                new_items.append(item)
            elif item.checked:
                acquisition_channels_to_show.append(channel)
            item.shown_acquisitions.append((path, acquisition.id))
        if len(new_items) > 0:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(new_items) - 1)
            self.items += new_items
            self.endInsertRows()
        return acquisition_channels_to_show

    def remove_acquisition(self, path: Path, acquisition: Acquisition) -> List[Channel]:
        acquisition_channels_to_hide = []
        for channel in acquisition.channels.values():
            row, item = next((row, item) for row, item in enumerate(self.items) if item.channel_label == channel.label)
            item.shown_acquisitions.remove((path, acquisition.id))
            acquisition_channels_to_hide.append(channel)
            if len(item.shown_acquisitions) == 0:
                self.beginRemoveRows(QModelIndex(), row, row)
                self.items.remove(item)
                self.endRemoveRows()
        return acquisition_channels_to_hide

    def rowCount(self, parent: Optional[QModelIndex] = None, *args, **kwargs) -> int:
        return len(self.items)

    def columnCount(self, parent: Optional[QModelIndex] = None, *args, **kwargs) -> int:
        return 2

    def data(self, index: QModelIndex, role: Optional[int] = None) -> Any:
        if index.isValid():
            item = self.items[index.row()]
            if role == Qt.DisplayRole and index.column() != self.check_column:
                return item.data[index.column()]
            if role == Qt.CheckStateRole and index.column() == self.check_column:
                return Qt.Checked if item.data[self.check_column] else Qt.Unchecked
        return None

    def setData(self, index: QModelIndex, value: Any, role: Optional[int] = None) -> bool:
        if index.isValid() and role == Qt.CheckStateRole and index.column() == self.check_column:
            item = self.items[index.row()]
            item.checked = (value == Qt.Checked)
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return super(IMCChannelTableModel, self).setData(index, value, role=role)

    def flags(self, index: QModelIndex) -> int:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = super(IMCChannelTableModel, self).flags(index)
        if index.column() == self.check_column:
            flags |= Qt.ItemIsUserCheckable
        return flags

    def headerData(self, section: int, orientation: int, role: Optional[int] = None) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and 0 <= section < len(self.section_headers):
            return self.section_headers[section]
        return None
