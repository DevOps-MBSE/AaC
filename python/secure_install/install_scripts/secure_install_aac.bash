#!/bin/bash

# This script will install AaC and its dependencies via the wheel files.

install_script_dir=$(dirname "$0")
cd $install_script_dir
cd ../

pip install --require-hashes -r requirements.txt