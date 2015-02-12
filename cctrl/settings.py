# -*- coding: utf-8 -*-
"""
    Copyright 2014 cloudControl GmbH

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
from cctrl.version import __version__

VERSION = __version__
CONFIG_ADDON = os.getenv('CONFIG_ADDON', 'config.free')


class Settings(object):
    def __init__(self,
                 api_url=None,
                 token_source_url=None,
                 ssh_forwarder_url=None,
                 env=os.environ,
                 encode_email=False,
                 user_registration_enabled=True,
                 user_registration_url='https://www.cloudcontrol.com',
                 register_addon_url=None,
                 login_name='Email   : ',
                 login_help_name='email',
                 login_creds={'email': 'CCTRL_EMAIL',
                              'pwd': 'CCTRL_PASSWORD'},
                 package_name='cctrl',
                 prefix_project_name=False,
                 home_path='.cloudControl',
                 ssh_auth=True):

        self.ssh_forwarder = ssh_forwarder_url or env.get('SSH_FORWARDER', 'sshforwarder.cloudcontrolled.com')
        self.ssh_forwarder_port = '2222'
        self.api_url = api_url or env.get('CCTRL_API_URL', 'https://api.cloudcontrolled.com')
        self.token_source_url = token_source_url or self.api_url + '/token/'
        self.encode_email = encode_email
        self.user_registration_enabled = user_registration_enabled
        self.user_registration_url = user_registration_url
        self.register_addon_url = register_addon_url
        self.login_name = login_name
        self.login_help_name = login_help_name
        self.login_creds = login_creds
        self.package_name = package_name
        self.prefix_project_name = prefix_project_name
        self.home_path = os.path.abspath(os.path.expanduser('~/{0}'.format(home_path)))
        self.token_path = os.path.join(self.home_path, 'token.json')
        self.config_path = os.path.join(self.home_path, 'user.cfg')
        self.ssh_auth = ssh_auth
