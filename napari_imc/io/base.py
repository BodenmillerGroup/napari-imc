import numpy as np

from abc import abstractmethod
from pathlib import Path
from typing import List, Tuple, Union

from napari_imc.models import IMCFileAcquisitionModel, IMCFilePanoramaModel

ImageDimensions = Tuple[float, float, float, float]


class FileReaderBase:
    suffixes = []

    def __init__(self, path: Union[str, Path]):
        self._path = Path(path)

    @abstractmethod
    def get_panoramas(self) -> List[IMCFilePanoramaModel]:
        pass

    @abstractmethod
    def get_acquisitions(self) -> List[IMCFileAcquisitionModel]:
        pass

    @abstractmethod
    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        pass

    @abstractmethod
    def read_acquisition(self, acquisition_id: int, channel_label: str) -> Tuple[ImageDimensions, np.ndarray]:
        pass

    @abstractmethod
    def __enter__(self) -> 'FileReaderBase':
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def accepts(cls, path: Union[str, Path]):
        return path.suffix.lower() in cls.suffixes
