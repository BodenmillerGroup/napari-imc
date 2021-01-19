from functools import partial
from imctools.data import Acquisition, Panorama
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QGridLayout, QLabel, QListWidget, QListWidgetItem
from typing import Sequence


class PanoramaListWidgetItem(QListWidgetItem):
    def __init__(self, panorama: Panorama):
        super(PanoramaListWidgetItem, self).__init__()
        self.setText(f'[P{panorama.id:02d}] {panorama.description}')
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Unchecked)
        self.panorama = panorama


class AcquisitionListWidgetItem(QListWidgetItem):
    def __init__(self, acquisition: Acquisition):
        super(AcquisitionListWidgetItem, self).__init__()
        self.setText(f'[A{acquisition.id:02d}] {acquisition.description}')
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Unchecked)
        self.acquisition = acquisition


class MCDDialog(QDialog):
    def __init__(self, panoramas: Sequence[Panorama], acquisitions: Sequence[Acquisition]):
        super(MCDDialog, self).__init__()
        self.setWindowTitle('Open MCD file')

        self.panorama_list_widget = QListWidget()
        for panorama in panoramas:
            self.panorama_list_widget.addItem(PanoramaListWidgetItem(panorama))
        self.select_all_panoramas_checkbox = QCheckBox('Select all')
        # noinspection PyUnresolvedReferences
        self.panorama_list_widget.itemChanged.connect(partial(
            self._on_list_widget_item_changed,
            list_widget=self.panorama_list_widget,
            select_all_checkbox=self.select_all_panoramas_checkbox
        ))
        # noinspection PyUnresolvedReferences
        self.select_all_panoramas_checkbox.stateChanged.connect(partial(
            self._on_select_all_checkbox_state_changed,
            list_widget=self.panorama_list_widget,
            select_all_checkbox=self.select_all_panoramas_checkbox
        ))

        self.acquisition_list_widget = QListWidget()
        for acquisition in acquisitions:
            self.acquisition_list_widget.addItem(AcquisitionListWidgetItem(acquisition))
        self.select_all_acquisitions_checkbox = QCheckBox('Select all')
        # noinspection PyUnresolvedReferences
        self.acquisition_list_widget.itemChanged.connect(partial(
            self._on_list_widget_item_changed,
            list_widget=self.acquisition_list_widget,
            select_all_checkbox=self.select_all_acquisitions_checkbox
        ))
        # noinspection PyUnresolvedReferences
        self.select_all_acquisitions_checkbox.stateChanged.connect(partial(
            self._on_select_all_checkbox_state_changed,
            list_widget=self.acquisition_list_widget,
            select_all_checkbox=self.select_all_acquisitions_checkbox
        ))

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # noinspection PyUnresolvedReferences
        self.button_box.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.button_box.rejected.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(QLabel('Panoramas:'), 0, 0)
        layout.addWidget(self.panorama_list_widget, 1, 0)
        layout.addWidget(self.select_all_panoramas_checkbox, 2, 0)
        layout.addWidget(QLabel('Acquisitions:'), 0, 1)
        layout.addWidget(self.acquisition_list_widget, 1, 1)
        layout.addWidget(self.select_all_acquisitions_checkbox, 2, 1)
        layout.addWidget(self.button_box, 3, 0, 1, 2)
        self.setLayout(layout)

    @staticmethod
    def _on_select_all_checkbox_state_changed(check_state, list_widget, select_all_checkbox):
        if check_state == Qt.Checked or check_state == Qt.Unchecked:
            list_widget.blockSignals(True)
            for i in range(list_widget.count()):
                list_widget.item(i).setCheckState(check_state)
            list_widget.blockSignals(False)
        elif check_state == Qt.PartiallyChecked:
            select_all_checkbox.setCheckState(Qt.Checked)

    @staticmethod
    def _on_list_widget_item_changed(list_widget, select_all_checkbox):
        all_checked = True
        all_unchecked = True
        for i in range(list_widget.count()):
            check_state = list_widget.item(i).checkState()
            if check_state == Qt.Checked:
                all_unchecked = False
            elif check_state == Qt.Unchecked:
                all_checked = False
        select_all_checkbox.blockSignals(True)
        if all_checked:
            select_all_checkbox.setCheckState(Qt.Checked)
        elif all_unchecked:
            select_all_checkbox.setCheckState(Qt.Unchecked)
        else:
            select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        select_all_checkbox.blockSignals(False)

    @property
    def selected_panoramas(self) -> Sequence[Panorama]:
        return [
            item.panorama for i in range(self.panorama_list_widget.count())
            if (item := self.panorama_list_widget.item(i)).checkState() == Qt.Checked
        ]

    @property
    def selected_acquisitions(self) -> Sequence[Acquisition]:
        return [
            item.acquisition for i in range(self.acquisition_list_widget.count())
            if (item := self.acquisition_list_widget.item(i)).checkState() == Qt.Checked
        ]
