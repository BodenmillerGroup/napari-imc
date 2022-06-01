from ._reader import napari_get_reader
from .imc_widget import IMCWidget

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__all__ = ["IMCWidget", "napari_get_reader"]
