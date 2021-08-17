set DATA_PATH=%1
@if "%2"=="" (
    set DEVICE="CPU:0"
) else (
    set DEVICE=%2
)

set OUTPUT_PLY_FILENAME="scene.ply"
set OUTPUT_LOG_FILENAME="trajectory.log"
.\bin\VoxelHashingGUI.exe %DATA_PATH% --intrinsics_json %DATA_PATH%\camera_intrinsic.json --device %DEVICE%
move scene.ply %DATA_PATH%
move trajectory.log %DATA_PATH%
move %OUTPUT_PLY_FILENAME% %DATA_PATH%
move %OUTPUT_LOG_FILENAME% %DATA_PATH%
