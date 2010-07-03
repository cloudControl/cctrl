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

from cctrl.error import PasswordsDontMatchException, InputErrorException,\
    messages
from cctrl.auth import get_credentials, delete_tokenfile
from pycclib.cclib import GoneError
from cctrl.output import print_keys

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
            name = args.name
            email = args.email
            password = args.password
        else:
            name = raw_input('Name  : ')
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
            self.api.update_user(args.user_name, activation_code=args.activation_code)
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
            delete_tokenfile()
        else:
            print messages['SecurityQuestionDenied']
    
    def addKey(self, args):
        """
            Add a public key to your user account.
        """
        users = self.api.read_users()
        keyFile = open(args.public_key, 'r')
        self.api.create_user_key(users[0]['username'], keyFile.read())
        keyFile.close()
      
    def listKeys(self, args):
        """
            List your public keys.
        """
        users = self.api.read_users()
        keys = self.api.read_user_keys(users[0]['username'])
        print_keys(keys)
    
    def removeKey(self, args):
        """
            Remove one of your public keys specified by key_id.
            
            listKeys() shows the key_ids.
        """
        users = self.api.read_users()
        if not args.force_delete:
            question = raw_input('Do you really want to remove your Key? Type "Yes" without the quotes to delete. ')
        else:
            question = 'Yes'
        if question == 'Yes':
            self.api.delete_user_key(users[0]['username'], args.id)
        else:
            print messages['SecurityQuestionDenied']
