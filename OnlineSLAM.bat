set DATA_PATH=%~dp0%1
@if "%2"=="" (
    set DEVICE="CPU:0"
) else (
    set DEVICE=%2
)

set INTRINSIC_FILE_PATH=%DATA_PATH%\camera_intrinsic.json
pushd .\open3d_bin\
.\OnlineSLAMRGBD.exe --dataset_path %DATA_PATH% --intrinsics_path %INTRINSIC_FILE_PATH% --device %DEVICE%
python ..\rotate_point_cloud.py .\scene.ply %DATA_PATH%\scene.ply 180 0 0
popd
