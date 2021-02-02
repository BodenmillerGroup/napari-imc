from napari_plugin_engine import napari_hook_implementation

from napari_imc.imc_widget import IMCWidget


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return IMCWidget, {'name': IMCWidget.NAME, 'area': IMCWidget.AREA, 'allowed_areas': IMCWidget.ALLOWED_AREAS}
