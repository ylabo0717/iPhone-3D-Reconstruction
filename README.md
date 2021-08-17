# 3D Reconstruction with iPhone and Open3D

## Environment

### Hardware

* iPhone 12 Pro/Pro Max
* Windows PC

### iPhone App

* Record3D 1.6.1

### PC Software

* Windows 10
* Python 3.8.10
* Python Package
    - opencv-python 4.5.3.56
    - record3d 1.3.0
    - open3d 0.13.0

## Install

### iPhone

* Install the Record3D app from the App Store.

    https://apps.apple.com/jp/app/record3d-3d-videos/id1477716895

### PC

* Install Python

    https://www.python.org/downloads/windows/

* Git Clone and Install Package

    ```bash
    git clone --recursive https://github.com/ylabo0717/iPhone-RGBD-Recorder.git

    # You can also update the submodule manually
    git submodule update --init --recursive
    ```

* Install Package (Sync Virtual Envirioment)

    ```bash
    cd iPhone-RGBD-Recorder
    pipenv sync
    pipenv shell
    ```

## Usage

### 1. Recording

  * [Recording with iPhone + Record3D](./doc/recording_with_record3d.md)


### 2. 3D Reconstrucion

* Open3D Reconstruction System

    Run the followint command.

    ```bash
    .\Reconstruction.bat <data path>

    # example
    .\Reconstruction.bat .\data\2021-08-13_012134
    ```

    The integrated.ply file are saved in <data path>/scene/ folder.

    ```
    data
    └── yyyy-mm-dd_HHMMSS
        └── scene
             └── integrated.ply
    ```


* Open3D VoxelHashingGUI

    Run the followint command.

    ```bash
    # CPU
    .\VoxelHashingGUI.bat <data path>

    # CUDA
    .\VoxelHashingGUI_cuda.bat <data path>

    # example
    .\VoxelHashingGUI.bat .\data\2021-08-13_012134
    ```

    The integrated.ply file are saved in <data path>/scene/ folder.

    ```
    data
    └── yyyy-mm-dd_HHMMSS
        └── scene.ply
    ```



