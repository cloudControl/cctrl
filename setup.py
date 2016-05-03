import os
import sys
from setuptools import setup, find_packages


execfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cctrl', 'version.py'))

required = [
    'pycclib>=1.6.0',
    'paramiko>=1.15.2,<2',
]

if sys.version_info < (2, 7):
    required.append('argparse')

srcscripts = ['cctrl/cctrlapp', 'cctrl/cctrluser', 'cctrl/exoapp', 'cctrl/exouser', 'cctrl/dcapp', 'cctrl/dcuser', 'cctrl/cnhapp', 'cctrl/cnhuser']

if sys.platform == 'win32':
    import py2exe

    required.append('paramiko')
    required.append('ecdsa')
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
                "includes": ["argparse", "pycclib", "paramiko", "Crypto", "ecdsa"],
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
    test_suite='tests',
    **extra_options
)

setup(
    name="dotcloudng",
    version=__version__,
    description='dotcloud command line utilities',
    author='dotcloud Team',
    author_email='info@dotcloud.com',
    url='https://www.dotcloud.com',
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
    **extra_options
)

setup(
    name="cnh",
    version=__version__,
    description='cloud&heat command line utilities',
    author='cloudControl Team',
    author_email='info@cloudcontrol.com',
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
    **extra_options
)
