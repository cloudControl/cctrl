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

if sys.version_info < (2, 6):
    has_str_format = False
else:
    has_str_format = True


def print_list_apps(apps):
    """
        Print a nice table of apps.
    """
    print 'Apps'
    if has_str_format:
        print " {0:3} {1:30} {2:6}".format('Nr', 'Name', 'Type')
        for i, app in enumerate(apps):
            print " {0:3} {1:30} {2:6}".format(
                i + 1,
                app['name'],
                app['type']['name'])
    else:
        print " %-3ls %-30ls %-6ls" % ('Nr', 'Name', 'Type')
        for i, app in enumerate(apps):
            print " %-3ls %-30ls %-6ls" % (
                i + 1,
                app['name'],
                app['type']['name'])


def print_app_details(app, public_key):
    """
        Print app details.
    """
    print 'App'
    if has_str_format:
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
    else:
        print " Name: %-30ls Type: %-10ls Owner: %-20ls" % (
            app['name'],
            app['type']['name'],
            app['owner']['username'])
        print ' Repository: %s' % (app['repository'])
        print '\n Public Key: %s' % public_key
        print '\n Users'
        print "   %-15ls %-35ls %-10ls %-10ls" % ('Name', 'Email', 'Role', 'Deployment')
        for user in app['users']:
            if 'deployment' not in user:
                user['deployment'] = '(app)'
            if 'role' not in user:
                user['role'] = ''

            print "   %(username)-15ls %(email)-35ls %(role)-10ls %(deployment)-10ls" % (user)
        print '\n Deployments'
        for deployment in app['deployments']:
            print "   %(name)-60ls" % (deployment)


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
    if has_str_format:
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

    else:
        print ' name: %(name)s' % (deployment)
        print ' stack: %s' % (stack)
        print ' URL: %s' % (url)
        print ' branch: %(branch)s' % (deployment)
        print ' last modified: %(date_modified)s' % (deployment)
        print ' current version: %(version)s' % (deployment)
        print ' current state: %(state)s' % (deployment)
        print ' containers: %(min_boxes)s' % (deployment)
        print ' memory: %(min_boxes)sMB' % (deployment) * 128

        if 'users' in deployment and deployment['users']:
            print '\n Users'
            print "   %-15ls %-35ls %-10ls %-10ls" % ('Name', 'Email', 'Role', 'Deployment')
            for user in deployment['users']:
                user['deployment'] = '(app)' if 'app' in user else deployment['name']
                print "   %(username)-15ls %(email)-35ls %(role)-10ls %(deployment)-10ls" % (user)


def print_user_list_app(app):
    print 'Users'
    if has_str_format:
        print "   {0:15} {1:35} {2:10} {3:10}".format('Name', 'Email', 'Role', 'Deployment')
        for user in app['users']:
            print "   {0:15} {1:35} {2:10} {3:10}".format(
                user['username'],
                user['email'],
                user['role'] if 'role' in user else '',
                user['deployment'] if 'deployment' in user else '(app)'
            )
    else:
        print "   %-15ls %-35ls %-10ls %-10ls" % ('Name', 'Email', 'Role', 'Deployment')
        for user in app['users']:
            if 'deployment' not in user:
                user['deployment'] = '(app)'
            if 'role' not in user:
                user['role'] = ''

            print "   %(username)-15ls %(email)-35ls %(role)-10ls %(deployment)-10ls" % (user)


def print_user_list_deployment(deployment):
    print 'Users'
    if has_str_format:
        print "   {0:15} {1:35} {2:10} {3:10}".format('Name', 'Email', 'Role', 'Deployment')
        for user in deployment['users']:
            print "   {0:15} {1:35} {2:10} {3:10}".format(
                user['username'],
                user['email'],
                user['role'],
                '(app)' if 'app' in user else deployment['name'],
            )
    else:
        print '\n Users'
        print "   %-15ls %-35ls %-10ls %-10ls" % ('Name', 'Email', 'Role', 'Deployment')
        for user in deployment['users']:
            user['deployment'] = '(app)' if 'app' in user else deployment['name']
            print "   %(username)-15ls %(email)-35ls %(role)-10ls %(deployment)-10ls" % (user)


