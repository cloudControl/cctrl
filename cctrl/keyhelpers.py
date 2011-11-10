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

from error import InputErrorException
from oshelpers import readContentOf, isValidFile



def isKeyValid(key):
    """
        Is the given key a valid SSH-key with RSA encryption?
    """        
    # check if provided SSH-key file exists ...
    if not isValidFile(key):
        return False
            
    # Ok, file found! Check if we can read the file's content ...
    file_content = readContentOf(key)
    if file_content == None:
        return False
                                  
    # File read! Now check if it's RSA encrypted ...
    if file_content[:8] != 'ssh-rsa ':
        return False
                
    # All Ok!
    return True
     
    

def generateRSAKey(user_ssh_path, key_file_name="id_rsa.pub"):
    """
        Generate an RSA-encrypted key for the user
        
        Will return public key string if all went well, otherwise "None"
    """                
    if key_file_name == "id_rsa.pub":            
        if not os.path.exists(user_ssh_path):
            os.mkdir(user_ssh_path, 0700)

    # Create the private key, first.
    key_base_name = key_file_name.rstrip(".pub")
    private_key = generatePrivateRSAKeyFile(user_ssh_path, key_base_name)

    # Now, create the public key (using the private key) ...
    public_key_string = generatePublicRSAKeyFile(private_key, user_ssh_path, key_base_name)
        
    return { "status" : 0, "pubkey" : public_key_string }   


def generatePrivateRSAKeyFile(ssh_path, key_base_name):
    """
        Generate a default PRIVATE SSH key file using RSA
    """
    key = RSAKey.generate(2048)
    private_key_file_name = ssh_path + "/" + key_base_name
    key.write_private_key_file(private_key_file_name)
    
    # Ok, pass back private key object
    return key
    
    
def generatePublicRSAKeyFile(private_key, ssh_path, key_base_name):
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
    
    
def createSSHKeysWithUserInPath(ssh_path):
    """
        Generate a set of private and public keys for user
        
        Returns content of public key if all went well. Otherwise,
        return "None"
    """
    question = raw_input('No valid SSH public key (RSA) found! ' +
                         'Type "Yes" to generate a keypair: ')
    if question != 'Yes':            
        raise InputErrorException('SecurityQuestionDenied')
                    
    return generateRSAKey(ssh_path)["pubkey"]
    
            
def askUserToUseDefaultSSHPublicKey(ssh_path):
    """
        Ask the user if the default public SSH-key (RSA)
        shall be used. If yes, return the full path to
        the public key file.
    """
    default_rsa_public_key = ssh_path + "/id_rsa.pub" 
    question = raw_input('Found default key {0} . '.format(default_rsa_public_key) +
                         'Type "Yes" to use the default key: ')
    if question != "Yes":
        raise InputErrorException('SecurityQuestionDenied')
    
    return default_rsa_public_key