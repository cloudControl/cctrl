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

from pycclib.cclib import *
from cctrl.error import InputErrorException, messages
from cctrl.auth import get_credentials, update_tokenfile, delete_tokenfile

def run(args, api):
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
    while True:
        try:
            try:
                args.func(args)
            except TokenRequiredError:
                email, password = get_credentials()
                try:
                    api.create_token(email, password)
                except UnauthorizedError:
                    sys.exit(messages['NotAuthorized'])
                else:
                    pass
            else:
                break
        except UnauthorizedError, e:
            if delete_tokenfile():
                api.set_token(None)
            else:
                sys.exit(messages['NotAuthorized'])
        except ForbiddenError, e:
            sys.exit(messages['NotAllowed'])
        except (ConnectionException, BadRequestError, ConflictDuplicateError, GoneError,
            InternalServerError, NotImplementedError, ThrottledError, InputErrorException), e:
            sys.exit(e)

def shutdown(api):
    """
        shutdown handles updating or deleting the tokenfile on disk each time
        cctrl finishes or get's interrupted.
    """
    if api.check_token():
        update_tokenfile(api)
    else:
        delete_tokenfile()
