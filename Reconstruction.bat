set DATA_PATH=%1
@if "%2"=="" (
    set CONFIG_FILENAME=config.json
) else (
    set CONFIG_FILENAME=%2
)
set CONFIG_PATH=%DATA_PATH%\%CONFIG_FILENAME%
set OUTPUT_PLY_FILENAME=%DATA_PATH%\scene\integrated.ply
pushd .\3rdparty\Open3D\examples\python\reconstruction_system\
python run_system.py %~dp0%CONFIG_PATH% --make --register --refine --integrate
popd
python rotate_point_cloud.py %OUTPUT_PLY_FILENAME% %OUTPUT_PLY_FILENAME% 180 0 0
