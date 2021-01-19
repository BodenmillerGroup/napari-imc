from imageio import imread
from imctools.io.mcd.mcdparser import McdParser
from imctools.io.txt.txtparser import TxtParser
from napari_plugin_engine import napari_hook_implementation
from pathlib import Path

from .mcd_dialog import MCDDialog


@napari_hook_implementation
def napari_get_reader(path):
    if isinstance(path, list):
        for p in path:
            suffix = Path(p).suffix.lower()
            if suffix != '.mcd' and suffix != '.txt':
                return None
        return read_imc
    suffix = Path(path).suffix.lower()
    if suffix == '.mcd' or suffix == '.txt':
        return read_imc
    return None


def read_imc(path):
    if isinstance(path, list):
        layer_data = []
        for p in path:
            layer_data += read_imc(p)
        return layer_data
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == '.mcd':
        return _read_mcd(path)
    if suffix == '.txt':
        return _read_txt(path)
    return None


def _read_mcd(path):
    layer_data = []
    with McdParser(path) as parser:
        panoramas = [p for p in parser.session.panoramas.values() if p.image_type != 'Default']
        acquisitions = [a for a in parser.session.acquisitions.values() if a.is_valid]
        dialog = MCDDialog(panoramas, acquisitions)
        if dialog.exec() == MCDDialog.Accepted:
            for acquisition in dialog.selected_acquisitions:
                acquisition_data = parser.get_acquisition_data(acquisition.id)
                layer_data.append(_load_acquisition(acquisition, acquisition_data, show_id=True))
            for panorama in dialog.selected_panoramas:
                panorama_data = parser.get_panorama_image(panorama.id)
                layer_data.append(_load_panorama(panorama, panorama_data))
    return layer_data[::-1]


def _read_txt(path):
    with TxtParser(path) as parser:
        acquisition_data = parser.get_acquisition_data()
        acquisition = acquisition_data.acquisition
        return [_load_acquisition(acquisition, acquisition_data, fallback_name=path.name)]


def _load_panorama(panorama, panorama_data):
    xs_physical = [panorama.x1, panorama.x2, panorama.x3, panorama.x4]
    ys_physical = [panorama.y1, panorama.y2, panorama.y3, panorama.y4]
    x_physical, y_physical = min(xs_physical), min(ys_physical)
    w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
    data = imread(panorama_data)
    if x_physical != panorama.x1:
        data = data[:, ::-1, :]
    if y_physical != panorama.y1:
        data = data[::-1, :, :]
    metadata = {
        'name': f'[P{panorama.id:02d}] {panorama.description}',
        'scale': (h_physical / data.shape[0], w_physical / data.shape[1]),
        'translate': (y_physical, x_physical),
    }
    return data, metadata, 'image'


def _load_acquisition(acquisition, acquisition_data, fallback_name=None, show_id=False):
    x_physical, y_physical = 0, 0
    w_physical, h_physical = acquisition.max_x, acquisition.max_y
    xs_physical = [acquisition.roi_start_x_pos_um, acquisition.roi_end_x_pos_um]
    ys_physical = [acquisition.roi_start_y_pos_um, acquisition.roi_end_y_pos_um]
    if None not in xs_physical and None not in ys_physical:
        x_physical, y_physical = min(xs_physical), min(ys_physical, default=0)
        w_physical, h_physical = max(xs_physical) - x_physical, max(ys_physical) - y_physical
    data = acquisition_data.image_data
    if x_physical != acquisition.roi_start_x_pos_um and acquisition.roi_start_x_pos_um is not None:
        data = data[:, :, ::-1]
    if y_physical != acquisition.roi_start_y_pos_um and acquisition.roi_start_y_pos_um is not None:
        data = data[:, ::-1, :]
    acquisition_id_str = f'{acquisition.id:02d}' if show_id else ''
    metadata = {
        'channel_axis': 0,
        'name': [
            f'[A{acquisition_id_str}] {channel_label} ({acquisition.description or fallback_name})'
            for channel_label in acquisition.channel_labels
        ],
        'scale': (h_physical / data.shape[1], w_physical / data.shape[2]),
        'translate': (y_physical, x_physical),
        'visible': False,
    }
    return data, metadata, 'image'
