try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .imc_widget import IMCWidget
from ._reader import napari_get_reader
from ._dock_widget import napari_experimental_provide_dock_widget

__all__ = [
    "IMCWidget",
    "napari_get_reader",
    "napari_experimental_provide_dock_widget",
]
