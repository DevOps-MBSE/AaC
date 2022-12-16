#!/usr/bin/env bash
tempdir=$(mktemp -d /tmp/wheelhouse-XXXXX)
python -m pip wheel -r requirements.txt --wheel-dir=$tempdir
cwd=`pwd`
platform=`uname -s -r`
(cd "$tempdir"; tar -cjvf "$cwd/${platform// /-}.tar.bz2" *)