def print_alias_list(aliases):
    """
        Print a list of aliases
    """
    if has_str_format:
        print 'Aliases'
        print ' {0:60} {1:8} {2:8}'.format('name', 'default', 'verified')
        for alias in aliases:
            print ' {0:60} {1:8} {2:8}'.format(
                alias['name'],
                alias['is_default'],
                alias['is_verified'])
    else:
        print 'Aliases'
        print ' %-60ls %-8ls %-8ls' % ('name', 'default', 'verified')
        for alias in aliases:
            print ' %(name)-60ls %(is_default)-8ls %(is_verified)-8ls' % (
                alias)


def print_alias_details(alias):
    """
        Print alias details.
    """
    if has_str_format:
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
    else:
        print '%-28ls: %s' % (
            'Alias',
            alias['name'])
        print '   %-25ls: %s' % (
            'is_default',
            str(alias['is_default']))
        print '   %-25ls: %s' % (
            'is_verified',
            str(alias['is_verified']))
        print '   %-25ls: %s' % (
            'verification_errors',
            alias['verification_errors'])
        print '   %-25ls: %s' % (
            'verification_code',
            alias['verification_code'])
        print '   %-25ls: %s' % (
            'date_created',
            alias['date_created'])
        print '   %-25ls: %s' % (
            'date_modified',
            alias['date_modified'])


