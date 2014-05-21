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

HOME_PATH = os.path.abspath(os.path.expanduser('~/.cloudControl'))
TOKEN_FILE_NAME = os.environ.get('CCTRL_TOKEN_FILE', 'token.json')
TOKEN_FILE_PATH = os.path.join(HOME_PATH, TOKEN_FILE_NAME)
VERSION = __version__
CONFIG_ADDON = os.getenv('CONFIG_ADDON', 'config.free')


class Settings(object):
    def __init__(self, api_url=None, token_source_url=None, ssh_forwarder_url=None, env=os.environ):
        self.ssh_forwarder = ssh_forwarder_url or env.get('SSH_FORWARDER', 'sshforwarder.cloudcontrolled.com')
        self.ssh_forwarder_port = '2222'
        self.api_url = api_url or env.get('CCTRL_API_URL', 'https://api.cloudcontrolled.com')
        self.token_source_url = token_source_url or self.api_url + '/token/'
