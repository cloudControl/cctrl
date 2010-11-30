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

import time
import re
from subprocess import check_call, CalledProcessError

from cctrl.error import InputErrorException, messages
from pycclib.cclib import *
from cctrl.output import print_deployment_details, print_app_details,\
    print_alias_details, print_log_entries, print_list_apps,\
    print_addon_details, print_addons, print_addon_list, print_alias_list

class AppsController():
    """
        This controller handles the special case where you want to get a list of
        applications.
    """

    api = None

    def __init__(self, api):
        self.api = api

    def list(self):
        apps = self.api.read_apps()
        print_list_apps(apps)

class AppController():
    """
        After parsing the command line in parse_cmdline() the related
        method of the ApplicationController gets called. Each method uses
        pycclib to fire a request and handles the response showing it to the
        user if needed.
    """

    api = None

    def __init__(self, api):
        self.api = api

    def create(self, args):
        """
            Creates a new application.
        """
        try:
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
        except ParseAppDeploymentName:
            raise InputErrorException('InvalidApplicationName')
        try:
            self.api.create_app(app_name, args.type)
            self.api.create_deployment(app_name, deployment_name=deployment_name)
        except GoneError:
            raise InputErrorException('WrongApplication')
        except ForbiddenError:
            raise InputErrorException('NotAllowed')
        else:
            return True


    def delete(self, args):
        """
            Delete an application. If we wouldn't check the token here it could
            happen that we ask the user for confirmation and then fire the api
            request. If the token wasn't valid this would result in a
            TokenRequiredError beeing raised and after getting the credentials
            and creating a token this method would be called a second time.

            This would result in asking the user two times if he really wants to
            delete the app which is a rather bad user experience.
        """
        if self.api.check_token():
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
            if deployment_name:
                raise InputErrorException('DeleteOnlyApplication')
            if not args.force_delete:
                question = raw_input('Do you really want to delete this application? Type "Yes" without the quotes to delete. ')
            else:
                question = 'Yes'
            if question == 'Yes':
                try:
                    self.api.delete_app(app_name)
                except ForbiddenError:
                    raise InputErrorException('NotAllowed')
                except BadRequestError:
                    raise InputErrorException('CannotDeleteDeploymentExist')
            else:
                print messages['SecurityQuestionDenied']
        else:
            raise TokenRequiredError

    def details(self, args):
        """
            Print application or deployment details.

            e.g.:

            'cctrlapp app_name details' prints application details

            'cctrlapp app_name/deployment_name details' prints deployment details
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if deployment_name:
            try:
                deployment = self.api.read_deployment(app_name, deployment_name)
            except GoneError:
                raise InputErrorException('WrongDeployment')
            else:
                print_deployment_details(deployment)
        else:
            try:
                app = self.api.read_app(app_name)
            except GoneError:
                raise InputErrorException('WrongApplication')
            else:
                print_app_details(app)

    def deploy(self, args):
        """
            Deploy a distinct version.

            Since we want to make it as easy as possible we first try to update
            the default deployment and start the newest version of that if no
            other arguments were passed at the command line.
        """
        try:
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
        except ParseAppDeploymentName:
            raise InputErrorException('InvalidApplicationName')
        try:
            self.api.update_deployment(app_name, version=args.version, deployment_name=deployment_name, min_boxes=args.min_boxes, max_boxes=args.max_boxes)
        except GoneError:
            try:
                self.api.create_deployment(app_name, deployment_name=deployment_name)
                self.api.update_deployment(app_name, version=args.version, deployment_name=deployment_name)
            except GoneError:
                raise InputErrorException('WrongApplication')
            except ForbiddenError:
                raise InputErrorException('NotAllowed')
        else:
            return True

    def undeploy(self, args):
        """
            Undeploys the deployment, deletes the database and files.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.force_delete:
                question = raw_input('Do you really want to delete this deployment? This will delete everything including files and the database. Type "Yes" without the quotes to delete. ')
        else:
            question = 'Yes'
        if question == 'Yes':
            args.force_delete = True
            try:
                self.api.delete_deployment(app_name, deployment_name)
            except GoneError:
                raise InputErrorException('WrongDeployment')
        else:
            print messages['SecurityQuestionDenied']
        return True

    def addAlias(self, args):
        """
            Adds the given alias to the deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.alias:
            raise InputErrorException('NoAliasGiven')
        self.api.create_alias(app_name, args.alias, deployment_name)
        return True

    def showAlias(self, args):
        """
            Shows the details of an alias.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.alias:
            aliases = self.api.read_aliases(app_name, deployment_name)
            print_alias_list(aliases)
            return True
        else:
            try:
                alias = self.api.read_alias(app_name, args.alias, deployment_name)
            except GoneError:
                raise InputErrorException('WrongAlias')
            else:
                print_alias_details(alias)
                return True
        return False

    def removeAlias(self, args):
        """
            Removes an alias form a deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.alias:
            raise InputErrorException('NoAliasGiven')
        try:
            self.api.delete_alias(app_name, args.alias, deployment_name)
        except GoneError:
            raise InputErrorException('WrongAlias')
        return True

    def listAddons(self, args):
        """
            Returns a list of all available addons
        """
        addons = self.api.read_addons()
        print_addons(addons)
        return True

    def addAddon(self, args):
        """
            Adds the given addon to the deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.addon:
            raise InputErrorException('NoAddonGiven')
        try:
            self.api.create_addon(app_name, deployment_name, args.addon)
        except ConflictDuplicateError:
            raise InputErrorException('DuplicateAddon')
        return True

    def showAddon(self, args):
        """
            Shows the details of an addon.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.addon:
            try:
                addons = self.api.read_addons(app_name, deployment_name)
            except:
                raise
            else:
                print_addon_list(addons)
                return True
        else:
            try:
                addon = self.api.read_addon(app_name, deployment_name, args.addon)
            except GoneError:
                raise InputErrorException('WrongAddon')
            else:
                print_addon_details(addon)
                return True
        return False

    def updateAddon(self, args):
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        try:
            self.api.update_addon(app_name, deployment_name, args.addon_old, args.addon_new)
        except GoneError:
            raise InputErrorException('WrongAddon')
        else:
            return True

    def removeAddon(self, args):
        """
            Removes an addon form a deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        if not args.addon:
            raise InputErrorException('NoAddonGiven')
        try:
            self.api.delete_addon(app_name, deployment_name, args.addon)
        except GoneError:
            raise InputErrorException('WrongAddon')
        return True

    def addUser(self, args):
        """
            Add a user specified by the e-mail address to an application.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        try:
            self.api.create_app_user(app_name, args.email)
        except ConflictDuplicateError:
            raise InputErrorException('UserBelongsToApp')
        return True

    def removeUser(self, args):
        """
            Remove a user specified by the user name from an application.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        try:
            self.api.delete_app_user(app_name, args.username)
        except GoneError:
            raise InputErrorException('RemoveUserGoneError')
        return True

    def log(self, args):
        """
        Show the log.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            raise InputErrorException('NoDeployment')
        last_time = None
        while True:
            logEntries = []
            try:
                logEntries = self.api.read_log(app_name, deployment_name, args.type, last_time=last_time)
            except GoneError:
                raise InputErrorException('WrongApplication')
            if len(logEntries) > 0:
                last_time = time.gmtime(float(logEntries[-1]["time"]))
                print_log_entries(logEntries, args.type)
            time.sleep(2)

    def push(self, args):
        """
            Push is actually only a shortcut for bzr push that automatically
            takes care of using the correct repository url.

            It queries the deployment details and uses whatever is in branch.

            If no deployment exists we automatically create one.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        try:
            if deployment_name == '':
                push_deployment_name = 'default'
            else:
                push_deployment_name = deployment_name
            deployment = self.api.read_deployment(app_name, push_deployment_name)
        except GoneError:
            push_deployment_name = ''
            if deployment_name != '':
                push_deployment_name = deployment_name
            try:
                deployment = self.api.create_deployment(app_name, deployment_name=push_deployment_name)
            except GoneError:
                raise InputErrorException('WrongApplication')
            except ForbiddenError:
                raise InputErrorException('NotAllowed')

        if args.source:
            cmd = ['bzr', 'push', deployment['branch'], '-d', args.source]
        else:
            cmd = ['bzr', 'push', deployment['branch']]
        try:
            check_call(cmd)
        except CalledProcessError, e:
            if e.returncode == 3:
                raise InputErrorException('PermissionDenied')
            print e

    def parse_app_deployment_name(self, name):
        match = re.match('^([a-z][a-z0-9]*)/((?:[a-z0-9]+\.)*[a-z0-9]+)$', name)
        if match:
            app_name = match.group(1)
            deployment_name = match.group(2)
            return app_name, deployment_name

        match = re.match('^([a-z][a-z0-9]*)$', name)
        if match:
            app_name = match.group(1)
            deployment_name = ''
            return app_name, deployment_name

        raise ParseAppDeploymentName

class ParseAppDeploymentName(Exception):
    """
        This Exception is raised if not a valid application name nor a valid application/deployment construct is given
    """
    pass
