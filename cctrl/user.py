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
import warnings

# paramiko uses pycrypto's RandomPool which throws a deprecation warning
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from paramiko import RSAKey

from cctrl.error import PasswordsDontMatchException, InputErrorException,\
    messages
from cctrl.auth import get_credentials, delete_tokenfile
from pycclib.cclib import GoneError
from cctrl.output import print_keys
from pycclib.cclib import ConflictDuplicateError
from output import print_key

class UserController():
    """
        This controller handles all user related actions.
    """

    api = None

    def __init__(self, api):
        self.api = api

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

    def activate(self, args):
        """
            Activate a new user using the information from the activation email.
        """
        self.api.set_token(None)
        try:
            self.api.update_user(args.user_name[0], activation_code=args.activation_code[0])
        except GoneError:
            raise InputErrorException('WrongUsername')

    def delete(self, args):
        """
            Delete your user account.
        """
        users = self.api.read_users()
        if not args.force_delete:
            question = raw_input('Do you really want to delete your user? Type "Yes" without the quotes to delete. ')
        else:
            question = 'Yes'
        if question == 'Yes':
            self.api.delete_user(users[0]['username'])
            # After we have deleted our user we should also delete the token_file
            # to avoid confusion
            self.api.set_token(None)
        else:
            print messages['SecurityQuestionDenied']

    def addKey(self, args):
        """
            Add a public key to your user account.
        """
        if os.path.basename(args.public_key) != 'id_rsa.pub':
            raise InputErrorException('WrongPubKeyName')
        pubkey_string = ''
        pubkey_path = os.path.abspath(args.public_key)
        privkey_path = os.path.abspath(args.public_key.rstrip('.pub'))
        ssh_path = os.path.dirname(pubkey_path)
        users = self.api.read_users()
        try:
            pubkey = open(pubkey_path, 'r')
        except IOError:
            question = raw_input('No public key found in "{0}". Type "Yes" to generate a keypair. '.format(ssh_path))
            if question == 'Yes':
                try:
                    if not os.path.exists(ssh_path):
                        os.mkdir(ssh_path, 0700)
                except Exception, e:
                    print str(e)
                print 'generating key... this may take a few moments.'
                key = RSAKey.generate(2048)
                key.write_private_key_file(privkey_path)
                try:
                    username = os.getlogin()
                except AttributeError:
                    username = os.getenv('USERNAME', 'cloudControl')
                try:   
                    hostname = os.uname()[1]
                except AttributeError:
                    hostname = os.getenv('COMPUTERNAME', 'localhost')
                pubkey_string = 'ssh-rsa {0} {1}@{2} \n'.format(
                    key.get_base64(),
                    username,
                    hostname
                )
                pubkey = open(pubkey_path, 'w')
                pubkey.write(pubkey_string)
            else:
                raise InputErrorException('NoSuchKeyFile')
        else:
            pubkey_string = str(pubkey.read())
        finally:
            if pubkey_string[:8] != 'ssh-rsa ':
                raise InputErrorException('WrongKeyFormat')
            if pubkey_string:
                try:
                    self.api.create_user_key(users[0]['username'], pubkey_string)
                except ConflictDuplicateError:
                    raise InputErrorException('KeyDuplicate')
                pubkey.close()

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
            question = raw_input('Do you really want to remove your key? Type "Yes" without the quotes to remove. ')
        else:
            question = 'Yes'
        if question == 'Yes':
            self.api.delete_user_key(users[0]['username'], args.id[0])
        else:
            print messages['SecurityQuestionDenied']

    def logout(self, args):
        """
            Logout a user by deleting the token.json file.
        """
        self.api.set_token(None)
