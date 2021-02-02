from napari._qt import QHRangeSlider
from napari.layers.base.base import Blending
from napari.layers.image.image import Interpolation
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QComboBox, QFormLayout, QSlider, QWidget
from typing import Optional, Tuple, TYPE_CHECKING

from napari_imc.widgets._color_picker import ColorPicker

if TYPE_CHECKING:
    from napari_imc.imc_controller import IMCController


class ChannelControlsWidget(QWidget):
    def __init__(self, controller: 'IMCController', parent: Optional[QWidget] = None):
        super(ChannelControlsWidget, self).__init__(parent)
        self._controller = controller

        self._opacity_slider = QSlider(Qt.Horizontal, self)
        self._opacity_slider.setMinimum(0)
        self._opacity_slider.setMaximum(100)

        self._contrast_range_slider = QHRangeSlider(parent=self)

        self._gamma_slider = QSlider(Qt.Horizontal, self)
        self._gamma_slider.setMinimum(2)
        self._gamma_slider.setMaximum(200)

        self._color_picker = ColorPicker(self)

        self._blending_combo_box = QComboBox(self)
        self._blending_combo_box.addItems(Blending.keys())

        self._interpolation_combo_box = QComboBox(self)
        self._interpolation_combo_box.addItems(Interpolation.keys())

        layout = QFormLayout(self)
        layout.addRow('Opacity:', self._opacity_slider)
        layout.addRow('Contrast:', self._contrast_range_slider)
        layout.addRow('Gamma:', self._gamma_slider)
        layout.addRow('Color:', self._color_picker)
        layout.addRow('Blending:', self._blending_combo_box)
        layout.addRow('Interpolation:', self._interpolation_combo_box)
        self.setLayout(layout)

        # noinspection PyUnresolvedReferences
        @self._opacity_slider.valueChanged.connect
        def on_opacity_slider_value_changed(value: int):
            for channel in self._controller.selected_channels:
                channel.opacity = value / 100

        # noinspection PyUnresolvedReferences
        @self._contrast_range_slider.valuesChanged.connect
        def on_contrast_range_slider_values_changed(values: Tuple[float, float]):
            for channel in self._controller.selected_channels:
                contrast_limits_range_min = min(
                    (layer.contrast_limits_range[0] for layer in channel.shown_imc_file_acquisition_layers.values()),
                    default=values[0]
                )
                contrast_limits_range_max = max(
                    (layer.contrast_limits_range[1] for layer in channel.shown_imc_file_acquisition_layers.values()),
                    default=values[1]
                )
                channel.contrast_limits = (
                    max(values[0], contrast_limits_range_min),
                    min(values[1], contrast_limits_range_max)
                )

        # noinspection PyUnresolvedReferences
        @self._gamma_slider.valueChanged.connect
        def on_gamma_slider_value_changed(value: int):
            for channel in self._controller.selected_channels:
                channel.gamma = value / 100

        # noinspection PyUnresolvedReferences
        @self._color_picker.events.color_changed.connect
        def on_color_picker_color_changed(color: QColor):
            for channel in self._controller.selected_channels:
                channel.color = (color.red() / 255, color.green() / 255, color.blue() / 255, color.alpha() / 255)

        # noinspection PyUnresolvedReferences
        blending_combo_box_activated = self._blending_combo_box.activated[str]

        # noinspection PyUnresolvedReferences
        @blending_combo_box_activated.connect
        def on_blending_combo_box_activated(text: str):
            for channel in self._controller.selected_channels:
                channel.blending = text

        # noinspection PyUnresolvedReferences
        interpolation_combo_box_activated = self._interpolation_combo_box.activated[str]

        # noinspection PyUnresolvedReferences
        @interpolation_combo_box_activated.connect
        def on_interpolation_combo_box_activated(text: str):
            for channel in self._controller.selected_channels:
                channel.interpolation = text

        self.refresh()

    def refresh(self):
        channels = self._controller.selected_channels
        if len(channels) > 0:
            mean_opacity = sum(channel.opacity for channel in channels) / len(channels)
            self._opacity_slider.blockSignals(True)
            self._opacity_slider.setValue(int(mean_opacity * 100))
            self._opacity_slider.blockSignals(False)

            contrast_limits_channels = [channel for channel in channels if channel.contrast_limits is not None]
            if len(contrast_limits_channels) > 0:
                layers = [layer for channel in channels for layer in channel.shown_imc_file_acquisition_layers.values()]
                if len(layers) > 0:
                    contrast_limits_min = min(channel.contrast_limits[0] for channel in contrast_limits_channels)
                    contrast_limits_max = max(channel.contrast_limits[1] for channel in contrast_limits_channels)
                    contrast_limits_range_min = min(layer.contrast_limits_range[0] for layer in layers)
                    contrast_limits_range_max = max(layer.contrast_limits_range[1] for layer in layers)
                    contrast_limits_min = max(contrast_limits_min, contrast_limits_range_min)
                    contrast_limits_max = min(contrast_limits_max, contrast_limits_range_max)
                    self._contrast_range_slider.blockSignals(True)
                    self._contrast_range_slider.setRange((contrast_limits_range_min, contrast_limits_range_max))
                    self._contrast_range_slider.setValues((contrast_limits_min, contrast_limits_max))
                    self._contrast_range_slider.blockSignals(False)

            mean_gamma = sum(channel.gamma for channel in channels) / len(channels)
            self._gamma_slider.blockSignals(True)
            self._gamma_slider.setValue(int(mean_gamma * 100))
            self._gamma_slider.blockSignals(False)

            color = tuple(int(x * 255) for x in channels[0].color)
            self._color_picker.blockSignals(True)
            self._color_picker.color = QColor(*color)
            self._color_picker.blockSignals(False)

            index = self._blending_combo_box.findText(channels[0].blending, Qt.MatchFixedString)
            self._blending_combo_box.blockSignals(True)
            self._blending_combo_box.setCurrentIndex(index)
            self._blending_combo_box.blockSignals(False)

            index = self._interpolation_combo_box.findText(channels[0].interpolation, Qt.MatchFixedString)
            self._interpolation_combo_box.blockSignals(True)
            self._interpolation_combo_box.setCurrentIndex(index)
            self._interpolation_combo_box.blockSignals(False)
