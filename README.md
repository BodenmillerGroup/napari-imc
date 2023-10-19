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

>  Windhager, J., Zanotelli, V.R.T., Schulz, D. et al. An end-to-end workflow for multiplexed image processing and analysis. Nat Protoc (2023). https://doi.org/10.1038/s41596-023-00881-0

    @article{Windhager2023,
        author = {Windhager, Jonas and Zanotelli, Vito R.T. and Schulz, Daniel and Meyer, Lasse and Daniel, Michelle and Bodenmiller, Bernd and Eling, Nils},
        title = {An end-to-end workflow for multiplexed image processing and analysis},
        year = {2023},
        doi = {10.1038/s41596-023-00881-0},
        URL = {https://www.nature.com/articles/s41596-023-00881-0},
        journal = {Nature Protocols}
    }

## Contributing

[Contributing](https://github.com/BodenmillerGroup/napari-imc/blob/main/CONTRIBUTING.md)

## Changelog

[Changelog](https://github.com/BodenmillerGroup/napari-imc/blob/main/CHANGELOG.md)

## License

[MIT](https://github.com/BodenmillerGroup/napari-imc/blob/main/LICENSE.md)