def print_log_entries(logEntries, apache_type):
    """
        Print log lines that fit the apache type.

        Either access or error.
    """
    if apache_type == 'access':
        if has_str_format:
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
        else:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%d/%b/%Y:%H:%M:%S +0000]')
                try:
                    print r'%s %s %s %s "%s" %s %s "%s" "%s"' % (
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
        if has_str_format:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
                print r'{0} {1} {2}'.format(
                    entry["time"],
                    entry["type"],
                    entry["message"].encode('utf-8'))
        else:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
                print r'%s %s %s' % (
                    entry["time"],
                    entry["type"],
                    entry["message"].encode('utf-8'))
    elif apache_type == 'worker':
        if has_str_format:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
                print r'{0} {1} {2}'.format(
                    entry["time"],
                    entry["wrk_id"],
                    entry["message"].encode('utf-8'))
        else:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
                print r'%s %s %s' % (
                    entry["time"],
                    entry["wrk_id"],
                    entry["message"].encode('utf-8'))
    elif apache_type == 'deploy':
        if has_str_format:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
                print r'{0} {1} {2} {3}'.format(
                    entry["time"],
                    entry['hostname'],
                    entry["level"],
                    entry["message"].encode('utf-8'))
        else:
            for entry in logEntries:
                dt = datetime.fromtimestamp(float(entry["time"]))
                entry["time"] = dt.strftime('[%a %b %d %H:%M:%S %Y]')
                print r'%s %s %s %s' % (
                    entry["time"],
                    entry['hostname'],
                    entry["level"],
                    entry["message"].encode('utf-8'))


def print_keys(keys):
    """
        Print a list of keys.
    """
    print 'Keys'
    if has_str_format:
        for key in keys:
            print ' {0:15}'.format(key['key_id'])
    else:
        for key in keys:
            print ' %(key_id)-15ls' % (key)


def print_key(key):
    """
        Print a users public key.
    """
    print key["key"]


def print_addons(addons):
    """
       Print all available addons.
    """
    if has_str_format:
        for addon in addons:
            print '\nAddon: {0}'.format(addon['name'])
            for option in addon['options']:
                print '   {0}'.format(option['name'])
    else:
        for addon in addons:
            print '\nAddon: %s' % (addon['name'])
            for option in addon['options']:
                print '   %s' % option['name']


def print_addon_creds(addons):
    creds_format = {}
    for addon in addons:
        if len(addon['settings']):
            name = addon['addon_option']['name'].split('.')[0].upper()
            creds_format[name] = addon['settings']
    print json.dumps(creds_format, indent=4, sort_keys=True)


def print_addon_list(addons):
    """
        Print a list of addon details
    """
    for addon in addons:
        print_addon_details(addon)
        print '\n'


def print_addon_details(addon):
    """
        Print addon details.
    """
    if has_str_format:
        print '{0:25}: {1}'.format('Addon', addon['addon_option']['name'])
        if len(addon['settings']) > 0:
            print '   \n Settings'
            for key, value in addon['settings'].items():
                print '   {0:25}: {1}'.format(key, value)
    else:
        print '%-25ls: %s' % ('Addon', addon['addon_option']['name'])
        if len(addon['settings']) > 0:
            print '   \n Settings'
            for key, value in addon['settings'].items():
                print '   %-25ls: %s' % (key, value)


def print_worker_list(workers):
    print 'Workers'
    if has_str_format:
        print ' {0:3} {1:11} {2}'.format('nr.', 'wrk_id', 'command')
        for count, worker in enumerate(workers):
            print ' {0:3} {1:11} {2}'.format(count + 1, worker['wrk_id'], worker['command'])
    else:
        print ' %-3ls %-11ls %s' % ('nr.', 'wrk_id', 'command')
        for count, worker in enumerate(workers):
            print ' %-3ls %-11ls %s' % (count + 1, worker['wrk_id'], worker['command'])


def print_worker_details(worker):
    print 'Worker'
    if has_str_format:
        print ' {0:9}: {1}'.format('wrk_id', worker['wrk_id'])
        try:
            print ' {0:9}: {1}'.format('command', worker['command'].encode('utf-8'))
        except UnicodeDecodeError:
            print ' {0:9}: {1}'.format('command', worker['command'])
        print ' {0:9}: {1}'.format('params', worker['params'])
        print ' {0:9}: {1}'.format('size', worker['size'])
        print ' {0:9}: {1}'.format('created', worker['date_created'])
    else:
        print ' %-9ls: %s' % ('wrk_id', worker['wrk_id'])
        print ' %-9ls: %s' % ('command', worker['command'])
        print ' %-9ls: %s' % ('params', worker['params'])
        print ' %-9ls: %s' % ('size', worker['size'])
        print ' %-9ls: %s' % ('created', worker['date_created'])


def print_cronjob_list(cronjobs):
    print 'Cronjobs'
    if has_str_format:
        print ' {0:3} {1:11}'.format('nr.', 'job_id')
        for count, cronjob in enumerate(cronjobs):
            print ' {0:3} {1:11}'.format(count + 1, cronjob['job_id'])
    else:
        print ' %-3ls %-11ls' % ('nr.', 'job_id')
        for count, cronjob in enumerate(cronjobs):
            job_id = cronjob['wrk_id']
            print ' %-3ls %-11ls' % (count + 1, job_id)


def print_cronjob_details(cronjob):
    print 'Cronjob'
    if has_str_format:
        print ' {0:9}: {1}'.format('job_id', cronjob['job_id'])
        print ' {0:9}: {1}'.format('url', cronjob['url'])
        print ' {0:9}: {1}'.format('next_run', cronjob['next_run'])
        print ' {0:9}: {1}'.format('created', cronjob['date_created'])
        print ' {0:9}: {1}'.format('modified', cronjob['date_modified'])
    else:
        print ' %-9ls: %s' % ('job_id', cronjob['job_id'])
        print ' %-9ls: %s' % ('url', cronjob['url'])
        print ' %-9ls: %s' % ('next_run', cronjob['next_run'])
        print ' %-9ls: %s' % ('created', cronjob['date_created'])
        print ' %-9ls: %s' % ('modified', cronjob['date_modified'])


def get_version(cctrlversion, cclibversion):
    """
        Prepare the version string
    """
    if has_str_format:
        return '%(prog)s {0} using pycclib {1}'.format(
            cctrlversion,
            cclibversion)
    else:
        return '%%(prog)s %s using pycclib %s' % (cctrlversion, cclibversion)


def print_config(config, key=None):
    if key and key in config:
        print config.get(key)
    elif key:
        print '[ERROR] Key `{0}` not found.'.format(key)
    else:
        for key in sorted(config):
            print u'{0}={1}'.format(key, pipes.quote(config.get(key) or ''))
