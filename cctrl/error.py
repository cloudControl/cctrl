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

messages = {}
messages['NoDeployment'] = r'You have to append the deployment name.'
messages['WrongApplication'] = r'This application is unknown.'
messages['WrongDeployment'] = r'This deployment is unknown.'
messages['PasswordsDontMatch'] = r"The passwords don't match."
messages['InvalidApplicationName'] = r'Name may only contain a-z and 0-9 and must not start with a number.'
messages['WrongUsername'] = r'This username is unknown.'
messages['UserBelongsToApp'] = r'This user already belongs to this application.'
messages['RemoveUserGoneError'] = r'No such app or user. Please check app name and user name or email address.'
messages['UserCreatedNowCheckEmail'] = r'User has been created. Please check you e-mail for your confirmation code.'
messages['DeleteOnlyApplication'] = r'You can only delete applications not deployments. Try the undeploy command.'
messages['NoAliasGiven'] = r'You have to specify an alias.'
messages['WrongAlias'] = r'This alias is unknown.'
messages['NotAllowed'] = r'Sorry. You are not allowed to perform this action.'
messages['CannotDeleteDeploymentExist'] = r'You have to undeploy all related deployments, before you can delete the application.'
messages['NotAuthorized'] = r'The authorization failed, check your e-mail address and password.'
messages['PermissionDenied'] = r'You are not allowed to push to this repository. Maybe check your keys using "cctrluser key".'
messages['SecurityQuestionDenied'] = r'Action canceled on user request.'
messages['WrongAddon'] = r'This addon is unknown for this app_name/deployment_name.'
messages['DuplicateAddon'] = r'You can not add the same addon option twice.'
messages['WrongPubKeyName'] = r'The public key file must be named "id_rsa.pub".'
messages['NoSuchKeyFile'] = r'No such key file. Please check your input.'
messages['WrongKeyFormat'] = r'Your id_rsa.pub public key file seems to be in the wrong format.'
messages['InvalidAppOrDeploymentName'] = r'The application or deployment name is invalid.'
messages['KeyDuplicate'] = r'This key was added previously.'
messages['NoWorkerCommandGiven'] = r'The worker command is missing. Try the path to your PHP file relative from your repository root.'
messages['NoRunCommandGiven'] = r'Run command is missing.'
messages['WrongWorker'] = r'There is no such worker for this app_name/deployment_name.'
messages['NeitherBazaarNorGitFound'] = r'Cannot find "git" nor "bzr"! Please make sure either Bazaar or Git executables are in your path.'
messages['BazaarRequiredToPush'] = r'Please make sure the Bazaar executable is in your path.'
messages['GitRequiredToPush'] = r'Please make sure the Git executable is in your path.'
messages['NoCronURLGiven'] = r'You must provide a URL for cron to call.'
messages['NoSuchCronJob'] = r'Sorry, we can not find cronjob with this ID.'
messages['FileReadOrWriteFailed'] = r'Sorry, could not read or write to file.'
messages['FileNotFound'] = r'Sorry, file not found!'
messages['UserShouldCreateKey'] = r'Sorry, something went wrong when creating a key. Please create a key on your system, then run the command again.'
messages['BazaarConfigFound'] = r'Bazaar configuration found! Using "Bazaar" as repository type.'
messages['GitConfigFound'] = r'Git configuration found! Using "Git" as repository type.'
messages['BazaarExecutableFound'] = r'Bazaar seems to be installed! Using "Bazaar" as repository type.'
messages['GitExecutableFound'] = r'Git seems to be installed! Using "Git" as repository type.'
messages['CreatingAppAsDefaultRepoType'] = r'Using default "Git" as repository type.'
messages['DeleteAppsBeforeUser'] = r'There are still applications associated with this user account. Undeploy and/or delete applications before deleting user.'
messages['NoSuchFile'] = r'File not found.'
messages['APIUnreachable'] = r'Could not connect to API...'
messages['NoBuildpackURL'] = r'You need to provide a buildpack URL for "custom" application type'
messages['NoCustomApp'] = r'You can only provide a buildpack URL if the app type is "custom"'
messages['NoValidBuildpackURL'] = r'The buildpack URL provided is not valid. Please try again.'
messages['AmbiguousSize'] = r'You can only specify one of --size or --memory'
messages['InvalidMemory'] = r'Memory size should be an integer between 128 and 1024 MB'
messages['InvalidSize'] = r'Size should be an integer between 1 and 8'

if sys.platform == 'win32':
    messages['UpdateAvailable'] = r'A newer version is available. Please update.'
    messages['UpdateRequired'] = r'A newer version is required. You need to upgrade before using this program.'
else:
    messages['UpdateAvailable'] = r'A newer version is available. To upgrade run: (sudo) pip install cctrl --upgrade'
    messages['UpdateRequired'] = r'A newer version is required. You need to upgrade before using this program. To upgrade run: (sudo) pip install cctrl --upgrade'


class InputErrorException(Exception):
    """
        This exception is raised if for some reason someone put something in we
        could not understand at all.
    """
    def __init__(self, errorKey):
        self.error_message = messages[errorKey]

    def __str__(self):
        return '[ERROR]' + ' ' + self.error_message


class PasswordsDontMatchException(Exception):
    """
        This exception is raised if the password and the password check weren't
        equal for three times.
    """
    pass
