#!/usr/bin/env bash
set -eu

apt-get update

DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
	python-dev python-pip python-virtualenv git


# WORKSPACE is required on prepare script
export WORKSPACE=/vagrant
pip install $WORKSPACE --upgrade
$WORKSPACE/ci/prepare
