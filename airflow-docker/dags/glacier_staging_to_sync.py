#!/usr/bin/env python3
"""
Creates and airflow DAG to process unglaciered bag files. The process is:
- de-bag
- (optionally) validate
Sync to Archive, using `syncOneWork.sh` (must be installed on host)
This initiates the DIP-pump workflow (see github://buda-base/archive-ops/scripts/dip-pump

Expected ObjectRestored message format:
We expect to get, in Response['Messages][0]['Body']['Records'] a set if dicts,
# noinspection SpellCheckingInspection
```
{
    "eventVersion": "2.1",
    "eventSource": "aws:s3",
    "awsRegion": "us-east-1",
    "eventTime": "2024-02-24T08:47:18.267Z",
    "eventName": "ObjectRestore:Completed",
    "userIdentity": {
        "principalId": "AmazonCustomer:A1JPP2WW1ZYN4F"
    },
    "requestParameters": {
        "sourceIPAddress": "s3.amazonaws.com"
    },
    "responseElements": {
        "x-amz-request-id": "6E5A5E04B1CFFAC5",
        "x-amz-id-2": \
        "Tt/6gfwuhCu9X06urpzaVuNBhSv4EW47BlmS2WrViVZ+MNDLo/ckEgLqLGi02IV6L3vshvP++ps1iPp9Zl3tPQ=="
    },
    "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "MGU5Zjk3MzItMjQ4Yi00MTU0LTk4ZGItNDBjYjU1MzhjMGU3",
        "bucket": {
            "name": "manifest.bdrc.org",
            "ownerIdentity": {
                "principalId": "A1JPP2WW1ZYN4F"
            },
            "arn": "arn:aws:s3:::manifest.bdrc.org"
        },
        "object": {
            "key": "ao1060/AWSIntake.zip",
            "size": 1637,
            "eTag": "6d3e031323ff7cb9ac0613d41a67d34e",
            "versionId": "rHKK9t5p3kcbTA8vLv.bZCnNitDHjIgz",
            "sequencer": "0065C3D18445E403D5"
        }
    },
    "glacierEventData": {
        "restoreEventData": {
            "lifecycleRestorationExpiryTime": "2024-03-06T00:00:00.000Z",
            "lifecycleRestoreStorageClass": "DEEP_ARCHIVE"
        }
    }
}
```
"""
import collections
import json
import os
from pprint import pp

import airflow.operators.bash

from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from bdrc_bag import bag_ops
from util_lib.version import bdrc_util_version

from staging_utils import *

# create a named tuple

# create a datetime.tzinfo for local time zone
def local_tz():
    import pytz
    return pytz.timezone('America/New_York')

Download_Map = collections.namedtuple('Download_Map', ['region_name', 'bucket', 'queue_name', 'config_section_name'])

# See AWSIntake.setup-aws.py for the queue names
# See 'deploy' for the config section names
download_map: [Download_Map] = [
    Download_Map('ap-northeast-2', 'glacier.staging.fpl.bdrc.org', 'FplReadyToIntake', 'ap_northeast'),
    Download_Map('ap-northeast-2', 'glacier.staging.nlm.bdrc.org', 'NlmReadyToIntake', 'ap_northeast'),
    Download_Map('us-east-1', 'manifest.bdrc.org', 'ManifestReadyToIntake', 'default')
]
# Region, SQS client

regional_queue_buckets: [()]
UNGLACIERED_QUEUE_NAME: str = 'ManifestReadyToIntake'

# For determining some file sys roots
DARWIN_PLATFORM: str = "darwin"

DEV_TIME_DELTA: timedelta = timedelta(minutes=10)
PROD_TIME_DELTA: timedelta = timedelta(minutes=60)

# DEBUG:
MY_TIME_DELTA = PROD_TIME_DELTA
REQUESTED_AWS_EVENTS: [str] = ['ObjectRestore:Completed', 'ObjectCreated:*']

# our buckets and SQS queues are in these sections of the config
REQUESTED_AWS_SECTIONS: [str] = ['default', 'ap_northeast']
#
# Use an environment variable to set the base path
# See docker-compose.yml for the roots/home/a
#
BASE_PATH = Path.home() / "bdrc" / "data"
# This was when we were local
DOWNLOAD_PATH = BASE_PATH / "Incoming"
STAGING_PATH = BASE_PATH / "work"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(STAGING_PATH, exist_ok=True)

# See docker-compose.yml for the location of the system logs. Should be a bind mount point
APP_LOG_ROOT = Path.home() / "bdrc" / "log"

# This value is a docker Bind Mount to a local dir - see ../airflow-docker/bdrc-docker-compose.yml
DEST_PATH = Path.home() / "extern" / "Archive"
# Non docker
_DB_CONFIG: Path = Path.home() / ".config" / "bdrc" / "db_apps.config" if not Path.exists(
    Path("/run/secrets/db_apps")) else Path("/run/secrets/db_apps")

