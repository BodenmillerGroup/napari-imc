from pathlib import Path
from qtpy.QtCore import Qt, QItemSelection, QItemSelectionModel, QModelIndex, QSortFilterProxyModel
from qtpy.QtWidgets import QFileDialog, QPushButton, QSizePolicy, QSplitter, QStackedWidget, QVBoxLayout, QWidget
from typing import Optional, TYPE_CHECKING

from napari_imc.models import IMCFileModel, IMCFileAcquisitionModel, IMCFilePanoramaModel
from napari_imc.widgets.channel_controls_widget import ChannelControlsWidget
from napari_imc.widgets.channel_table_model import ChannelTableModel
from napari_imc.widgets.channel_table_view import ChannelTableView
from napari_imc.widgets.imc_file_tree_model import IMCFileTreeModel
from napari_imc.widgets.imc_file_tree_view import IMCFileTreeView

if TYPE_CHECKING:
    from napari_imc import IMCController


class IMCWidget(QWidget):
    def __init__(self, controller: 'IMCController'):
        # noinspection PyArgumentList
        super(IMCWidget, self).__init__()
        self._controller = controller

        self._open_imc_file_button = QPushButton('Open IMC file', self)

        self._imc_file_tree_model = IMCFileTreeModel(controller, parent=self)
        self._imc_file_tree_view = IMCFileTreeView(parent=self)
        self._imc_file_tree_view.setModel(self._imc_file_tree_model)

        self._channel_table_model = ChannelTableModel(controller, parent=self)
        self._channel_table_proxy_model = QSortFilterProxyModel(self)
        self._channel_table_proxy_model.setSourceModel(self._channel_table_model)
        self._channel_table_proxy_model.sort(self._channel_table_model.label_column)
        self._channel_table_view = ChannelTableView(parent=self)
        self._channel_table_view.setModel(self._channel_table_proxy_model)

        self._channel_controls_widget = ChannelControlsWidget(controller, parent=self)
        self._channel_controls_container = QStackedWidget(self)
        self._channel_controls_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self._channel_controls_container.addWidget(QWidget(self))
        self._channel_controls_container.addWidget(self._channel_controls_widget)

        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical, self)
        # noinspection PyArgumentList
        imc_file_panel = QWidget(self)
        imc_file_panel_layout = QVBoxLayout(imc_file_panel)
        # noinspection PyArgumentList
        imc_file_panel_layout.addWidget(self._open_imc_file_button)
        # noinspection PyArgumentList
        imc_file_panel_layout.addWidget(self._imc_file_tree_view)
        imc_file_panel.setLayout(imc_file_panel_layout)
        splitter.addWidget(imc_file_panel)
        # noinspection PyArgumentList
        channel_panel = QWidget(self)
        channel_panel_layout = QVBoxLayout(channel_panel)
        # noinspection PyArgumentList
        channel_panel_layout.addWidget(self._channel_table_view)
        # noinspection PyArgumentList
        channel_panel_layout.addWidget(self._channel_controls_container)
        channel_panel.setLayout(channel_panel_layout)
        splitter.addWidget(channel_panel)
        # noinspection PyArgumentList
        layout.addWidget(splitter)
        self.setLayout(layout)

        channel_table_selection_model: QItemSelectionModel = self._channel_table_view.selectionModel()
        # noinspection PyUnresolvedReferences
        self._open_imc_file_button.clicked.connect(self._on_open_imc_file_button_clicked)
        # noinspection PyUnresolvedReferences
        self._imc_file_tree_model.dataChanged.connect(self._on_imc_file_tree_model_data_changed)
        # noinspection PyUnresolvedReferences
        self._imc_file_tree_view.events.imc_file_closed.connect(self._on_imc_file_tree_view_imc_file_closed)
        # noinspection PyUnresolvedReferences
        self._channel_table_model.dataChanged.connect(self._on_channel_table_model_data_changed)
        # noinspection PyUnresolvedReferences
        channel_table_selection_model.selectionChanged.connect(self._on_channel_table_view_selection_changed)

    def select_channel(self, channel_index: int):
        top_left = self._channel_table_model.index(channel_index, 0)
        top_left = self._channel_table_proxy_model.mapFromSource(top_left)
        bottom_right = self._channel_table_model.index(channel_index, self._channel_table_model.columnCount() - 1)
        bottom_right = self._channel_table_proxy_model.mapFromSource(bottom_right)
        selection_model: QItemSelectionModel = self._channel_table_view.selectionModel()
        selection_model.clearSelection()  # first clear the selection, to make sure the channel controls refresh
        selection_model.select(QItemSelection(top_left, bottom_right), QItemSelectionModel.Select)

    def refresh_channel_controls_widget(self):
        self._channel_controls_widget.refresh()
        if len(self._controller.selected_channels) > 0:
            self._channel_controls_container.setCurrentIndex(1)
        else:
            self._channel_controls_container.setCurrentIndex(0)

    @property
    def imc_file_tree_model(self):
        return self._imc_file_tree_model

    @property
    def channel_table_model(self):
        return self._channel_table_model

    # noinspection PyUnusedLocal
    def _on_open_imc_file_button_clicked(self, checked: bool = False):
        # noinspection PyArgumentList
        imc_file_paths, _ = QFileDialog.getOpenFileNames(self, filter='Imaging mass cytometry files (*.txt *.mcd)')
        open_imc_file_paths = [imc_file.path for imc_file in self._controller.imc_files]
        for imc_file_path in imc_file_paths:
            imc_file_path = Path(imc_file_path)
            if imc_file_path not in open_imc_file_paths:
                self._controller.open_imc_file(imc_file_path)

    # noinspection PyUnusedLocal
    def _on_imc_file_tree_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex,
                                             roles: Optional[int] = None):
        item = top_left.internalPointer()
        if isinstance(item, IMCFilePanoramaModel):
            if item.is_shown:
                self._controller.hide_imc_file_panorama(item)
            else:
                self._controller.show_imc_file_panorama(item)
        elif isinstance(item, IMCFileAcquisitionModel):
            if item.is_loaded:
                self._controller.unload_imc_file_acquisition(item)
            else:
                self._controller.load_imc_file_acquisition(item)

    def _on_imc_file_tree_view_imc_file_closed(self, imc_file: IMCFileModel):
        self._controller.close_imc_file(imc_file)

    # noinspection PyUnusedLocal
    def _on_channel_table_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex,
                                             roles: Optional[int] = None):
        channel = self._controller.channels[top_left.row()]
        if channel.is_shown:
            self._controller.hide_channel(channel)
        else:
            self._controller.show_channel(channel)

    # noinspection PyUnusedLocal
    def _on_channel_table_view_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        selected_channels = []
        for index in self._channel_table_view.selectedIndexes():
            index = self._channel_table_proxy_model.mapToSource(index)
            channel = self._controller.channels[index.row()]
            selected_channels.append(channel)
        self._controller.selected_channels = selected_channels
