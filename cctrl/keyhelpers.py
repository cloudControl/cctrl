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
import base64
import hashlib
import commands

from subprocess import call
from error import InputErrorException, SignatureException
from oshelpers import readContentOf, isValidFile

import paramiko.agent
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import PasswordRequiredException
from paramiko.message import Message


def is_key_valid(key):
    """
        Is the given key a valid SSH-key with RSA encryption?
    """
    if not isValidFile(key):
        return False

    file_content = readContentOf(key)
    if not file_content:
        return False

    # File read! Now check if it's RSA encrypted ...
    if file_content[:8] != 'ssh-rsa ':
        return False

    return True


def generate_rsa_keys():
    """
        Create new set of SSH keys via shell with 'ssh-keygen'
        or, for win32, via paramiko
    """
    ssh_path = get_default_ssh_dir()

    # If we're on Windows, we need to take a different approach
    if sys.platform == 'win32':
        return generate_rsa_key_manually(ssh_path)

    # Check if default keys already exist. If yes, bail out!
    if os.path.exists(get_default_ssh_key_path()):
        return False

    # Check if "ssh-keygen" is installed. If not, stop right here!
    error_code = commands.getstatusoutput("which ssh-keygen")[0]
    if error_code != 0:
        return False

    # Call "ssh-keygen" to let the users create his/her keys ...
    call(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", ssh_path + "/id_rsa"])

    return True


def generate_rsa_key_manually(user_ssh_path, key_file_name="id_rsa.pub"):
    """
        Generate an RSA-encrypted key for the user
        Will return public key string if all went well, otherwise "None"
    """
    if key_file_name == "id_rsa.pub":
        if not os.path.exists(user_ssh_path):
            os.mkdir(user_ssh_path, 0700)

    # Create the private key, first.
    key_base_name = key_file_name.rstrip(".pub")
    private_key = generate_private_rsa_key_file(user_ssh_path, key_base_name)

    # Now, create the public key (using the private key) ...
    generate_public_rsa_key_file(private_key, user_ssh_path, key_base_name)

    return True


def generate_private_rsa_key_file(ssh_path, key_base_name):
    """
        Generate a default PRIVATE SSH key file using RSA
    """
    # paramiko uses pycrypto's RandomPool which throws a deprecation warning
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from paramiko import RSAKey

    key = RSAKey.generate(2048)
    private_key_file_name = ssh_path + "/" + key_base_name
    key.write_private_key_file(private_key_file_name)

    # Ok, pass back private key object
    return key


def generate_public_rsa_key_file(private_key, ssh_path, key_base_name):
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

    return True


def create_new_default_ssh_keys():
    """
        Generate a set of private and public keys for user
    """
    question = raw_input('Type "Yes" to generate a new default SSH-key pair: ')
    if question.lower() != 'yes':
        raise InputErrorException('SecurityQuestionDenied')

    # Let user create key, then check if everything went fine!
    if not generate_rsa_keys():
        raise InputErrorException('UserShouldCreateKey')

    # Ok, new SSH default keys seemed to be created.
    return True


def ask_user_to_use_default_ssh_public_key():
    """
        Ask the user if the default public SSH-key (RSA)
        shall be used.
    """
    default_rsa_public_key = get_default_ssh_key_path()

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


def get_public_key_fingerprint(key_path):
    if not key_path:
        key_path = get_default_ssh_key_path()

    try:
        public_key = open(key_path).read()
    except IOError:
        return None

    key = base64.b64decode(public_key.strip().split()[1].encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))


def get_default_ssh_dir():
    return os.path.join(os.path.expanduser('~'), ".ssh")


def get_default_ssh_key_path():
    return get_default_ssh_dir() + "/id_rsa.pub"


def get_key_from_agent(fingerprint):
    a = paramiko.agent.Agent()
    for key in a.get_keys():
        fp = base64.b16encode(key.get_fingerprint())
        if fp == fingerprint.replace(':', '').upper():
            return key
    return None


def sign_token(key_path, fingerprint, data):
    # from agent
    pkey = get_key_from_agent(fingerprint)
    if not pkey:
        # or from file (without passphrase)
        # assuming '.pub' file extension
        if not os.path.exists(key_path[:-4]):
            raise SignatureException('WrongKeyPath')
        try:
            pkey = RSAKey.from_private_key_file(key_path[:-4])
        except PasswordRequiredException:
            raise SignatureException('EncryptedKey')

    if not pkey:
        raise SignatureException('KeyNotFound')

    try:
        # paramiko is inconsistent here in that the agent's key
        # returns Message objects for 'sign_ssh_data' whereas RSAKey
        # objects returns byte strings.
        # Workaround: cast both return values to string and build a
        # new Message object
        s = str(pkey.sign_ssh_data(data))
        m = Message(s)
        m.rewind()
        if not m.get_string() == 'ssh-rsa':
            raise SignatureException('RSAKeyRequired')
        return base64.b64encode(m.get_string())
    except Exception:
        raise SignatureException('SignatureCreateFailure')