# select a level (used in syncing)
prod_level: str = 'qa'  # 'prod' in production
# used in syncing
util_ver: str
try:
    util_ver: str = bdrc_util_version()
except:
    util_ver = "Unknown"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    #    'start_date': datetime(2024, 2, 20),
    #    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 22,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
    'schedule_interval': None
}

# -----------------  mocks for testing / debugging ------------------------
# Set up this copy for mock objects, because debagging is destructive
# removed - just set a bag zip file in AWS s3 and set up mock_message to get it
# mock_downloads: [str] = [
#     str(shutil.copy(BASE_PATH / "save-W1FPL2251.bag.zip", DOWNLOAD_PATH / "miniW1FPL2251.bag.zip"))]

mock_message: [] = [
    dict(
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "ap-northeast-2",
            "eventTime": "2024-04-06T00:11:23.730Z",
            "eventName": "ObjectRestore:Completed",
            "userIdentity": {
                "principalId": "AmazonCustomer:A1JPP2WW1ZYN4F"
            },
            "requestParameters": {
                "sourceIPAddress": "s3.amazonaws.com"
            },
            "responseElements": {
                "x-amz-request-id": "439897F6741FD9BA",
                "x-amz-id-2": "MF0oW9le+g8K5/R/uUks1QuFbZxNuSmZDWQ5utu8ZTcHEKSGFHzdFBEtebICzrPtG3YL1YVmffxhRw4nDPTZ1w=="
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "BagCreatedNotification",
                "bucket": {
                    "name": "glacier.staging.nlm.bdrc.org",
                    "ownerIdentity": {
                        "principalId": "A1JPP2WW1ZYN4F"
                    },
                    "arn": "arn:aws:s3:::glacier.staging.nlm.bdrc.org"
                },
                "object": {
                    "key": "Archive0/00/W1NLM4700/W1NLM4700.bag.zip",
                    "size": 17017201852,
                    "eTag": "41654cbd2a8f2d3c0abc83444fde825b-2029",
                    "sequencer": "00638792A45B638391"
                }
            },
            "glacierEventData": {
                "restoreEventData": {
                    "lifecycleRestorationExpiryTime": "2024-04-12T00:00:00.000Z",
                    "lifecycleRestoreStorageClass": "DEEP_ARCHIVE"
                }
            }
        }
    )]

mock_message1: [] = [
    dict(eventVersion="2.1", eventSource="aws:s3", awsRegion="us-east-1", eventTime="2024-02-24T08:47:18.267Z",
         eventName="ObjectRestore:Completed", userIdentity={
            "principalId": "AmazonCustomer:A1JPP2WW1ZYN4F"
        }, requestParameters={
            "sourceIPAddress": "s3.amazonaws.com"
        }, responseElements={
            "x-amz-request-id": "6E5A5E04B1CFFAC5",
            "x-amz-id-2": "Tt/6gfwuhCu9X06urpzaVuNBhSv4EW47BlmS2WrViVZ+MNDLo/ckEgLqLGi02IV6L3vshvP++ps1iPp9Zl3tPQ=="
        }, s3={
            "s3SchemaVersion": "1.0",
            "configurationId": "MGU5Zjk3MzItMjQ4Yi00MTU0LTk4ZGItNDBjYjU1MzhjMGU3",
            "bucket": {
                "name": "manifest.bdrc.org",
                "ownerIdentity": {
                    "principalId": "A1JPP2WW1ZYN4F"
                },
                "arn": "arn:aws:s3:::manifest.bdrc.org"
            },
            "object": {
                "key": "ao1060/W1FPL2251.bag.zip",
                "size": 78668981,
                "eTag": "405202973fc17c6f4b26cb56022c6201-10",
                "versionId": "vwfO4VqvGTlWeuSAtXDOhPzFhl.6YrSG",
                "sequencer": "0065C3D18445E403D5"
            }
        }, glacierEventData={
            "restoreEventData": {
                "lifecycleRestorationExpiryTime": "2024-03-06T00:00:00.000Z",
                "lifecycleRestoreStorageClass": "DEEP_ARCHIVE"
            }
        })
]


#  ----------------------   utils  -------------------------

# Take the given AWS region name and return the first section in download map that matches the region name
def get_download_map_for_region(region_name: str) -> Download_Map:
    """
    Get the download map entry for the given region
    :param region_name:
    :return:
    """
    return next((dm for dm in download_map if dm.region_name == region_name), None)


cached_sessions: {} = {}


