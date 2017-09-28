#!/bin/sh
#
# EBDO-FeatureService test runner
# Widely adapted from Restbase
# Copyright (C) 2017 Project-EBDO
# Author: Joseph Allemandou
#

mod_dir=$( cd "$( dirname "$0" )"/../.. && pwd )/node_modules
mocha="$mod_dir"/mocha/bin/mocha
istanbul="$mod_dir"/istanbul/lib/cli.js


if [ "$1" = "test" ]; then
    "${mocha}"
elif [ "$1" = "coverage" ]; then
    "${istanbul}" cover node_modules/.bin/_mocha -- -R spec
fi
