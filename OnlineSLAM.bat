set DATA_PATH=%~dp0%1
@if "%2"=="" (
    set DEVICE="CPU:0"
) else (
    set DEVICE=%2
)

set INTRINSIC_FILE_PATH=%DATA_PATH%\camera_intrinsic.json
set OUTPUT_FILE_PATH=%DATA_PATH%\pointcloud.ply
pushd .\bin\Release\
.\OnlineSLAMRGBD.exe --dataset_path %DATA_PATH% --intrinsics_path %INTRINSIC_FILE_PATH% --device %DEVICE%
popd