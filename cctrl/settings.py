# -*- coding: utf-8 -*-
"""
    Copyright 2010 cloudControl UG (haftungsbeschraenkt)

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
CACHE_DIR = None
VERSION = __version__
SSH_FORWARDER = os.environ.pop('SSH_FORWARDER', 'ssh.cloudcontrolled.net')
SSH_FORWARDER_PORT = '2222'
