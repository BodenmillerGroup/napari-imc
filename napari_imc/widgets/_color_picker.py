from typing import Optional

from qtpy.QtCore import QObject, Qt, Signal
from qtpy.QtGui import QColor, qGray
from qtpy.QtWidgets import QColorDialog, QMenu, QPushButton, QWidget, QWidgetAction


class ColorPicker(QPushButton):
    class Events(QObject):
        color_changed = Signal(QColor)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(ColorPicker, self).__init__(parent)
        self.events = ColorPicker.Events()
        self.setAutoFillBackground(True)

        self._color_dialog = QColorDialog(self)
        self._color_dialog.setWindowFlags(Qt.WindowType.Widget)
        self._color_dialog.setOptions(
            QColorDialog.ColorDialogOption.DontUseNativeDialog
            | QColorDialog.ColorDialogOption.NoButtons
        )

        self._menu = QMenu(self)
        action = QWidgetAction(self)
        action.setDefaultWidget(self._color_dialog)
        self._menu.addAction(action)
        self.setMenu(self._menu)

        self._menu.aboutToShow.connect(lambda: self._color_dialog.show())
        self._color_dialog.currentColorChanged.connect(self.events.color_changed)
        self._color_dialog.currentColorChanged.connect(lambda color: self.update())

        self.update()

    def update(self):
        color = self._color_dialog.currentColor()
        self.setText(color.name())
        text_color_name = "black" if qGray(color.rgb()) > 127 else "white"
        self.setStyleSheet(
            "ColorPicker "
            f"{{ color: {text_color_name}; background-color: {color.name()}; }}"
        )
        super(ColorPicker, self).update()

    @property
    def color(self) -> QColor:
        return self._color_dialog.currentColor()

    @color.setter
    def color(self, color: QColor):
        self._color_dialog.setCurrentColor(color)
