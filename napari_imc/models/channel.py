from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from napari.layers import Image
from napari.utils import Colormap

from napari_imc.models.base import ModelBase

if TYPE_CHECKING:
    from napari_imc.models.imc_file_acquisition import IMCFileAcquisitionModel

Color = Tuple[float, float, float, float]


class ChannelModel(ModelBase):
    def __init__(self, label: str, opacity: float = 1., gamma: float = 1., color: Color = (1., 1., 1., 1.),
                 blending: str = 'additive', interpolation: str = 'nearest'):
        ModelBase.__init__(self)
        self._label = label
        self._opacity = opacity
        self._gamma = gamma
        self._color = color
        self._blending = blending
        self._interpolation = interpolation
        self._contrast_limits = None
        self._loaded_imc_file_acquisitions: List['IMCFileAcquisitionModel'] = []
        self._shown_imc_file_acquisition_layers: Dict['IMCFileAcquisitionModel', Image] = {}
        self._is_shown = False

    @property
    def label(self) -> str:
        return self._label

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, opacity: float):
        self._opacity = opacity
        for layer in self._shown_imc_file_acquisition_layers.values():
            layer.opacity = opacity

    @property
    def contrast_limits(self) -> Optional[Tuple[float, float]]:
        return self._contrast_limits

    @contrast_limits.setter
    def contrast_limits(self, contrast_limits: Tuple[float, float]):
        self._contrast_limits = contrast_limits
        for layer in self._shown_imc_file_acquisition_layers.values():
            layer.contrast_limits = contrast_limits

    @property
    def gamma(self) -> float:
        return self._gamma

    @gamma.setter
    def gamma(self, gamma: float):
        self._gamma = gamma
        for layer in self._shown_imc_file_acquisition_layers.values():
            layer.gamma = gamma

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, color: Color):
        self._color = color
        for layer in self._shown_imc_file_acquisition_layers.values():
            layer.colormap = self.create_colormap()

    @property
    def blending(self) -> str:
        return self._blending

    @blending.setter
    def blending(self, blending: str):
        self._blending = blending
        for layer in self._shown_imc_file_acquisition_layers.values():
            layer.blending = blending

    @property
    def interpolation(self) -> str:
        return self._interpolation

    @interpolation.setter
    def interpolation(self, interpolation: str):
        self._interpolation = interpolation
        for layer in self._shown_imc_file_acquisition_layers.values():
            layer.interpolation = interpolation

    @property
    def loaded_imc_file_acquisitions(self) -> List['IMCFileAcquisitionModel']:
        return self._loaded_imc_file_acquisitions

    @property
    def shown_imc_file_acquisition_layers(self) -> Dict['IMCFileAcquisitionModel', Image]:
        return self._shown_imc_file_acquisition_layers

    @property
    def is_shown(self) -> bool:
        return self._is_shown

    def set_shown(self, imc_file_acquisition_layers: Dict['IMCFileAcquisitionModel', Image]):
        self._shown_imc_file_acquisition_layers.clear()
        self._shown_imc_file_acquisition_layers.update(imc_file_acquisition_layers)
        self._is_shown = True

    def set_hidden(self):
        self._shown_imc_file_acquisition_layers.clear()
        self._is_shown = False

    def create_colormap(self) -> Colormap:
        return Colormap(name='IMC', colors=[[0., 0., 0., 0.], list(self._color)], interpolation='linear')

    def __eq__(self, other):
        if other is None or not isinstance(other, ChannelModel):
            return False
        return other._label == self._label

    def __hash__(self):
        return hash(self._label)

    def __repr__(self):
        return self._label
