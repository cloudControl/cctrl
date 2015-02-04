import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mock import patch, call, Mock
from cctrl.error import InputErrorException
from cctrl.app import AppController
from cctrl.settings import Settings
from pycclib.cclib import GoneError


class AppControllerTestCase(unittest.TestCase):

    def test_get_size_from_memory_1gb(self):
        app = AppController(None, Settings())
        self.assertEqual(8, app._get_size_from_memory('1GB'))

    @patch('cctrl.app.sys')
    def test_get_size_from_memory_mb_rounded(self, _sys):
        app = AppController(None, Settings())
        self.assertEqual(6, app._get_size_from_memory('666MB'))
        self.assertEqual([
            call.stderr.write(
                'Memory size has to be a multiple of 128MB and has been ' +
                'rounded up to 768MB.'),
            call.stderr.write('\n')], _sys.mock_calls)

    def test_get_size_from_memory_nop_match(self):
        with self.assertRaises(InputErrorException) as ctx:
            AppController(None, Settings())._get_size_from_memory('0.7')
        self.assertEqual(
            '[ERROR] Memory size should be an integer between 128 and 1024 MB.',
            str(ctx.exception))

    def test_get_size_from_memory_unrecognized_unit(self):
        with self.assertRaises(InputErrorException) as ctx:
            AppController(None, Settings())._get_size_from_memory('4kb')
        self.assertEqual(
            '[ERROR] Memory size should be an integer between 128 and 1024 MB.',
            str(ctx.exception))

    @patch('cctrl.app.check_call')
    def test_push_with_ship(self, check_call):
        app = AppController(None, Settings())
        app.redeploy = Mock()
        app.log_from_now = Mock()
        app._get_or_create_deployment = Mock(
            return_value=({'branch': 'default', 'name': 'dep'}, 'name'))
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
        app._get_or_create_deployment = Mock(
            return_value=({'branch': 'default'}, 'name'))
        args = Mock()
        args.name = 'app/dep'
        args.ship = False
        app.push(args)
        self.assertTrue(check_call.called)
        self.assertTrue(app.redeploy.called)

    @patch('cctrl.app.check_call')
    def test_push_with_ship_and_deploy_error(self, check_call):
        app = AppController(None, Settings())
        app._get_or_create_deployment = Mock(
            return_value=({'branch': 'default', 'name': 'dep'}, 'name'))
        args = Mock()
        args.name = 'app/dep'
        with self.assertRaises(InputErrorException) as sd:
            app.push(args)
        self.assertEqual(
            '[ERROR] --ship and --push options cannot be used simultaneously.',
            str(sd.exception))

    def test_restart_worker_with_wrk(self):
        app = AppController(None, Settings())
        app._restartWorker = Mock()
        app._restartWorkers = Mock()
        app.api = Mock()
        app.api.read_worker.return_value = {'wrk_id': 'wrk1', 'command': 'command', 'params': 'params', 'size': 'size'}
        args = Mock()
        args.name = 'app/dep'
        args.wrk_id = 'wrk1'
        args.all = False
        app.restartWorker(args)
        self.assertTrue(app._restartWorker.called)
        self.assertFalse(app._restartWorkers.called)

    def test_restart_worker_with_all(self):
        app = AppController(None, Settings())
        app._restartWorker = Mock()
        app._restartWorkers = Mock()
        app.api = Mock()
        app.api.read_worker.return_value = {'wrk_id': 'wrk1', 'command': 'command', 'params': 'params', 'size': 'size'}
        args = Mock()
        args.name = 'app/dep'
        args.wrk_id = False
        args.all = True
        app.restartWorker(args)
        self.assertTrue(app._restartWorkers.called)

    def test_restart_worker_gone_error(self):
        app = AppController(None, Settings())
        app._restartWorker = Mock()
        app._restartWorkers = Mock()
        app.api = Mock()
        app.api.read_worker.side_effect = GoneError
        args = Mock()
        args.name = 'app/dep'
        args.wrk_id = 'wrkgone'
        args.all = False
        self.assertRaises(InputErrorException, app.restartWorker, args)
        self.assertFalse(app._restartWorker.called)
        self.assertFalse(app._restartWorkers.called)

    def test__restart_workers(self):
        app = AppController(None, Settings())
        app.api = Mock()
        app.api.read_workers.return_value = [{'wrk_id': 'wrk1'}]
        app.api.read_worker.return_value = {'wrk_id': 'wrk1', 'command': 'command', 'params': 'params', 'size': 8}

        app._restartWorkers('app', 'dep')

        self.assertTrue(app.api.delete_worker.called)
        self.assertTrue(app.api.create_worker.called)

    def test__restart_worker(self):
        app = AppController(None, Settings())
        app.api = Mock()
        app._restartWorker('app_name', 'deployment_name', 'wrk_id', 'command', 'params', 'size')
        self.assertTrue(app.api.delete_worker.called)
        self.assertTrue(app.api.create_worker.called)

    @patch('cctrl.app.time')
    def test_deploy_restart_workers(self, time):
        app = AppController(None, Settings())
        app.api = Mock()
        app.api.read_deployment.return_value = {'state': 'deployed'}
        app._restartWorkers = Mock()
        args = Mock()
        args.name = 'app/dep'
        args.memory = False
        app.deploy(args)
        self.assertTrue(app._restartWorkers.called)
        self.assertEqual(call('app', 'dep'), app.api.read_deployment.call_args_list[0])

    @patch('cctrl.app.time')
    def test_deploy_restart_workers_no_dep_name(self, time):
        app = AppController(None, Settings())
        app.api = Mock()
        app.api.read_deployment.return_value = {'state': 'deployed'}
        app._restartWorkers = Mock()
        args = Mock()
        args.name = 'app'
        args.memory = False
        app.deploy(args)
        self.assertTrue(app._restartWorkers.called)
        self.assertEqual(call('app', 'default'), app.api.read_deployment.call_args_list[0])
