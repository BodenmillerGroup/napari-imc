import numpy as np

from imageio import imread
from pathlib import Path
from typing import List, Optional, Tuple, Union

from ..io.base import FileReaderBase, ImageDimensions
from ..models import (
    IMCFileModel,
    IMCFileAcquisitionModel,
    IMCFilePanoramaModel,
)

try:
    import zarr
except Exception:
    zarr = None


class ImaxtFileReader(FileReaderBase):
    def __init__(self, path: Union[str, Path]) -> None:
        super(ImaxtFileReader, self).__init__(self._get_zarr_path(path))
        self._zarr_group: Optional["zarr.hierarchy.Group"] = None

    def _get_imc_file_panoramas(
        self, imc_file: IMCFileModel
    ) -> List[IMCFilePanoramaModel]:
        return [
            IMCFilePanoramaModel(
                imc_file, panorama["id"], panorama["type"], panorama["description"]
            )
            for panorama in self._zarr_group.attrs["meta"]["panoramas"]
            if panorama["type"] != "Default"
        ]

    def _get_imc_file_acquisitions(
        self, imc_file: IMCFileModel
    ) -> List[IMCFileAcquisitionModel]:
        return [
            IMCFileAcquisitionModel(
                imc_file,
                acquisition["id"],
                acquisition["description"],
                [channel["target"] for channel in acquisition["channels"]],
            )
            for acquisition in self._zarr_group.attrs["meta"]["acquisitions"]
        ]

    def read_panorama(self, panorama_id: int) -> Tuple[ImageDimensions, np.ndarray]:
        # FIXME change to new ImageDimensions model
        raise NotImplementedError()
        panorama = next(
            filter(
                lambda x: x["id"] == panorama_id,
                self._zarr_group.attrs["meta"]["panoramas"],
            )
        )
        data = imread(self._path / Path(panorama["file"]))
        xs_physical = [x for x, y in panorama["slide_pos_um"]]
        ys_physical = [y for x, y in panorama["slide_pos_um"]]
        x_physical, y_physical = min(xs_physical), min(ys_physical)
        w_physical, h_physical = (
            max(xs_physical) - x_physical,
            max(ys_physical) - y_physical,
        )
        if x_physical != xs_physical[0]:
            data = data[:, ::-1, :]
        if y_physical != ys_physical[0]:
            data = data[::-1, :, :]
        return (x_physical, y_physical, w_physical, h_physical), data

    def read_acquisition(
        self, acquisition_id: int, channel_label: str
    ) -> Tuple[ImageDimensions, np.ndarray]:
        # FIXME change to new ImageDimensions model
        raise NotImplementedError()
        acquisition = next(
            filter(
                lambda x: x["id"] == acquisition_id,
                self._zarr_group.attrs["meta"]["acquisitions"],
            )
        )
        channel_index = [
            channel["target"] for channel in acquisition["channels"]
        ].index(channel_label)
        xs_physical = [
            acquisition["roi_start_pos_um"][0] / 1000,
            acquisition["roi_end_pos_um"][0],
        ]
        ys_physical = [
            acquisition["roi_start_pos_um"][1] / 1000,
            acquisition["roi_end_pos_um"][1],
        ]
        x_physical, y_physical = min(xs_physical), min(ys_physical)
        w_physical, h_physical = (
            max(xs_physical) - x_physical,
            max(ys_physical) - y_physical,
        )
        acquisition_group = self._zarr_group[acquisition["group"]]
        channel_index = list(acquisition_group["channel"]).index(channel_index)
        data = acquisition_group[acquisition["group"]][channel_index]
        if x_physical != xs_physical[0]:
            data = data[:, ::-1]
        if y_physical != ys_physical[0]:
            data = data[::-1, :]
        return (x_physical, y_physical, w_physical, h_physical), data

    def __enter__(self) -> "FileReaderBase":
        self._zarr_group = zarr.open_group(str(self._path), mode="r")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def accepts(cls, path: Union[str, Path]) -> bool:
        if zarr:
            try:
                with zarr.open_group(
                    str(cls._get_zarr_path(path)), mode="r"
                ) as zarr_group:
                    meta = zarr_group.attrs.get("meta")
                    if meta is not None:
                        return meta.get("scan_type") == "IMC"
            except Exception:
                pass  # ignored intentionally
        return False

    @staticmethod
    def _get_zarr_path(path: Union[str, Path]) -> Path:
        path = Path(path)
        if path.is_file() and path.name == "mcd_schema.xml":
            path = path.parent
        return path
