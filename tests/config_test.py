import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mock import patch, Mock

from cctrl.app import AppController
from cctrl.error import InputErrorException
from cctrl.settings import Settings


class AppControllerTestCase(unittest.TestCase):
    @patch('cctrl.app.parse_config_variables')
    def test_add_config(self, parse_config_variables):
        app = AppController(None, Settings())
        app.api = Mock()
        args = Mock()
        args.name = 'app/dep'
        args.force_add = False
        args.variables = ['foo=bar']
        app.addConfig(args)
        self.assertTrue(parse_config_variables.called)
        self.assertTrue(app.api.update_addon.called)

    @patch('cctrl.app.parse_config_variables')
    def test_add_config_force_flag(self, parse_config_variables):
        app = AppController(None, Settings())
        app.api = Mock()
        args = Mock()
        args.name = 'app/dep'
        args.force_add = True
        args.variables = ['foo=bar']
        app.addConfig(args)
        self.assertTrue(parse_config_variables.called)
        self.assertTrue(app.api.update_addon.called)

    @patch('cctrl.app.parse_config_variables')
    def test_add_config_force_arg(self, parse_config_variables):
        app = AppController(None, Settings())
        app.api = Mock()
        args = Mock()
        args.name = 'app/dep'
        args.force_add = False
        args.variables = ['foo=bar', '--force']
        app.addConfig(args)
        self.assertTrue(parse_config_variables.called)
        self.assertTrue(app.api.update_addon.called)

    @patch('cctrl.app.parse_config_variables')
    def test_add_config_no_variables_given(self, parse_config_variables):
        app = AppController(None, Settings())
        app.api = Mock()
        args = Mock()
        args.name = 'app/dep'
        args.force_add = False
        args.variables = None
        with self.assertRaises(InputErrorException) as nvg:
            app.addConfig(args)

        self.assertEqual(
            '[ERROR] You must provide some variables.',
            str(nvg.exception))
        self.assertFalse(parse_config_variables.called)
        self.assertFalse(app.api.update_addon.called)

    @patch('cctrl.app.parse_config_variables')
    def test_add_config_duplicated_flag(self, parse_config_variables):
        app = AppController(None, Settings())
        app.api = Mock()
        args = Mock()
        args.name = 'app/dep'
        args.force_add = True
        args.variables = ['foo=bar', '-f']
        with self.assertRaises(InputErrorException) as df:
            app.addConfig(args)

        self.assertEqual(
            '[ERROR] Please, specify a flag only once.',
            str(df.exception))
        self.assertFalse(parse_config_variables.called)
        self.assertFalse(app.api.update_addon.called)
