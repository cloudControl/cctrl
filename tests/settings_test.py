import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from cctrl.settings import Settings


class TestSettings(unittest.TestCase):

    def test_api_url_set_by_argument(self):
        test_env = {'CCTRL_API_URL': "any.env_api.url"}
        settings = Settings(api_url='my.api.url', env=test_env)
        self.assertEqual('my.api.url', settings.api_url)

    def test_api_url_set_by_environment(self):
        test_env = {'CCTRL_API_URL': "my.env_api.url"}
        settings = Settings(env=test_env)
        self.assertEqual('my.env_api.url', settings.api_url)

    def test_api_url_default(self):
        settings = Settings(env={})
        self.assertEqual('https://api.cloudcontrolled.com', settings.api_url)

    def test_token_source_url_set_by_constructor(self):
        settings = Settings(
            token_source_url='my.token_source.url',
            api_url='any.api.url')
        self.assertEqual('my.token_source.url', settings.token_source_url)

    def test_token_source_url_should_default_to_api_url(self):
        settings = Settings(api_url='my.api.url')
        self.assertEqual('my.api.url/token/', settings.token_source_url)

    def test_token_path_given_home_path(self):
        settings = Settings(home_path='.cloudControl')
        self.assertTrue(settings.token_path.endswith('.cloudControl/token.json'))

    def test_config_path_given_home_path(self):
        settings = Settings(home_path='.cloudControl')
        self.assertTrue(settings.config_path.endswith('.cloudControl/user.cfg'))

    def test_ssh_forwarder_url_default(self):
        settings = Settings(env={})
        self.assertEqual(
            'sshforwarder.cloudcontrolled.com',
            settings.ssh_forwarder)

    def test_ssh_forwarder_url_set_by_argument(self):
        test_env = {'SSH_FORWARDER': "any.env_api.url"}
        settings = Settings(
            ssh_forwarder_url='my.ssh_forwarder.url',
            env=test_env)
        self.assertEqual('my.ssh_forwarder.url', settings.ssh_forwarder)

    def test_ssh_forwarder_set_by_environment(self):
        test_env = {'SSH_FORWARDER': "my.ssh_forwarder.url"}
        settings = Settings(env=test_env)
        self.assertEqual('my.ssh_forwarder.url', settings.ssh_forwarder)
