#!/usr/bin/env bash
# Build and provision the bdrc airflow image
# Stage sync scripts
export tbin=sync-scripts
mkdir -p $tbin

# FML - arg to copylinksToBin has to be absolute because of its stupid pushdir
full_tbin=$(readlink -f "$tbin")

# make sync scripts
~/dev/archive-ops/scripts/syncAnywhere/deployment/copyLinksToBin "$full_tbin"

cleanup() {
  rm -rf $tbin

}

trap cleanup EXIT
#ls -l $tbin
#read -p "Should be a buncha files Press any key to continue... " -n1 -s

set -vx
docker build  --build-arg SYNC_SCRIPTS_HOME="${tbin}" -t bdrc-airflow .
