#!/bin/bash

set -e

echo "[INFO] Checking env..."
ENV=$1

if [ ! -f "$PYTHON_HOME" ]; then
	PYTHON_HOME=c:/Python27
fi

if [ ! -f "$ISCC_HOME" ]; then
	ISCC_HOME="C:/Program Files/Inno Setup 5"
fi

log_dir=$(pwd)

function handle_log() {
	cat 2>>$log_dir/build.log 1>&2
}

echo "[INFO] Installing paramiko..."
git clone https://github.com/paramiko/paramiko 2>&1 | handle_log
pushd paramiko > /dev/null
"$PYTHON_HOME/python.exe" setup.py install_lib 2>&1 | handle_log
popd > /dev/null

echo "[INFO] Installing certifi..."
git clone https://github.com/certifi/python-certifi 2>&1 | handle_log
pushd python-certifi > /dev/null
"$PYTHON_HOME/python.exe" setup.py install_lib 2>&1 | handle_log
popd > /dev/null

echo "[INFO] Installing pycclib..."
git clone https://github.com/cloudControl/pycclib 2>&1 | handle_log
pushd pycclib > /dev/null
"$PYTHON_HOME/python.exe" setup.py install_lib 2>&1 | handle_log
popd > /dev/null

echo "[INFO] Installing cctrl..."
if [ ! -d  "$2" ]; then
	git clone https://github.com/cloudControl/cctrl 2>&1 | handle_log
	cctrl_dir=cctrl
else
	cctrl_dir="$2"
fi

pushd "$cctrl_dir" > /dev/null
"$PYTHON_HOME/python.exe" setup.py py2exe 2>&1 | handle_log
pushd win32 > /dev/null
echo "[INFO] Building executable..."
"$ISCC_HOME/ISCC.exe" wininstaller_$ENV.iss 2>&1 | handle_log
popd > /dev/null
popd > /dev/null
echo "[INFO] Build successful :-)"
