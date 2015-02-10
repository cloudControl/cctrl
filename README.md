cctrl [![Build Status](https://travis-ci.org/cloudControl/cctrl.svg?branch=master)](https://travis-ci.org/cloudControl/cctrl)[![PyPI version](https://badge.fury.io/py/cctrl.svg)](http://badge.fury.io/py/cctrl) 
=====

`cctrl` is a set of command line utilities to help you create and manage applications
and users hosted on platforms compatible with [cloudControl](https://www.cloudcontrol.com).


Dependencies
------------

 * python 2.6.x and later
 * python modules:
    * argparse
    * pycclib


Installation
------------
To install `cctrl`:

* Via pip (non-windows compatible)

    `$ (sudo) pip install cctrl`

* Via setup.py

    `$ (sudo) python setup.py install`


    Dependencies should be automatically fetched by `easy_install`.

* Via executable (windows only)

    https://www.cloudcontrol.com/download/win


To upgrade `cctrl` (non-windows compatible):

    $ (sudo) pip install cctrl --upgrade


Vagrant Support
---------------

This project includes Vagrant support, so you can start an Ubuntu virtual machine
with your local `cctrl` version installed and ready to use. It might be also useful
for Windows users, so they can have a more Unix-like experience.

To start a `cctrl` Vagrant box you need to be inside the project directory and follow
these steps:

	$ vagrant up
	$ vagrant ssh
	$ cctrlapp -h

If you're working on project development and want to update your changes, run:

	$ vagrant provision

You can find documentation on Vagrant installation and configuration on their [official
site](http://docs.vagrantup.com/v2/installation/index.html).
