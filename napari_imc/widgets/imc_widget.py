import napari

from imageio import imread
from imctools.io.mcd.mcdparser import McdParser
from imctools.io.txt.txtparser import TxtParser
from pathlib import Path
from qtpy.QtCore import Qt, QItemSelection, QModelIndex, QSortFilterProxyModel
from qtpy.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QSplitter, QWidget
from typing import Optional

from napari_imc.widgets import IMCChannelControlsWidget, IMCChannelTableView, IMCFileTreeView
from napari_imc.widgets.models import IMCChannelTableModel, IMCFileTreeModel
from napari_imc.widgets.utils import create_imc_acquisition_colormap


class IMCWidget(QWidget):
    def __init__(self, parent=None):
        super(IMCWidget, self).__init__(parent)

        self.open_imc_file_button = QPushButton('Open IMC file', self)
        # noinspection PyUnresolvedReferences
        self.open_imc_file_button.clicked.connect(self.on_open_imc_file_button_clicked)

        self.imc_file_tree_model = IMCFileTreeModel(self)
        # noinspection PyUnresolvedReferences
        self.imc_file_tree_model.dataChanged.connect(self.on_imc_file_tree_model_data_changed)
        self.imc_file_tree_view = IMCFileTreeView(self)
        self.imc_file_tree_view.setModel(self.imc_file_tree_model)

        self.imc_channel_table_model = IMCChannelTableModel(self)
        # noinspection PyUnresolvedReferences
        self.imc_channel_table_model.dataChanged.connect(self.on_imc_channel_table_model_data_changed)
        self.imc_channel_table_proxy_model = QSortFilterProxyModel(self)
        self.imc_channel_table_proxy_model.setSourceModel(self.imc_channel_table_model)
        self.imc_channel_table_proxy_model.sort(self.imc_channel_table_model.label_column)
        self.imc_channel_table_view = IMCChannelTableView(self)
        self.imc_channel_table_view.setModel(self.imc_channel_table_proxy_model)
        imc_channel_table_selection_model = self.imc_channel_table_view.selectionModel()
        # noinspection PyUnresolvedReferences
        imc_channel_table_selection_model.selectionChanged.connect(self.on_imc_channel_table_view_selection_changed)

        self.imc_channel_controls_widget = IMCChannelControlsWidget(self)

        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical, self)
        imc_file_widget = QWidget(self)
        imc_file_widget_layout = QVBoxLayout(imc_file_widget)
        imc_file_widget_layout.addWidget(self.open_imc_file_button)
        imc_file_widget_layout.addWidget(self.imc_file_tree_view)
        imc_file_widget.setLayout(imc_file_widget_layout)
        splitter.addWidget(imc_file_widget)
        splitter.setStretchFactor(0, 1)
        imc_channel_widget = QWidget(self)
        imc_channel_widget_layout = QVBoxLayout(imc_channel_widget)
        imc_channel_widget_layout.addWidget(self.imc_channel_table_view)
        imc_channel_widget_layout.addWidget(self.imc_channel_controls_widget)
        imc_channel_widget.setLayout(imc_channel_widget_layout)
        splitter.addWidget(imc_channel_widget)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def on_open_imc_file_button_clicked(self, checked: bool = False):
        files, _ = QFileDialog.getOpenFileNames(parent=self, filter='Imaging mass cytometry files (*.txt *.mcd)')
        for file in files:
            path = Path(file)
            if path.suffix.lower() == '.mcd':
                with McdParser(path) as parser:
                    panoramas = [p for p in parser.session.panoramas.values() if p.image_type != 'Default']
                    acquisitions = [a for a in parser.session.acquisitions.values() if a.is_valid]
                    self.imc_file_tree_model.add_imc_file(path, panoramas, acquisitions)
            elif path.suffix.lower() == '.txt':
                with TxtParser(path) as parser:
                    acquisition_data = parser.get_acquisition_data()
                    self.imc_file_tree_model.add_imc_file(path, [], [acquisition_data.acquisition])

    def on_imc_file_tree_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex,
                                            roles: Optional[int] = None):
        item = top_left.internalPointer()
        if isinstance(item, IMCFileTreeModel.PanoramaItem):
            if item.checked:
                self.add_panorama_layer(item.imc_file_item.path, item.panorama.id)
            else:
                self.remove_panorama_layer(item.imc_file_item.path, item.panorama.id)
        elif isinstance(item, IMCFileTreeModel.AcquisitionItem):
            path = item.imc_file_item.path
            if item.checked:
                for channel in self.imc_channel_table_model.add_acquisition(path, item.acquisition):
                    self.add_acquisition_layer(path, item.acquisition.id, channel.label)
            else:
                for channel in self.imc_channel_table_model.remove_acquisition(path, item.acquisition):
                    self.remove_acquisition_layer(path, item.acquisition.id, channel.label)

    def on_imc_channel_table_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex,
                                                roles: Optional[int] = None):
        item = self.imc_channel_table_model.items[top_left.row()]
        if item.checked:
            for path, acquisition_id in item.shown_acquisitions:
                self.add_acquisition_layer(path, acquisition_id, item.channel_label)
        else:
            for path, acquisition_id in item.shown_acquisitions:
                self.remove_acquisition_layer(path, acquisition_id, item.channel_label)
        self.refresh_imc_channel_controls_widget()

    def on_imc_channel_table_view_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        self.refresh_imc_channel_controls_widget()

    def add_panorama_layer(self, path: Path, panorama_id: int):
        with McdParser(path) as parser:
            panorama = parser.session.panoramas[panorama_id]
            xs_physical = [panorama.x1, panorama.x2, panorama.x3, panorama.x4]
            ys_physical = [panorama.y1, panorama.y2, panorama.y3, panorama.y4]
            x_physical, y_physical = min(xs_physical), min(ys_physical)
            w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
            data = imread(parser.get_panorama_image(panorama.id))
            if x_physical != panorama.x1:
                data = data[:, ::-1, :]
            if y_physical != panorama.y1:
                data = data[::-1, :, :]
        self.viewer.add_image(
            data,
            name=f'{path.name} [P{panorama.id:02d}]',
            metadata={
                'imc_panorama_layer': True,
                'path': path,
                'panorama_id': panorama_id
            },
            scale=(h_physical / data.shape[0], w_physical / data.shape[1]),
            translate=(y_physical, x_physical),
        )

    def remove_panorama_layer(self, path: Path, panorama_id: int):
        layers_to_remove = []
        for layer in self.viewer.layers:
            imc_panorama_layer = layer.metadata.get('imc_panorama_layer', False)
            path_matching = (layer.metadata.get('path') == path)
            panorama_id_matching = (layer.metadata.get('panorama_id') == panorama_id)
            if imc_panorama_layer and path_matching and panorama_id_matching:
                layers_to_remove.append(layer)
        for layer in layers_to_remove:
            self.viewer.layers.remove(layer)

    def add_acquisition_layer(self, path: Path, acquisition_id: int, channel_label: str):
        if path.suffix.lower() == '.mcd':
            with McdParser(path) as parser:
                acquisition = parser.session.acquisitions[acquisition_id]
                xs_physical = [acquisition.roi_start_x_pos_um, acquisition.roi_end_x_pos_um]
                ys_physical = [acquisition.roi_start_y_pos_um, acquisition.roi_end_y_pos_um]
                x_physical, y_physical = min(xs_physical), min(ys_physical, default=0)
                w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
                data = parser.get_acquisition_data(acquisition.id).get_image_by_label(channel_label)
                if x_physical != acquisition.roi_start_x_pos_um:
                    data = data[:, ::-1]
                if y_physical != acquisition.roi_start_y_pos_um:
                    data = data[::-1, :]
        elif path.suffix.lower() == '.txt':
            with TxtParser(path) as parser:
                acquisition_data = parser.get_acquisition_data()
                acquisition = acquisition_data.acquisition
                x_physical, y_physical = 0, 0
                w_physical, h_physical = acquisition.max_x, acquisition.max_y
                data = acquisition_data.get_image_by_label(channel_label)
        self.viewer.add_image(
            data,
            colormap=create_imc_acquisition_colormap(1., 1., 1., 1.),
            contrast_limits=(0, data.max()),  # sets contrast_limits_range
            name=f'{path.name} [A{acquisition_id:02d} {channel_label}]',
            metadata={
                'imc_acquisition_layer': True,
                'path': path,
                'acquisition_id': acquisition_id,
                'channel_label': channel_label
            },
            scale=(h_physical / data.shape[0], w_physical / data.shape[1]),
            translate=(y_physical, x_physical),
            blending='additive',
        )

    def remove_acquisition_layer(self, path: Path, acquisition_id: int, channel_label: str):
        layers_to_remove = []
        for layer in self.viewer.layers:
            imc_acquisition_layer = layer.metadata.get('imc_acquisition_layer', False)
            path_matching = (layer.metadata.get('path') == path)
            acquisition_id_matching = (layer.metadata.get('acquisition_id') == acquisition_id)
            channel_label_matching = (layer.metadata.get('channel_label') == channel_label)
            if imc_acquisition_layer and path_matching and acquisition_id_matching and channel_label_matching:
                layers_to_remove.append(layer)
        for layer in layers_to_remove:
            self.viewer.layers.remove(layer)

    def refresh_imc_channel_controls_widget(self):
        self.imc_channel_controls_widget.layers.clear()
        for index in self.imc_channel_table_view.selectedIndexes():
            index = self.imc_channel_table_proxy_model.mapToSource(index)
            item = self.imc_channel_table_model.items[index.row()]
            for layer in self.viewer.layers:
                imc_acquisition_layer = layer.metadata.get('imc_acquisition_layer', False)
                channel_label_matching = (layer.metadata.get('channel_label') == item.channel_label)
                if imc_acquisition_layer and channel_label_matching:
                    self.imc_channel_controls_widget.layers.append(layer)
        self.imc_channel_controls_widget.refresh()

    @property
    def viewer(self) -> napari.Viewer:
        return self.parent().qt_viewer.viewer
