#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Copyright 2014 cloudControl GmbH

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

import argparse

from pycclib.version import __version__ as cclibversion

import cctrl.common as common
from cctrl.output import get_version
from cctrl.settings import VERSION
from cctrl.user import UserController


def parse_cmdline(user):
    """
      We parse the commandline using argparse from
      http://code.google.com/p/argparse/.
    """
    version = get_version(VERSION, cclibversion)
    usage = '%(prog)s [-h, --help] [command]'
    description = '%(prog)s controls your user account'
    epilog = "And now you're in control"

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        usage=usage)

    parser.add_argument('-v', '--version', action='version', version=version)

    subparsers = parser.add_subparsers(
        title='commands',
        description='available commands',
        metavar='')

    create_subparser = subparsers.add_parser('create', help="create user")
    create_subparser.add_argument(
        "--name",
        nargs=1,
        action="store",
        dest="name",
        help="the username")
    create_subparser.add_argument(
        "--email",
        nargs=1,
        action="store",
        dest="email",
        help="the email")
    create_subparser.add_argument(
        "--password",
        nargs=1,
        action="store",
        dest="password",
        help="the password")
    create_subparser.set_defaults(func=user.create)

    setup_subparser = subparsers.add_parser('setup', help="setup user")
    setup_subparser.add_argument(
        "--email",
        action="store",
        dest="email",
        help="user email")
    setup_subparser.add_argument(
        "--ssh-auth",
        action='store',
        choices=['yes', 'no'],
        dest="ssh_auth",
        default=None,
        help="disable ssh public key auth")
    setup_subparser.add_argument(
        "--ssh-key-path",
        action="store",
        dest="ssh_key_path",
        default=None,
        help="path of the default public key")
    setup_subparser.set_defaults(func=user.setup)

    activate_subparser = subparsers.add_parser(
        'activate',
        help="activate user")
    activate_subparser.add_argument(
        'user_name',
        nargs=1,
        help='your user name')
    activate_subparser.add_argument(
        'activation_code',
        nargs=1,
        help='activation code from the email')
    activate_subparser.set_defaults(func=user.activate)

    delete_subparser = subparsers.add_parser('delete', help="delete user")
    delete_subparser.add_argument(
        '-f',
        '--force',
        action="store_true",
        dest="force_delete",
        help="don't ask for confirmation")
    delete_subparser.set_defaults(func=user.delete)

    listUsers_subparser = subparsers.add_parser(
        'key',
        help="list public keys and key ids")
    listUsers_subparser.add_argument(
        'id',
        nargs='?',
        help='print key by id')
    listUsers_subparser.set_defaults(func=user.listKeys)

    addKey_subparser = subparsers.add_parser('key.add', help="add public key")
    addKey_subparser.add_argument(
        'public_key',
        nargs='?',
        default=os.path.expanduser('~/.ssh/id_rsa.pub'),
        help='path to id_rsa.pub file')
    addKey_subparser.set_defaults(func=user.addKey)

    removeKey_subparser = subparsers.add_parser(
        'key.remove',
        help="remove public key")
    removeKey_subparser.add_argument(
        '-f',
        '--force',
        action="store_true",
        dest="force_delete",
        help="don't ask for confirmation")
    removeKey_subparser.add_argument(
        'id',
        nargs=1,
        help='the key_id of the key - see listKeys')
    removeKey_subparser.set_defaults(func=user.removeKey)

    logout_subparser = subparsers.add_parser(
        'logout',
        help="logout - this deletes the saved token")
    logout_subparser.set_defaults(func=user.logout)

    check_token_subparser = subparsers.add_parser('checktoken')
    check_token_subparser.set_defaults(func=user.checktoken)

    registerAddon_subparser = subparsers.add_parser('addon.register', help="registers an addon")
    registerAddon_subparser.add_argument(
        'manifest',
        help='path to the manifest file')
    registerAddon_subparser.set_defaults(func=user.registerAddon)

    args = parser.parse_args()

    common.run(args, user.api, user.settings)


def setup_cli(settings):
    api = common.init_api(settings)
    try:
        user = UserController(api, settings)
        parse_cmdline(user)
    except KeyboardInterrupt:
        pass
    finally:
        common.shutdown(api, settings)
