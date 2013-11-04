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

from cctrl.error import PasswordsDontMatchException, InputErrorException, messages
from cctrl.auth import get_credentials
from pycclib.cclib import GoneError
from cctrl.output import print_keys
from pycclib.cclib import ConflictDuplicateError
from output import print_key
from oshelpers import readContentOf
from keyhelpers import is_key_valid, ask_user_to_use_default_ssh_public_key, \
    create_new_default_ssh_keys
from pycclib import cclib


class UserController():
    """
        This controller handles all user related actions.
    """

    api = None

    def __init__(self, api):
        self.api = api

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
        self.api.set_token(None)
        if args.name and args.email and args.password:
            name = args.name[0]
            email = args.email[0]
            password = args.password[0]
        else:
            name = raw_input('Username: ')
            try:
                email, password = get_credentials(create=True)
            except PasswordsDontMatchException:
                return
        self.api.create_user(name, email, password)
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

    def delete(self, args):
        """
            Delete your user account.
        """
        apps = self.api.read_apps()
        if len(apps) > 0:
            raise InputErrorException('DeleteAppsBeforeUser')

        users = self.api.read_users()
        if not args.force_delete:
            question = raw_input('Do you really want to delete your user? ' +
                                 'Type "Yes" without the quotes to delete: ')
        else:
            question = 'Yes'
        if question.lower() == 'yes':
            self.api.delete_user(users[0]['username'])
            # After we have deleted our user we should also delete
            # the token_file to avoid confusion
            self.api.set_token(None)
        else:
            raise InputErrorException('SecurityQuestionDenied')

    def addKey(self, args):
        """
            Add a given public key to cloudControl user account.
        """
        if sys.platform == 'win32':
            default_key_path = os.path.expanduser('~') + "/.ssh/id_rsa.pub"
        else:
            default_key_path = os.getenv("HOME") + "/.ssh/id_rsa.pub"

        # Possibility #1: User is providing a non-default SSH key
        key_to_read = args.public_key
        if not is_key_valid(key_to_read):

            # Possibility #2: Try the default RSA public key
            print "Key '{0}' seems to be invalid or not found!".format(key_to_read)
            ask_user_to_use_default_ssh_public_key()

            # Possibility #3: All failed! Let's just create new keys for user!
            if not is_key_valid(default_key_path):
                if key_to_read != default_key_path:
                    print "Default key '{0}' seems to be invalid or not found!".format(default_key_path)
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
