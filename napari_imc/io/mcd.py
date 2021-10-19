import numpy as np

from napari_imc.io.base import FileReaderBase, ImageDimensions
from pathlib import Path
from readimc import IMCMcdFile
from typing import List, Optional, Tuple, Union

from napari_imc.models import IMCFileModel, IMCFileAcquisitionModel, IMCFilePanoramaModel


class McdFileReader(FileReaderBase):
    def __init__(self, path: Union[str, Path]):
        super(McdFileReader, self).__init__(path)
        self._mcd_file: Optional[IMCMcdFile] = None

    def _get_imc_file_panoramas(self, imc_file: IMCFileModel) -> List[IMCFilePanoramaModel]:
        return [
            IMCFilePanoramaModel(imc_file, panorama.id, panorama.metadata.get("Type"), panorama.description)
            for slide in self._mcd_file.slides for panorama in slide.panoramas
        ]

    def _get_imc_file_acquisitions(self, imc_file: IMCFileModel) -> List[IMCFileAcquisitionModel]:
        return [
            IMCFileAcquisitionModel(imc_file, acquisition.id, acquisition.description, acquisition.channel_labels)
            for slide in self._mcd_file.slides for acquisition in slide.acquisitions
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        panorama = next(
            panorama
            for slide in self._mcd_file.slides
            for panorama in slide.panoramas
            if panorama.id == panorama_id
        )
        x = min(panorama.x1_um, panorama.x2_um, panorama.x3_um, panorama.x4_um)
        y = min(panorama.y1_um, panorama.y2_um, panorama.y3_um, panorama.y4_um)
        img = self._mcd_file.read_panorama(panorama)
        if x != panorama.x1_um:
            img = img[:, ::-1, :]
        if y != panorama.y1_um:
            img = img[::-1, :, :]
        return (x, y, panorama.width_um, panorama.height_um), img

    def read_acquisition(self, acquisition_id: int, channel_label: str) -> Tuple[ImageDimensions, np.ndarray]:
        acquisition = next(
            acquisition
            for slide in self._mcd_file.slides
            for acquisition in slide.acquisitions
            if acquisition.id == acquisition_id
        )
        channel_index = acquisition.channel_labels.index(channel_label)
        x = min(acquisition.start_x_um, acquisition.end_x_um)
        y = min(acquisition.start_y_um, acquisition.end_y_um)
        channel_img = self._mcd_file.read_acquisition(acquisition)[channel_index]
        if x != acquisition.start_x_um:
            channel_img = channel_img[:, ::-1]
        if y != acquisition.start_y_um:
            channel_img = channel_img[::-1, :]
        return (x, y, acquisition.width_um, acquisition.height_um), channel_img

    def __enter__(self) -> 'FileReaderBase':
        self._mcd_file = IMCMcdFile(self._path)
        self._mcd_file.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mcd_file.close()
        self._mcd_file = None

    @classmethod
    def accepts(cls, path: Union[str, Path]) -> bool:
        return Path(path).suffix.lower() == '.mcd'
