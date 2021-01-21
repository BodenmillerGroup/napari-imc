import napari
import sys

from napari_imc.widgets import IMCWidget


def main():
    with napari.gui_qt():
        viewer = napari.Viewer(title='napari [IMC]')
        viewer.window.add_dock_widget(IMCWidget(), name='Imaging mass cytometry', area='right')


if __name__ == '__main__':
    sys.exit(main())
