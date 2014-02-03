#!/bin/bash

# Script for building cloudControl CLI Windows installer

# Preparation steps:
# Install python 2.7.6 via msi installer: http://www.python.org/download/releases/2.7.6/
# Install setuptool: https://bitbucket.org/pypa/setuptools#rst-header-windows
# Install pycrypto for python 2.7: http://www.voidspace.org.uk/python/modules.shtml#pycrypto
# Install p2exe: http://sourceforge.net/projects/py2exe
# Install Inno Setup: http://www.jrsoftware.org/isdl.php#stable

set -e

echo "[INFO] Checking env..."

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

echo "[INFO] Installing cctrl..."
if [ ! -d  "$1" ]; then
	git clone https://github.com/cloudControl/cctrl 2>&1 | handle_log
	cctrl_dir=cctrl
else
	cctrl_dir="$1"
fi

pushd "$cctrl_dir" > /dev/null
"$PYTHON_HOME/python.exe" setup.py py2exe 2>&1 | handle_log
pushd win32 > /dev/null
echo "[INFO] Building executable..."
"$ISCC_HOME/ISCC.exe" wininstaller.iss 2>&1 | handle_log
popd > /dev/null
popd > /dev/null
echo "[INFO] Build successful :-)"