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
import sys

if sys.version_info < (2, 6):
    has_str_format = False
else:
    has_str_format = True
    
def print_list_apps(apps):
    """
        Print a nice table of apps.
    """
    if has_str_format:
        print "{0:3} {1:30} {2:6} {3:10}".format('i', 'Name', 'Type', 'Owner')
        for i, app in enumerate(apps):
            print "{0:3} {1:30} {2:6} {3:10}".format(i, app['name'], app['type']['name'], app['owner']['username'])
    else:
        print "%-3ls %-30ls %-6ls %-10ls" % ('i', 'Name', 'Type', 'Owner')
        for i, app in enumerate(apps):
            print "%-3ls %-30ls %-6ls %-10ls" % (i, app['name'], app['type']['name'], app['owner']['username'])

def print_deployment_details(deployment):
    """
        Print deployment details.
    """
    if has_str_format:
        print 'name: {0}'.format(deployment['name'])
        print 'branch: {0}'.format(deployment['branch'])
        print 'last modified: {0}'.format(deployment['date_modified'])
        print 'current version: {0}'.format(deployment['version'])
        print ' '
        print 'db user: {0}'.format(deployment['dep_id'])
        print 'db password: {0}'.format(deployment['db_password'])
        print ' '
        print 'aliases:'
        print '{0:60} {1:8} {2:8}'.format('name', 'default', 'verified')
        for alias in deployment['aliases']:
            print '{0:60} {1:8} {2:8}'.format(alias['name'], alias['is_default'], alias['is_verified'])
    else:
        print 'name: %(name)s' % (deployment)
        print 'branch: %(branch)s' % (deployment)
        print 'last modified: %(date_modified)s' % (deployment)
        print 'current version: %(version)s' % (deployment)
        print ' '
        print 'db user: %(dep_id)s' % (deployment)
        print 'db password: %(db_password)s' % (deployment)
        print ' '
        print 'aliases:'
        print '%-60ls %-8ls %-8ls' % ('name', 'default', 'verified')
        for alias in deployment['aliases']:
            print '%(name)-60ls %(is_default)-8ls %(is_verified)-8ls' % (alias)
            
def print_app_details(app):
    """
        Print app details.
    """
    if has_str_format:
        print "name: {0:30} type: {1:10} owner: {2:20}".format(app['name'], app['type']['name'], app['owner']['username'])
        print ' '
        print 'users:'
        print "{0:40} {1:20}".format('name', 'email')
        for user in app['users']:
            print "{0:40} {1:20}".format(user['username'], user['email'])
        print ' '
        print 'deployments:'
        print "{0:60} {1:7} {2:10}".format('name', 'version', 'state')
        for deployment in app['deployments']:
            print "{0:60} {1:7} {2:10}".format(deployment['name'], deployment['version'], deployment['state'])
    else:
        print "name: %-30ls type: %-10ls owner: %-20ls" % (app['name'], app['type']['name'], app['owner']['username'])
        print ' '
        print 'users:'
        print "%-40ls %-20ls" % ('name', 'email')
        for user in app['users']:
            print "%(username)-40ls %(email)-20ls" % (user)
        print ' '
        print 'deployments:'
        print "%-60ls %-7ls %-10ls" % ('name', 'version', 'state')
        for deployment in app['deployments']:
            print "%(name)-60ls %(version)-7ls %(state)-10ls" % (deployment)
            
def print_alias_details(alias):
    """
        Print alias details.
    """
    if has_str_format:
        print '{0:25}: {1}'.format('Alias', alias['name'])
        print '{0:25}: {1}'.format('is_default', str(alias['is_default']))
        print '{0:25}: {1}'.format('is_verified', str(alias['is_verified']))
        print '{0:25}: {1}'.format('verification_errors', alias['verification_errors'])
        print '{0:25}: {1}'.format('verification_code', alias['verification_code'])
        print '{0:25}: {1}'.format('date_created', alias['date_created'])
        print '{0:25}: {1}'.format('date_modified', alias['date_modified'])
    else:
        print '%-25ls: %s' % ('Alias', alias['name'])
        print '%-25ls: %s' % ('is_default', str(alias['is_default']))
        print '%-25ls: %s' % ('is_verified', str(alias['is_verified']))
        print '%-25ls: %s' % ('verification_errors', alias['verification_errors'])
        print '%-25ls: %s' % ('verification_code', alias['verification_code'])
        print '%-25ls: %s' % ('date_created', alias['date_created'])
        print '%-25ls: %s' % ('date_modified', alias['date_modified'])
        
def print_log_entries(logEntries, type):
    """
        Print log lines that fit the apache type.
        
        Either access or error.
    """
    if type == 'access':
        if has_str_format:
            for entry in logEntries:
                entry["time"] = time.strftime('[%d/%b/%Y:%H:%M:%S +0000]', time.gmtime(float(entry["time"])))
                print r'{0} {1} {2} {3} \"{4}\" {5} {6} \"{7}\" \"{8}\"'.format(entry["remote_host"], entry["remote_logname"], entry["remote_user"], entry["time"], entry["first_request_line"], entry["status"], entry["response_size_CLF"], entry["referer"], entry["user_agent"])
        else:
            for entry in logEntries:
                entry["time"] = time.strftime('[%d/%b/%Y:%H:%M:%S +0000]', time.gmtime(float(entry["time"])))
                print r'%s %s %s %s \"%s\" %s %s \"%s\" \"%s\"' % (entry["remote_host"], entry["remote_logname"], entry["remote_user"], entry["time"], entry["first_request_line"], entry["status"], entry["response_size_CLF"], entry["referer"], entry["user_agent"])            
    elif type == 'error':
        if has_str_format:
            for entry in logEntries:
                entry["time"] = time.strftime('[%a %b %d %H:%M:%S %Y]', time.gmtime(float(entry["time"])))
                print r'{0} {1} {2}'.format(entry["time"], entry["type"], entry["message"])
        else:
            for entry in logEntries:
                entry["time"] = time.strftime('[%a %b %d %H:%M:%S %Y]', time.gmtime(float(entry["time"])))
                print r'%s %s %s' % (entry["time"], entry["type"], entry["message"])
                
def print_keys(keys):
    """
        Print a list of keys.
    """
    if has_str_format:
        print '{0:15} {1}'.format('ID', 'Public Key')
        for key in keys:
            print '{0:15} {1}'.format(key['key_id'], key['key'])
    else:
        print '%-15ls %s' % ('ID', 'Public Key')
        for key in keys:
            print '%(key_id)-15ls %(key)s' % (key)
