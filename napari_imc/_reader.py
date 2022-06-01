from typing import Optional

from napari.viewer import Viewer

from .imc_controller import IMCController
from .imc_widget import IMCWidget


def napari_get_reader(path):
    if isinstance(path, list):
        if any(not IMCController.is_imc_file(p) for p in path):
            return None
    elif not IMCController.is_imc_file(path):
        return None
    return reader_function


def reader_function(path):
    viewer = _get_viewer()
    if viewer is not None:
        imc_widget = _get_imc_widget(viewer)
        paths = [path] if not isinstance(path, list) else path
        for path in paths:
            imc_file = imc_widget.controller.open_imc_file(path)
            if imc_file is not None:
                for panorama in imc_file.panoramas:
                    if panorama.image_type == "Imported":
                        imc_widget.controller.show_imc_file_panorama(panorama)
        return [(None,)]  # empty layer sentinel
    return None


# TODO https://github.com/napari/napari/issues/2202
def _get_viewer() -> Optional[Viewer]:
    import inspect

    frame = inspect.currentframe().f_back
    while frame:
        instance = frame.f_locals.get("self")
        if instance is not None and isinstance(instance, Viewer):
            return instance
        frame = frame.f_back
    return None


def _get_imc_widget(viewer: Viewer) -> IMCWidget:
    # TODO https://github.com/napari/napari/issues/2203
    dock_widget = viewer.window._dock_widgets.get("Imaging Mass Cytometry")
    if dock_widget is not None:
        imc_widget = dock_widget.widget()
    else:
        imc_widget = IMCWidget(napari_viewer=viewer)
        viewer.window.add_dock_widget(imc_widget, name="Imaging Mass Cytometry")
    return imc_widget
