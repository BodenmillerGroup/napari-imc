from pathlib import Path
from typing import Any, List, Optional

from napari_imc.models.base import IMCFileTreeItem, ModelBase
from napari_imc.models.imc_file_acquisition import IMCFileAcquisitionModel
from napari_imc.models.imc_file_panorama import IMCFilePanoramaModel


class IMCFileModel(ModelBase, IMCFileTreeItem):
    def __init__(self, path: Path, imc_file_tree_root_item: IMCFileTreeItem):
        ModelBase.__init__(self)
        IMCFileTreeItem.__init__(self)
        self._path = path
        self._imc_file_tree_root_item = imc_file_tree_root_item
        self._panoramas: List[IMCFilePanoramaModel] = []
        self._acquisitions: List[IMCFileAcquisitionModel] = []
        self._imc_file_tree_panorama_root_item = IMCFileModel.IMCFileTreePanoramaRootItem(self)
        self._imc_file_tree_acquisition_root_item = IMCFileModel.IMCFileTreeAcquisitionRootItem(self)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def panoramas(self) -> List[IMCFilePanoramaModel]:
        return self._panoramas

    @property
    def acquisitions(self) -> List[IMCFileAcquisitionModel]:
        return self._acquisitions

    @property
    def imc_file_tree_panorama_root_item(self) -> 'IMCFileModel.IMCFileTreePanoramaRootItem':
        return self._imc_file_tree_panorama_root_item

    @property
    def imc_file_tree_acquisition_root_item(self) -> 'IMCFileModel.IMCFileTreeAcquisitionRootItem':
        return self._imc_file_tree_acquisition_root_item

    @property
    def _imc_file_tree_data(self) -> List[Any]:
        return [self._path.name]

    @property
    def _imc_file_tree_parent(self) -> Optional[IMCFileTreeItem]:
        return self._imc_file_tree_root_item

    @property
    def _imc_file_tree_children(self) -> List[IMCFileTreeItem]:
        return [self._imc_file_tree_panorama_root_item, self._imc_file_tree_acquisition_root_item]

    def __eq__(self, other):
        if other is None or not isinstance(other, IMCFileModel):
            return False
        return other._path.samefile(self._path)

    def __hash__(self):
        return hash(self._path)

    def __repr__(self):
        return str(self._path)

    class IMCFileTreePanoramaRootItem(IMCFileTreeItem):
        def __init__(self, imc_file: 'IMCFileModel'):
            super(IMCFileModel.IMCFileTreePanoramaRootItem, self).__init__()
            self._imc_file = imc_file

        @property
        def _imc_file_tree_data(self) -> List[Any]:
            return ['Panoramas']

        @property
        def _imc_file_tree_parent(self) -> Optional[IMCFileTreeItem]:
            return self._imc_file

        @property
        def _imc_file_tree_children(self) -> List[IMCFileTreeItem]:
            return self._imc_file.panoramas

    class IMCFileTreeAcquisitionRootItem(IMCFileTreeItem):
        def __init__(self, imc_file: 'IMCFileModel'):
            super(IMCFileModel.IMCFileTreeAcquisitionRootItem, self).__init__()
            self._imc_file = imc_file

        @property
        def _imc_file_tree_data(self) -> List[Any]:
            return ['Acquisitions']

        @property
        def _imc_file_tree_parent(self) -> Optional[IMCFileTreeItem]:
            return self._imc_file

        @property
        def _imc_file_tree_children(self) -> List[IMCFileTreeItem]:
            return self._imc_file.acquisitions
