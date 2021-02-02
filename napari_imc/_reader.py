from napari import Viewer
from napari_plugin_engine import napari_hook_implementation
from pathlib import Path
from typing import Optional

from napari_imc.imc_widget import IMCWidget
from napari_imc.imc_controller import IMCController


@napari_hook_implementation
def napari_get_reader(path):
    suffixes = [suffix.lower() for file_reader in IMCController.FILE_READERS for suffix in file_reader.suffixes]
    if isinstance(path, list):
        if any(Path(p).suffix.lower() not in suffixes for p in path):
            return None
    elif Path(path).suffix.lower() not in suffixes:
        return None
    return reader_function


def reader_function(path):
    viewer = _get_viewer()
    if viewer is not None:
        imc_widget = _get_imc_widget(viewer)
        paths = [path] if not isinstance(path, list) else path
        for path in paths:
            imc_widget.controller.open_imc_file(path)
        return []
    return None


# TODO https://github.com/napari/napari/issues/2202
def _get_viewer() -> Optional[Viewer]:
    import inspect
    frame = inspect.currentframe().f_back
    while frame:
        instance = frame.f_locals.get('self')
        if instance is not None and isinstance(instance, Viewer):
            return instance
        frame = frame.f_back
    return None


def _get_imc_widget(viewer: Viewer) -> IMCWidget:
    # noinspection PyProtectedMember
    # TODO https://github.com/napari/napari/issues/2203
    dock_widget = viewer.window._dock_widgets.get(IMCWidget.FULL_NAME)
    if dock_widget is not None:
        imc_widget = dock_widget.widget()
    else:
        imc_widget = IMCWidget(napari_viewer=viewer, parent=viewer.window.qt_viewer)
        viewer.window.add_dock_widget(imc_widget, name=IMCWidget.FULL_NAME, area=IMCWidget.AREA,
                                      allowed_areas=IMCWidget.ALLOWED_AREAS)
    return imc_widget
