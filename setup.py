"""
    setup script for cloudControl command line utilites
    
    usage: sudo python setup.py install
"""

from shutil import copy
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

srcscripts = ['cctrl/cctrlapp', 'cctrl/cctrluser']

if sys.platform == 'win32':
    import py2exe
    extra_options = dict(
        setup_requires=['py2exe'],
        console = srcscripts,
        zipfile = "lib/library.zip",
        options = {
            "py2exe": {
                "compressed": 1,
                "optimize": 2,
                "excludes": ['_scproxy', 'email.FeedParser', 'email.Message', 'email.Utils', 'hexdump', 'isapi', 'pythoncom', 'pywintypes', 'simplejson', 'socks', 'win32com', 'win32com.client'],
                "includes": ["argparse", "pycclib"],
                "packages": find_packages()
            }
        }
    )
else:
    extra_options = dict(
        scripts=srcscripts,
        packages=find_packages()
    )

setup(
    name="cctrl",
    version='0.1.1',
    description='cloudControl command line utilities',
    author = 'cloudControl Team',
    author_email = 'info@cloudcontrol.de',
    url = 'https://launchpad.net/cctrl',
    download_url = 'https://launchpad.net/cctrl/+download',
    license = 'Apache 2.0',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Internet'
          ],
    install_requires=[
        'pycclib',
        'argparse'
    ],
    **extra_options
)
