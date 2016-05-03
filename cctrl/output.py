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
from datetime import datetime
import sys
import json
import pipes


def print_list_apps(apps):
    """
        Print a nice table of apps.
    """
    print 'Apps'
    print " {0:3} {1:30} {2:6}".format('Nr', 'Name', 'Type')
    for i, app in enumerate(apps):
        print " {0:3} {1:30} {2:6}".format(
            i + 1,
            app['name'],
            app['type']['name'])


def print_app_details(app, public_key):
    """
        Print app details.
    """
    print 'App'
    print " Name: {0:30} Type: {1:10} Owner: {2:20}".format(
        app['name'],
        app['type']['name'],
        app['owner']['username'])
    if app['type']['name'] == 'custom':
        print ' Buildpack URL: {0}\n'.format(app['buildpack_url'])
    print ' Repository: {0}'.format(app['repository'])
    print '\n Public Key: {0}'.format(public_key)

    print '\n Users'
    print "   {0:15} {1:35} {2:10} {3:10}".format('Name', 'Email', 'Role', 'Deployment')
    for user in app['users']:
        print "   {0:15} {1:35} {2:10} {3:10}".format(
            user['username'],
            user['email'],
            user['role'] if 'role' in user else '',
            user['deployment'] if 'deployment' in user else '(app)'
        )
    print '\n Deployments'
    for deployment in app['deployments']:
        print "   {0:60}".format(deployment['name'])


def print_deployment_details(deployment):
    """
        Print deployment details.
    """
    app, dep = deployment['name'].split("/")
    url = "http://{0}".format(deployment['default_subdomain'])

    if deployment['stack']:
        stack = deployment['stack']['name']
    else:
        stack = None
    print 'Deployment'
    print ' name: {0}'.format(deployment['name'])
    print ' stack: {0}'.format(stack)
    print ' URL: {0}'.format(url)
    print ' branch: {0}'.format(deployment['branch'])
    print ' last modified: {0}'.format(deployment['date_modified'])
    print ' current version: {0}'.format(deployment['version'])
    print ' current state: {0}'.format(deployment['state'])
    print ' containers: {0}'.format(deployment['min_boxes'])
    print ' memory: {0}MB'.format(deployment['max_boxes'] * 128)

    if 'users' in deployment and deployment['users']:
        print '\n Users'
        print "   {0:15} {1:35} {2:10} {3:10}".format('Name', 'Email', 'Role', 'Deployment')
        for user in deployment['users']:
            print "   {0:15} {1:35} {2:10} {3:10}".format(
                user['username'],
                user['email'],
                user['role'],
                '(app)' if 'app' in user else deployment['name'],
            )


def print_user_list_app(app):
    print 'Users'
    print "   {0:15} {1:35} {2:10} {3:10}".format('Name', 'Email', 'Role', 'Deployment')
    for user in app['users']:
        print "   {0:15} {1:35} {2:10} {3:10}".format(
            user['username'],
            user['email'],
            user['role'] if 'role' in user else '',
            user['deployment'] if 'deployment' in user else '(app)'
        )


def print_user_list_deployment(deployment):
    print 'Users'
    print "   {0:15} {1:35} {2:10} {3:10}".format('Name', 'Email', 'Role', 'Deployment')
    for user in deployment['users']:
        print "   {0:15} {1:35} {2:10} {3:10}".format(
            user['username'],
            user['email'],
            user['role'],
            '(app)' if 'app' in user else deployment['name'],
        )


def print_alias_list(aliases):
    """Print a list of aliases"""
    print 'Aliases'
    print ' {0:60} {1:8} {2:8}'.format('name', 'default', 'verified')
    for alias in aliases:
        print ' {0:60} {1:8} {2:8}'.format(
            alias['name'],
            alias['is_default'],
            alias['is_verified'])


def print_alias_details(alias):
    """Print alias details."""
    print '{0:28}: {1}'.format('Alias', alias['name'])
    print '   {0:25}: {1}'.format(
        'is_default',
        str(alias['is_default']))
    print '   {0:25}: {1}'.format(
        'is_verified',
        str(alias['is_verified']))
    print '   {0:25}: {1}'.format(
        'verification_errors',
        alias['verification_errors'])
    print '   {0:25}: {1}'.format(
        'verification_code',
        alias['verification_code'])
    print '   {0:25}: {1}'.format(
        'date_created',
        alias['date_created'])
    print '   {0:25}: {1}'.format(
        'date_modified',
        alias['date_modified'])