def get_cached_session(profile_name: str) -> boto3.Session:
    """
    Get a cached session for the given profile name. Exploits the
    :param profile_name: key into cached sessions
    :return:
    """

    # This way recommended by PyLine, so cs not referenced before assignment
    # noinspection PyTypeChecker
    cs: boto3.Session = cached_sessions.get(profile_name, None)

    if not cs:
        cs = create_session(profile_name)
        cached_sessions[profile_name] = cs

    return cs


def close_cached_sessions():
    """
    Close all cached sessions (not necessary, actually, and clear the map
    :return:
    """
    cached_sessions.clear()


def create_fetch_sessions(dm: [Download_Map]) -> {}:
    """
    create sessions dictionary keyed by region, for each distinct config entry
    in the download map
    Sessions are used by clients ('s3' and 'sqs')
    :return:
    """
    # set de-duplicates
    out_sessions: {} = {}
    for dmentry in dm:
        if dmentry.region_name not in out_sessions:
            out_sessions[dmentry.region_name] = create_session(dmentry.config_section_name)

    pp(out_sessions)
    return out_sessions


def build_sync_env(execution_date) -> dict:
    """
    See sync_debagged task
       You have to emulate this stanza in bdrcSync.sh to set logging paths correctly
    # tool versions
    export logDipVersion=$(log_dip -v)
    export auditToolVersion=$(audit-tool -v)

    # date/time tags
    export jobDateTime=$(date +%F_%H.%M.%S)
    export jobDate=$(echo $jobDateTime | cut -d"_" -f1)
    export jobTime=$(echo $jobDateTime | cut -d"_" -f2)

    # log dirs
    # NOTE: these are dependent on logDir which is declared in the config file
    export syncLogDateTimeDir="$logDir/sync-logs/$jobDate/$jobDateTime"
    export syncLogDateTimeFile="$syncLogDateTimeDir/sync-$jobDateTime.log"
    export syncLogTempDir="$syncLogDateTimeDir/tempFiles"

    export auditToolLogDateTimeDir="$logDir/audit-test-logs/$jobDate/$jobDateTime"
    """

    # set up times
    year, month, day, hour, minute, second, *_ = execution_date.timetuple()

    # sh: $(date +%F_%H.%M.%S)
    job_time: str = f"{hour:0>2}.{minute:0>2}.{second:0>2}"
    # sh: $(date +%F)
    job_date: str = f"{year}-{month:0>2}-{day:0>2}"
    # $(date +%F_%H.%M.%S)
    job_date_time: str = f"{job_date}_{job_time}"

    # DEBUG: make local while testing
    # _root: Path = Path.home() / "dev" / "tmp" / "Projects" / "airflow" / "glacier_staging_to_sync" / "log"
    logDir: Path = APP_LOG_ROOT
    sync_log_home: Path = logDir / "sync-logs" / job_date / job_date_time
    sync_log_file = sync_log_home / f"sync-{job_date_time}.log"
    audit_log_home: Path = logDir / "audit-test-logs" / job_date / job_date_time
    os.makedirs(sync_log_home, exist_ok=True)
    os.makedirs(audit_log_home, exist_ok=True)

    return {
        "DEBUG_SYNC": "true",
        "DB_CONFIG": f"{prod_level}:{str(_DB_CONFIG)}",
        "hostName": "airflow_platform",
        "userName": "airflow_platform_user",
        "logDipVersion": util_ver,
        "auditToolVersion": "unknown",
        "jobDateTime": job_date_time,
        "jobDate": job_date,
        "jobTime": job_time,
        "auditToolLogDateTimeDir": str(audit_log_home),
        "syncLogDateTimeDir": str(sync_log_home),
        "syncLogDateTimeFile": str(sync_log_file),
        "syncLogTempDir": str(sync_log_home / "tempFiles"),
        "PATH": os.getenv("PATH")
    }


# ----------------------   airflow task declarations  -------------------------


