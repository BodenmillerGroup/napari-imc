import numpy as np

from napari import Viewer
from napari.layers import Image
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Type, TYPE_CHECKING, Union

from .io import McdFileReader, TxtFileReader
from .io.base import FileReaderBase
from .models import (
    ChannelModel,
    IMCFileModel,
    IMCFileAcquisitionModel,
    IMCFilePanoramaModel,
)
from .models.base import IMCFileTreeItem

if TYPE_CHECKING:
    from .imc_widget import IMCWidget


class IMCController(IMCFileTreeItem):
    PANORAMA_LAYER_TYPE = "imc_panorama_layer"
    ACQUISITION_LAYER_TYPE = "imc_acquisition_layer"
    FILE_READERS: List[Type[FileReaderBase]] = [
        # ImaxtFileReader,
        McdFileReader,
        TxtFileReader,
    ]

    def __init__(self, viewer: Viewer, widget: "IMCWidget") -> None:
        super(IMCController, self).__init__()
        self._viewer: Viewer = viewer
        self._widget: "IMCWidget" = widget
        self._imc_files: List[IMCFileModel] = []
        self._channels: List[ChannelModel] = []
        self._selected_channels: List[ChannelModel] = []
        self._closed_imc_files_qt_memory_hack: List[IMCFileModel] = []

    @classmethod
    def is_imc_file(cls, path: Union[str, Path]) -> bool:
        return any(file_reader.accepts(path) for file_reader in cls.FILE_READERS)

    def open_imc_file(self, imc_file_path: Union[str, Path]) -> Optional[IMCFileModel]:
        imc_file_path = Path(imc_file_path).resolve()
        for imc_file in self.imc_files:
            if imc_file.path.samefile(imc_file_path):
                return imc_file
        imc_file = None
        for file_reader in self.FILE_READERS:
            if file_reader.accepts(imc_file_path):
                try:
                    with file_reader(imc_file_path) as f:
                        imc_file = f.get_imc_file(self)
                except Exception:
                    pass  # ignored intentionally
        if imc_file is None:
            return None
        with self._widget.imc_file_tree_model.append_imc_file():
            self._imc_files.append(imc_file)
        return imc_file

    def close_imc_file(self, imc_file: IMCFileModel):
        for imc_file_panorama in imc_file.panoramas:
            if imc_file_panorama.is_shown:
                self.hide_imc_file_panorama(imc_file_panorama)
        for imc_file_acquisition in imc_file.acquisitions:
            if imc_file_acquisition.is_loaded:
                self.unload_imc_file_acquisition(imc_file_acquisition)
        imc_file_index = self._imc_files.index(imc_file)
        with self._widget.imc_file_tree_model.remove_imc_file(imc_file_index):
            imc_file.mark_deleted()
            self._imc_files.remove(imc_file)
            self._closed_imc_files_qt_memory_hack.append(imc_file)

    def show_imc_file_panorama(
        self, imc_file_panorama: IMCFilePanoramaModel
    ) -> Optional[Image]:
        dims, data = None, None
        for file_reader in self.FILE_READERS:
            if file_reader.accepts(imc_file_panorama.imc_file.path):
                try:
                    with file_reader(imc_file_panorama.imc_file.path) as f:
                        dims, data = f.read_panorama(imc_file_panorama.id)
                except Exception:
                    pass  # ignored intentionally
        if dims is None or data is None:
            return None
        new_layer_index = self._get_next_panorama_layer_index()
        layer = self._viewer.add_image(
            data,
            name=(
                f"{imc_file_panorama.imc_file.path.name} "
                f"[P{imc_file_panorama.id:02d}]"
            ),
            metadata={
                self.PANORAMA_LAYER_TYPE: True,
                "imc_file_panorama": str(imc_file_panorama),
            },
            scale=(dims.height / data.shape[0], dims.width / data.shape[1]),
            translate=(dims.y, dims.x),
            rotate=dims.rotation,
            opacity=0.5,
        )
        old_layer_index = self.viewer.layers.index(layer)
        self.viewer.layers.move(old_layer_index, new_layer_index)
        imc_file_panorama.set_shown(layer)
        return layer

    def hide_imc_file_panorama(self, imc_file_panorama: IMCFilePanoramaModel):
        if imc_file_panorama.shown_layer in self._viewer.layers:
            self._viewer.layers.remove(imc_file_panorama.shown_layer)
        imc_file_panorama.set_hidden()

    def load_imc_file_acquisition(
        self, imc_file_acquisition: IMCFileAcquisitionModel
    ) -> List[Image]:
        channels: List[ChannelModel] = []
        channels_to_show: List[ChannelModel] = []
        channels_to_append: List[ChannelModel] = []
        for channel_label in imc_file_acquisition.channel_labels:
            channel = next(
                (c for c in self._channels if c.label == channel_label), None
            )
            if channel is None:
                channel = ChannelModel(channel_label)
                channels_to_append.append(channel)
            channel.loaded_imc_file_acquisitions.append(imc_file_acquisition)
            if channel.is_shown:
                channels_to_show.append(channel)
            channels.append(channel)
        imc_file_acquisition.set_loaded(channels)
        if len(channels_to_append) > 0:
            with self._widget.channel_table_model.append_channels(
                len(channels_to_append)
            ):
                self._channels += channels_to_append
        layers = []
        for channel in channels_to_show[::-1]:
            layer = self._show_imc_file_acquisition_channel(
                imc_file_acquisition, channel
            )
            if layer is not None:
                channel.shown_imc_file_acquisition_layers[imc_file_acquisition] = layer
                layers.append(layer)
        return layers

    def unload_imc_file_acquisition(
        self, imc_file_acquisition: IMCFileAcquisitionModel
    ):
        for channel_label in imc_file_acquisition.channel_labels:
            channel_index, channel = next(
                (i, c) for i, c in enumerate(self._channels) if c.label == channel_label
            )
            if channel.is_shown:
                self._hide_imc_file_acquisition_channel(imc_file_acquisition, channel)
            channel.loaded_imc_file_acquisitions.remove(imc_file_acquisition)
            if len(channel.loaded_imc_file_acquisitions) == 0:
                with self._widget.channel_table_model.remove_channel(channel_index):
                    self._channels.remove(channel)
        imc_file_acquisition.set_unloaded()

    def show_channel(self, channel: ChannelModel) -> List[Image]:
        imc_file_acquisition_layers = {}
        for imc_file_acquisition in channel.loaded_imc_file_acquisitions[::-1]:
            layer = self._show_imc_file_acquisition_channel(
                imc_file_acquisition, channel
            )
            if layer is not None:
                imc_file_acquisition_layers[imc_file_acquisition] = layer
        channel.set_shown(imc_file_acquisition_layers)
        self._widget.select_channel(self._channels.index(channel))
        return list(imc_file_acquisition_layers.values())

    def hide_channel(self, channel: ChannelModel):
        for imc_file_acquisition in channel.loaded_imc_file_acquisitions:
            self._hide_imc_file_acquisition_channel(imc_file_acquisition, channel)
        channel.set_hidden()
        self._widget.select_channel(self._channels.index(channel))

    def _show_imc_file_acquisition_channel(
        self, imc_file_acquisition: IMCFileAcquisitionModel, channel: ChannelModel
    ) -> Optional[Image]:
        dims, data = None, None
        for file_reader in self.FILE_READERS:
            if file_reader.accepts(imc_file_acquisition.imc_file.path):
                try:
                    with file_reader(imc_file_acquisition.imc_file.path) as f:
                        dims, data = f.read_acquisition(
                            imc_file_acquisition.id, channel.label
                        )
                except Exception:
                    pass  # ignored intentionally
        if dims is None or data is None:
            return None
        if channel.contrast_limits is None:
            channel.contrast_limits = (0, np.amax(data))
        new_layer_index = self._get_next_acquisition_layer_index()
        layer = self._viewer.add_image(
            data,
            colormap=channel.create_colormap(),
            gamma=channel.gamma,
            interpolation=channel.interpolation,
            contrast_limits=(0, np.amax(data)),  # sets contrast_limits_range
            name=(
                f"{imc_file_acquisition.imc_file.path.name} "
                f"[A{imc_file_acquisition.id:02d} {channel.label}]"
            ),
            metadata={
                self.ACQUISITION_LAYER_TYPE: True,
                "imc_file_acquisition": str(imc_file_acquisition),
                "channel": str(channel),
            },
            scale=(dims.height / data.shape[0], dims.width / data.shape[1]),
            translate=(dims.y, dims.x),
            rotate=dims.rotation,
            opacity=channel.opacity,
            blending=channel.blending,
        )
        layer.contrast_limits = channel.contrast_limits
        old_layer_index = self.viewer.layers.index(layer)
        self.viewer.layers.move(old_layer_index, new_layer_index)
        return layer

    def _hide_imc_file_acquisition_channel(
        self, imc_file_acquisition: IMCFileAcquisitionModel, channel: ChannelModel
    ):
        layer = channel.shown_imc_file_acquisition_layers.get(imc_file_acquisition)
        if layer is not None and layer in self._viewer.layers:
            self._viewer.layers.remove(layer)

    def _get_layer_index(self, layer_type: str, last: bool = False):
        layer_enumerator = enumerate(self.viewer.layers)
        if last:
            layer_enumerator = reversed(list(layer_enumerator))
        for i, layer in layer_enumerator:
            if layer.metadata.get(layer_type, False):
                return i
        return None

    def _get_next_panorama_layer_index(self):
        last_panorama_layer_index = self._get_layer_index(
            self.PANORAMA_LAYER_TYPE, last=True
        )
        if last_panorama_layer_index is not None:
            return last_panorama_layer_index + 1
        first_acquisition_layer_index = self._get_layer_index(
            self.ACQUISITION_LAYER_TYPE, last=False
        )
        if first_acquisition_layer_index is not None:
            return max(0, first_acquisition_layer_index - 1)
        return len(self.viewer.layers)

    def _get_next_acquisition_layer_index(self):
        last_acquisition_layer_index = self._get_layer_index(
            self.ACQUISITION_LAYER_TYPE, last=True
        )
        if last_acquisition_layer_index is not None:
            return last_acquisition_layer_index + 1
        return len(self.viewer.layers)

    @property
    def viewer(self) -> Viewer:
        return self._viewer

    @property
    def widget(self) -> "IMCWidget":
        return self._widget

    @property
    def imc_files(self) -> Tuple[IMCFileModel, ...]:
        return tuple(self._imc_files)

    @property
    def channels(self) -> Tuple[ChannelModel, ...]:
        return tuple(self._channels)

    @property
    def selected_channels(self) -> Tuple[ChannelModel, ...]:
        return tuple(self._selected_channels)

    @selected_channels.setter
    def selected_channels(self, selected_channels: Sequence[ChannelModel]):
        self._selected_channels = selected_channels
        self._widget.refresh_channel_controls_widget()

    @property
    def _imc_file_tree_data(self) -> List[Any]:
        return []

    @property
    def _imc_file_tree_parent(self) -> Optional[IMCFileTreeItem]:
        return None

    @property
    def _imc_file_tree_children(self) -> List[IMCFileTreeItem]:
        return self._imc_files
