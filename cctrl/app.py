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
from __builtin__ import raw_input, str, filter, float, len
import exceptions
import os
import time
import re
import subprocess
import shlex
import webbrowser
import math
import sys
import urlparse

from settings import CONFIG_ADDON
from datetime import datetime, timedelta

from pycclib.cclib import GoneError, ForbiddenError, TokenRequiredError, \
    BadRequestError, ConflictDuplicateError, UnauthorizedError, \
    NotImplementedError, ThrottledError
from subprocess import check_call, CalledProcessError
from cctrl.error import InputErrorException, messages
from cctrl.oshelpers import check_installed_rcs, is_buildpack_url_valid, \
    ssh_cmd, check_output
from cctrl.output import print_deployment_details, print_app_details,\
    print_alias_details, print_log_entries, print_list_apps,\
    print_addon_details, print_addons, print_addon_list, print_alias_list, \
    print_worker_list, print_worker_details, print_cronjob_list, \
    print_cronjob_details, print_addon_creds, print_config
from output import print_user_list_app, print_user_list_deployment
from cctrl.addonoptionhelpers import parse_additional_addon_options, \
    parse_config_variables, extract_flag_from_variables


class AppsController():
    """
        This controller handles the special case where you want to get a
        list of applications.
    """

    api = None

    def __init__(self, api):
        self.api = api

    def list(self):  # @ReservedAssignment
        apps = self.api.read_apps()
        print_list_apps(apps)


class CVSType():
    """
        A simple class for both supported repository types.
    """
    GIT = 'git'
    BZR = 'bzr'

    @staticmethod
    def by_path(application_path):
        """
            Provides the cvs (repo) type by checking if given directory
            contains a ".git" or ".bzr" configuration directory.
        """
        for (dirname, cvstype, msg) in [(".git", CVSType.GIT, 'GitConfigFound'),
                                        (".bzr", CVSType.BZR, 'BazaarConfigFound')]:
            if os.path.exists(os.path.join(application_path, dirname)):
                return (cvstype, msg)

        return (None, None)

    @staticmethod
    def by_env():
        """
            Provides the cvs (repo) type by checking environment variable
            PATH for existence of either Bazaar or Git.
        """
        for (execname, cvstype, msg) in [('git', CVSType.GIT, 'GitExecutableFound'),
                                         ('bzr', CVSType.BZR, 'BazaarExecutableFound')]:
            if check_installed_rcs(execname):
                return (cvstype, msg)

        return (None, None)


