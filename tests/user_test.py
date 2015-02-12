import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mock import call, patch, Mock, MagicMock

from cctrl.user import UserController
from cctrl.error import InputErrorException
from cctrl.settings import Settings


@patch('cctrl.user.sys.stderr', MagicMock())
@patch('cctrl.user.readContentOf', MagicMock())
@patch('cctrl.user.get_default_ssh_key_path', Mock(return_value='/default/path/to/key'))
@patch('cctrl.user.create_new_default_ssh_keys')
@patch('cctrl.user.set_user_config')
class UserControllerTestCase(unittest.TestCase):
    @patch('cctrl.user.is_key_valid')
    @patch('cctrl.user.get_user_config')
    def test_setup(self,
                   _get_user_config,
                   _is_key_valid,
                   _set_user_config, *args):
        user = UserController(Mock(), Settings())
        user.api.read_users.return_value = [{'username': 'foo'}]
        args = Mock(email='info@example.org',
                    ssh_key_path='/path/to/key',
                    ssh_auth='no')

        _is_key_valid.return_value = True
        _get_user_config.return_value = {}

        user.setup(args)

        self.assertTrue(user.api.read_users.called)
        self.assertTrue(user.api.create_user_key.called)
        self.assertEqual(2, len(_set_user_config.mock_calls))
        self.assertEqual(call(user.settings, email='info@example.org'),
                         _set_user_config.mock_calls[0])
        self.assertEqual(call(user.settings,
                              ssh_auth=False,
                              ssh_path='/path/to/key'),
                         _set_user_config.mock_calls[1])

    @patch('cctrl.user.os.path.abspath', MagicMock())
    @patch('cctrl.user.is_key_valid')
    def test_setup_wrong_public_key(self, _is_key_valid, *args):
        user = UserController(Mock(), Settings())
        args = Mock(email='test@example.org',
                    ssh_key_path='not-existing',
                    ssh_auth='yes')

        _is_key_valid.return_value = False

        with self.assertRaises(InputErrorException) as iep:
            user.setup(args)

        self.assertEqual(
            '[ERROR] Public Key not found or invalid.',
            str(iep.exception))
        self.assertFalse(user.api.read_users.called)
        self.assertFalse(user.api.create_user_key.called)

    @patch('cctrl.user.is_key_valid')
    @patch('cctrl.user.get_user_config')
    def test_setup_non_existing_default_public_key(self,
                                                   _get_user_config,
                                                   _is_key_valid,
                                                   _set_user_config,
                                                   _create_default_ssh):
        user = UserController(Mock(), Settings())
        user.api.read_users.return_value = [{'username': 'foo'}]
        args = Mock(email='info@example.org',
                    ssh_key_path='/default/path/to/key',
                    ssh_auth='yes')

        _is_key_valid.return_value = False
        _get_user_config.return_value = {}

        user.setup(args)

        self.assertTrue(user.api.read_users.called)
        self.assertTrue(user.api.create_user_key.called)
        self.assertTrue(_create_default_ssh.called)
        self.assertEqual(2, len(_set_user_config.mock_calls))
        self.assertEqual(call(user.settings, email='info@example.org'),
                         _set_user_config.mock_calls[0])
        self.assertEqual(call(user.settings,
                              ssh_auth=True,
                              ssh_path='/default/path/to/key'),
                         _set_user_config.mock_calls[1])

    @patch('cctrl.user.is_key_valid')
    @patch('cctrl.user.get_user_config')
    def test_setup_no_args_provided(self,
                                    _get_user_config,
                                    _is_key_valid,
                                    _set_user_config, *args):
        user = UserController(Mock(), Settings())
        user.api.read_users.return_value = [{'username': 'foo'}]
        args = Mock(email=None,
                    ssh_key_path=None,
                    ssh_auth='yes')

        _get_user_config.return_value = {}
        _is_key_valid.return_value = True

        user.setup(args)

        self.assertTrue(user.api.read_users.called)
        self.assertTrue(user.api.create_user_key.called)
        self.assertEqual(1, len(_set_user_config.mock_calls))
        _set_user_config.assert_called_once_with(user.settings,
                                                 ssh_auth=True,
                                                 ssh_path='/default/path/to/key')

    @patch('cctrl.user.is_key_valid')
    @patch('cctrl.user.get_user_config')
    def test_setup_only_email_provided(self,
                                       _get_user_config,
                                       _is_key_valid,
                                       _set_user_config, *args):
        user = UserController(Mock(), Settings())
        user.api.read_users.return_value = [{'username': 'foo'}]
        args = Mock(email='info@example.org',
                    ssh_key_path=None,
                    ssh_auth=None)

        _get_user_config.return_value = {'ssh_auth': True,
                                         'ssh_path': '/path/to/key'}
        _is_key_valid.return_value = True

        user.setup(args)

        self.assertTrue(user.api.read_users.called)
        self.assertTrue(user.api.create_user_key.called)
        self.assertEqual(2, len(_set_user_config.mock_calls))
        self.assertEqual(call(user.settings, email='info@example.org'),
                         _set_user_config.mock_calls[0])
        self.assertEqual(call(user.settings,
                              ssh_auth=True,
                              ssh_path='/path/to/key'),
                         _set_user_config.mock_calls[1])
