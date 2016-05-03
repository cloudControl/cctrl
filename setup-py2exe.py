import os.path
from distutils.core import setup

import py2exe

execfile(os.path.join(os.path.dirname(__file__), 'cctrl', 'version.py'))

setup(
	name="cctrl",
	version=__version__,
	description="cloudControl command line utilities",
	author="cloudControl Team",
	author_email="info@cloucontrol.de",
	license="Apache 2.0",
	console=["cctrl/cctrlapp", "cctrl/cctrluser",
	         "cctrl/exoapp", "cctrl/exouser"],
	data_files=[("", ["cctrl/cacerts.txt"])]
)
