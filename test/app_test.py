import unittest
from mock import patch, call
from cctrl.error import InputErrorException
from cctrl.app import AppController


class AppControllerTestCase(unittest.TestCase):

    def test_get_size_from_memory_1gb(self):
        self.assertEqual(8, AppController(None)._get_size_from_memory('1GB'))

    @patch('cctrl.app.sys')
    def test_get_size_from_memory_mb_rounded(self, _sys):
        self.assertEqual(6, AppController(None)._get_size_from_memory('666MB'))
        self.assertEqual([
            call.stderr.write('Memory size has to be a multiple of 128MB and has been rounded up to 768MB.'),
            call.stderr.write('\n')], _sys.mock_calls)

    def test_get_size_from_memory_nop_match(self):
        with self.assertRaises(InputErrorException) as ctx:
            AppController(None)._get_size_from_memory('0.7')
        self.assertEqual('[ERROR] Memory size should be an integer between 128 and 1024 MB', str(ctx.exception))

    def test_get_size_from_memory_unrecognized_unit(self):
        with self.assertRaises(InputErrorException) as ctx:
            AppController(None)._get_size_from_memory('4kb')
        self.assertEqual('[ERROR] Memory size should be an integer between 128 and 1024 MB', str(ctx.exception))
