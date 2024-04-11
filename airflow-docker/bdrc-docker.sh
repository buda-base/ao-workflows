#!/usr/bin/env bash

# Build the airflow docker image.
# See README.rst

# all or nothing
set -e

export ME=$(basename $0)
export INIT_SYS=~/bin/init_sys.sh

source ${INIT_SYS}

# D'OH AIRFLOW_UID is a **BUILD**arg.
# Test see if this is necessary - when a sync goes through
# Must be invoked on a system that has the uid service
#
# prod
#xa_uid=$(id -u service)
# dev (fix aslo in bdrc-docker-compose.yml)
xa_uid=$(id -u)
export AIRFLOW_UID="${xa_uid}"

usage() {
  # Brackets without spaces mess up ReST
  echo "Usage: ${ME}  [ -h|--help ]  [ -m|--requirements <dag-requirements-file> ] [ -d|--build_dir <build-dir> ]"
  echo "Invokes the any_service:build target in bdrc-docker-compose.yml"
  echo "  -c|--config_dir <config_dir>: the elements of the 'bdrc' folder under .config. the config dir must contain at least folder 'bdrc'" 
  echo "  -h|--help"
  echo "  -m|--requirements <dag-requirements-file>: default: ./StagingGlacierProcess-requirements.txt"
  echo "  -d|--build_dir <build-dir>: default: ~/tmp/compose-build"
  echo ""
  echo "** CAUTION: ONLY COPY config what is needed. db_apps is NOT needed.**"
  echo "** DO NOT COPY the entire bdrc tree!"
}


prepare_pyPI_requirements() {
  # Merge StagingGlacier and sync requirements
  # ARG - no /tmp - must be local
  if [[ ! -d ${1:-"MRMXYZPTLK"} ]] ; then
    log_echo ${1} must exist, but doesnt. Cannot continue.
    exit 1
  fi
  full_tbin=merged-requirements.txt
  cat ${1}/bin/sync-requirements.txt ./StagingGlacierProcess-requirements.txt | sort -u | awk -F'[>,~=]' '{print $1}'> ${1}/${full_tbin}
  echo ${full_tbin}
}

# You have to export these because some of them will be used in the build target in bdrc-docker-compose.yml
export DAG_REQUIREMENTS_DEFAULT="./StagingGlacierProcess-requirements.txt"
export COMPOSE_AIRFLOW_IMAGE=bdrc-airflow
export COMPOSE_BDRC_DOCKER=bdrc-docker-compose.yml
export COMPOSE_BDRC_DOCKERFILE=Dockerfile-bdrc
export BIN=bin
export AUDIT_HOME=
export BUILD_CONFIG_ROOT=.config

#
# Location for everything that needs to be added to the image.
# used in 'docker-compose-bdrc.yml in the build step
export COMPOSE_BUILD_DIR=~/tmp/compose-build

# See README.rst
export DEV_DIR=~/dev
export AUDIT_TOOL_INSTALLER=audit-v1-beta_1.0-beta-1-2022-05-12_amd64.deb

# Build the path to an audit tool config
# This is for the Dockerfile-bdrc.
# You can always update at run time
# docker cp ~/.config/blasdlasd ./config/blash

# this var is needed in bdrc-docker-compose.yml


build_flag=
CLI_ARGS="$@"
OPTIONS=$(getopt -o rhm:d:c: --long rebuild,help,requirements,build_dir,config_dir -- "$@")

while true; do  # Parse command line options
    case "$1" in
	-r|--rebuild)
	    rebuildFlag=1
	    shift
	    ;;
	-m|--requirements)
	    tdag=$2
	    shift 2
	    ;;
	-d|--build_dir)
	    COMPOSE_BUILD_DIR=$2
	    shift 2
	    ;;
	
	-h|--help)
	    usage
	    exit 1
	    ;;
	
	-c|--config_dir)
	    CONFIG_SRC_HOME=$2
	    shift 2
	    ;;
	--)
	    shift
	    break
	    ;;
	*)
	    break
	    ;;
    esac
done

xx=${CONFIG_SRC_HOME?"-c|--config_dir is required"}

[[ ! -d ${CONFIG_SRC_HOME} ]] &&  { echo  $CONFIG_SRC_HOME not found or not a directory; exit 2 ; }
[[ ! -r ${CONFIG_SRC_HOME} ]] &&  { echo  $CONFIG_SRC_HOME not a readable directory ; exit 5 ; }
   
export DAG_REQUIREMENTS=${tdag:-$DAG_REQUIREMENTS_DEFAULT}
log_echo "${ME} ${CLI_ARGS} "

# resolve DAG_REQUIREMENTS

log_echo "rti: build_flag: ${build_flag} -m|--requirements: ${tdag} -d|--build_dir: ${COMPOSE_BUILD_DIR} DAG_REQUIREMENTS: ${DAG_REQUIREMENTS}"

if [[ ! -f ${DAG_REQUIREMENTS} ]]  ; then
  log_echo "DAG requirements file not found: ${DAG_REQUIREMENTS}"
  exit 1
fi

if [[ -n "${rebuildFlag}" ]] ; then
    log_echo rebuilding compose build
  if [[ -d ${COMPOSE_BUILD_DIR} ]] ; then
    rm -rf ${COMPOSE_BUILD_DIR}
  fi
else
   log_echo refreshing compose build
fi

mkdir -p "${COMPOSE_BUILD_DIR}"/${BIN}
# Build and provision the bdrc airflow image
# Note that all material COPY'd into the image in Dockerfile
# **MUST** be relative to this path.
# See docker compose args

#------    Stage sync scripts
# FML - arg to copylinksToBin has to be absolute because of its stupid pushdir
# Also note the echo has to be blank (copyLinksToBin has an escape clause)
$DEV_DIR/archive-ops/scripts/syncAnywhere/deployment/copyLinksToBin $(readlink -f "${COMPOSE_BUILD_DIR}/${BIN}") < <(echo "")

# ------------- calculate and copy pip requirements
export COMPOSE_PY_REQS=$(prepare_pyPI_requirements "${COMPOSE_BUILD_DIR}")

# -------------- copy the Dockerfile
log_echo rsync ${COMPOSE_BDRC_DOCKERFILE} ${COMPOSE_BUILD_DIR}
rsync ${COMPOSE_BDRC_DOCKERFILE} ${COMPOSE_BUILD_DIR}

# Hack to have docker-compose find it locally
export COMPOSE_BDRC_DOCKERFILE=$(basename ${COMPOSE_BDRC_DOCKERFILE})

# ------------- Get audit-tool executable
log_echo Getting audit tool
if [[ ! -f ${COMPOSE_BUILD_DIR}/${AUDIT_TOOL_INSTALLER} ]] ; then
  wget -O ${COMPOSE_BUILD_DIR}/${AUDIT_TOOL_INSTALLER}  https://github.com/buda-base/asset-manager/releases/download/v1.0-beta/${AUDIT_TOOL_INSTALLER}
fi

# ----- set up config
# WARNING - the user has to pre-set the config dir. This is a hack.
mkdir -p ${COMPOSE_BUILD_DIR}/${BUILD_CONFIG_ROOT}
#
log_echo "Setting up config"
# The /*t  is important - copy the contents, not the container.
cp -r ${CONFIG_SRC_HOME}/* ${COMPOSE_BUILD_DIR}/${BUILD_CONFIG_ROOT}
#


#
# finally, do_real_work
# What were formerly build args are now environment

log_echo 
docker compose --file "${COMPOSE_BDRC_DOCKER}" build  --no-cache $@




