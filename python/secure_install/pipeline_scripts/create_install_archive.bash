#!/bin/bash

# This script gathers AaC's runtime dependencies, creates a hash file, pulls in install scripts, and generally
#   prepares the secure installation file. We'll delegate to Github Action's automatic zipping of artifacts to
#   ultimately compress the directory into an archive.

install_script_dir=$(dirname "$0")
cd $install_script_dir
cd ../

version=$(aac version)
install_dir="aac_secure_install_$version"

[[ -d $install_dir ]] && rm -r $install_dir
mkdir $install_dir
cp -p -r install_scripts/*.bash $install_dir
cp README.md $install_dir
cd $install_dir

pip wheel ../../
pip-compile --generate-hashes ../../setup.py
mv ../../requirements.txt .
pip download --python-version 3.9 -r requirements.txt -d . --no-deps
pip download --python-version 3.10 -r requirements.txt -d . --no-deps
pip download --python-version 3.11 -r requirements.txt -d . --no-deps
pip hash aac-*.whl | sed -r "s/l:/l \\\/g" | sed -r "s/--hash/    --hash/g" >> requirements.txt # This will only work for the main-branch pipeline that is deploying the artifact to PyPI

echo "$install_dir" > ../install_dir_name.txt
