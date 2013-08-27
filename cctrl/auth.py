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
    #noinspection PyUnresolvedReferences
    import simplejson as json

from cctrl.error import messages, PasswordsDontMatchException
from cctrl.settings import TOKEN_FILE_PATH, HOME_PATH, CONFIG_FILE_PATH


def update_tokenfile(api):
    """
        Because it is a real pain we don't want to ask developers for their
        username and password every time they call a method.

        Therefore we authenticate users via token for each request and only
        require email and password for a new token.
        A token is valid for a given period of time. Each successful API
        request resets the expiration time.
    """
    if api.check_token():
        write_tokenfile(api)
        return True
    return False


def read_tokenfile():
    """
        Read the token from the token_file in TOKEN_FILE_PATH specified in
        cctrl.settings
    """
    token = None
    if os.path.exists(TOKEN_FILE_PATH):
        token_file = open(TOKEN_FILE_PATH, "r")
        try:
            token = json.load(token_file)
        except ValueError:
            token = None
        token_file.close()
    return token


def write_tokenfile(api):
    """
        This method checks, if the .cloudControl directory inside the
        users home exists or is a file. If not, we create it and then
        write the token file.
    """
    if os.path.isdir(HOME_PATH):
        pass
    elif os.path.isfile(HOME_PATH):
        print 'Error: ' + HOME_PATH + ' is a file, not a directory.'
        sys.exit(1)
    else:
        os.mkdir(HOME_PATH)

    tokenfile = open(TOKEN_FILE_PATH, "w")
    json.dump(api.get_token(), tokenfile)
    tokenfile.close()
    return True


def delete_tokenfile():
    """
        We delete the tokenfile if we don't have a valid token to save.
    """
    if os.path.exists(TOKEN_FILE_PATH):
        os.remove(TOKEN_FILE_PATH)
        return True
    return False


def read_configfile():
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH) as config_fp:
                config_json = json.loads(config_fp.read())
            return config_json['email'], config_json['password']
        except (ValueError, IOError, KeyError):
            # fall through to normal authorization
            pass


def write_configfile(*args):
    if os.path.exists(CONFIG_FILE_PATH):
        question = raw_input(
                "'%s' exsits, type 'Yes' without the quotes to overwrite:"
                % CONFIG_FILE_PATH)
    if question.lower() == 'yes':
        email, password = get_credentials(read=False)
        with open(CONFIG_FILE_PATH, 'w') as config_fp:
            config_fp.write(json.dumps({'email': email, 'password': password}))


def get_credentials(create=False, read=True):
    """
        We use this to ask the user for his credentials in case we have no
        valid token.
        If create is true, the user is asked twice for the password,
        to make sure, that no typing error occurred. This is done three times
        after that a PasswordsDontMatchException is thrown.
    """
    if read:
        credentials = read_configfile()
        if credentials is not None:
            return credentials
    email = raw_input('Email   : ')
    password = None
    for i in range(3):
        #noinspection PyArgumentEqualDefault
        password = recode_input(getpass('Password: '))
        if create:
            password2 = recode_input(getpass('Password (again): '))
            if password != password2:
                print messages['PasswordsDontMatch']
                if i == 2:
                    #noinspection PyExceptionInherit
                    raise PasswordsDontMatchException()
            else:
                break
        else:
            break
    return email, password
