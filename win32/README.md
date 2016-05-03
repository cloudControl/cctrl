Building cloudControl CLI Windows installer
============================

### PRE-INSTALLATION STEPS

1. Install https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi
2. Install [Microsoft Visual C++ Compiler for Python 2.7
](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
3. Install py2exe: [http://sourceforge.net/projects/py2exe](http://sourceforge.net/projects/py2exe)
4. Install Inno Setup: [http://www.jrsoftware.org/isdl.php#stable](http://www.jrsoftware.org/isdl.php#stable)
5. Install git bash: [http://msysgit.github.io/](http://msysgit.github.io/)

### BUILDING

* To start build, simply execute (use git bash):

	~~~bash
	$ win32/build_installer.sh
	~~~

	where:
	- `PATH_TO_CCTRL_DIR` is an optional parameter specifying path to cctrl source directory. If not specified build script will clone master version.

Optionally, you can specify locations of `Python` and `ISCC` home directories by setting these env variables: `PYTHON_HOME` and `ISCC_HOME`. After successful build, executable file is located in `win32setup` directory.
