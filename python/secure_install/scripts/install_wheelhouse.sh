#!/usr/bin/env bash
set -e
tempdir=$(mktemp -d /tmp/wheelhouse-XXXXX)
cwd=`pwd`
platform=`uname -s -r`
echo "$cwd/${platform// /-}.tar.bz2"
(cd $tempdir; tar -xvf "$cwd/${platform// /-}.tar.bz2")
echo "looks"
python -m pip install --force-reinstall --require-hashes -r --no-index --no-deps $tempdir/*