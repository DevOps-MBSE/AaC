REM This script will install AaC and its dependencies via the wheel files.

@echo off

cd /D "%~dp0"

python -m pip "install" "--require-hashes" "--no-deps" "-r" "requirements.txt" "--no-index" "--find-links" "./"
