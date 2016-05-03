import os
import sys
from setuptools import setup


execfile(os.path.join(os.path.dirname(__file__), 'cctrl', 'version.py'))

required = [
    'pycclib>=1.6.0',
    'paramiko>=1.15.2,<2',
]

if sys.version_info < (2, 7):
    required.append('argparse')

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
    test_suite='tests',
    scripts=["cctrl/cctrlapp", "cctrl/cctrluser",
             "cctrl/exoapp", "cctrl/exouser"],
    package_data={"cctrl": ["cacerts.txt"]},
    packages=['cctrl']
)
