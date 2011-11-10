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
import commands

from subprocess import call
from error import InputErrorException
from oshelpers import readContentOf, isValidFile


def is_key_valid(key):
    """
        Is the given key a valid SSH-key with RSA encryption?
    """        
    if not isValidFile(key):
        return False
            
    file_content = readContentOf(key)
    if file_content == None:
        return False
                                  
    # File read! Now check if it's RSA encrypted ...
    if file_content[:8] != 'ssh-rsa ':
        return False
                
    return True
         

def generate_rsa_keys_via_shell():
    """
        Create new set of SSH keys via shell with 'ssh-keygen'            
    """
    # If we're on Windows, we should not execute this function!        
    if sys.platform == 'win32':
        return -1
    
    # Check if default keys already exist. If yes, bail out!
    ssh_path = os.getenv("HOME") + "/.ssh"
    if os.path.exists(ssh_path + "/id_rsa.pub"):
        return -1 
                    
    # Check if "ssh-keygen" is installed. If not, stop right here!
    error_code = commands.getstatusoutput("which ssh-keygen")[0]
    if error_code != 0:
        return -1
    
    # Call "ssh-keygen" to let the users create his/her keys ...    
    call(["ssh-keygen","-t", "rsa", "-b", "2048", "-f", ssh_path + "/id_rsa"])
    
    # 0 if everything went fine!
    return 0
        

def create_new_default_ssh_keys():
    """
        Generate a set of private and public keys for user                
    """
    question = raw_input('Type "Yes" to generate a new default SSH-key pair: ')
    if question.lower() != 'yes':            
        raise InputErrorException('SecurityQuestionDenied')
                        
    # Let user create key, then check if everything went fine!
    if generate_rsa_keys_via_shell() == -1:
        raise InputErrorException('UserShouldCreateKey')
        
    # Ok, new SSH default keys seemed to be created.    
    return 0 
    
            
def ask_user_to_use_default_ssh_public_key():
    """
        Ask the user if the default public SSH-key (RSA)
        shall be used.
    """
    default_rsa_public_key = os.getenv("HOME") + "/.ssh/id_rsa.pub" 
    
    # Check first if we actually have a default SSH public key.
    # If we don't then simply return nothing ("")
    if not isValidFile(default_rsa_public_key):
        return ""
    
    # Ok, found! Ask user if we should use this one ...
    question = raw_input("Found default key '{0}' . ".format(default_rsa_public_key) +
                         'Type "Yes" to use the default key: ')
    if question.lower() != 'yes':
        raise InputErrorException('SecurityQuestionDenied')
    
    return 0