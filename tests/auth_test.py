import unittest
from mock import patch, call, Mock
from cctrl.error import InputErrorException
from cctrl.auth import ask_for_ssh_key_path
from cctrl.keyhelpers import get_default_ssh_key_path


class AuthTestCase(unittest.TestCase):
    @patch('cctrl.auth.sys')
    @patch('cctrl.auth.raw_input')
    @patch('cctrl.auth.set_configfile')
    @patch('cctrl.auth.os.path.isfile')
    def test_ask_for_ssh_key_path_exists(self, isfile, set_configfile, raw_input, sys):
        settings = Mock()
        raw_input.return_value = 'path'
        isfile.return_value = True
        ask_for_ssh_key_path(settings)

        self.assertIn([], sys.mock_calls)
        self.assertEquals([call(settings, ssh_path='path')], set_configfile.mock_calls)

    @patch('cctrl.auth.sys')
    @patch('cctrl.auth.raw_input')
    @patch('cctrl.auth.set_configfile')
    @patch('cctrl.auth.os.path.isfile')
    @patch('cctrl.auth.get_default_ssh_key_path')
    def test_ask_for_ssh_key_path_take_default(self, default_key_path, isfile, set_configfile, raw_input, sys):
        settings = Mock()
        raw_input.return_value = ''
        default_key_path.return_value = '/default/key/path.pub'
        isfile.return_value = True
        ask_for_ssh_key_path(settings)

        self.assertEquals([], sys.mock_calls)
        self.assertEquals([call(settings, ssh_path='/default/key/path.pub')], set_configfile.mock_calls)

    @patch('cctrl.auth.sys')
    @patch('cctrl.auth.raw_input')
    @patch('cctrl.auth.set_configfile')
    @patch('cctrl.auth.os.path.isfile')
    @patch('cctrl.auth.get_default_ssh_key_path')
    def test_ask_for_ssh_key_path_does_not_exist(self, default_key_path, isfile, set_configfile, raw_input, sys):
        settings = Mock()
        raw_input.return_value = 'path'
        default_key_path.return_value = '/default/key/path.pub'
        isfile.return_value = False

        with self.assertRaises(InputErrorException):
            ask_for_ssh_key_path(settings)

        self.assertEquals([], set_configfile.mock_calls)
        self.assertEquals([call.stderr.write('File does not exist: path'), call.stderr.write('\n')] * 3, sys.mock_calls)
        self.assertEquals([call('Set ssh key path (/default/key/path.pub):')] * 3, raw_input.mock_calls)

    @patch('cctrl.auth.sys')
    @patch('cctrl.auth.raw_input')
    @patch('cctrl.auth.set_configfile')
    @patch('cctrl.auth.os.path.isfile')
    @patch('cctrl.auth.get_default_ssh_key_path')
    def test_ask_for_ssh_key_path_default_path_does_not_exist(self, default_key_path, isfile, set_configfile, raw_input, sys):
        settings = Mock()
        raw_input.return_value = ''
        default_key_path.return_value = '/default/key/path.pub'
        isfile.return_value = False

        with self.assertRaises(InputErrorException):
            ask_for_ssh_key_path(settings)

        self.assertEquals([], set_configfile.mock_calls)
        self.assertEquals([call.stderr.write('File does not exist: /default/key/path.pub'), call.stderr.write('\n')] * 3, sys.mock_calls)
        self.assertEquals([call('Set ssh key path (/default/key/path.pub):')] * 3, raw_input.mock_calls)
