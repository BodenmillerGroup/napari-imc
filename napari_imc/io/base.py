import numpy as np

from abc import abstractmethod
from pathlib import Path
from typing import List, Tuple, Union

from napari_imc.models import IMCFileModel, IMCFileAcquisitionModel, IMCFilePanoramaModel
from napari_imc.models.base import IMCFileTreeItem

ImageDimensions = Tuple[float, float, float, float]


class FileReaderBase:
    def __init__(self, path: Union[str, Path]):
        self._path = Path(path)

    def get_imc_file(self, imc_file_tree_root_item: IMCFileTreeItem) -> IMCFileModel:
        imc_file = IMCFileModel(self._path, imc_file_tree_root_item)
        imc_file.panoramas.extend(self._get_imc_file_panoramas(imc_file))
        imc_file.acquisitions.extend(self._get_imc_file_acquisitions(imc_file))
        return imc_file

    @abstractmethod
    def _get_imc_file_panoramas(self, imc_file: IMCFileModel) -> List[IMCFilePanoramaModel]:
        pass

    @abstractmethod
    def _get_imc_file_acquisitions(self, imc_file: IMCFileModel) -> List[IMCFileAcquisitionModel]:
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
    def accepts(cls, path: Union[str, Path]) -> bool:
        return False
