# sithom README

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Python package](https://github.com/sdat2/sithom/actions/workflows/pytest.yml/badge.svg)](https://github.com/sdat2/sithom/actions/workflows/pytest.yml)[![Documentation Status](https://readthedocs.org/projects/get_era5/badge/?version=latest)](https://get_era5.readthedocs.io/en/latest/?badge=latest)[![PyPI version](https://badge.fury.io/py/get_era5.svg)](https://badge.fury.io/py/get_era5)[![DOI](https://zenodo.org/badge/496635214.svg)](https://zenodo.org/badge/latestdoi/496635214)


## Description

A package for downloading ERA5 easily.


## Install using pip

```txt
pip install get_era5
```

## Install using conda

```txt
conda install -c conda-forge get_era5
```

## Package structure

```txt

├── CHANGELOG.txt      <- List of main changes at each new package version.
├── CITATION.cff       <- File to allow you to easily cite this repository.
├── LICENSE            <- MIT Open software license.
├── Makefile           <- Makefile with commands.
├── pytest.ini         <- Enable doctest unit-tests.
├── README.md          <- The top-level README for developers using this project.
├── setup.py           <- Python setup file for pip install.
|
├── get_era5             <- Package folder.
|   |
│   ├── __init__.py    <- Init file.
│   ├── _version.py    <- Key package information.
|
└── tests              <- Test folder.

```

## Requirements

 - Python 3.8+
 - `sithom`
 - `cdsapi`
 - `xarray`
