from napari._qt import QHRangeSlider  # TODO
from napari.layers.base.base import Blending
from napari.layers.image.image import Image, Interpolation
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QComboBox, QFormLayout, QSlider, QWidget
from typing import List, Tuple

from napari_imc.widgets import ColorPicker
from napari_imc.widgets.utils import create_imc_acquisition_colormap


class IMCChannelControlsWidget(QWidget):
    opacity_slider_factor = 100
    gamma_slider_factor = 100

    def __init__(self, parent=None):
        super(IMCChannelControlsWidget, self).__init__(parent)
        self.layers: List[Image] = []

        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        # noinspection PyUnresolvedReferences
        self.opacity_slider.valueChanged.connect(self.on_opacity_slider_value_changed)

        self.contrast_range_slider = QHRangeSlider(parent=self)
        # noinspection PyUnresolvedReferences
        self.contrast_range_slider.valuesChanged.connect(self.on_contrast_range_slider_values_changed)

        self.gamma_slider = QSlider(Qt.Horizontal, self)
        self.gamma_slider.setMinimum(2)
        self.gamma_slider.setMaximum(200)
        # noinspection PyUnresolvedReferences
        self.gamma_slider.valueChanged.connect(self.on_gamma_slider_value_changed)

        self.color_picker = ColorPicker()
        self.color_picker.color_changed.connect(self.on_color_picker_color_changed)

        self.blending_combo_box = QComboBox(self)
        self.blending_combo_box.addItems(Blending.keys())
        # noinspection PyUnresolvedReferences
        self.blending_combo_box.activated[str].connect(self.on_blending_combo_box_activated)

        self.interpolation_combo_box = QComboBox(self)
        self.interpolation_combo_box.addItems(Interpolation.keys())
        # noinspection PyUnresolvedReferences
        self.interpolation_combo_box.activated[str].connect(self.on_interpolation_combo_box_activated)

        layout = QFormLayout(self)
        layout.addRow('Opacity:', self.opacity_slider)
        layout.addRow('Contrast:', self.contrast_range_slider)
        layout.addRow('Gamma:', self.gamma_slider)
        layout.addRow('Color:', self.color_picker)
        layout.addRow('Blending:', self.blending_combo_box)
        layout.addRow('Interpolation:', self.interpolation_combo_box)
        self.setLayout(layout)
        self.refresh()

    def on_opacity_slider_value_changed(self, value: int):
        for layer in self.layers:
            layer.opacity = value / 100

    def on_contrast_range_slider_values_changed(self, values: Tuple[float, float]):
        for layer in self.layers:
            layer.contrast_limits = values

    def on_gamma_slider_value_changed(self, value: int):
        for layer in self.layers:
            layer.gamma = value / 100

    def on_color_picker_color_changed(self, color: QColor):
        for layer in self.layers:
            layer.colormap = create_imc_acquisition_colormap(
                color.red() / 255,
                color.green() / 255,
                color.blue() / 255,
                color.alpha() / 255
            )

    def on_blending_combo_box_activated(self, text: str):
        for layer in self.layers:
            layer.blending = text

    def on_interpolation_combo_box_activated(self, text: str):
        for layer in self.layers:
            layer.interpolation = text

    def refresh(self):
        if len(self.layers) > 0:
            self.opacity_slider.blockSignals(True)
            mean_opacity = sum(layer.opacity for layer in self.layers) / len(self.layers)
            self.opacity_slider.setValue(int(mean_opacity * self.opacity_slider_factor))
            self.opacity_slider.blockSignals(False)

            self.contrast_range_slider.blockSignals(True)
            contrast_limits_min = min(layer.contrast_limits[0] for layer in self.layers)
            contrast_limits_max = max(layer.contrast_limits[1] for layer in self.layers)
            contrast_limits_range_min = min(layer.contrast_limits_range[0] for layer in self.layers)
            contrast_limits_range_max = max(layer.contrast_limits_range[1] for layer in self.layers)
            self.contrast_range_slider.setRange((contrast_limits_range_min, contrast_limits_range_max))
            self.contrast_range_slider.setValues((contrast_limits_min, contrast_limits_max))
            self.contrast_range_slider.blockSignals(False)

            self.gamma_slider.blockSignals(True)
            mean_gamma = sum(layer.gamma for layer in self.layers) / len(self.layers)
            self.gamma_slider.setValue(int(mean_gamma * self.gamma_slider_factor))
            self.gamma_slider.blockSignals(False)

            self.color_picker.blockSignals(True)
            r, g, b, a = self.layers[0].colormap.colors[-1, :]
            self.color_picker.color = QColor(int(r * 255), int(g * 255), int(b * 255), int(a * 255))
            self.color_picker.blockSignals(False)

            self.blending_combo_box.blockSignals(True)
            first_layer_blending_index = self.blending_combo_box.findText(self.layers[0].blending, Qt.MatchFixedString)
            self.blending_combo_box.setCurrentIndex(first_layer_blending_index)
            self.blending_combo_box.blockSignals(False)

            self.interpolation_combo_box.blockSignals(True)
            first_layer_interpolation_index = self.interpolation_combo_box.findText(self.layers[0].interpolation,
                                                                                    Qt.MatchFixedString)
            self.interpolation_combo_box.setCurrentIndex(first_layer_interpolation_index)
            self.interpolation_combo_box.blockSignals(False)

            self.show()
        else:
            self.hide()
