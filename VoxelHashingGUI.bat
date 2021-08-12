set DATA_PATH=%1
.\bin\VoxelHashingGUI.exe %DATA_PATH% --intrinsics_json %DATA_PATH%\camera_intrinsic.json --device CPU:0
