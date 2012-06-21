::
:: INSTALLATION SCRIPT FOR BUILDING CCTRL
::

::
:: PRE-INSTALL STEPS
::
:: Make sure to install following before running this script:
::
:: 1. Install libraries
:: c:\> \Python26\Scripts\easy_install.exe --upgrade httplib2
:: c:\> \Python26\Scripts\easy_install.exe --upgrade argparse
:: 
:: 2. Get py2exe
:: http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.6.exe/download?use_mirror=switch
::
:: 3. Install py2exe via Windows Installer
:: 
:: 4. Download paramiko
:: http://www.lag.net/paramiko
::
:: 5. Install paramiko
:: c:\> cd <paramiko_download_folder>
:: c:\> c:\Python26\python.exe setup.py install_lib
::
:: 6. Run this script!
::

:: Remove all old directories, first.
:: echo ">>> Removing OLD directories ..."
:: IF EXIST c:\Users\admin\cctrl\pycclib rmdir/S /Q c:\Users\admin\cctrl\pycclib
:: IF EXIST c:\Users\admin\cctrl\cctrl rmdir /S /Q c:\Users\admin\cctrl\cctrl

:: Clone pycclib and cctrl from github
echo ">>> Getting pycclib + cctrl sources ..."
cd \users\admin\cctrl
"c:\Program Files (x86)\Git\bin\git.exe" clone https://github.com/cloudControl/cctrl.git
"c:\Program Files (x86)\Git\bin\git.exe" clone https://github.com/cloudControl/pycclib.git  

:: Install paramiko libraries
cd \users\admin\Downloads\paramiko-1.7.7.1
\Python26\python.exe setup.py install_lib

:: Build pycclib and install the libraries
echo ">>> Building pycclib sources ..."
cd \Users\admin\cctrl\pycclib
\Python26\python.exe setup.py install_lib

:: Build cctrlapp and make an exe out of it
echo ">>> Building cctrl sources ..."
cd \Users\admin\cctrl\cctrl
\Python26\python.exe setup.py py2exe

:: Run InnoSetup to build the executable Installation file
:: Do some smart steps here
cd \Users\admin\cctrl\cctrl\win32
"c:\Program Files (x86)\Inno Setup 5"\iscc /q wininstaller.iss
cd \Users\admin\cctrl