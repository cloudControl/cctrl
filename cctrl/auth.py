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
import sys

from __builtin__ import open, raw_input, range
from exceptions import ImportError, ValueError

import ConfigParser
from getpass import getpass
from cctrl.oshelpers import recode_input

try:
    import json
except ImportError:
    import simplejson as json

from pycclib import cclib

from cctrl.keyhelpers import get_default_ssh_key_path, \
    get_public_key_fingerprint, sign_token
from cctrl.error import SignatureException, \
    PublicKeyException, messages, PasswordsDontMatchException


def create_config_dir(settings):
    if os.path.isdir(settings.home_path):
        return
    elif os.path.isfile(settings.home_path):
        print >> sys.stderr, 'Error: ' + settings.home_path + ' is a file, not a directory.'
        sys.exit(1)
    else:
        os.mkdir(settings.home_path)


def create_token(api, settings, email, password):
    while True:
        try:
            if get_user_config(settings).get('ssh_auth') and password is None:
                key_path = get_user_config(settings).get('ssh_path',
                                                         get_default_ssh_key_path())
                fingerprint = get_public_key_fingerprint(key_path)
                if not fingerprint:
                    raise PublicKeyException('WrongPublicKey')

                ssh_token = api.create_ssh_token()
                signature = sign_token(key_path, fingerprint, ssh_token)
                return api.create_token_ssh_auth(email,
                                                 ssh_token,
                                                 signature,
                                                 fingerprint)
            else:
                return api.create_token_basic_auth(email, password)

        except (cclib.APIException, SignatureException, PublicKeyException) as e:
            if password is not None:
                sys.exit(messages['NotAuthorized'])

            print >> sys.stderr, str(e) + " " + messages['NotAuthorizedPublicKey']
            password = get_password_env(settings)
            if not password:
                password = get_password()


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
    create_config_dir(settings)

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


def set_user_config(settings, email=None, ssh_auth=None, ssh_path=None):
    create_config_dir(settings)
    config = ConfigParser.ConfigParser()
    config.read(settings.config_path)

    if not config.has_section('user'):
        config.add_section('user')

    if email:
        config.set('user', 'email', email)

    if ssh_auth is not None:
        config.set('user', 'ssh_auth', ssh_auth)

    if ssh_path:
        config.set('user', 'ssh_path', ssh_path)

    with open(settings.config_path, 'w') as user_config:
        config.write(user_config)


def get_user_config(settings):
    config = ConfigParser.ConfigParser()
    config.read(settings.config_path)
    if config.has_section('user'):
        cf = dict(config.items('user'))
        if 'ssh_auth' in cf:
            cf['ssh_auth'] = config.getboolean('user', 'ssh_auth')

        return cf

    return {}


def get_email_and_password(settings):
    email = get_email_env(settings) or \
        get_user_config(settings).get('email') or \
        get_email(settings)

    if get_user_config(settings).get('ssh_auth'):
        return email, None

    password = get_password_env(settings)
    if password is None:
        password = get_password()

    return email, password


def get_email(settings):
    sys.stderr.write(settings.login_name)
    sys.stderr.flush()

    email = raw_input()
    set_user_config(settings, email=email)
    return email


def get_email_env(settings):
    try:
        email = os.getenv(settings.login_creds['email'])
    except KeyError:
        return None

    return email


def get_password(create=False):
    password = None
    for i in range(3):
        password = recode_input(getpass('Password: '))
        if create:
            password2 = recode_input(getpass('Password (again): '))
            if password != password2:
                print >> sys.stderr, messages['PasswordsDontMatch']
                if i == 2:
                    raise PasswordsDontMatchException()
            else:
                break
        else:
            break

    return password


def get_password_env(settings):
    try:
        password = os.getenv(settings.login_creds['pwd'])
    except KeyError:
        return None

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