class AppController():
    """
        After parsing the command line in parse_cmdline() the related
        method of the ApplicationController gets called. Each method uses
        pycclib to fire a request and handles the response showing it to the
        user if needed.
    """
    def __init__(self, api, settings):
        self.api = api
        self.settings = settings

    def run_cmd(self, args):
        try:
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
        except ParseAppDeploymentName:
            raise InputErrorException('InvalidApplicationName')

        if not deployment_name:
            deployment_name = 'default'

        user_host = '{app}-{dep}@{host}'.format(app=app_name, dep=deployment_name, host=self.settings.ssh_forwarder)

        # Refresh our token before sending it to the forwarder.
        try:
            self.api.read_deployment(app_name, deployment_name)
        except GoneError:
            raise InputErrorException('WrongApplication')
        env = 'TOKEN={token}'.format(token=self.api.get_token()['token'])
        if len(args.command) > 0:
            command = '{env} {command}'.format(env=env, command=args.command)
        else:
            raise InputErrorException('NoRunCommandGiven')
        sshopts = shlex.split(os.environ.get('CCTRL_SSHOPTS', ''))
        ssh_command = ['ssh', '-t'] + sshopts + ['-p', self.settings.ssh_forwarder_port, '--', user_host, command]
        subprocess.call(ssh_command)

    def rollback_cmd(self, args):
        """
           Rollback command
        """

        try:
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
        except ParseAppDeploymentName:
            raise InputErrorException('InvalidApplicationName')

        if not deployment_name:
            deployment_name = 'default'

        logEntries = []

        try:
            logEntries = self.api.read_log(
                app_name,
                deployment_name,
                'deploy',
                last_time=None)
        except GoneError:
            raise InputErrorException('WrongApplication')

        deployments = [e['message'].split(':')[1].strip() for e in logEntries
                       if 'Deployed version' in e['message']]

        try:
            current_deployment = deployments.pop()
        except IndexError:
            raise InputErrorException('NoPreviousVersionFound')

        previous_deployment = None

        while not previous_deployment:
            try:
                deployment_version = deployments.pop()
                if deployment_version != current_deployment:
                    previous_deployment = deployment_version
            except IndexError:
                raise InputErrorException('NoPreviousVersionFound')

        try:
            self.api.update_deployment(
                app_name,
                version=previous_deployment,
                deployment_name=deployment_name)
        except GoneError:
            raise InputErrorException('WrongApplication')
        except ForbiddenError:
            raise InputErrorException('NotAllowed')

    def create(self, args):
        """
            Creates a new application.
        """
        try:
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
        except ParseAppDeploymentName:
            raise InputErrorException('InvalidApplicationName')

        if args.buildpack:
            # Did the user choose a default app type and provided a buildpack url?
            if not args.type == 'custom':
                raise InputErrorException('NoCustomApp')
            # Did the user provide a valid buildpack URL?
            elif not is_buildpack_url_valid(args.buildpack):
                raise InputErrorException('NoValidBuildpackURL')
        # Did the user provide a buildpack url if app has a custom type?
        elif args.type == 'custom':
            raise InputErrorException('NoBuildpackURL')

        # Did the user provide the repo type as argument?
        if args.repo:
            repo_type = args.repo
            detection_method = None
        else:
            # No, he/she didn't! Then check if current directory is an app and already has a CVS type ...
            (repo_type, detection_method) = CVSType.by_path(os.getcwd())

            if repo_type is None:
                # Hmm, current directory was nothing. Let's check if either 'bzr' or 'git' is installed ...
                (repo_type, detection_method) = CVSType.by_env()

            if repo_type is None:
                # Hmm, also nothing installed! Ok, we give up and set default = GIT and hope for better times ...
                detection_method = 'CreatingAppAsDefaultRepoType'
                repo_type = CVSType.GIT

        try:
            self.api.create_app(app_name, args.type, repo_type, args.buildpack)
            self.api.create_deployment(
                app_name,
                deployment_name=deployment_name)
            if detection_method:
                print messages[detection_method]
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
            TokenRequiredError being raised and after getting the credentials
            and creating a token this method would be called a second time.

            This would result in asking the user two times if he really wants
            to delete the app which is a rather bad user experience.
        """
        if self.api.check_token():
            app_name, deployment_name = self.parse_app_deployment_name(args.name)
            if not self.does_app_exist(app_name):
                raise InputErrorException('WrongApplication')
            if deployment_name:
                raise InputErrorException('DeleteOnlyApplication')
            if not args.force_delete:
                question = raw_input("Do you really want to delete application '{0}'? ".format(app_name) +
                                     'Type "Yes" without the quotes to delete: ')
            else:
                question = 'Yes'
            if question.lower() == 'yes':
                try:
                    self.api.delete_app(app_name)
                except ForbiddenError:
                    raise InputErrorException('NotAllowed')
                except BadRequestError:
                    raise InputErrorException('CannotDeleteDeploymentExist')
                except GoneError:
                    raise InputErrorException('WrongApplication')
            else:
                print messages['SecurityQuestionDenied']
        else:
            raise TokenRequiredError

    def _details(self, app_or_deployment_name):
        app_name, deployment_name = self.parse_app_deployment_name(app_or_deployment_name)
        if deployment_name:
            try:
                deployment = self.api.read_deployment(
                    app_name,
                    deployment_name)

                try:
                    app_users = self.api.read_app_users(app_name)
                except (UnauthorizedError, ForbiddenError, NotImplementedError):
                    # ok since possibly I am not allowed to see users at all
                    pass

                else:
                    deployment['users'] = [
                        dict(au, app=True)
                        for au in app_users
                    ] + deployment['users']

            except GoneError:
                raise InputErrorException('WrongDeployment')
            else:
                return app_name, deployment_name, deployment
        else:
            try:
                app = self.api.read_app(app_name)

                # only get deployment-users if i can see app-users
                if len(app['users']):
                    try:
                        for deployment in app['deployments']:
                            appname, depname = self.parse_app_deployment_name(deployment['name'])

                            depusers = self.api.read_deployment_users(appname, depname)

                            app['users'].extend(
                                dict(du, deployment=depname)
                                for du in depusers
                            )
                    except (NotImplementedError, BadRequestError):  # for old api-servers
                        pass

            except GoneError:
                raise InputErrorException('WrongApplication')
            else:
                return app_name, deployment_name, app

    def details(self, args):
        """
            Print application or deployment details.

            e.g.:

            'cctrlapp APP_NAME details' prints application details

            'cctrlapp APP_NAME/DEP_NAME details' prints deployment details
        """
        app_name, deployment_name, obj = self._details(args.name)
        if deployment_name:
            print_deployment_details(obj)
        else:
            public_key_content = self._get_public_key(app_name, obj)
            print_app_details(obj, public_key_content)

    def _get_deployment_url(self, obj):
        return "http://{0}".format(obj.get('default_subdomain'))

    def _get_repository_url(self, obj):
        return urlparse.urlsplit(obj.get('repository')).netloc

    def get_deployment_from_app_deployment_name(self, app_or_deployment_name):
        app_name, deployment_name = self.parse_app_deployment_name(app_or_deployment_name)
        if not deployment_name:
            deployment_name = 'default'

        try:
            deployment = self.api.read_deployment(
                app_name,
                deployment_name)

        except GoneError:
            raise InputErrorException('WrongDeployment')
        else:
            return app_name, deployment_name, deployment

    def _open(self, url):
        savout = os.dup(1)
        os.close(1)
        os.open(os.devnull, os.O_RDWR)
        try:
            webbrowser.open_new_tab(url)
        finally:
            os.dup2(savout, 1)

    def open(self, args):
        """
            Open deployment URL on the default browser.

            e.g.:

            'cctrlapp APP_NAME open' opens the default deployment's URL

            'cctrlapp APP_NAME/DEP_NAME open' opens the deployment's URL
        """
        app_name, deployment_name, obj = self.get_deployment_from_app_deployment_name(args.name)
        url = self._get_deployment_url(obj)
        self._open(url)

    def _get_size_from_memory(self, memory):
        res = re.match(r'(\d+)(.*)', memory.lower())
        if not res:
            raise InputErrorException('InvalidMemory')
        if res.group(2) in ['mb', 'm', '']:
            size = float(res.group(1)) / 128
        elif res.group(2) in ['gb', 'g']:
            size = float(res.group(1)) * 2 ** 10 / 128
        else:
            raise InputErrorException('InvalidMemory')
        final_size = int(math.ceil(size))
        if final_size != size:
            print >> sys.stderr, 'Memory size has to be a multiple of 128MB and has been rounded up to {0}MB.'.format(final_size * 128)
        return final_size

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
        if not deployment_name:
            deployment_name = 'default'
        if args.size:
            size = args.size
            if args.memory:
                raise InputErrorException('AmbiguousSize')
        elif args.memory:
            memory = args.memory
            size = self._get_size_from_memory(memory)
        else:
            size = None
        try:
            try:
                self.api.update_deployment(
                    app_name,
                    version=args.version,
                    deployment_name=deployment_name,
                    min_boxes=args.containers,
                    max_boxes=size,
                    stack=args.stack)
            except GoneError:
                try:
                    self.api.create_deployment(
                        app_name,
                        deployment_name=deployment_name,
                        stack=args.stack)
                    self.api.update_deployment(
                        app_name,
                        version=args.version,
                        deployment_name=deployment_name,
                        min_boxes=args.containers,
                        max_boxes=size,
                        stack=args.stack)
                except GoneError:
                    raise InputErrorException('WrongApplication')
                except ForbiddenError:
                    raise InputErrorException('NotAllowed')
        except BadRequestError as e:
            if 'max_boxes_over_max_process_limit' in e.msgs:
                if args.memory:
                    raise InputErrorException('InvalidMemory')
                if args.size:
                    raise InputErrorException('InvalidSize')
            else:
                raise

        if args.restart_workers:
            deployment = {'state': 'unknown'}
            while deployment['state'] != 'deployed':
                time.sleep(1)
                deployment = self.api.read_deployment(app_name, deployment_name)
            self._restartWorkers(app_name, deployment_name)

        return True

    def redeploy(self, deployment):
        """
            Redeploy an existing application with same options and configuration.
        """
        try:
            app_name, deployment_name = self.parse_app_deployment_name(deployment['name'])
            self.api.update_deployment(
                app_name,
                version=-1,
                deployment_name=deployment_name,
                min_boxes=deployment['min_boxes'],
                max_boxes=deployment['max_boxes'],
                stack=deployment['stack']['name'])
        except (KeyError, GoneError, BadRequestError):
            raise InputErrorException('DeploymentFailed')

    def undeploy(self, args):
        """
            Undeploys the deployment, deletes the database and files.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not self.does_app_exist(app_name):
            raise InputErrorException('WrongApplication')
        if not args.force_delete:
            question = raw_input("Do you really want to delete deployment '{0}'? ".format(args.name) +
                                 'This will delete everything including files and the database. Type "Yes" without the quotes to delete: ')
        else:
            question = 'Yes'
        if question.lower() == 'yes':
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
            deployment_name = 'default'
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
            deployment_name = 'default'
        if not args.alias:
            aliases = self.api.read_aliases(app_name, deployment_name)
            print_alias_list(aliases)
            return True
        else:
            try:
                alias = self.api.read_alias(
                    app_name,
                    args.alias,
                    deployment_name)
            except GoneError:
                raise InputErrorException('WrongAlias')
            else:
                print_alias_details(alias)
                return True

    def removeAlias(self, args):
        """
            Removes an alias form a deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.alias:
            raise InputErrorException('NoAliasGiven')
        try:
            self.api.delete_alias(app_name, args.alias, deployment_name)
        except GoneError:
            raise InputErrorException('WrongAlias')
        return True

    def addWorker(self, args):
        """
            Adds the given worker to the deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if args.size:
            size = args.size
            if args.memory:
                raise InputErrorException('AmbiguousSize')
        elif args.memory:
            memory = args.memory
            size = self._get_size_from_memory(memory)
        else:
            size = None
        if not deployment_name:
            deployment_name = 'default'
        if not args.command:
            raise InputErrorException('NoWorkerCommandGiven')
        try:
            self.api.create_worker(
                app_name,
                deployment_name,
                args.command,
                params=args.params,
                size=size)
        except BadRequestError as e:
            if 'size' in e.msgs:
                if args.memory:
                    raise InputErrorException('InvalidMemory')
                if args.size:
                    raise InputErrorException('InvalidSize')
            else:
                raise
        return True

    def showWorker(self, args):
        """
            Shows the details of an worker.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.wrk_id:
            workers = (self.api.read_worker(app_name, deployment_name, worker['wrk_id']) for worker in self.api.read_workers(app_name, deployment_name))
            print_worker_list(workers)
            return True
        else:
            try:
                worker = self.api.read_worker(
                    app_name,
                    deployment_name,
                    args.wrk_id)
            except GoneError:
                raise InputErrorException('WrongWorker')
            else:
                print_worker_details(worker)
                return True

    def removeWorker(self, args):
        """
            Removes an worker form a deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        try:
            self.api.delete_worker(app_name, deployment_name, args.wrk_id)
        except GoneError:
            raise InputErrorException('WrongWorker')
        return True

    def _restartWorker(self, app_name, deployment_name, wrk_id, command, params, size):
        self.api.delete_worker(app_name, deployment_name, wrk_id)
        self.api.create_worker(
            app_name,
            deployment_name,
            command,
            params,
            size)

    def _restartWorkers(self, app_name, deployment_name):
        workers = (self.api.read_worker(app_name, deployment_name, worker['wrk_id']) for worker in self.api.read_workers(app_name, deployment_name))
        for worker in workers:
            self._restartWorker(app_name, deployment_name, worker['wrk_id'], worker['command'], worker['params'], worker['size'])

    def restartWorker(self, args):
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'

        if args.wrk_id:
            try:
                worker = self.api.read_worker(app_name, deployment_name, args.wrk_id)
            except GoneError:
                raise InputErrorException('WrongWorker')

            self._restartWorker(app_name, deployment_name, worker['wrk_id'], worker['command'], worker['params'], worker['size'])
            return

        if args.all:
            self._restartWorkers(app_name, deployment_name)

    def addCron(self, args):
        """
            Adds the given worker to the deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.url:
            raise InputErrorException('NoCronURLGiven')
        self.api.create_cronjob(
            app_name,
            deployment_name,
            args.url)
        return True

    def showCron(self, args):
        """
            Shows the details of an worker.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.job_id:
            cronjobs = self.api.read_cronjobs(app_name, deployment_name)
            print_cronjob_list(cronjobs)
            return True
        else:
            try:
                cronjob = self.api.read_cronjob(
                    app_name,
                    deployment_name,
                    args.job_id)
            except GoneError:
                raise InputErrorException('NoSuchCronJob')
            else:
                print_cronjob_details(cronjob)
                return True

    def removeCron(self, args):
        """
            Removes an worker form a deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        try:
            self.api.delete_cronjob(app_name, deployment_name, args.job_id)
        except GoneError:
            raise InputErrorException('NoSuchCronJob')
        return True

    def _get_config_vars(self, app_name, deployment_name):
        try:
            addon = self.api.read_addon(app_name, deployment_name, CONFIG_ADDON)
            return addon['settings']['CONFIG_VARS']
        except (KeyError, GoneError):
            return {}

    def showConfig(self, args):
        """
            Shows the config variables
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'

        config = self._get_config_vars(app_name, deployment_name)

        if config:
            print_config(config, args.key)
        else:
            print '[ERROR] No configuration variables for this deployment.'

        return True

    def addConfig(self, args):
        """
            Adds the given variable and value to the config addon.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.variables:
            raise InputErrorException('NoVariablesGiven')

        args_variables, force = extract_flag_from_variables(args.variables,
                                                            ('-f', '--force'),
                                                            args.force_add)

        variables = parse_config_variables(args_variables, 'add')

        try:
            self.api.update_addon(
                app_name,
                deployment_name,
                CONFIG_ADDON,
                CONFIG_ADDON,
                settings=variables,
                force=force)
        except GoneError:
            # Add addon if it didn't exist.
            self.api.create_addon(app_name, deployment_name, CONFIG_ADDON, variables)
        except ThrottledError as te:
            # Overwrite the variable if didn't force, but type Yes
            question = raw_input('{0} Do you really want to overwrite it? '
                                 'Type "Yes" without the quotes to proceed: '.format(te.message))
            if question.lower() == 'yes':
                self.api.update_addon(
                    app_name,
                    deployment_name,
                    CONFIG_ADDON,
                    CONFIG_ADDON,
                    settings=variables,
                    force=True)

        return True

    def removeConfig(self, args):
        """
            Remove the given variable if it exists.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.variables:
            raise InputErrorException('NoVariablesGiven')

        variables = parse_config_variables(args.variables, 'remove')

        try:
            self.api.update_addon(
                app_name,
                deployment_name,
                CONFIG_ADDON,
                CONFIG_ADDON,
                settings=variables)
        except GoneError:
            raise InputErrorException('WrongAddon')

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
            deployment_name = 'default'
        if not args.addon:
            raise InputErrorException('NoAddonGiven')

        options = None
        if args.options:
            options = parse_additional_addon_options(args.options)

        try:
            self.api.create_addon(app_name, deployment_name, args.addon, options)
        except ConflictDuplicateError:
            raise InputErrorException('DuplicateAddon')
        except BadRequestError as e:
            if 'This is not a valid addon name' in str(e):
                raise InputErrorException('InvalidAddon')
            raise
        except ForbiddenError:
            raise InputErrorException('ForbiddenAddon')

        return True

    def showAddon(self, args):
        """
            Shows the details of an addon.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
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
                addon = self.api.read_addon(
                    app_name,
                    deployment_name,
                    args.addon)
            except GoneError:
                raise InputErrorException('WrongAddon')
            else:
                print_addon_details(addon)
                return True

    def showAddonCreds(self, args):
        """
            Print the creds.json of all Add-ons
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        if not args.addon:
            try:
                addons = self.api.read_addons(app_name, deployment_name)
            except:
                raise
            else:
                print_addon_creds(addons)
                return True
        else:
            try:
                addon = self.api.read_addon(
                    app_name,
                    deployment_name,
                    args.addon)
            except GoneError:
                raise InputErrorException('WrongAddon')
            else:
                print_addon_creds([addon])
                return True

    def updateAddon(self, args):
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        try:
            self.api.update_addon(
                app_name,
                deployment_name,
                args.addon_old,
                args.addon_new)
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
            deployment_name = 'default'
        if not args.addon:
            raise InputErrorException('NoAddonGiven')
        try:
            self.api.delete_addon(app_name, deployment_name, args.addon)
        except GoneError:
            raise InputErrorException('WrongAddon')
        return True

    def showUser(self, args):
        """
            List users
        """

        app_name, deployment_name, obj = self._details(args.name)

        if deployment_name:
            print_user_list_deployment(obj)
        else:
            print_user_list_app(obj)

        return True

    def addUser(self, args):
        """
            Add a user specified by the e-mail address to an application or deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)

        if self.settings.prefix_project_name:
            if len(args.email.split(':')) != 2:
                prefix = self.api.read_users()[0]['email'].split(':')[0]
                args.email = '{0}:{1}'.format(prefix, args.email)

        try:
            if deployment_name:
                self.api.create_deployment_user(app_name, deployment_name, args.email, args.role)

            else:
                self.api.create_app_user(app_name, args.email, args.role)

        except ConflictDuplicateError:
            raise InputErrorException('UserBelongsToApp')
        except NotImplementedError:
            raise InputErrorException('CommandNotImplemented')
        return True

    def removeUser(self, args):
        """
            Remove a user specified by the user name or email address from an application or deployment.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if '@' in args.username:
            if deployment_name:
                users = self.api.read_deployment_users(app_name, deployment_name)
            else:
                users = self.api.read_app(app_name)['users']
            try:
                username = [user['username'] for user in users
                            if user['email'] == args.username][0]
            except IndexError:
                raise InputErrorException('RemoveUserGoneError')
        else:
            username = args.username
        try:
            if deployment_name:
                self.api.delete_deployment_user(app_name, deployment_name,
                                                username)

            else:
                self.api.delete_app_user(app_name, username)

        except GoneError:
            raise InputErrorException('RemoveUserGoneError')
        except NotImplementedError:
            raise InputErrorException('CommandNotImplemented')
        return True

    def log(self, args):
        """
        Show the log.
        """
        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        if not deployment_name:
            deployment_name = 'default'
        last_time = None
        while True:
            logEntries = []
            try:
                logEntries = self.api.read_log(
                    app_name,
                    deployment_name,
                    args.type,
                    last_time=last_time)
            except GoneError:
                raise InputErrorException('WrongApplication')
            if len(logEntries) > 0:
                last_time = datetime.fromtimestamp(float(logEntries[-1]["time"]))
                if args.type == 'worker' and args.wrk_id:
                    logEntries = filter(lambda entry:
                                        entry['wrk_id'] == args.wrk_id, logEntries)
                if args.filter:
                    if args.type in ["error", "worker"]:
                        logEntries = filter(
                            lambda entry: re.search(
                                re.compile(args.filter, re.IGNORECASE),
                                entry['message']),
                            logEntries)
                    if args.type == 'access':
                        logEntries = filter(lambda entry:
                                            re.search(
                                                re.compile(args.filter, re.IGNORECASE),
                                                entry['first_request_line'] +
                                                entry['referer'] +
                                                entry['user_agent'] +
                                                entry['remote_host']),
                                            logEntries)
                print_log_entries(logEntries, args.type)
            time.sleep(2)

    def log_from_now(self, app_name, deployment_name, type_):
        last_time = datetime.now() - timedelta(seconds=10)
        while True:
            logEntries = []
            try:
                logEntries = self.api.read_log(
                    app_name,
                    deployment_name,
                    type_,
                    last_time=last_time)
            except GoneError:
                raise InputErrorException('WrongApplication')

            if len(logEntries) > 0:
                last_time = datetime.fromtimestamp(float(logEntries[-1]["time"]))
                print_log_entries(logEntries, type_)

            time.sleep(1)

    def _get_or_create_deployment(self, app_name, deployment_name, clear_cache):
        try:
            if deployment_name == '':
                push_deployment_name = 'default'
            else:
                push_deployment_name = deployment_name

            deployment = self.api.read_deployment(
                app_name,
                push_deployment_name)

            if clear_cache:
                self._clear_cache(app_name, deployment_name, deployment)
        except GoneError:
            push_deployment_name = ''
            if deployment_name != '':
                push_deployment_name = deployment_name

            try:
                deployment = self.api.create_deployment(
                    app_name,
                    deployment_name=push_deployment_name)
            except GoneError:
                raise InputErrorException('WrongApplication')
            except ForbiddenError:
                raise InputErrorException('NotAllowed')

        return deployment, push_deployment_name

    def _push_cmd(self, deployment, push_deployment_name, source):
        cmd = None
        if deployment['branch'].startswith('bzr+ssh'):
            rcs = check_installed_rcs('bzr')
            if not rcs:
                raise InputErrorException('BazaarRequiredToPush')

            if source:
                cmd = [rcs, 'push', deployment['branch'], '-d', source]
            else:
                cmd = [rcs, 'push', deployment['branch']]
        elif deployment['branch'].startswith('ssh'):
            rcs = check_installed_rcs('git')
            if not rcs:
                raise InputErrorException('GitRequiredToPush')

            if push_deployment_name == 'default':
                git_branch = 'master'
            else:
                git_branch = push_deployment_name

            if source:
                git_dir = os.path.join(source, '.git')
                cmd = [
                    rcs,
                    '--git-dir=' + git_dir,
                    'push',
                    deployment['branch'],
                    git_branch]
            else:
                cmd = [rcs, 'push', deployment['branch'], git_branch]

        return cmd

    def push(self, args):
        """
            Push is actually only a shortcut for bzr and git push commands
            that automatically takes care of using the correct repository url.

            It queries the deployment details and uses whatever is in branch.

            If deployment exists will clear the buildpack cache if
            --clear-cache flag is set.

            If no deployment exists we automatically create one.


        """
        if not check_installed_rcs('bzr') and not check_installed_rcs('git'):
            raise InputErrorException('NeitherBazaarNorGitFound')

        if args.deploy and args.ship:
            raise InputErrorException('ShipAndDeploy')

        app_name, deployment_name = self.parse_app_deployment_name(args.name)
        deployment, push_deployment_name = self._get_or_create_deployment(app_name, deployment_name, args.clear_cache)

        cmd = self._push_cmd(deployment, push_deployment_name, args.source)

        try:
            check_call(cmd)
        except CalledProcessError, e:
            print str(e)
            sys.exit(1)

        if args.deploy:
            print
            print "Deploying newest version."
            self.redeploy(deployment)

        if args.ship:
            print
            print "Deploying newest version. Press Ctrl+C to open {0} in your browser.".format(deployment['name'])
            self.redeploy(deployment)

            try:
                self.log_from_now(app_name, deployment_name, 'deploy')
            except KeyboardInterrupt:
                print
                print "Opening in browser..."
                self._open(self._get_deployment_url(deployment))

    def _clear_cache(self, app_name, deployment_name, deployment):
        subdomain = self._get_deployment_url(deployment).split('.', 1)[1]
        host_name = '{0}@{1}'.format(app_name, subdomain)

        cmd = ssh_cmd(host_name, 'delete-cache', deployment_name)

        try:
            check_call(cmd)
        except CalledProcessError:
            raise InputErrorException('ClearCacheFailed')

    def _get_public_key(self, app_name, application):
        host_name = self._get_repository_url(application)

        cmd = ssh_cmd(host_name, 'get-public-key')
        try:
            return check_output(cmd)
        except CalledProcessError:
            return "Not available. Have you added your Public Key?"

    def parse_app_deployment_name(self, name):
        match = re.match(
            '^([a-z][a-z0-9]*)/((?:[a-z0-9]+\.)*[a-z0-9]+)$',
            name)
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

    def does_app_exist(self, app_name):
        for app in self.api.read_apps():
            if app_name == app['name']:
                return True
        return False


class ParseAppDeploymentName(exceptions.Exception):
    """
        This Exception is raised if not a valid application name nor a
        valid application/deployment construct is given
    """
    pass
