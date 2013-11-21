# -*- coding: utf-8 -*-
"""
    setup script for cloudControl command line utilities

    usage: sudo python setup.py install
"""

import os
import sys
from cctrl.version import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

execfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cctrl', 'version.py'))

if sys.version_info < (2, 6):
    required = ['simplejson']
else:
    required = []

required.append('pycclib>=1.4.0')
required.append('argparse>=1.1')

srcscripts = ['cctrl/cctrlapp', 'cctrl/cctrluser', 'cctrl/cctrltunnel']

if sys.platform == 'win32':
    import py2exe

    required.append('paramiko')
    extra_options = dict(
        setup_requires=['py2exe'],
        console=srcscripts,
        zipfile=None,
        data_files=[("", ["cctrl/cacerts.txt", ])],
        options={
            "py2exe": {
                "compressed": True,
                "optimize": 2,
                "excludes": [
                    '_scproxy',
                    'hexdump',
                    'isapi',
                    'pythoncom',
                    'pywintypes',
                    'simplejson',
                    'socks',
                    'win32com',
                    'win32com.client',
                    'doctest',
                    'pickle',
                    'difflib',
                    'unittest'],
                "includes": ["argparse", "pycclib", "paramiko", "Crypto"],
                "packages": find_packages()
            }
        }
    )
else:
    extra_options = dict(
        scripts=srcscripts,
        package_data={"cctrl": ["cacerts.txt"]},
        packages=find_packages()
    )

setup(
    name="cctrl",
    version=__version__,
    description='cloudControl command line utilities',
    author='cloudControl Team',
    author_email='info@cloudcontrol.de',
    url='https://www.cloudcontrol.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    install_requires=required,
    tests_require=['mock'],
    test_suite='test',
    **extra_options
)
