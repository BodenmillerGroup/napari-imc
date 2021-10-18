import numpy as np
import re

from napari_imc.io.base import FileReaderBase, ImageDimensions
from pathlib import Path
from readimc import IMCTxtFile
from typing import List, Optional, Tuple, Union

from napari_imc.models import IMCFileModel, IMCFileAcquisitionModel, IMCFilePanoramaModel


class TxtFileReader(FileReaderBase):
    def __init__(self, path: Union[str, Path]):
        super(TxtFileReader, self).__init__(path)
        self._txt_file: Optional[IMCTxtFile] = None

    def _get_imc_file_panoramas(self, imc_file: IMCFileModel) -> List[IMCFilePanoramaModel]:
        return []

    def _get_imc_file_acquisitions(self, imc_file: IMCFileModel) -> List[IMCFileAcquisitionModel]:
        m = re.match(r"(?P<description>.*)_(?P<id>[0-9]+)", self._path.stem)
        acquisition_id = int(m.group("id")) if m is not None else 0
        acquisition_description = m.group("description") if m is not None else self._path.stem
        return [
            IMCFileAcquisitionModel(imc_file, acquisition_id, acquisition_description, self._txt_file.channel_labels)
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        raise RuntimeError('This operation is not supported')

    def read_acquisition(self, acquisition_id: int, channel_label: str) -> Tuple[ImageDimensions, np.ndarray]:
        channel_index = self._txt_file.channel_labels.index(channel_label)
        channel_img = self._txt_file.read_acquisition()[channel_index]
        x_physical, y_physical = 0, 0
        h_physical, w_physical = channel_img.shape
        return (x_physical, y_physical, w_physical, h_physical), channel_img

    def __enter__(self) -> 'FileReaderBase':
        self._txt_file = IMCTxtFile(self._path)
        self._txt_file.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._txt_file.close()
        self._txt_file = None

    @classmethod
    def accepts(cls, path: Union[str, Path]) -> bool:
        return Path(path).suffix.lower() == '.txt'
