#!/usr/bin/env bash
set -eu

apt-get update

DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
	python-dev python-pip git

sudo pip install /vagrant 
