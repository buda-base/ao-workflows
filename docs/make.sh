#!/usr/bin/env bash
#
# Build these here docs

# default target is build
set -vx
_target=${1:-build}


make SOURCEDIR=../doc/source BUILDDIR=build $_target

