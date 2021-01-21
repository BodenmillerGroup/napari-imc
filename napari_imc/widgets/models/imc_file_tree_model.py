from abc import abstractmethod
from imctools.data import Acquisition, Panorama
from pathlib import Path
from qtpy.QtCore import Qt, QAbstractItemModel, QModelIndex
from typing import Any, cast, List, Optional, Sequence


class IMCFileTreeModel(QAbstractItemModel):
    class Item:
        is_checkable = False

        def __init__(self, parent: Optional['IMCFileTreeModel.Item']):
            self.parent = parent
            self.children: List['IMCFileTreeModel.Item'] = []

        @property
        @abstractmethod
        def data(self) -> Sequence[Any]:
            pass

    class RootItem(Item):
        def __init__(self):
            super(IMCFileTreeModel.RootItem, self).__init__(None)

        @property
        def data(self) -> Sequence[Any]:
            return []

    class IMCFileItem(Item):
        def __init__(self, parent: 'IMCFileTreeModel.RootItem', path: Path):
            super(IMCFileTreeModel.IMCFileItem, self).__init__(parent)
            self.path = path
            self.panorama_root_item = IMCFileTreeModel.PanoramaRootItem(self)
            self.acquisition_root_item = IMCFileTreeModel.AcquisitionRootItem(self)
            self.children = [self.panorama_root_item, self.acquisition_root_item]

        @property
        def data(self) -> Sequence[Any]:
            return [self.path.name]

    class PanoramaRootItem(Item):
        @property
        def data(self) -> Sequence[Any]:
            return ["Panoramas"]

    class AcquisitionRootItem(Item):
        @property
        def data(self) -> Sequence[Any]:
            return ["Acquisitions"]

    class PanoramaItem(Item):
        is_checkable = True

        def __init__(self, parent: 'IMCFileTreeModel.PanoramaRootItem', panorama: Panorama):
            super(IMCFileTreeModel.PanoramaItem, self).__init__(parent)
            self.panorama = panorama
            self.checked = False

        @property
        def data(self) -> Sequence[Any]:
            return [self.checked, self.panorama.id, self.panorama.description]

        @property
        def imc_file_item(self) -> 'IMCFileTreeModel.IMCFileItem':
            return cast(IMCFileTreeModel.IMCFileItem, self.parent.parent)

    class AcquisitionItem(Item):
        is_checkable = True

        def __init__(self, parent: 'IMCFileTreeModel.AcquisitionRootItem', acquisition: Acquisition):
            super(IMCFileTreeModel.AcquisitionItem, self).__init__(parent)
            self.acquisition = acquisition
            self.checked = False

        @property
        def data(self) -> Sequence[Any]:
            return [self.checked, self.acquisition.id, self.acquisition.description]

        @property
        def imc_file_item(self) -> 'IMCFileTreeModel.IMCFileItem':
            return cast(IMCFileTreeModel.IMCFileItem, self.parent.parent)

    section_headers = ['', 'ID', 'Description']
    check_column = 0
    id_column = 1
    description_column = 2

    def __init__(self, parent=None):
        super(IMCFileTreeModel, self).__init__(parent)
        self.root_item = IMCFileTreeModel.RootItem()

    def add_imc_file(self, path: Path, panoramas: Sequence[Panorama], acquisitions: Sequence[Acquisition]):
        if not any(cast(IMCFileTreeModel.IMCFileItem, item).path.samefile(path) for item in self.root_item.children):
            session_item = IMCFileTreeModel.IMCFileItem(self.root_item, path)
            for panorama in panoramas:
                panorama_item = IMCFileTreeModel.PanoramaItem(session_item.panorama_root_item, panorama)
                session_item.panorama_root_item.children.append(panorama_item)
            for acquisition in acquisitions:
                acquisition_item = IMCFileTreeModel.AcquisitionItem(session_item.acquisition_root_item, acquisition)
                session_item.acquisition_root_item.children.append(acquisition_item)
            self.beginInsertRows(self.createIndex(0, 0, self.root_item), self.rowCount(), self.rowCount())
            self.root_item.children.append(session_item)
            self.endInsertRows()

    def index(self, row: int, column: int, parent: QModelIndex = None, **kwargs) -> QModelIndex:
        if self.hasIndex(row, column, parent=parent):
            parent_item = self.root_item
            if parent is not None and parent.isValid():
                parent_item: IMCFileTreeModel.Item = parent.internalPointer()
            if 0 <= row < len(parent_item.children):
                child_item: IMCFileTreeModel.Item = parent_item.children[row]
                if 0 <= column < len(child_item.data):
                    return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex = None, **kwargs) -> QModelIndex:
        if index is not None and index.isValid():
            parent_item: IMCFileTreeModel.Item = index.internalPointer().parent
            if parent_item is not None and parent_item.parent is not None:
                parent_row = parent_item.parent.children.index(parent_item)
                return self.createIndex(parent_row, 0, parent_item)
        return QModelIndex()

    def rowCount(self, parent: Optional[QModelIndex] = None, **kwargs) -> int:
        parent_item = self.root_item
        if parent is not None and parent.isValid():
            parent_item: IMCFileTreeModel.Item = parent.internalPointer()
        return len(parent_item.children)

    def columnCount(self, parent: Optional[QModelIndex] = None, **kwargs) -> int:
        return 3

    def data(self, index: QModelIndex, role: Optional[int] = None) -> Any:
        if index.isValid():
            item: IMCFileTreeModel.Item = index.internalPointer()
            if role == Qt.DisplayRole and (index.column() != self.check_column or not item.is_checkable):
                return item.data[index.column()]
            if role == Qt.CheckStateRole and index.column() == self.check_column and item.is_checkable:
                return Qt.Checked if item.data[self.check_column] else Qt.Unchecked
        return None

    def setData(self, index: QModelIndex, value: Any, role: Optional[int] = None) -> bool:
        if index.isValid() and role == Qt.CheckStateRole and index.column() == self.check_column:
            item: IMCFileTreeModel.Item = index.internalPointer()
            if item.is_checkable:
                item.checked = (value == Qt.Checked)
                # noinspection PyUnresolvedReferences
                self.dataChanged.emit(index, index, [Qt.CheckStateRole])
                return True
        return super(IMCFileTreeModel, self).setData(index, value, role=role)

    def flags(self, index: QModelIndex) -> int:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = super(IMCFileTreeModel, self).flags(index)
        item: IMCFileTreeModel.Item = index.internalPointer()
        if index.column() == self.check_column and item.is_checkable:
            flags |= Qt.ItemIsUserCheckable
        return flags

    def headerData(self, section: int, orientation: int, role: Optional[int] = None) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and 0 <= section < len(self.section_headers):
            return self.section_headers[section]
        return None
