#!/usr/bin/env python
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

import argparse

from cctrl.settings import VERSION
from pycclib.cclib import *
from pycclib.version import __version__ as cclibversion
import cctrl.common as common
from cctrl.app import AppController, AppsController
from cctrl.output import get_version


class list_action(argparse.Action):
    """
        This action is needed by argparse because we use --list to get a list
        of apps that a user has access too. This is not directly supported by
        one of the other argpase actions. Therefore we needed to write our own.

        #TODO: Right now we do the error handling here and in common.run.
        It would be better to use common.run here too.
    """

    def __init__(self, api, settings, **kwargs):
        super(list_action, self).__init__(**kwargs)
        self.api = api
        self.settings = settings

    def __call__(self, parser, namespace, value, option_string=None):
        try:
            common.check_for_updates(self.settings.package_name, self.api.check_versions()['cctrl'])
        except KeyError:
            pass
        except ConnectionException:
            pass

        apps = AppsController(self.api)
        common.execute_with_authenticated_user(self.api, lambda: apps.list(), self.settings)
        parser.exit()


def parse_cmdline(app, settings):
    """
        We parse the commandline using argparse from
        http://code.google.com/p/argparse/.

        argparse works with parsers and subparsers.

        Our main parser for cctrlapp always requires a name argument. We then
        add subparses for each action available for the app identified by name.

        Each subparser then may have it's own arguments needed for that
        particular subparsers action to work.
    """
    version = get_version(VERSION, cclibversion)
    description = "%(prog)s controls your cloudControl apps"
    epilog = "And now you're in control"

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    list_apps = parser.add_argument_group(
        'list apps',
        'get a list of all your apps')
    list_apps.add_argument(
        '-l',
        '--list',
        action=list_action,
        nargs=0,
        api=app.api,
        settings=app.settings,
        help='list apps')

    control_apps = parser.add_argument_group(
        'control apps',
        'control app or deployment')

    control_apps.add_argument(
        'name',
        help='app_name for apps or app_name/deployment_name for deployments',
        metavar='app_name[/deployment_name]')

    subparsers = parser.add_subparsers(
        title='commands',
        description='available commands',
        metavar='')

    run_cmd_subparser = subparsers.add_parser(
        'run',
        help="run command")
    run_cmd_subparser.add_argument(
        'command',
        help='command to execute')
    run_cmd_subparser.set_defaults(func=app.run_cmd)

    rollback_cmd_subparser = subparsers.add_parser(
        'rollback',
        help="rollback to previous deployment")
    rollback_cmd_subparser.set_defaults(func=app.rollback_cmd)

    create_subparser = subparsers.add_parser(
        'create',
        help="create new application")
    create_subparser.add_argument(
        'type',
        help='app-type (language)',
        metavar='type')
    create_subparser.add_argument(
        '--buildpack',
        help='custom buildpack URL (for "custom" app type)',
        default=None,
        metavar='url')
    create_subparser.add_argument(
        '--repo',
        choices=['bzr', 'git'],
        help='bzr or git',
        default=None,
        metavar='repo')
    create_subparser.set_defaults(func=app.create)

    details_subparser = subparsers.add_parser(
        'details',
        help="app or deployment details")
    details_subparser.set_defaults(func=app.details)

    delete_subparser = subparsers.add_parser(
        'delete',
        help="delete application")
    delete_subparser.add_argument(
        '-f',
        '--force',
        action="store_true",
        dest="force_delete",
        help="don't ask for confirmation")
    delete_subparser.set_defaults(func=app.delete)

    push_subparser = subparsers.add_parser('push', help="push local changes")
    push_subparser.add_argument(
        'source',
        nargs='?',
        help='path to local branch')
    push_subparser.add_argument(
        '--ship',
        action='store_true',
        dest='ship',
        help='deploy, show logs and open last version in browser after pushing')
    push_subparser.add_argument(
        '--clear-buildpack-cache',
        action='store_true',
        dest='clear_cache',
        help="clear the deployment buildpack cache so all dependencies are downloaded again")
    push_subparser.add_argument(
        '--deploy',
        action='store_true',
        dest='deploy',
        help='deploy after pushing')
    push_subparser.set_defaults(func=app.push)

    deploy_subparser = subparsers.add_parser('deploy', help="deploy version")
    deploy_subparser.add_argument(
        '--containers', '--min',
        type=int,
        metavar='NUM',
        help="number of containers")
    deploy_subparser.add_argument(
        '--size', '--max',
        type=int,
        help="container memory size in units of 128MB")
    deploy_subparser.add_argument(
        '--memory',
        help="container size in MB, --memory=X*128 maps to --size=X")
    deploy_subparser.add_argument(
        '--stack',
        action="store",
        nargs='?',
        default=None,
        dest="stack",
        help="desired stack name")
    deploy_subparser.add_argument(
        'version',
        nargs='?',
        default=-1,
        help='optionally accepts a version')
    deploy_subparser.add_argument(
        '--restart-workers',
        action='store_true',
        dest='restart_workers',
        help='restart the worker after deploying')
    push_subparser.set_defaults(func=app.push)
    deploy_subparser.set_defaults(func=app.deploy)

    undeploy_subparser = subparsers.add_parser(
        'undeploy',
        help="delete deployment")
    undeploy_subparser.add_argument(
        '-f',
        '--force',
        action="store_true",
        dest="force_delete",
        help="don't ask for confirmation")
    undeploy_subparser.set_defaults(func=app.undeploy)

    showUser_subparser = subparsers.add_parser('user', help="list app users")
    showUser_subparser.set_defaults(func=app.showUser)

    addUser_subparser = subparsers.add_parser(
        'user.add',
        help="add user by {0}".format(settings.login_help_name))
    addUser_subparser.add_argument('email', metavar=settings.login_help_name)
    addUser_subparser.add_argument(
        '--role',
        action="store",
        nargs='?',
        default=None,
        dest="role",
        help="role")
    addUser_subparser.set_defaults(func=app.addUser)

    removeUser_subparser = subparsers.add_parser(
        'user.remove',
        help="remove user by username or {0}".format(settings.login_help_name))
    removeUser_subparser.add_argument('username', help='username or {0}'.format(settings.login_help_name))
    removeUser_subparser.set_defaults(func=app.removeUser)

    showConfig_subparser = subparsers.add_parser('config', help="list config vars")
    showConfig_subparser.add_argument(
        'key',
        nargs='?',
        help='name of the key e.g. foo')
    showConfig_subparser.set_defaults(func=app.showConfig)

    addConfig_subparser = subparsers.add_parser(
        'config.add',
        help="add config vars")
    addConfig_subparser.add_argument(
        '-f',
        '--force',
        action="store_true",
        dest="force_add",
        help="don't ask for confirmation")
    addConfig_subparser.add_argument(
        'variables',
        nargs=argparse.REMAINDER,
        help='variables to add passed through to the config add-on e.g foo=bar baz=faa')
    addConfig_subparser.set_defaults(func=app.addConfig)

    removeConfig_subparser = subparsers.add_parser(
        'config.remove',
        help="remove config variables")
    removeConfig_subparser.add_argument(
        'variables',
        nargs=argparse.REMAINDER,
        help='variables to remove on the config add-on e.g. foo baz')
    removeConfig_subparser.set_defaults(func=app.removeConfig)

    showAddon_subparser = subparsers.add_parser('addon', help="show addon")
    showAddon_subparser.add_argument(
        'addon',
        nargs='?',
        help='name of the addon e.g. mysql.free')
    showAddon_subparser.set_defaults(func=app.showAddon)

    showAddon_subparser = subparsers.add_parser(
        'addon.list',
        help="list all available addons")
    showAddon_subparser.set_defaults(func=app.listAddons)

    showAddon_subparser = subparsers.add_parser(
        'addon.creds',
        help="print creds.json format to stdout")
    showAddon_subparser.add_argument(
        'addon',
        nargs='?',
        help='name of the addon e.g. mysql.free')
    showAddon_subparser.set_defaults(func=app.showAddonCreds)

    addAddon_subparser = subparsers.add_parser(
        'addon.add',
        help="add addon")
    addAddon_subparser.add_argument(
        'addon',
        help='name of the addon e.g. mysql.free')
    addAddon_subparser.add_argument(
        'options',
        nargs=argparse.REMAINDER,
        help='options passed through to the add-on - if path to file the content is sent')
    addAddon_subparser.set_defaults(func=app.addAddon)

    addAddon_subparser = subparsers.add_parser(
        'addon.upgrade',
        help="upgrade addon")
    addAddon_subparser.add_argument(
        'addon_old',
        help='current addon option')
    addAddon_subparser.add_argument(
        'addon_new',
        help='addon option to upgrade to')
    addAddon_subparser.set_defaults(func=app.updateAddon)

    addAddon_subparser = subparsers.add_parser(
        'addon.downgrade',
        help="downgrade addon")
    addAddon_subparser.add_argument(
        'addon_old',
        help='current addon option')
    addAddon_subparser.add_argument(
        'addon_new',
        help='addon option to downgrade to')
    addAddon_subparser.set_defaults(func=app.updateAddon)

    removeAddon_subparser = subparsers.add_parser(
        'addon.remove',
        help="remove addon")
    removeAddon_subparser.add_argument(
        'addon',
        help='name of the addon e.g. mysql.free')
    removeAddon_subparser.set_defaults(func=app.removeAddon)

    showAlias_subparser = subparsers.add_parser('alias', help="show alias")
    showAlias_subparser.add_argument(
        'alias',
        nargs='?',
        help='name of the alias e.g. www.example.com')
    showAlias_subparser.set_defaults(func=app.showAlias)

    addAlias_subparser = subparsers.add_parser('alias.add', help="add alias")
    addAlias_subparser.add_argument(
        'alias',
        help='name of the alias e.g. www.example.com')
    addAlias_subparser.set_defaults(func=app.addAlias)

    removeAlias_subparser = subparsers.add_parser(
        'alias.remove',
        help="remove alias")
    removeAlias_subparser.add_argument(
        'alias',
        help='name of the alias e.g. www.example.com')
    removeAlias_subparser.set_defaults(func=app.removeAlias)

    showWorker_subparser = subparsers.add_parser(
        'worker',
        help="show worker")
    showWorker_subparser.add_argument(
        'wrk_id',
        nargs='?',
        help='optional wrk_id for single worker details')
    showWorker_subparser.set_defaults(func=app.showWorker)

    addWorker_subparser = subparsers.add_parser(
        'worker.add',
        help="start worker")
    addWorker_subparser.add_argument(
        'command',
        help='the command to execute')
    addWorker_subparser.add_argument(
        'params',
        nargs='?',
        default=None,
        help='optional parameters to append to the command')
    addWorker_subparser.add_argument(
        '--size',
        type=int,
        help="container memory size in units of 128MB")
    addWorker_subparser.add_argument(
        '--memory',
        help="container size in MB, --memory=X*128 maps to --size=X")
    addWorker_subparser.set_defaults(func=app.addWorker)

    removeWorker_subparser = subparsers.add_parser(
        'worker.remove',
        help="stop worker")
    removeWorker_subparser.add_argument(
        'wrk_id',
        help='stop worker by wrk_id')
    removeWorker_subparser.set_defaults(func=app.removeWorker)

    restartWorker_subparser = subparsers.add_parser(
        'worker.restart',
        help="restart worker")
    restart_worker_group = restartWorker_subparser.add_mutually_exclusive_group(required=True)
    restart_worker_group.add_argument(
        'wrk_id',
        help='restart worker by wrk_id',
        nargs='?'
    )
    restart_worker_group.add_argument(
        '--all',
        action='store_true',
        dest='all',
        help='restart all currently running workers')
    restart_worker_group.set_defaults(func=app.restartWorker)

    showCron_subparser = subparsers.add_parser('cron', help="show cronjobs")
    showCron_subparser.add_argument(
        'job_id',
        nargs='?',
        help='optional job_id for single worker details')
    showCron_subparser.set_defaults(func=app.showCron)

    addCron_subparser = subparsers.add_parser('cron.add', help="add cronjob")
    addCron_subparser.add_argument('url', help='url to call')
    addCron_subparser.set_defaults(func=app.addCron)

    removeCron_subparser = subparsers.add_parser(
        'cron.remove',
        help="remove cronjob")
    removeCron_subparser.add_argument(
        'job_id',
        help='remove cronjob by job_id')
    removeCron_subparser.set_defaults(func=app.removeCron)

    log_subparser = subparsers.add_parser('log', help="show the log")
    log_subparser.add_argument(
        'type',
        choices=['access', 'error', 'worker', 'deploy'])
    log_subparser.add_argument(
        '-w',
        '--wrk_id',
        action="store",
        nargs='?',
        default=None,
        dest="wrk_id",
        help="a wrk_id to filter the worker log")
    log_subparser.add_argument(
        '-g',
        '--grep',
        action="store",
        nargs='?',
        default=None,
        dest="filter",
        help="pattern to search for within the log entry")
    log_subparser.set_defaults(func=app.log)

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=version,
        help='show version string')

    open_subparser = subparsers.add_parser(
        'open',
        help="open deployment on default browser"
    )
    open_subparser.set_defaults(func=app.open)

    args = parser.parse_args()

    common.run(args, app.api, app.settings)


def setup_cli(settings):
    api = common.init_api(settings)
    try:
        app = AppController(api, settings)
        parse_cmdline(app, settings)
    except KeyboardInterrupt:
        pass
    finally:
        common.shutdown(api, settings)
