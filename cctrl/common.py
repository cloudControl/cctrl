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

import sys
import os

from pycclib import cclib

from cctrl.error import InputErrorException, messages
from cctrl.settings import VERSION
from cctrl.app import ParseAppDeploymentName
from cctrl.auth import update_tokenfile, delete_tokenfile, \
    read_tokenfile, get_email_and_password, create_token


def check_for_updates(package_name, latest_version_str, our_version_str=VERSION):
    """
        check if the API reports a version that is greater then our currently
        installed one
    """
    our = dict()
    latest = dict()
    for version, suffix in ((our, our_version_str), (latest, latest_version_str)):
        for part in ['major', 'minor', 'patch']:
            version[part], _, suffix = suffix.partition('.')
            version[part] = int(version[part])
        version['suffix'] = suffix

    for part in ['major', 'minor', 'patch', 'suffix']:
        if latest[part] > our[part]:
            if part == 'major':
                sys.exit(messages['UpdateRequired'].format(package_name))
            else:
                print >> sys.stderr, messages['UpdateAvailable'].format(package_name)
            return


def init_api(settings):
    """
        This methods initializes the API but first checks for a
        CCTRL_API_URL environment variable and uses it if found.
        For Windows we also need to load ca_certs differently,
        because the httplib2 provided ones are not included due to
        py2exe.
    """
    dirname = os.path.dirname(__file__)
    while len(dirname) > 1:
        p = os.path.join(dirname, 'cacerts.txt')

        if os.path.exists(p):
            cclib.CA_CERTS = p
            break

        dirname = os.path.dirname(dirname)
    return cclib.API(token=read_tokenfile(settings),
                     url=settings.api_url,
                     token_source_url=settings.token_source_url,
                     register_addon_url=settings.register_addon_url,
                     encode_email=settings.encode_email)


def execute_command(api, command, settings):
    while True:
        try:
            command()
            break
        except (cclib.TokenRequiredError, cclib.UnauthorizedError):
            email, password = get_email_and_password(settings)
            create_token(api, settings, email, password)
        except ParseAppDeploymentName:
            sys.exit(messages['InvalidAppOrDeploymentName'])


def execute_with_authenticated_user(api, command, settings):
    while True:
        try:
            execute_command(api, command, settings)
            break
        except cclib.ForbiddenError, e:
            sys.exit(messages['NotAllowed'])
        except cclib.ConnectionException:
            sys.exit(messages['APIUnreachable'])
        except (cclib.APIException, InputErrorException) as e:
            sys.exit(e)


def run(args, api, settings):
    """
        run takes care of calling the action with the needed arguments parsed
        using argparse.

        We first try to call the action. In case the called action requires a
        valid token and the api instance does not have one a TokenRequiredError
        gets raised. In this case we catch the error and ask the user for a
        email/password combination to create a new token. After that we call
        the action again.

        pycclib raises an exception any time the API does answer with a
        HTTP STATUS CODE other than 200, 201 or 204. We catch these exceptions
        here and stop cctrlapp using sys.exit and show the error message to the
        user.
    """

    execute_with_authenticated_user(api, (lambda: args.func(args)), settings)


def shutdown(api, settings):
    """
        shutdown handles updating or deleting the token file on disk each time
        cctrl finishes or gets interrupted.
    """
    if api.check_token():
        update_tokenfile(api, settings)
    else:
        delete_tokenfile(settings)
