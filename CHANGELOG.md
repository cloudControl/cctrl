# Changelog

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [v1.16.1]

* a44f042 - Enable ssh authentication on Cloud&Heat
* 8318e62 - Logout user when setup email differs
* a0addbe - Add setting to enable/disable version checks
* 07ae1f8 - Better message for invalid key
* f975a3b - Deprecate ez_setup.py file
* c0318e2 - Add VersionEye support
* ba2d6fa - Upgrade requirements.txt

## [v1.16.0]

* ade3edf - Vagrant: Run tests when starting box
* ec91895 - Add changelog file
* 165df99 - Update README.md
* 34cc09c - Introduce setup command to handle user config
* 25a155d - Make string formatting compatible with python 2.6
* 17a70ab - Introduce SSH public key authentication
* 281305a - Introduce config file
* 53a26f3 - Add Vagrant support
* f9cc9e7 - ci: Exit with error if dist upload fails

## v1.15.2

* e4a5141 - Fix sshforwarder url for cnhapp
* 6c4951d - Update README.md
* 6163c52 - White-label home config directory

## v1.15.1

* 37fb65d - Make `cctrluser create` work

## v1.15.0

* 6a951a9 - Password and login could be set in an environment separately

## v1.14.3

* 2feed67 - Make help text for user.add and remove configurable
* 5e70354 - Update and pin argparse==1.2.2 and pycclib==1.5.5
* 096777f - Enable python setup.py tests

## v1.14.2

* 267e91b - Prefix user invation with project name
* 7246934 - config.add: Allow multipositional force flag
* 78899ab - config.add: Add output message for NoVariablesGiven error

## v1.14.1

* 8b95e1d - Improve cnh windows installation
* 48c4ce7 - Change cloud&heat env variable to CNH_LOGIN 

## v1.14.0

* 349dc0d - Read dedicated login creds for each platform

## v1.13.3

* f967ca4 - Update addon.register endpoint for exoscale

## v1.13.2

* ca40e7b - Prompt for updating right package when old version

## v1.13.1

* 2b75a10 - Catch exception on addon.register
* d6eb063 - Make the login prompt configurable

## v1.13.0

* a00d4ce - Add cnhuser addon.register
* f88cca0 - Adapt addon.add error message to the called cli

## v1.12.2

* 0799ed7 - Update settings for platforms w/o user management

## v1.12.1

* 6cc9d7f - Add cnhapp and cnhuser 

## v1.12.0

* 078051c - Automate new version release via Jenkins 
* c257751 - Update win32 install documentation 


[unreleased]: https://github.com/cloudControl/cctrl/compare/v1.16.1...HEAD
[v1.16.1]: https://github.com/cloudControl/cctrl/compare/v1.16.0...v1.16.1
[v1.16.0]: https://github.com/cloudControl/cctrl/compare/v1.15.2...v1.16.0
