#!/usr/bin/env bash

#
# build and or run Docker image
# Arguments
# [-b|--build] build a replacement airflow image
# [-r|--run] run the composed container ** default action if no flags given
# [-h|--help]
# [-r|--refresh_build ] if building, purge all built material and start over
# [-m|--requirements <dag-requirements-file>] default: "./StagingGlacierProcess-requirements.txt"
# [-l|--build_dir <build-dir>]" default ~/tmp/compose-build

usage() {
echo "Usage: $(basename $0) [-b|--build] [-r|--run] [-h|--help] [ -r|--refresh_build ] [-m|--requirements <dag-requirements-file>] [-l|--build_dir <build-dir>]"
echo "  -d|--down: suspend the airflow image"
echo "  -b|--build: build a replacement airflow image"
echo "  -r|--run: run the composed container ** default action if no flags given"
echo "  -h|--help"
echo "  -r|--refresh_build: if building, purge all built material and start over"
echo "  -m|--requirements <dag-requirements-file>: default: ./StagingGlacierProcess-requirements.txt"
echo "  -l|--build_dir <build-dir>: default: ~/tmp/compose-build"
}


prepare_pyPI_requirements() {
  # Merge StagingGlacier and sync requirements
  # ARG - no /tmp - must be local
  if [[ ! -d ${1:-"MRMXYZPTLK"} ]] ; then
    echo ${1} must exist, but doesnt. Cannot continue.
    exit 1
  fi
  full_tbin=merged-requirements.txt
  cat ${1}/bin/sync-requirements.txt ./StagingGlacierProcess-requirements.txt | sort -u | awk -F'[>,~=]' '{print $1}'> ${1}/${full_tbin}
  echo ${full_tbin}
}

export DAG_REQUIREMENTS_DEFAULT="./StagingGlacierProcess-requirements.txt"
export COMPOSE_AIRFLOW_IMAGE=bdrc-airflow
export COMPOSE_BDRC_DOCKER=bdrc-docker-compose.yml
export COMPOSE_BDRC_DOCKERFILE=Dockerfile-bdrc
export BIN=bin
#
# Location for everything that needs to be added to the image.
# used in 'docker-compose-bdrc.yml in the build step
export COMPOSE_BUILD_DIR=~/tmp/compose-build

# See README.rst
export DEV_DIR=~/dev
export AUDIT_TOOL_INSTALLER=audit-v1-beta_1.0-beta-1-2022-05-12_amd64.deb

down_flag=
build_flag=
run_flag=
refresh_flag=
OPTIONS=$(getopt -o dbrhfm:l: --long down,build,run,help, refresh,requirements,build_dir -- "$@")

while true; do  # Parse command line options
  case "$1" in
    -d|--down)
      down_flag=1
      shift
      ;;
    -b|--build)
      build_flag=1
      shift
      ;;
    -r|--run)
      run_flag=1
      shift
      ;;
    -f|--refresh_build)
      refresh_flag=1
      shift
      ;;
    -m|--requirements)
      tdag=$2
      shift 2
      ;;
    -l|--build_dir)
      COMPOSE_BUILD_DIR=$2
      shift 2
      ;;

    -h|--help)
      usage
      exit 1
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

if [[ -z "${build_flag}" && -z "${run_flag}"   && -z "${down_flag}" ]] ; then
  echo "default action is to run"
  export run_flag=1
fi

set -e  # all or nothing

# resolve DAG_REQUIREMENTS
export DAG_REQUIREMENTS=${tdag:-DAG_REQUIREMENTS_DEFAULT}
if [[ -n "${build_flag}" ]] ; then
  if [[ ! -f ${DAG_REQUIREMENTS} ]]  ; then
    echo "DAG requirements file not found: ${DAG_REQUIREMENTS}"
    exit 1
  fi

  if [[ -n "${refresh_flag}" ]] ; then
    if [[ -d ${COMPOSE_BUILD_DIR} ]] ; then
      rm -rf ${COMPOSE_BUILD_DIR}
    fi
  fi
  mkdir -p ${COMPOSE_BUILD_DIR}/${BIN}
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
  rsync ${COMPOSE_BDRC_DOCKERFILE} ${COMPOSE_BUILD_DIR}
  # Hack to have docker-compose find it locally
  export COMPOSE_BDRC_DOCKERFILE=$(basename ${COMPOSE_BDRC_DOCKERFILE})
  # ------------- Get audit-tool
  if [[ ! -f ${COMPOSE_BUILD_DIR}/${AUDIT_TOOL_INSTALLER} ]] ; then
    wget -O ${COMPOSE_BUILD_DIR}/${AUDIT_TOOL_INSTALLER}  https://github.com/buda-base/asset-manager/releases/download/v1.0-beta/${AUDIT_TOOL_INSTALLER}
  fi

#
  # finally, do_real_work
  # What were formerly build args are now environment variables
  docker compose --file "${COMPOSE_BDRC_DOCKER}" build  --no-cache
fi

if [[ -n "${run_flag}" ]] ; then
  # Secrets are a compose runtime, not a build. Exported into docker-compose, which can read the environment.
  export SECRETS=~/.docker-secrets
  mkdir -p "${SECRETS}"
  cp -v ~/.config/bdrc/docker/* "${SECRETS}" || exit 1
  ./extract-section.pl ~/.aws/credentials default  > ${SECRETS}/aws-credentials || exit 1
  chmod u-w "${SECRETS}"
  docker compose --file "${COMPOSE_BDRC_DOCKER}" up -d
fi

if [[ -n "${down_flag}" ]] ; then
  docker compose --file "${COMPOSE_BDRC_DOCKER}" down
fi



