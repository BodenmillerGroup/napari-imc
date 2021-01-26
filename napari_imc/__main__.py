import napari
import sys

from napari_imc import IMCController


def main():
    with napari.gui_qt():
        viewer = napari.Viewer(title='napari [IMC]')
        controller = IMCController(viewer)
        controller.initialize()


if __name__ == '__main__':
    sys.exit(main())
