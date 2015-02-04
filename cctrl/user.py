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
import json

from pycclib.cclib import GoneError, NotImplementedError, ForbiddenError
from pycclib.cclib import ConflictDuplicateError
from pycclib import cclib

from cctrl.error import PasswordsDontMatchException, InputErrorException, \
    messages
from cctrl.auth import get_credentials, set_user_config, get_user_config
from cctrl.output import print_keys
from cctrl.common import get_email_and_password

from output import print_key
from oshelpers import readContentOf
from keyhelpers import is_key_valid, ask_user_to_use_default_ssh_public_key, \
    create_new_default_ssh_keys, get_default_ssh_key_path


class UserController(object):
    """
        This controller handles all user related actions.
    """

    api = None

    def __init__(self, api, settings):
        self.api = api
        self.settings = settings

    def checktoken(self, args):
        try:
            self.api.read_users()
        except cclib.TokenRequiredError:
            sys.exit(1)
        sys.exit(0)

    def create(self, args):
        """
            Create a new user.
        """
        if not self.settings.user_registration_enabled:
            print messages['RegisterDisabled'].format(self.settings.user_registration_url)
            return

        self.api.set_token(None)
        if args.name and args.email and args.password:
            name = args.name[0]
            email = args.email[0]
            password = args.password[0]
        else:
            name = raw_input('Username: ')
            try:
                email, password = get_credentials(self.settings, create=True)
            except PasswordsDontMatchException:
                return
        try:
            self.api.create_user(name, email, password)
        except NotImplementedError:
            raise InputErrorException('CommandNotImplemented')

        print messages['UserCreatedNowCheckEmail']

    def activate(self, args):
        """
            Activate a new user using the information from the
            activation email.
        """
        self.api.set_token(None)
        try:
            self.api.update_user(
                args.user_name[0],
                activation_code=args.activation_code[0])
        except GoneError:
            raise InputErrorException('WrongUsername')
        except NotImplementedError:
            raise InputErrorException('CommandNotImplemented')

    def delete(self, args):
        """
            Delete your user account.
        """

        users = self.api.read_users()
        if not args.force_delete:
            question = raw_input('Do you really want to delete your user? ' +
                                 'Type "Yes" without the quotes to delete: ')
        else:
            question = 'Yes'
        if question.lower() == 'yes':
            try:
                self.api.delete_user(users[0]['username'])
            except NotImplementedError:
                raise InputErrorException('CommandNotImplemented')
            except ForbiddenError:
                raise InputErrorException('DeleteAppsBeforeUser')

            # After we have deleted our user we should also delete
            # the token_file to avoid confusion
            self.api.set_token(None)
        else:
            raise InputErrorException('SecurityQuestionDenied')

    def addKey(self, args):
        """
            Add a given public key to cloudControl user account.
        """
        default_key_path = get_default_ssh_key_path()

        # Possibility #1: User is providing a non-default SSH key
        key_to_read = args.public_key
        if not is_key_valid(key_to_read):

            # Possibility #2: Try the default RSA public key
            print >> sys.stderr, "Key '{0}' seems to be invalid or not found!".format(key_to_read)
            ask_user_to_use_default_ssh_public_key()

            # Possibility #3: All failed! Let's just create new keys for user!
            if not is_key_valid(default_key_path):
                if key_to_read != default_key_path:
                    print >> sys.stderr, "Default key '{0}' seems to be invalid or not found!".format(default_key_path)
                create_new_default_ssh_keys()

            # We've filtered all cases: the key must be the default one!
            key_to_read = default_key_path

        # Good, we have the key! Now, read the content of the key!
        public_rsa_key_content = readContentOf(key_to_read)

        # Add public RSA-key to cloudControl user account
        try:
            users = self.api.read_users()
            self.api.create_user_key(
                users[0]['username'],
                public_rsa_key_content)

        except ConflictDuplicateError:
            raise InputErrorException('KeyDuplicate')

    def listKeys(self, args):
        """
            List your public keys.
        """
        users = self.api.read_users()
        if args.id:
            key = self.api.read_user_key(users[0]['username'], args.id)
            print_key(key)
        else:
            keys = self.api.read_user_keys(users[0]['username'])
            print_keys(keys)

    def removeKey(self, args):
        """
            Remove one of your public keys specified by key_id.

            listKeys() shows the key_ids.
        """
        users = self.api.read_users()
        if not args.force_delete:
            question = raw_input('Do you really want to remove your key? ' +
                                 'Type "Yes" without the quotes to remove: ')
        else:
            question = 'Yes'
        if question.lower() == 'yes':
            self.api.delete_user_key(users[0]['username'], args.id[0])
        else:
            raise InputErrorException('SecurityQuestionDenied')

    def logout(self, args):
        """
            Logout a user by deleting the token.json file.
        """
        self.api.set_token(None)

    def registerAddon(self, args):
        file_content = readContentOf(args.manifest)
        email, password = get_email_and_password(self.settings)
        try:
            self.api.register_addon(email, password, json.loads(file_content))
        except cclib.UnauthorizedError:
            sys.exit(messages['NotAuthorized'])
        except cclib.ForbiddenError, e:
            sys.exit(messages['NotAllowed'])
        except cclib.ConnectionException:
            sys.exit(messages['APIUnreachable'])
        except Exception as e:
            sys.exit(e)

    def setup(self, args):
        user_config = get_user_config(self.settings)
        ssh_key_path = self._get_setup_ssh_key_path(user_config, args)
        if not is_key_valid(ssh_key_path):
            # If given key path is not default and does not exist
            # we raise an error
            if ssh_key_path != get_default_ssh_key_path():
                raise InputErrorException('WrongPublicKey')

            # If given key path was the default one, we create the key
            # pair for the user
            print >> sys.stderr, "Key '{0}' seems to be invalid or not found!".format(ssh_key_path)
            create_new_default_ssh_keys()

        ssh_key_content = readContentOf(ssh_key_path)

        ssh_auth = self._get_setup_ssh_auth(self.settings, user_config, args)

        if args.email:
            set_user_config(self.settings, email=args.email)

        try:
            users = self.api.read_users()
            self.api.create_user_key(
                users[0]['username'],
                ssh_key_content)

        except ConflictDuplicateError:
            # Key already added, nothing to do.
            pass

        set_user_config(self.settings,
                        ssh_auth=ssh_auth,
                        ssh_path=ssh_key_path)

    def _get_setup_ssh_key_path(self, user_config, args):
        if args.ssh_key_path:
            return os.path.abspath(args.ssh_key_path)

        if user_config.get('ssh_path'):
            return user_config.get('ssh_path')

        return get_default_ssh_key_path()

    def _get_setup_ssh_auth(self, settings, user_config, args):
        if not settings.ssh_auth:
            return False

        if args.ssh_auth:
            return args.ssh_auth == 'yes'

        return user_config.get('ssh_auth', True)
