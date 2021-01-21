from napari.utils import Colormap


def create_imc_acquisition_colormap(r: float, g: float, b: float, a: float):
    return Colormap(name='IMC', colors=[[0., 0., 0., 0.], [r, g, b, a]], interpolation='linear')