def print_log_entries(logEntries, apache_type):
    """
        Print log lines that fit the apache type.

        Either access or error.
    """
    if apache_type == 'access':
        for entry in logEntries:
            dt = datetime.fromtimestamp(float(entry["time"]))
            entry["time"] = dt.strftime('[%d/%b/%Y:%H:%M:%S +0000]')
            try:
                print r'{0} {1} {2} {3} "{4}" {5} {6} "{7}" "{8}"'.format(
                    entry["remote_host"],
                    entry["remote_logname"],
                    entry["remote_user"],
                    entry["time"],
                    entry["first_request_line"],
                    entry["status"],
                    entry["response_size_CLF"],
                    entry["referer"],
                    entry["user_agent"])
            except KeyError:
                pass
    elif apache_type == 'error':
        for entry in logEntries:
            dt = datetime.fromtimestamp(float(entry["time"]))
            entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
            print r'{0} {1} {2}'.format(
                entry["time"],
                entry["type"],
                entry["message"].encode('utf-8'))
    elif apache_type == 'worker':
        for entry in logEntries:
            dt = datetime.fromtimestamp(float(entry["time"]))
            entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
            print r'{0} {1} {2}'.format(
                entry["time"],
                entry["wrk_id"],
                entry["message"].encode('utf-8'))
    elif apache_type == 'deploy':
        for entry in logEntries:
            dt = datetime.fromtimestamp(float(entry["time"]))
            entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
            print r'{0} {1} {2} {3}'.format(
                entry["time"],
                entry['hostname'],
                entry["level"],
                entry["message"].encode('utf-8'))


def print_keys(keys):
    """Print a list of keys."""
    print 'Keys'
    for key in keys:
        print ' {0:15}'.format(key['key_id'])


def print_key(key):
    """Print a users public key."""
    print key["key"]


def print_addons(addons):
    """Print all available addons."""
    for addon in addons:
        print '\nAddon: {0}'.format(addon['name'])
        for option in addon['options']:
            print '   {0}'.format(option['name'])


def print_addon_creds(addons):
    creds_format = {}
    for addon in addons:
        if len(addon['settings']):
            name = addon['addon_option']['name'].split('.')[0].upper()
            creds_format[name] = addon['settings']
    print json.dumps(creds_format, indent=4, sort_keys=True)


def print_addon_list(addons):
    """Print a list of addon details"""
    for addon in addons:
        print_addon_details(addon)
        print '\n'


def print_addon_details(addon):
    """Print addon details."""
    print '{0:25}: {1}'.format('Addon', addon['addon_option']['name'])
    if len(addon['settings']) > 0:
        print '   \n Settings'
        for key, value in addon['settings'].items():
            print '   {0:25}: {1}'.format(key, value)


def print_worker_list(workers):
    print 'Workers'
    print ' {0:3} {1:11} {2}'.format('nr.', 'wrk_id', 'command')
    for count, worker in enumerate(workers):
        print ' {0:3} {1:11} {2}'.format(count + 1, worker['wrk_id'], worker['command'])


def print_worker_details(worker):
    print 'Worker'
    print ' {0:9}: {1}'.format('wrk_id', worker['wrk_id'])
    try:
        print ' {0:9}: {1}'.format('command', worker['command'].encode('utf-8'))
    except UnicodeDecodeError:
        print ' {0:9}: {1}'.format('command', worker['command'])
    print ' {0:9}: {1}'.format('params', worker['params'])
    print ' {0:9}: {1}'.format('size', worker['size'])
    print ' {0:9}: {1}'.format('created', worker['date_created'])


def print_cronjob_list(cronjobs):
    print 'Cronjobs'
    print ' {0:3} {1:11}'.format('nr.', 'job_id')
    for count, cronjob in enumerate(cronjobs):
        print ' {0:3} {1:11}'.format(count + 1, cronjob['job_id'])


def print_cronjob_details(cronjob):
    print 'Cronjob'
    print ' {0:9}: {1}'.format('job_id', cronjob['job_id'])
    print ' {0:9}: {1}'.format('url', cronjob['url'])
    print ' {0:9}: {1}'.format('next_run', cronjob['next_run'])
    print ' {0:9}: {1}'.format('created', cronjob['date_created'])
    print ' {0:9}: {1}'.format('modified', cronjob['date_modified'])


def get_version(cctrlversion, cclibversion):
    """Prepare the version string"""
    return '%(prog)s {0} using pycclib {1}'.format(
        cctrlversion,
        cclibversion)


def print_config(config, key=None):
    if key and key in config:
        print config.get(key)
    elif key:
        print '[ERROR] Key `{0}` not found.'.format(key)
    else:
        for key in sorted(config):
            print u'{0}={1}'.format(key, pipes.quote(config.get(key) or ''))
