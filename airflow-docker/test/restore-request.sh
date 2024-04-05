#!/usr/bin/env bash

set -e
export ME=$(basename $(readlink -f $0))
~/bin/init_sys.sh

# create a getopt line that accepts a bucket name and a work directory
OPTIONS=$(getopt -o lb:w: --long list,bucket,work -- "$@")

while true; do
  case "$1" in
  -l | --list)
    list_only=1
    shift
    ;;
  -b | --bucket)
    bucket=${2}
    shift 2
    ;;
  -w | --work)
    work=${2}
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

if [ -z "${bucket}" ]; then
  echo "No bucket specified"
  exit 1
fi

# Derive the complete path to the work, which is bucket/Archive{work_parent}/work_number_suffix/work_number/work_number.bag.zip

# Extract the last two characters of work
work_number_suffix=${work: -2}

# Is the work all digits?
if [[ ! "${work_number_suffix}" =~ ^[0-9]+$ ]]; then
  work_number_suffix="00"
fi

# find the work div and mod 50
# Note this is specific to the glacier.staging.xxx.bdrc.org buckets, NOT the archive
work_parent=$(($work_number_suffix / 50))

work_key_parent="Archive${work_parent}/${work_number_suffix}/${work}"
work_key="${work_key_parent}/${work}.bag.zip"

if [[ -z "${list_only}" ]]; then
  aws s3api restore-object  --bucket "${bucket}" --key ${work_key} --restore-request '{"Days": 5, "GlacierJobParameters": {"Tier": "Standard"}}'
fi

#
# Log the request

req_details=$(aws s3api head-object --bucket "${bucket}" --key ${work_key})
echo "${work_key}:${req_details}" | tee ./${work}_restore_request.log

if [[ -z "${list_only}" ]]; then
  aws s3 mv ./${work}_restore_request.log s3://manifest.bdrc.org/ao1060/restore_requests/${work}_restore_request.log
else
  cat ./${work}_restore_request.log
  rm ./${work}_restore_request.log
fi

