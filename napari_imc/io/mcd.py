import numpy as np

from pathlib import Path
from readimc import MCDFile
from typing import List, Optional, Tuple, Union

from ..io.base import FileReaderBase, ImageDimensions
from ..models import (
    IMCFileModel,
    IMCFileAcquisitionModel,
    IMCFilePanoramaModel,
)


class McdFileReader(FileReaderBase):
    def __init__(self, path: Union[str, Path]) -> None:
        super(McdFileReader, self).__init__(path)
        self._mcd_file: Optional[MCDFile] = None

    def _get_imc_file_panoramas(
        self, imc_file: IMCFileModel
    ) -> List[IMCFilePanoramaModel]:
        return [
            IMCFilePanoramaModel(
                imc_file,
                panorama.id,
                panorama.metadata.get("Type"),
                panorama.description,
            )
            for slide in self._mcd_file.slides
            for panorama in slide.panoramas
        ]

    def _get_imc_file_acquisitions(
        self, imc_file: IMCFileModel
    ) -> List[IMCFileAcquisitionModel]:
        return [
            IMCFileAcquisitionModel(
                imc_file,
                acquisition.id,
                acquisition.description,
                acquisition.channel_labels,
            )
            for slide in self._mcd_file.slides
            for acquisition in slide.acquisitions
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        panorama = next(
            panorama
            for slide in self._mcd_file.slides
            for panorama in slide.panoramas
            if panorama.id == panorama_id
        )
        img = self._mcd_file.read_panorama(panorama)[::-1, :]
        rotation = -np.arctan2(
            panorama.points_um[1][1] - panorama.points_um[0][1],
            panorama.points_um[1][0] - panorama.points_um[0][0],
        )
        dims = ImageDimensions(
            panorama.points_um[0][0],
            panorama.points_um[0][1] - panorama.height_um,
            panorama.width_um,
            panorama.height_um,
            rotation=rotation,
        )
        return dims, img

    def read_acquisition(
        self, acquisition_id: int, channel_label: str
    ) -> Tuple[ImageDimensions, np.ndarray]:
        acquisition = next(
            acquisition
            for slide in self._mcd_file.slides
            for acquisition in slide.acquisitions
            if acquisition.id == acquisition_id
        )
        img = self._mcd_file.read_acquisition(acquisition)[
            acquisition.channel_labels.index(channel_label), ::-1, :
        ]
        rotation = -np.arctan2(
            acquisition.roi_points_um[1][1] - acquisition.roi_points_um[0][1],
            acquisition.roi_points_um[1][0] - acquisition.roi_points_um[0][0],
        )
        dims = ImageDimensions(
            acquisition.roi_points_um[0][0],
            acquisition.roi_points_um[0][1] - acquisition.height_um,
            acquisition.width_um,
            acquisition.height_um,
            rotation=rotation,
        )
        return dims, img

    def __enter__(self) -> "FileReaderBase":
        self._mcd_file = MCDFile(self._path)
        self._mcd_file.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mcd_file.close()
        self._mcd_file = None

    @classmethod
    def accepts(cls, path: Union[str, Path]) -> bool:
        return Path(path).suffix.lower() == ".mcd"
