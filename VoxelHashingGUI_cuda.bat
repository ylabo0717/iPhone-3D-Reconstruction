set DATA_PATH=%1
.\bin\VoxelHashingGUI.exe %DATA_PATH% --intrinsics_json %DATA_PATH%\camera_intrinsic.json --device CUDA:0
move scene.ply %DATA_PATH%
move trajectory.log %DATA_PATH%