@task
def get_restored_object_messages():
    """
    Pull a message from SQS
    :return:
    """
    # DEBUG
    return mock_message

    # output buffer
    s3_records = []
    session_dict: {} = {}

    # read from an SQS Queue
    # map of sessions, keyed by region
    try:
        session_dict = create_fetch_sessions(download_map)

        for dm_entry in download_map:
            region_name: str = dm_entry.region_name
            sqs = session_dict[region_name].client('sqs')

            queue_url = f"https://sqs.{region_name}.amazonaws.com/170602929106/{dm_entry.queue_name}"
            pp(f"Polling  {queue_url}")
            # Receive message from SQS queue
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=5,
                VisibilityTimeout=10,  # hide it from other consumers for 10 seconds
                WaitTimeSeconds=1
            )

            pp(f"Received {response}")

            if 'Messages' in response:

                # We could receive a number of messages. Since we only process the ones that contain a certain record
                # type (REQUESTED_EVENTS) It is required that each message ONLY contain the REQUESTED_EVENTS, because
                # we delete it if any of its records contain one of those events.
                for each_message in response['Messages']:
                    receipt_handle = each_message['ReceiptHandle']
                    pp("Message:")
                    pp(each_message['Body'], indent=4, width=40, depth=None, compact=False, sort_dicts=True)
                    message = response['Messages'][0]
                    message_body: [] = json.loads(message['Body'])
                    if 'Records' in message_body:
                        records = message_body['Records']
                        msg_s3_records = [r for r in records if
                                          match_any_event_class(r.get("eventName"), REQUESTED_AWS_EVENTS)]
                        if msg_s3_records:
                            s3_records.extend(msg_s3_records)
                            pp(f"Added {len(records)}")
                    else:
                        pp('No records in message')

                    pp(f"Deleting message {receipt_handle}")
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=receipt_handle
                    )

                else:
                    pp('No messages to receive')
    finally:
        pass
        #     for session in session_dict.values():
        #         session.close()
    # DEBUG
    # return mock_message

    pp(f"Returning {len(s3_records)}")
    return s3_records


@task
def download_from_messages(s3_records) -> [str]:
    """

    :param s3_records: object restored format
    :return: Nothing
    """

    downloaded_paths: [] = []
    #
    # DEBUG
    # raise EnvironmentError("DEBUG:  Not downloading")

    from botocore.exceptions import ClientError

    for s3_record in s3_records:
        bucket: str = "unset"
        key: str = "unset"
        try:
            awsRegion: str = s3_record['awsRegion']
            bucket = s3_record['s3']['bucket']['name']
            key = s3_record['s3']['object']['key']

            # DEBUG
            # key += "simulate_failureHack"

            download_full_path: Path = DOWNLOAD_PATH / key
            dfp_str: str = str(download_full_path)
            os.makedirs(download_full_path.parent, exist_ok=True)

            # maybe a use for this later
            # hash = s3_record['s3']['object']['eTag']

            s3 = get_cached_session(get_download_map_for_region(awsRegion).config_section_name).client('s3')
            s3.download_file(bucket, key, dfp_str)

            pp(f"Downloaded S3://{bucket}/{key} to {dfp_str}")
            downloaded_paths.append(str(download_full_path))
        except KeyError as e:
            pp(f'KeyError: {e}')
        except ClientError as e:
            pp(f"Could not retrieve S3://{bucket}/{key}:  {e} ")
    else:
        pp('No messages')

    return downloaded_paths


@task
def debag_downloads(downs: [str]) -> [str]:
    """
    Debags each unload
    :param downs: list of downloaded files
    :return: list of **path names** of  unbagged work archives. path object is not serializable,
    so returning strings
    """
    os.makedirs(STAGING_PATH, exist_ok=True)
    debagged: [Path] = []

    # BUG  Not everything that gets here is a bag.
    # Fixed: in bucket event notification configuration (see AWSIntake.setup-aws.py)
    # BUG - can have multiple entries for same zip. Deduplicate

    unique_downs = list(set(downs))

    for down in unique_downs:
        debagged.extend([str(d) for d in bag_ops.debag(down, str(STAGING_PATH))])
    return debagged


# create a set from a list of strings

#
@task
def sync_debagged(downs: [str], **context):
    """
    Syncs each debagged work
    :param downs:
    :param context: airflow context
    """

    env: {} = build_sync_env(context['execution_date'])

    for download in downs:
        # syncOneWork.sh [ -h ] [ -a archiveParent ] [ -w webParent ] [ -s successWorkList ] workPath
        airflow.operators.bash.BashOperator(
            task_id="sync_debag",
            bash_command=f"syncOneWork.sh -a {str(DEST_PATH)}  -s $(mktemp) {download} 2>&1 | tee $syncLogDateTimeFile",
            env=env
        ).execute(context)


with DAG('sqs_scheduled_dag',
         schedule=DEV_TIME_DELTA,
         start_date=datetime(2024, 4, 5,9,  32),
         end_date=datetime(2024, 4, 8, hour=23),
         tags=['bdrc'],
         catchup=False, # SUPER important. Catchups can confuse the Postgres DB
         max_active_runs=4) as sync_dag:
    # smoke test
    # notify = BashOperator(
    #     task_id="notify",
    #     bash_command='echo "HOWDY! There are now $(ls /tmp/images/ | wc -l) images."')

    msgs = get_restored_object_messages()
    downloads = download_from_messages(msgs)
    to_sync = debag_downloads(downloads)
    sync_debagged(to_sync)

if __name__ == '__main__':
    # noinspection PyArgumentList
    sync_dag.test()
    # gs_dag.cli()
