try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from napari_imc.imc_widget import IMCWidget
from napari_imc._reader import napari_get_reader
from napari_imc._dock_widget import napari_experimental_provide_dock_widget

__all__ = [
    'IMCWidget',
    'napari_get_reader',
    'napari_experimental_provide_dock_widget',
]
