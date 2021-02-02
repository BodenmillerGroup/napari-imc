from napari import Viewer
from qtpy.QtCore import Qt, QItemSelection, QItemSelectionModel, QModelIndex, QSortFilterProxyModel
from qtpy.QtWidgets import QSizePolicy, QSplitter, QStackedWidget, QVBoxLayout, QWidget
from typing import Optional

from napari_imc.imc_controller import IMCController
from napari_imc.models import IMCFileModel, IMCFileAcquisitionModel, IMCFilePanoramaModel
from napari_imc.widgets import (
    ChannelControlsWidget,
    ChannelTableModel, ChannelTableView,
    IMCFileTreeModel, IMCFileTreeView
)


class IMCWidget(QWidget):
    NAME = 'Imaging Mass Cytometry'
    FULL_NAME = f'napari-imc: {NAME}'
    AREA = 'right'
    ALLOWED_AREAS = ['left', 'right']

    def __init__(self, napari_viewer: Viewer, parent: Optional[QWidget] = None):
        super(IMCWidget, self).__init__(parent)
        self._controller = IMCController(napari_viewer, self)

        self._imc_file_tree_model = IMCFileTreeModel(self._controller, parent=self)
        self._imc_file_tree_view = IMCFileTreeView(parent=self)
        self._imc_file_tree_view.setModel(self._imc_file_tree_model)

        self._channel_table_model = ChannelTableModel(self._controller, parent=self)
        self._channel_table_proxy_model = QSortFilterProxyModel(self)
        self._channel_table_proxy_model.setSourceModel(self._channel_table_model)
        self._channel_table_proxy_model.sort(self._channel_table_model.LABEL_COLUMN)
        self._channel_table_view = ChannelTableView(parent=self)
        self._channel_table_view.setModel(self._channel_table_proxy_model)

        self._channel_controls_widget = ChannelControlsWidget(self._controller, parent=self)
        self._channel_controls_container = QStackedWidget(self)
        self._channel_controls_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self._channel_controls_container.addWidget(QWidget(self))
        self._channel_controls_container.addWidget(self._channel_controls_widget)

        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical, self)
        splitter.addWidget(self._imc_file_tree_view)
        channel_panel = QWidget(self)
        channel_panel_layout = QVBoxLayout()
        channel_panel_layout.addWidget(self._channel_table_view)
        channel_panel_layout.addWidget(self._channel_controls_container)
        channel_panel.setLayout(channel_panel_layout)
        splitter.addWidget(channel_panel)
        layout.addWidget(splitter)
        self.setLayout(layout)

        # noinspection PyUnusedLocal
        # noinspection PyUnresolvedReferences
        @self._imc_file_tree_model.dataChanged.connect
        def on_imc_file_tree_model_data_changed(top_left: QModelIndex, bottom_right: QModelIndex,
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

        # noinspection PyUnresolvedReferences
        @self._imc_file_tree_view.events.imc_file_closed.connect
        def on_imc_file_tree_view_imc_file_closed(imc_file: IMCFileModel):
            self._controller.close_imc_file(imc_file)

        # noinspection PyUnusedLocal
        # noinspection PyUnresolvedReferences
        @self._channel_table_model.dataChanged.connect
        def on_channel_table_model_data_changed(top_left: QModelIndex, bottom_right: QModelIndex,
                                                roles: Optional[int] = None):
            channel = self._controller.channels[top_left.row()]
            if channel.is_shown:
                self._controller.hide_channel(channel)
            else:
                self._controller.show_channel(channel)

        channel_table_selection_model: QItemSelectionModel = self._channel_table_view.selectionModel()

        # noinspection PyUnusedLocal
        # noinspection PyUnresolvedReferences
        @channel_table_selection_model.selectionChanged.connect
        def on_channel_table_view_selection_changed(selected: QItemSelection, deselected: QItemSelection):
            selected_channels = []
            for index in self._channel_table_view.selectedIndexes():
                index = self._channel_table_proxy_model.mapToSource(index)
                channel = self._controller.channels[index.row()]
                selected_channels.append(channel)
            self._controller.selected_channels = selected_channels

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
    def controller(self):
        return self._controller

    @property
    def imc_file_tree_model(self) -> IMCFileTreeModel:
        return self._imc_file_tree_model

    @property
    def channel_table_model(self) -> ChannelTableModel:
        return self._channel_table_model
