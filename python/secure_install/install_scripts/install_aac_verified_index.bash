#!/bin/bash

# This script will install AaC and its dependencies via PyPI.

install_script_dir=$(dirname "$0")
cd $install_script_dir

pip install --require-hashes --no-deps -r requirements.txt
