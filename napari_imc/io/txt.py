import numpy as np

from imctools.io.txt.txtparser import TxtParser
from napari_imc.io.base import FileReaderBase, ImageDimensions
from pathlib import Path
from typing import List, Optional, Tuple, Union

from napari_imc.models import IMCFileAcquisitionModel, IMCFilePanoramaModel


class TxtFileReader(FileReaderBase):
    suffixes = ['.txt']

    def __init__(self, path: Union[str, Path]):
        super(TxtFileReader, self).__init__(path)
        self._txt_parser: Optional[TxtParser] = None

    def get_panoramas(self) -> List[IMCFilePanoramaModel]:
        return []

    def get_acquisitions(self) -> List[IMCFileAcquisitionModel]:
        acquisition = self._txt_parser.get_acquisition_data().acquisition
        return [
            IMCFileAcquisitionModel(self._path, acquisition.id, acquisition.description, acquisition.channel_labels)
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        raise RuntimeError('This operation is not supported')

    def read_acquisition(self, acquisition_id: int, channel_label: str) -> Tuple[ImageDimensions, np.ndarray]:
        acquisition_data = self._txt_parser.get_acquisition_data()
        acquisition = acquisition_data.acquisition
        x_physical, y_physical = 0, 0
        w_physical, h_physical = acquisition.max_x, acquisition.max_y
        data = acquisition_data.get_image_by_label(channel_label)
        return (x_physical, y_physical, w_physical, h_physical), data

    def __enter__(self) -> 'FileReaderBase':
        self._txt_parser = TxtParser(self._path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
