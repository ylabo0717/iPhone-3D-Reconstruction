# 3D Reconstruction with iPhone and Open3D

This is a toolchain for 3D Reconstruction with iPhone 12 Pro/Pro Max.   
Tools for recording RGB-D data and 3D reconstruction are provided.

## Environment

### Hardware

* iPhone 12 Pro/Pro Max
* Windows PC

### iPhone App

* [Record3D](https://apps.apple.com/jp/app/record3d-3d-videos/id1477716895) 1.6.1

### PC Software

* Windows 10
* Python 3.8.10
* Python Package
    - [opencv-python](https://github.com/opencv/opencv) 4.5.3.56
    - [record3d](https://github.com/marek-simonik/record3d) 1.3.0
    - [open3d](https://github.com/isl-org/Open3D) 0.13.0

## Installation

### iPhone

* Install the Record3D app from the App Store.

    https://apps.apple.com/jp/app/record3d-3d-videos/id1477716895

### PC

* Install Python

    https://www.python.org/downloads/windows/

* Install pipenv

    ```bash
    pip install pipenv
    ```

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

    Run the following command.

    ```bash
    ./Reconstruction.bat <data path>

    # example
    ./Reconstruction.bat ./data/2021-08-13_012134
    ```

    The integrated.ply file are saved in <data path>/scene/ folder.

    ```
    data
    └── yyyy-mm-dd_HHMMSS
        └── scene
             └── integrated.ply
    ```


* Open3D VoxelHashingGUI

    Run the following command.

    ```bash
    # CPU
    ./VoxelHashingGUI.bat <data path>

    # CUDA
    ./VoxelHashingGUI_cuda.bat <data path>

    # example
    ./VoxelHashingGUI.bat ./data/2021-08-13_012134
    ```

    The integrated.ply file are saved in <data path>/scene/ folder.

    ```
    data
    └── yyyy-mm-dd_HHMMSS
        └── scene.ply
    ```

### 3. Visualization

Run the following command.

```bash
./visualizer_pcd.py <point cloud data path>

# example
python ./visualizer_pcd.py ./data/2021-08-13_012134/integrated.ply
```

For more information, please visit the following website.
http://www.open3d.org/docs/latest/tutorial/Basic/visualization.html


## License

Distributed under the MIT License. See [LICENSE](./LICENSE) for more information.
