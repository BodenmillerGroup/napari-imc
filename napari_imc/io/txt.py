import numpy as np
import re

from pathlib import Path
from readimc import TXTFile
from typing import List, Optional, Tuple, Union

from ..io.base import FileReaderBase, ImageDimensions
from ..models import (
    IMCFileModel,
    IMCFileAcquisitionModel,
    IMCFilePanoramaModel,
)


class TxtFileReader(FileReaderBase):
    def __init__(self, path: Union[str, Path]) -> None:
        super(TxtFileReader, self).__init__(path)
        self._txt_file: Optional[TXTFile] = None

    def _get_imc_file_panoramas(
        self, imc_file: IMCFileModel
    ) -> List[IMCFilePanoramaModel]:
        return []

    def _get_imc_file_acquisitions(
        self, imc_file: IMCFileModel
    ) -> List[IMCFileAcquisitionModel]:
        m = re.match(r"(?P<description>.*)_(?P<id>[0-9]+)", self._path.stem)
        acquisition_id = int(m.group("id")) if m is not None else 0
        acquisition_description = (
            m.group("description") if m is not None else self._path.stem
        )
        return [
            IMCFileAcquisitionModel(
                imc_file,
                acquisition_id,
                acquisition_description,
                self._txt_file.channel_labels,
            )
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        raise RuntimeError("This operation is not supported")

    def read_acquisition(
        self, acquisition_id: int, channel_label: str
    ) -> Tuple[ImageDimensions, np.ndarray]:
        img = self._txt_file.read_acquisition()[
            self._txt_file.channel_labels.index(channel_label), ::-1, :
        ]
        dims = ImageDimensions(0, 0, img.shape[1], img.shape[0])
        return dims, img

    def __enter__(self) -> "FileReaderBase":
        self._txt_file = TXTFile(self._path)
        self._txt_file.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._txt_file.close()
        self._txt_file = None

    @classmethod
    def accepts(cls, path: Union[str, Path]) -> bool:
        return Path(path).suffix.lower() == ".txt"
