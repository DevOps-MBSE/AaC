REM https://daniel-sc.github.io/bash-shell-to-bat-converter/
@echo off

cd /D "%~dp0"

SET install_script_dir="%cd%"
cd "%install_script_dir%"
cd "../"
SET version=%aac version%
SET install_dir="aac_secure_install_%version%"
IF EXIST "%install_dir%" (
  DEL /S "%install_dir%"
)
mkdir "%install_dir%"
COPY  "install_scripts\*" "%install_dir%"
COPY  "README.md" "%install_dir%"
cd "%install_dir%"
python -m pip "wheel" "%CD%\..\..\setup.py"
python -m pip-compile "--generate-hashes" "%CD%\..\..\setup.py"
mv "%CD%\..\..\requirements.txt" "."
REM UNKNOWN: {"type":"Pipeline","commands":[{"type":"Command","name":{"text":"pip","type":"Word"},"suffix":[{"text":"hash","type":"Word"},{"text":"aac-*.whl","type":"Word"}]},{"type":"Command","name":{"text":"sed","type":"Word"},"suffix":[{"text":"-r","type":"Word"},{"text":"s/l:/l \\/g","type":"Word"}]},{"type":"Command","name":{"text":"sed","type":"Word"},"suffix":[{"text":"-r","type":"Word"},{"text":"s/--hash/    --hash/g","type":"Word"},{"type":"Redirect","op":{"text":">>","type":"dgreat"},"file":{"text":"requirements.txt","type":"Word"}}]}]}
echo "%install_dir%" REM UNKNOWN: {"type":"Redirect","op":{"text":">","type":"great"},"file":{"text":"../install_dir_name.txt","type":"Word"}}