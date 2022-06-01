# napari-imc

[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-imc)](https://napari-hub.org/plugins/napari-imc)
[![PyPI](https://img.shields.io/pypi/v/napari-imc.svg?color=green)](https://pypi.org/project/napari-imc)
[![License](https://img.shields.io/pypi/l/napari-imc.svg?color=green)](https://github.com/BodenmillerGroup/napari-imc/raw/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-imc.svg?color=green)](https://python.org)
[![Issues](https://img.shields.io/github/issues/BodenmillerGroup/napari-imc)](https://github.com/BodenmillerGroup/napari-imc/issues)
[![Pull requests](https://img.shields.io/github/issues-pr/BodenmillerGroup/napari-imc)](https://github.com/BodenmillerGroup/napari-imc/pulls)

Imaging Mass Cytometry (IMC) file type support for napari

Load panoramas and multi-channel acquisitions co-registered within the machine's coordinate system from Fluidigm TXT/MCD files

## Installation

You can install napari-imc via [pip](https://pypi.org/project/pip/):

    pip install napari-imc
    
Alternatively, you can install napari-imc via [conda](https://conda.io/):

    conda install -c conda-forge napari-imc
    
For example, to install napari and napari-imc in a fresh conda environment using pip:

    conda create -n napari-imc python=3.9
    conda activate napari-imc
    pip install "napari[all]" napari-imc
    
## Usage

Simply open your Fluidigm TXT/MCD file using napari.

## Authors

Created and maintained by Jonas Windhager [jonas.windhager@uzh.ch](mailto:jonas.windhager@uzh.ch)

## Citation

Please cite the following paper when using napari-imc in your work:

> Windhager J, Bodenmiller B, Eling N (2021). An end-to-end workflow for multiplexed image processing and analysis. bioRxiv. doi: https://doi.org/10.1101/2021.11.12.468357.

    @article{Windhager2021,
      author = {Windhager, Jonas and Bodenmiller, Bernd and Eling, Nils},
      title = {An end-to-end workflow for multiplexed image processing and analysis},
      year = {2021},
      doi = {10.1101/2021.11.12.468357},
      URL = {https://www.biorxiv.org/content/early/2021/11/13/2021.11.12.468357},
      journal = {bioRxiv}
    }

## Contributing

[Contributing](https://github.com/BodenmillerGroup/napari-imc/blob/main/CONTRIBUTING.md)

## Changelog

[Changelog](https://github.com/BodenmillerGroup/napari-imc/blob/main/CHANGELOG.md)

## License

[MIT](https://github.com/BodenmillerGroup/napari-imc/blob/main/LICENSE.md)
