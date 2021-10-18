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
        xs_physical = [panorama.x1_um, panorama.x2_um, panorama.x3_um, panorama.x4_um]
        ys_physical = [panorama.y1_um, panorama.y2_um, panorama.y3_um, panorama.y4_um]
        x_physical, y_physical = min(xs_physical), min(ys_physical)
        w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
        data = self._mcd_file.read_panorama(panorama)
        if x_physical != panorama.x1_um:
            data = data[:, ::-1, :]
        if y_physical != panorama.y1_um:
            data = data[::-1, :, :]
        return (x_physical, y_physical, w_physical, h_physical), data

    def read_acquisition(self, acquisition_id: int, channel_label: str) -> Tuple[ImageDimensions, np.ndarray]:
        acquisition = next(
            acquisition
            for slide in self._mcd_file.slides
            for acquisition in slide.acquisitions
            if acquisition.id == acquisition_id
        )
        channel_index = acquisition.channel_labels.index(channel_label)
        xs_physical = [acquisition.start_x_um, acquisition.end_x_um]
        ys_physical = [acquisition.start_y_um, acquisition.end_y_um]
        x_physical, y_physical = min(xs_physical), min(ys_physical)
        w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
        channel_img = self._mcd_file.read_acquisition(acquisition)[channel_index]
        if x_physical != acquisition.start_x_um:
            channel_img = channel_img[:, ::-1]
        if y_physical != acquisition.start_y_um:
            channel_img = channel_img[::-1, :]
        return (x_physical, y_physical, w_physical, h_physical), channel_img

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
