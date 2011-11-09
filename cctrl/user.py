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
from cctrl.auth import get_credentials
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
        users = self.api.read_users()
        if not args.force_delete:
            question = raw_input('Do you really want to delete your user? ' +
                                 'Type "Yes" without the quotes to delete: ')
        else:
            question = 'Yes'
        if question == 'Yes':
            self.api.delete_user(users[0]['username'])
            # After we have deleted our user we should also delete
            # the token_file to avoid confusion
            self.api.set_token(None)
        else:
            print messages['SecurityQuestionDenied']


    def addKey(self, args):
        """
            Add a given public key to cloudControl user account.
        """
        # Check if key is valid (= valid file and RSA-encrypted)
        # If yes, read content ...
        if  self._isKeyValid(args.public_key):                                
            public_rsa_key_content = self._readContentOf(args.public_key)
        else:
            print "Key seemed to be invalid! "
            ssh_path = os.getenv("HOME") + "/.ssh"
            
            # Given key is not valid! Then, let's ask user if we should
            # try to use the default RSA public key ...                                                                            
            default_public_key = self._askUserToUserDefaultSSHPublicKey(ssh_path) 
            if self._isKeyValid(default_public_key):
                # Default RSA SSH public key found! Read it!                
                public_rsa_key_content = self._readContentOf(default_public_key)
            else:
                # We can't even find a default key! Then let's create one
                # if the user accepts ...
                public_rsa_key_content = self._createSSHKeysWithUserInPath(ssh_path)
                                        
        # Add public RSA-key to cloudControl user account
        try:
            users = self.api.read_users()
            self.api.create_user_key(
                users[0]['username'],
                public_rsa_key_content)
            
            print "Note: Please make sure to add newly created keys to your SSH configuration!"
        except ConflictDuplicateError:
            raise InputErrorException('KeyDuplicate')
        
    def addKeyOriginal(self, args):
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
            question = raw_input('No public key found in ' + ssh_path + ' . ' +
                                 'Type "Yes" to generate a keypair: ')
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
                    hostname)
                pubkey = open(pubkey_path, 'w')
                pubkey.write(pubkey_string)
            else:
                raise InputErrorException('SecurityQuestionDenied')
        else:
            pubkey_string = str(pubkey.read())
            
        if pubkey_string[:8] != 'ssh-rsa ':
            raise InputErrorException('WrongKeyFormat')
        if pubkey_string:
            try:
                self.api.create_user_key(
                    users[0]['username'],
                    pubkey_string)
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
            question = raw_input('Do you really want to remove your key? ' +
                                 'Type "Yes" without the quotes to remove: ')
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
        
    
    
    # #############################################################################
    # HELPERS
    #
        
    def _isKeyValid(self, key):
        """
            Is the given key a valid SSH-key with RSA encryption?
        """        
        # check if provided SSH-key file exists ...
        if not self._isValidFile(key):
            return False
                
        # Ok, file found! Check if we can read the file's content ...
        file_content = self._readContentOf(key)
        if file_content == None:
            return False
                                      
        # File read! Now check if it's RSA encrypted ...
        if file_content[:8] != 'ssh-rsa ':
            return False
                    
        # All Ok!
        return True
         
         
    def _isValidFile(self, filename):
        """
            Is the given filename a valid file?
        """
        return os.path.isfile(os.path.abspath(filename))
                    
                  
    def _readContentOf(self, filename):
        """
            Read a given file's content into a string
            
            Returns contents of given file as string, otherwise "None"
        """
        file_content = ''
        
        # check if file exists
        if not os.path.isfile(os.path.abspath(filename)):
            return InputErrorException('FileNotFound')
        
        # open file and read into string
        try:
            open_file = open(os.path.abspath(filename), 'r')
            file_content = str(open_file.read())
        except IOError:
            raise InputErrorException('FileReadOrWriteFailed')
        
        # pass back content
        return file_content

        

    def _generateRSAKey(self, user_ssh_path, key_file_name="id_rsa.pub"):
        """
            Generate an RSA-encrypted key for the user
            
            Will return public key string if all went well, otherwise "None"
        """                
        if key_file_name == "id_rsa.pub":            
            if not os.path.exists(user_ssh_path):
                os.mkdir(user_ssh_path, 0700)

        # Create the private key, first.
        key_base_name = key_file_name.rstrip(".pub")
        private_key = self._generatePrivateRSAKeyFile(user_ssh_path, key_base_name)
    
        # Now, create the public key (using the private key) ...
        public_key_string = self._generatePublicRSAKeyFile(private_key, user_ssh_path, key_base_name)
            
        return { "status" : 0, "pubkey" : public_key_string }   
    
    
    def _generatePrivateRSAKeyFile(self, ssh_path, key_base_name):
        """
            Generate a default PRIVATE SSH key file using RSA
        """
        key = RSAKey.generate(2048)
        private_key_file_name = ssh_path + "/" + key_base_name
        key.write_private_key_file(private_key_file_name)
        
        # Ok, pass back private key object
        return key
        
        
    def _generatePublicRSAKeyFile(self, private_key, ssh_path, key_base_name):
        """
            Generate a default PUBLIC SSH key file using RSA
        """
        try:
            username = os.getlogin()
        except AttributeError:
            username = os.getenv('USERNAME', 'cloudControl')
            
        try:
            hostname = os.uname()[1]
        except AttributeError:
            hostname = os.getenv('COMPUTERNAME', 'localhost')
            
        # Create the content of the public key as string
        pubkey_string = 'ssh-rsa {0} {1}@{2} \n'.format(
            private_key.get_base64(),
            username,
            hostname)
        
        # Write the public key to file system
        public_key_filename = ssh_path + "/" + key_base_name + ".pub"
        pubkey = open(public_key_filename, 'w')
        pubkey.write(pubkey_string)
        pubkey.close()
        
        # Ok, pass back public key file name
        return pubkey_string
        
        
    def _createSSHKeysWithUserInPath(self, ssh_path):
        """
            Generate a set of private and public keys for user
            
            Returns content of public key if all went well. Otherwise,
            return "None"
        """
        question = raw_input('No valid SSH public key (RSA) found! ' +
                             'Type "Yes" to generate a keypair: ')
        if question != 'Yes':            
            raise InputErrorException('SecurityQuestionDenied')
                        
        return self._generateRSAKey(ssh_path)["pubkey"]
        
                
    def _askUserToUserDefaultSSHPublicKey(self, ssh_path):
        """
            Ask the user if the default public SSH-key (RSA)
            shall be used. If yes, return the full path to
            the public key file.
        """
        default_rsa_public_key = ssh_path + "/id_rsa.pub" 
        question = raw_input('Found default key {0} . '.format(default_rsa_public_key) +
                             'Type "Yes" to use the default key: ')
        if question != "Yes":
            raise InputErrorException('NoPublicKeyProvided')
        
        return default_rsa_public_key
        
