REM https://daniel-sc.github.io/bash-shell-to-bat-converter/
@echo off

cd /D "%~dp0"

SET install_script_dir="%cd%\..\"
cd "%install_script_dir%"

For /F %%A in ('"python -m aac version"') do SET version=%%A
echo "Version %version%"
SET install_dir=%cd%"/aac_secure_install_%version%"
IF EXIST "%install_dir%" (
  DEL /S "%install_dir%"
)
mkdir "%install_dir%"
COPY "%cd%/install_scripts\*" "%install_dir%"
COPY "%cd%/README.md" "%install_dir%"
cd "%install_dir%"

python -m piptools compile "--generate-hashes" "%CD%\..\..\setup.py"
mv "%CD%\..\..\requirements.txt" "."
python -m pip wheel -r "%CD%\requirements.txt"

SET aac_wheel=Get-ChildItem -Path "%CD%" -Filter *.whl -Name
echo "Wheel: %aac_wheel%"
python -m pip hash "%aac_wheel%"
echo %install_dir% > "%CD%\install_dir_name.txt"