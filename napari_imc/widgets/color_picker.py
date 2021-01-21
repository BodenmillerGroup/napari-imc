from qtpy.QtCore import Qt
from qtpy.QtGui import QColor, qGray
from qtpy.QtWidgets import QColorDialog, QMenu, QPushButton, QWidgetAction


class ColorPicker(QPushButton):
    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)
        self.setAutoFillBackground(True)

        self.color_dialog = QColorDialog(self)
        self.color_dialog.setWindowFlags(Qt.Widget)
        self.color_dialog.setOptions(QColorDialog.DontUseNativeDialog | QColorDialog.NoButtons)

        self.menu = QMenu(self)
        action = QWidgetAction(self)
        action.setDefaultWidget(self.color_dialog)
        self.menu.addAction(action)
        self.setMenu(self.menu)

        # noinspection PyUnresolvedReferences
        self.menu.aboutToShow.connect(lambda: self.color_dialog.show())
        # noinspection PyUnresolvedReferences
        self.color_dialog.currentColorChanged.connect(self.on_color_dialog_current_color_changed)
        self.update()

    def on_color_dialog_current_color_changed(self, _: QColor):
        self.update()

    def update(self):
        color = self.color_dialog.currentColor()
        self.setText(color.name())
        text_color_name = 'black' if qGray(color.rgb()) > 127 else 'white'
        self.setStyleSheet(f'ColorPicker {{ color: {text_color_name}; background-color: {color.name()}; }}')
        super(ColorPicker, self).update()

    @property
    def color(self):
        return self.color_dialog.currentColor()

    @color.setter
    def color(self, color):
        self.color_dialog.setCurrentColor(color)

    @property
    def color_changed(self):
        return self.color_dialog.currentColorChanged
