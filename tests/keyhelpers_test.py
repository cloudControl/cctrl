import os
import binascii
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mock import patch, call, Mock, DEFAULT
from cctrl.keyhelpers import get_public_key_fingerprint, sign_token
import struct


@patch.multiple(
    '__builtin__',
    open=DEFAULT
)
@patch.multiple(
    'cctrl.keyhelpers',
    os=DEFAULT,
    get_default_ssh_key_path=Mock(return_value=os.path.expanduser('~') + '/.ssh/id_rsa.pub'),
    RSAKey=DEFAULT,
    paramiko=DEFAULT
)
class KeyHelpersTestCase(unittest.TestCase):
    TEST_PUB_KEY = '''ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCpnGl7MiSArN350FHyQ+ZdgXlvMoCjPbghWStCnETpMimWe6VBNn4cmdfqc/wIJIWKW0WkndUAWkCaTG/1BAtDtxCPnrncwAqJxGsIsP14GPcsRMEfkYdStTQDyrAw3r1lFj8sxAvhtbxIzyfADrIbWh9Vu2RSZ1/oeKxncD6bNN7UPLmVd83hINjZZx/2AtbC19aVJ9ZV4QvsUUjYZVgPVMtu//8PtoSVOj+6GXZFzT1b85XIWxm7fi5iwA9p4Qbki7HcdVsfHpuJgM/bWyLBZ0bQQaY0UCsBEwD5Lq9wMlHYNna7POSvFPjZXpr/gzoQU7AFL6hjIRD7vVyNpn07 mw@cloudcontrol.de'''
    TEST_FINGERPRINT = '4a:4c:5b:3e:47:21:d5:7f:c9:8c:d9:2e:a7:22:73:65'

    def test_get_public_key_fingerprint(self, open, **kwargs):
        open.return_value.read.return_value = self.TEST_PUB_KEY
        self.assertEqual(self.TEST_FINGERPRINT, get_public_key_fingerprint('path'))
        self.assertEqual([call('path'), call().read()], open.mock_calls)

    def test_get_public_key_fingerprint_use_default_path(self, open, **kwargs):
        open.return_value.read.return_value = self.TEST_PUB_KEY
        self.assertEqual(self.TEST_FINGERPRINT, get_public_key_fingerprint(None))
        self.assertEqual([call(os.path.expanduser('~') + '/.ssh/id_rsa.pub'), call().read()], open.mock_calls)

    def test_get_public_key_fingerprint_key_not_found(self, open, **kwargs):
        open.side_effect = IOError('File not found')
        self.assertEqual(None, get_public_key_fingerprint('path'))
        self.assertEqual([call('path')], open.mock_calls)

    @patch('cctrl.keyhelpers.get_key_from_agent', Mock(return_value=None))
    def test_sign_token_with_private_key(self, os, RSAKey, **kwargs):
        os.path.exist.return_value = True

        private_key = Mock()
        prefix = 'ssh-rsa'
        content = "BBBBBB"
        private_key.sign_ssh_data.return_value = struct.pack('>I', len(prefix)) + prefix + struct.pack('>I', len(content)) + content

        RSAKey.from_private_key_file.return_value = private_key

        result = sign_token('/path/to/pkey.pub', 'fingerprint', 'somedata')
        self.assertEqual(content.encode('base64').strip(), result)

    def test_sign_token_with_agent(self, os, paramiko, **kwargs):
        os.path.exist.return_value = False

        private_key = Mock()
        private_key.get_fingerprint.return_value = binascii.a2b_hex('4a:4c:5b:3e:47:21:d5:7f:c9:8c:d9:2e:a7:22:73:65'.replace(':', ''))
        prefix = 'ssh-rsa'
        content = "BBBBBB"
        private_key.sign_ssh_data.return_value = struct.pack('>I', len(prefix)) + prefix + struct.pack('>I', len(content)) + content

        agent = paramiko.agent.Agent.return_value
        agent.get_keys.return_value = [private_key]

        result = sign_token(None, '4a:4c:5b:3e:47:21:d5:7f:c9:8c:d9:2e:a7:22:73:65', 'somedata')
        self.assertEqual(content.encode('base64').strip(), result)
