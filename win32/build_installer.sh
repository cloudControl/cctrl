#!/bin/bash
set -e
"${PYTHON_HOME:-c:/Python27}/python.exe" -m pip install -U pip
"${PYTHON_HOME:-c:/Python27}/python.exe" -m pip install -r requirements.txt
"${PYTHON_HOME:-c:/Python27}/python.exe" setup-py2exe.py py2exe
pushd win32 > /dev/null
echo "[INFO] Building executable..."
"${ISCC_HOME:-C:/Program Files (x86)/Inno Setup 5}/ISCC.exe" wininstaller_cctrl.iss
popd > /dev/null
echo "[INFO] Build successful :-)"
