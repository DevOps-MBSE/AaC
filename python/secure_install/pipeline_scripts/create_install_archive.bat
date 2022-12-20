@REM https://daniel-sc.github.io/bash-shell-to-bat-converter/
@REM This script gathers AaC's runtime dependencies, creates a hash file, pulls in install scripts, and generally
@REM   prepares the secure installation file. We'll delegate to Github Action's automatic zipping of artifacts to
@REM   ultimately compress the directory into an archive.
@echo off

cd /D "%~dp0"

SET install_script_dir="%cd%\..\"
cd "%install_script_dir%"

For /F %%A in ('"python -m aac version"') do SET version=%%A
echo "Version %version%"
SET install_dir="%cd%\aac_secure_install_%version%"
IF EXIST "%install_dir%" (
  DEL /S "%install_dir%"
)
mkdir "%install_dir%"
for /R "%cd%\install_scripts\" %%f in (*.bat) do echo %%f "%install_dir%\."
for /R "%cd%\install_scripts\" %%f in (*.bat) do COPY %%f "%install_dir%\."
COPY "%cd%\README.md" "%install_dir%"
cd "%install_dir%"

python -m piptools compile "--generate-hashes" "%CD%\..\..\setup.py"
mv "%CD%\..\..\requirements.txt" "."
python -m pip wheel "%CD%\..\.."
@PowerShell "(python -m pip hash 'aac-%version%-py3-none-any.whl')"
@PowerShell "(python -m pip hash 'aac-%version%-py3-none-any.whl')|%%{$_ -Replace 'l:','l \'}"
@PowerShell "(python -m pip hash 'aac-%version%-py3-none-any.whl')|%%{$_ -Replace 'l:','l \'}|%%{$_ -Replace '--hash','    --hash'}"
@PowerShell "(python -m pip hash 'aac-%version%-py3-none-any.whl')|%%{$_ -Replace 'l:','l \'}|%%{$_ -Replace '--hash','    --hash'} >> .\requirements.txt"
type "requirements.txt"
echo %install_dir% > "%CD%\install_dir_name.txt"