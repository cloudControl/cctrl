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

import sys
from os import path
import re
import json
from cctrl.oshelpers import recode_input
from cctrl.error import InputErrorException


def if_file_get_content(value):
    """
        if value is the path to a local file, read the content and return it
        otherwise just return value
    """
    file_path = path.abspath(value)
    if path.isfile(file_path):
        try:
            f = open(file_path, 'rU')
        except IOError:
            pass
        else:
            content = f.read()
            f.close()
            return content

    if sys.platform == 'win32':
        # in windows, sys.argv is encoded in windows-1252
        return value.decode('windows-1252').encode('UTF-8')
    else:
        # all others use the same encoding for stdin and argv
        return recode_input(value)


def parse_additional_addon_options(options):
    regex = re.compile('^(\w+)[=\s]?(.*)$')
    joined_options = ' '.join(options).split('--')
    result = {}
    for entry in joined_options:
        match = regex.match(entry)
        if match:
            if match.group(2):
                result[match.group(1)] = if_file_get_content(match.group(2).rstrip())
            else:
                result[match.group(1)] = 'true'
    return json.dumps(result)


def parse_config_variables(variables, method):
    if not variables:
        return None

    result = {}
    if method == 'remove':
        for var in variables:
            result[var.strip()] = None

    if method == 'add':
        for var in variables:
            if '=' in var:
                k, v = var.split('=', 1)
                result[k.strip()] = if_file_get_content(v.strip())
            else:
                result[var.strip()] = 'true'

    return json.dumps(result)


def extract_flag_from_variables(variables, flag_names, flag_value):
    flag_found = False

    for flag_name in flag_names:
        if flag_name in variables:
            variables.remove(flag_name)
            flag_found = True

    if flag_value and flag_found:
        raise InputErrorException('DuplicatedFlag')

    return variables, flag_value or flag_found
