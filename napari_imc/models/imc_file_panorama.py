from napari.layers import Image
from typing import Any, List, Optional, TYPE_CHECKING

from napari_imc.models.base import IMCFileTreeItem, ModelBase

if TYPE_CHECKING:
    from napari_imc.models.imc_file import IMCFileModel


class IMCFilePanoramaModel(ModelBase, IMCFileTreeItem):
    imc_file_tree_is_checkable = True

    def __init__(self, imc_file: 'IMCFileModel', id_: int, description: str):
        ModelBase.__init__(self)
        IMCFileTreeItem.__init__(self)
        self._imc_file = imc_file
        self._id = id_
        self._description = description
        self._shown_layer: Optional[Image] = None
        self._is_shown = False

    @property
    def imc_file(self) -> 'IMCFileModel':
        return self._imc_file

    @property
    def id(self) -> int:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @property
    def shown_layer(self) -> Optional[Image]:
        return self._shown_layer

    @property
    def is_shown(self) -> bool:
        return self._is_shown

    @property
    def _imc_file_tree_data(self) -> List[Any]:
        return [self.is_shown, f'P{self.id:02d}', self.description]

    @property
    def _imc_file_tree_parent(self) -> Optional[IMCFileTreeItem]:
        return self._imc_file.imc_file_tree_panorama_root_item

    @property
    def _imc_file_tree_children(self) -> List[IMCFileTreeItem]:
        return []

    @property
    def imc_file_tree_is_checked(self) -> bool:
        return self.is_shown

    def set_shown(self, layer: Image):
        self._shown_layer = layer
        self._is_shown = True

    def set_hidden(self):
        self._shown_layer = None
        self._is_shown = False

    def __eq__(self, other):
        if other is None or not isinstance(other, IMCFilePanoramaModel):
            return False
        return other._imc_file == self._imc_file and other._id == self._id

    def __hash__(self):
        return hash((self._imc_file, self._id))

    def __repr__(self):
        return f'{self._imc_file} P{self._id:02d}'
