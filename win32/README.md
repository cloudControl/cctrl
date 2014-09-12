Building cloudControl CLI Windows installer
============================

### PRE-INSTALLATION STEPS

1. Install python 2.7.6 via msi installer: [http://www.python.org/download/releases/2.7.6/](http://www.python.org/download/releases/2.7.6/)
2. Install setuptools: [https://bitbucket.org/pypa/setuptools#rst-header-windows](https://bitbucket.org/pypa/setuptools#rst-header-windows)
3. Install pycrypto for python 2.7: [http://www.voidspace.org.uk/python/modules.shtml#pycrypto](http://www.voidspace.org.uk/python/modules.shtml#pycrypto)
4. Install p2exe: [http://sourceforge.net/projects/py2exe](http://sourceforge.net/projects/py2exe)
5. Install Inno Setup: [http://www.jrsoftware.org/isdl.php#stable](http://www.jrsoftware.org/isdl.php#stable)
6. Install git bash: [http://msysgit.github.io/](http://msysgit.github.io/)

### BUILDING CLI FOR SPECIFIC ENVIRONMENT

* To start build, simply execute (use git bash):

	~~~bash
	$ win32/build_installer.sh ENV PATH_TO_CCTRL_DIR
	~~~

	where:

	- `ENV` is `[cctrl|dotcloudng]`
	- `PATH_TO_CCTRL_DIR` is an optional parameter specifying path to cctrl source directory. If not specified build script will clone master version.

Optionally, you can specify locations of `Python` and `ISCC` home directories by setting these env variables: `PYTHON_HOME` and `ISCC_HOME`. After successful build, executable file is located in `win32setup` directory.