import numpy as np

from imageio import imread
from imctools.io.mcd.mcdparser import McdParser
from napari_imc.io.base import FileReaderBase, ImageDimensions
from pathlib import Path
from typing import List, Optional, Tuple, Union

from napari_imc.models import IMCFileAcquisitionModel, IMCFilePanoramaModel


class McdFileReader(FileReaderBase):
    suffixes = ['.mcd']

    def __init__(self, path: Union[str, Path]):
        super(McdFileReader, self).__init__(path)
        self._mcd_parser: Optional[McdParser] = None

    def get_panoramas(self) -> List[IMCFilePanoramaModel]:
        return [
            IMCFilePanoramaModel(self._path, panorama.id, panorama.description)
            for panorama in self._mcd_parser.session.panoramas.values() if panorama.image_type != 'Default'
        ]

    def get_acquisitions(self) -> List[IMCFileAcquisitionModel]:
        return [
            IMCFileAcquisitionModel(self._path, acquisition.id, acquisition.description, acquisition.channel_labels)
            for acquisition in self._mcd_parser.session.acquisitions.values() if acquisition.is_valid
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        panorama = self._mcd_parser.session.panoramas[panorama_id]
        xs_physical = [panorama.x1, panorama.x2, panorama.x3, panorama.x4]
        ys_physical = [panorama.y1, panorama.y2, panorama.y3, panorama.y4]
        x_physical, y_physical = min(xs_physical), min(ys_physical)
        w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
        data = imread(self._mcd_parser.get_panorama_image(panorama_id))
        if x_physical != panorama.x1:
            data = data[:, ::-1, :]
        if y_physical != panorama.y1:
            data = data[::-1, :, :]
        return (x_physical, y_physical, w_physical, h_physical), data

    def read_acquisition(self, acquisition_id: int, channel_label: str) -> Tuple[ImageDimensions, np.ndarray]:
        acquisition = self._mcd_parser.session.acquisitions[acquisition_id]
        xs_physical = [acquisition.roi_start_x_pos_um, acquisition.roi_end_x_pos_um]
        ys_physical = [acquisition.roi_start_y_pos_um, acquisition.roi_end_y_pos_um]
        x_physical, y_physical = min(xs_physical), min(ys_physical)
        w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
        data = self._mcd_parser.get_acquisition_data(acquisition.id).get_image_by_label(channel_label)
        if x_physical != acquisition.roi_start_x_pos_um:
            data = data[:, ::-1]
        if y_physical != acquisition.roi_start_y_pos_um:
            data = data[::-1, :]
        return (x_physical, y_physical, w_physical, h_physical), data

    def __enter__(self) -> 'FileReaderBase':
        self._mcd_parser = McdParser(self._path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mcd_parser.close()
