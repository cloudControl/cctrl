# -*- coding: utf-8 -*-

"""
    Copyright 2010 cloudControl UG (haftungsbeschraenkt)

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import os
import subprocess
import sys
import shlex

from cctrl.error import InputErrorException


def isValidFile(filename):
        """
            Is the given filename a valid file?
        """
        return os.path.isfile(os.path.abspath(filename))


def readContentOf(filename):
    """
        Read a given file's content into a string
        Returns contents of given file as string, otherwise "None"
    """
    file_content = ''

    if not os.path.isfile(os.path.abspath(filename)):
        raise InputErrorException('FileNotFound')

    try:
        open_file = open(os.path.abspath(filename), 'r')
        file_content = str(open_file.read())
    except IOError:
        raise InputErrorException('FileReadOrWriteFailed')

    return file_content.strip()


def which(programs):
    """
        from http://stackoverflow.com/questions/377017/ \
        test-if-executable-exists-in-python/377028#377028
    """
    def is_exe(file_path):
        return os.path.exists(file_path) and os.access(file_path, os.X_OK)

    for program in programs:
        file_path, file_name = os.path.split(program)
        if file_path:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

    return None


def check_installed_rcs(name):
    """
        Check if either "bzr" or "git" is installed (and can be found
        via PATH variable)
    """
    rcs_executables = {
        'bzr': ['bzr.exe', 'bzr.bat', 'bzr'],
        'git': ['git', 'git.exe', 'git.cmd']}
    return which(rcs_executables[name])


def is_buildpack_url_valid(buildpack_url):
    """
        Is the given url a valid buildpack url?
    """
    try:
        branch = buildpack_url.split('#')[1]
    except IndexError:
        branch = 'master'
    sp = subprocess.Popen(
        ['git', 'ls-remote', buildpack_url.split('#')[0], branch],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
    )
    stdout, _ = sp.communicate()
    valid = True if sp.returncode == 0 and 'refs/heads' in stdout else False
    return valid


def recode_input(input):
    return input.decode(sys.stdin.encoding or 'UTF-8').encode('UTF-8')


def ssh_cmd(host_name, *args):
    sshopts = shlex.split(os.environ.get('CCTRL_SSHOPTS', ''))
    return ['ssh'] + sshopts + ['--'] + [host_name] + list(args)

def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    Backported from Python 2.7 as it's implemented as pure python on stdlib.

    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output
