import unittest
from mock import patch, call, Mock
from cctrl.error import InputErrorException
from cctrl.app import AppController
from cctrl.settings import Settings


class AppControllerTestCase(unittest.TestCase):

    def test_get_size_from_memory_1gb(self):
        self.assertEqual(8, AppController(None, Settings())._get_size_from_memory('1GB'))

    @patch('cctrl.app.sys')
    def test_get_size_from_memory_mb_rounded(self, _sys):
        self.assertEqual(6, AppController(None, Settings())._get_size_from_memory('666MB'))
        self.assertEqual([
            call.stderr.write('Memory size has to be a multiple of 128MB and has been rounded up to 768MB.'),
            call.stderr.write('\n')], _sys.mock_calls)

    def test_get_size_from_memory_nop_match(self):
        with self.assertRaises(InputErrorException) as ctx:
            AppController(None, Settings())._get_size_from_memory('0.7')
        self.assertEqual('[ERROR] Memory size should be an integer between 128 and 1024 MB', str(ctx.exception))

    def test_get_size_from_memory_unrecognized_unit(self):
        with self.assertRaises(InputErrorException) as ctx:
            AppController(None, Settings())._get_size_from_memory('4kb')
        self.assertEqual('[ERROR] Memory size should be an integer between 128 and 1024 MB', str(ctx.exception))

    @patch('cctrl.app.check_call')
    def test_push_with_ship(self, check_call):
        app = AppController(None, Settings())
        app.redeploy = Mock()
        app.log_from_now = Mock()
        app._get_or_create_deployment = Mock(return_value=({'branch': 'default', 'name': 'dep'}, 'name'))
        args = Mock()
        args.name = 'app/dep'
        args.deploy = False
        app.push(args)
        self.assertTrue(check_call.called)
        self.assertTrue(app.redeploy.called)
        self.assertTrue(app.log_from_now.called)

    @patch('cctrl.app.check_call')
    def test_push_with_deploy(self, check_call):
        app = AppController(None, Settings())
        app.redeploy = Mock()
        app._get_or_create_deployment = Mock(return_value=({'branch': 'default'}, 'name'))
        args = Mock()
        args.name = 'app/dep'
        args.ship = False
        app.push(args)
        self.assertTrue(check_call.called)
        self.assertTrue(app.redeploy.called)

    @patch('cctrl.app.check_call')
    def test_push_with_ship_and_deploy_error(self, check_call):
        app = AppController(None, Settings())
        app._get_or_create_deployment = Mock(return_value=({'branch': 'default', 'name': 'dep'}, 'name'))
        args = Mock()
        args.name = 'app/dep'
        with self.assertRaises(InputErrorException) as sd:
            app.push(args)
        self.assertEqual('[ERROR] --ship and --push options cannot be used simultaneously.', str(sd.exception))
