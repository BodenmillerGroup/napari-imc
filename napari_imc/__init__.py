try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from napari_imc.imc_controller import IMCController

__all__ = [
    'IMCController',
]
