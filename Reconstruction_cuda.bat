set CONFIG_PATH=%1
pushd .\3rdparty\Open3D\examples\python\reconstruction_system\
python .\run_system.py %~dp0%CONFIG_PATH% --make --register --refine --integrate --device cuda:0
popd
