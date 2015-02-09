import os
import sys
import xmlrpclib

from shutil import rmtree
from subprocess import check_call

TEMP_DIR = 'tmp'
PROJECT_NAME = 'cctrl'
DIST_DIR = os.path.join(TEMP_DIR, 'dist')


def main():
    if is_current_version():
        sys.exit("Version is not updated. Aborting release.")

    dist()
    cleanup()


def is_current_version():
    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    return pypi.package_releases('cctrl')[0] == __version__


def dist():
    try:
        check_call(['python',
                    'setup.py',
                    'sdist',
                    '--dist-dir={0}'.format(DIST_DIR),
                    '--formats=gztar',
                    'upload'])
    except OSError as e:
        cleanup()
        sys.exit(e)


def cleanup():
    rmtree(TEMP_DIR)

if __name__ == '__main__':
    execfile(os.path.join(PROJECT_NAME, 'version.py'))
    main()
