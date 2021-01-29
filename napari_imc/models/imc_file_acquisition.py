from typing import Any, List, Optional, Sequence, TYPE_CHECKING

from napari_imc.models.base import IMCFileTreeItem, ModelBase

if TYPE_CHECKING:
    from napari_imc.models.channel import ChannelModel
    from napari_imc.models.imc_file import IMCFileModel


class IMCFileAcquisitionModel(ModelBase, IMCFileTreeItem):
    imc_file_tree_is_checkable = True

    def __init__(self, imc_file: 'IMCFileModel', id_: int, description: str, channel_labels: Sequence[str]):
        ModelBase.__init__(self)
        IMCFileTreeItem.__init__(self)
        self._imc_file = imc_file
        self._id = id_
        self._description = description
        self._channel_labels = list(channel_labels)
        self._loaded_channels: List['ChannelModel'] = []
        self._is_loaded = False

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
    def channel_labels(self) -> List[str]:
        return self._channel_labels

    @property
    def loaded_channels(self) -> List['ChannelModel']:
        return self._loaded_channels

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def _imc_file_tree_data(self) -> List[Any]:
        return [self.is_loaded, f'A{self.id:02d}', self.description]

    @property
    def _imc_file_tree_parent(self) -> Optional[IMCFileTreeItem]:
        return self._imc_file.imc_file_tree_acquisition_root_item

    @property
    def _imc_file_tree_children(self) -> List[IMCFileTreeItem]:
        return []

    @property
    def imc_file_tree_is_checked(self) -> bool:
        return self.is_loaded

    def set_loaded(self, channels: Sequence['ChannelModel']):
        self._loaded_channels.clear()
        self._loaded_channels += channels
        self._is_loaded = True

    def set_unloaded(self):
        self._loaded_channels.clear()
        self._is_loaded = False

    def __eq__(self, other):
        if other is None or not isinstance(other, IMCFileAcquisitionModel):
            return False
        return other._imc_file == self._imc_file and other._id == self._id

    def __hash__(self):
        return hash((self._imc_file, self._id))

    def __repr__(self):
        return f'{self._imc_file} A{self._id:02d}'
