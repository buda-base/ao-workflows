#!/usr/bin/env bash
set -e
# Build and provision the bdrc airflow image
# Note that all material COPY'd into the image in Dockerfile
# **MUST** be realtive to this path.

# See README.rst
export DEV_DIR=~/dev
export AUDIT_TOOL_INSTALLER=audit-v1-beta_1.0-beta-1-2022-05-12_amd64.deb

prepare_pyPI_requirements() {
  # Merge StagingGlacier and sync requirements
  # ARG - no /tmp - must be local
  reqs="${tbin}/merged-requirements.txt"
  cat ${full_tbin}/sync-requirements.txt ./StagingGlacierProcess-requirements.txt | sort -u | awk -F'[>,~=]' '{print $1}'> $reqs
  echo $reqs

}

#------    Stage sync scripts
export tbin=bin
mkdir -p $tbin

# FML - arg to copylinksToBin has to be absolute because of its stupid pushdir
export full_tbin=$(readlink -f "$tbin")

# make sync scripts
$DEV_DIR/archive-ops/scripts/syncAnywhere/deployment/copyLinksToBin "$full_tbin"
# ------  End stage sync scripts

cleanup() {
  rm -rf $tbin
  rm -r $reqs
  rm -rf $docker_tmp_dir
}
# -------------
# trap cleanup EXIT
#ls -l $tbin
#read -p "Should be a buncha files Press any key to continue... " -n1 -s
reqs=$(prepare_pyPI_requirements)
#
# Get audit-tool
if [[ ! -f ${AUDIT_TOOL_INSTALLER} ]] ; then
  wget -O ${AUDIT_TOOL_INSTALLER}  https://github.com/buda-base/asset-manager/releases/download/v1.0-beta/${AUDIT_TOOL_INSTALLER}
fi
# finally, do_real_work
docker build  --no-cache --build-arg SYNC_SCRIPTS_HOME="${tbin}" --build-arg PY_REQS="${reqs}"  -t bdrc-airflow .
