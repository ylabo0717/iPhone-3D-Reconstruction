set DATA_PATH=%~dp0%1
@if "%2"=="" (
    set DEVICE="CPU:0"
) else (
    set DEVICE=%2
)

set COLOR_DIR=%DATA_PATH%\color
set DEPTH_DIR=%DATA_PATH%\depth
set INTRINSIC_FILE_PATH=%DATA_PATH%\camera_intrinsic.json
set OUTPUT_FILE_PATH=%DATA_PATH%\scene.ply
pushd .\open3d_bin\
.\OfflineSLAM.exe --color_folder_path %COLOR_DIR% --depth_folder_path %DEPTH_DIR% --intrinsic_path %INTRINSIC_FILE_PATH% --device %DEVICE% --pointcloud temp.ply --vis
python ..\rotate_point_cloud.py .\temp.ply %OUTPUT_FILE_PATH% 180 0 0
popd
