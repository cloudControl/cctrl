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
from __builtin__ import open, raw_input, range
from exceptions import ImportError, ValueError

from getpass import getpass
import sys
import os
from cctrl.oshelpers import recode_input

try:
    import json
except ImportError:
    import simplejson as json

from cctrl.error import messages, PasswordsDontMatchException


def update_tokenfile(api, settings):
    """
        Because it is a real pain we don't want to ask developers for their
        username and password every time they call a method.

        Therefore we authenticate users via token for each request and only
        require email and password for a new token.
        A token is valid for a given period of time. Each successful API
        request resets the expiration time.
    """
    if api.check_token():
        write_tokenfile(api, settings)
        return True
    return False


def read_tokenfile(settings):
    """
        Read the token from the token_path specified in
        cctrl.settings
    """
    token = None
    if os.path.exists(settings.token_path):
        token_file = open(settings.token_path, "r")
        try:
            token = json.load(token_file)
        except ValueError:
            token = None
        token_file.close()
    return token


def write_tokenfile(api, settings):
    """
        This method checks, if the .cloudControl directory inside the
        users home exists or is a file. If not, we create it and then
        write the token file.
    """
    if os.path.isdir(settings.home_path):
        pass
    elif os.path.isfile(settings.home_path):
        print 'Error: ' + settings.home_path + ' is a file, not a directory.'
        sys.exit(1)
    else:
        os.mkdir(settings.home_path)

    token_file = open(settings.token_path, "w")
    json.dump(api.get_token(), token_file)
    token_file.close()
    return True


def delete_tokenfile(settings):
    """
        We delete the tokenfile if we don't have a valid token to save.
    """
    if os.path.exists(settings.token_path):
        os.remove(settings.token_path)
        return True
    return False


def get_email(settings):
    sys.stderr.write(settings.login_name)
    sys.stderr.flush()

    email = raw_input()

    return email


def get_password(create=False):
    password = None
    for i in range(3):
        password = recode_input(getpass('Password: '))
        if create:
            password2 = recode_input(getpass('Password (again): '))
            if password != password2:
                print messages['PasswordsDontMatch']
                if i == 2:
                    raise PasswordsDontMatchException()
            else:
                break
        else:
            break

    return password


def get_credentials(settings, create=False):
    """
        We use this to ask the user for his credentials in case we have no
        valid token.
        If create is true, the user is asked twice for the password,
        to make sure, that no typing error occurred. This is done three times
        after that a PasswordsDontMatchException is thrown.
    """

    email = get_email(settings)

    password = get_password(create)

    return email, password
