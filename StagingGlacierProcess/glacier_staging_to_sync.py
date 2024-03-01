#!/usr/bin/env python3
"""
Creates and airflow DAG to process unglaciered bag files. The process is:
- unbag
- (optionally) validate
Sync to Archive, using `syncOneWork.sh` (must be installed on host)
This initiates the DIP-pump workflow (see github://bdua-base/archive-ops/scripts/dip-pump

Expected ObjectRestored message format:
We expect to get, in Response['Messages][0]['Body']['Records'] a set if dicts,

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

import json
import os
import shutil
from pathlib import Path
import platform

from airflow.operators.bash import BashOperator
from pendulum import datetime

from airflow import DAG
from airflow.decorators import task
from datetime import timedelta
from bdrc_bag import bag_ops
from util_lib.version import bdrc_util_version
from archive_ops.api import get_archive_location

UNGLACIERED_QUEUE_NAME: str = 'ManifestReadyToIntake'

# For determining some file sys roots
DARWIN_PLATFORM: str = "darwin"

DEV_TIME_DELTA: timedelta = timedelta(seconds=30)
PROD_TIME_DELTA: timedelta = timedelta(hours=1)

# DEBUG:
MY_TIME_DELTA = DEV_TIME_DELTA
REQUESTED_EVENTS = ['ObjectRestore:Completed']

# TODO: Put this into an enviro. var?
BASE_PATH = Path.home() / "dev" / "tmp" / "Projects" / "airflow" / "glacier_staging_to_sync"
DOWNLOAD_PATH = BASE_PATH / "Incoming"
STAGING_PATH = BASE_PATH / "work"
DEST_PATH = BASE_PATH / "archive"

# More staging:
for ii in range(0,3):
    os.makedirs(BASE_PATH / f"archive{ii:0>1}", exist_ok=True)
for jj in range(0,99):
    w_path:Path = Path(get_archive_location(str(BASE_PATH / "archive"), f"W{jj:0>4}"))
    os.makedirs(w_path.parent, exist_ok=True)



os.makedirs(DEST_PATH, exist_ok=True)
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(STAGING_PATH, exist_ok=True)

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
    'start_date': datetime(2024, 2, 20),
    #    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# -----------------  mocks for testing / debugging ------------------------
# Set up this copy for mock objects, because debagging is destructive
mock_downloads: [str] = [str(shutil.copy(BASE_PATH / "save-W1FPL2251.bag.zip", DOWNLOAD_PATH / "miniW1FPL2251.bag.zip"))]

mock_message: [] = [
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
                "key": "ao1060/AWSIntake.zip",
                "size": 1637,
                "eTag": "6d3e031323ff7cb9ac0613d41a67d34e",
                "versionId": "rHKK9t5p3kcbTA8vLv.bZCnNitDHjIgz",
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


def build_sync_env(execution_date) -> dict:
    """
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

    current_mnt_root: str = "Volumes" if platform.system().lower() == DARWIN_PLATFORM else "mnt"

    # DEBUG: make local while testing
    _root: Path = Path.home() / "dev" / "tmp" / "Projects" / "airflow" / "glacier_staging_to_sync" / "log"
    # _root: Path = Path("/")
    logDir: Path = _root / current_mnt_root / "processing" / "logs"
    sync_log_home: Path = logDir / "sync-logs" / job_date / job_date_time
    sync_log_file = sync_log_home / f"sync-{job_date_time}.log"
    audit_log_home: Path = logDir / "audit-test-logs" / job_date / job_date_time
    os.makedirs(sync_log_home, exist_ok=True)
    os.makedirs(audit_log_home, exist_ok=True)

    return {
        "DB_CONFIG": f"{prod_level}:~/.config/bdrc/db_apps.config",
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
        "PATH" : os.getenv("PATH")
    }
# ----------------------   airflow task declarations  -------------------------

@task
def get_restored_object_messages():
    """
    Pull a message from SQS
    :return:
    """
    import boto3

    # read from an SQS Queue
    sqs = boto3.client('sqs')

    # URL of your SQS queue
    queue_url = 'https://sqs.us-east-1.amazonaws.com/170602929106/ManifestReadyToIntake'

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All'],
        MaxNumberOfMessages=5,
        VisibilityTimeout=10,  # hide it from other consumers for 10 seconds
        WaitTimeSeconds=0
    )

    s3_records = []

    if 'Messages' in response:

        # We could receive a number of messages. Since we only process the ones that contain a certain record
        # type (REQUESTED_EVENTS)) It is required that each message ONLY contain the REQUESTED_EVENTS, because
        # we delete it if any of its records contain one of those events.
        for message in response['Messages']:
            print('Received message: {0}'.format(message['Body']))
            message = response['Messages'][0]
            records: [] = json.loads(message['Body'])['Records']

            msg_s3_records = [x for x in records if x.get("eventName") in REQUESTED_EVENTS]
            if msg_s3_records:
                s3_records.extend(msg_s3_records)
                receipt_handle = message['ReceiptHandle']
                # Now delete the message
                # sqs.delete_message(
                #    QueueUrl=queue_url,
                #    ReceiptHandle=receipt_handle
                # )
                print('Message not deleted - in DEBUG')
        else:
            print('No messages to receive')

    return mock_message
    # return s3_records

@task
def download_from_messages(s3_records) -> [Path]:
    """

    :param s3_records: object restored format
    :param kwargs: context
    :return: Nothing
    """
    import boto3

    downloaded_paths: [] = []
    from botocore.exceptions import ClientError
    for s3_record in s3_records:
        bucket: str = "unset"
        key: str = "unset"
        try:
            bucket = s3_record['s3']['bucket']['name']
            key = s3_record['s3']['object']['key']
            key += "simulate_failureHack"

            download_full_path: Path = DOWNLOAD_PATH / key
            dfp_str: str = str(download_full_path)
            os.makedirs(download_full_path.parent, exist_ok=True)

            hash = s3_record['s3']['object']['eTag']
            s3 = boto3.client('s3')
            s3.download_file(bucket, key, dfp_str)

            print(f"Downloaded S3://{bucket}/{key} to {dfp_str}")
            downloaded_paths.append(download_full_path)
        except KeyError as e:
            print(f'KeyError: {e}')
        except ClientError as e:
            print(f"Could not retrieve S3://{bucket}/{key}:  {e} ")
    else:
        print('No messages')

    return mock_downloads
    # return downloaded_paths


@task
def debag_downloads(downloads: [str]) -> [str]:
    """
    Debags each unload
    :param downloads:
    :param kwargs:
    :return: list of unbagged work archives. path object is not serializable,
    so returning strings
    """
    os.makedirs(STAGING_PATH, exist_ok=True)
    debagged: [Path] = []
    for download in downloads:
        debagged.extend([str(x) for x in bag_ops.debag(download, str(STAGING_PATH))])
    return debagged


@task
def sync_debagged(downloads: [str], **context):
    """
    Syncs each debagged work
    :param downloads:
    :param context: airflow context
    :return: None. this os tje terminal task
    """

    env:{} = build_sync_env(context['execution_date'])

    for download in downloads:
        # syncOneWork.sh [ -h ] [ -a archiveParent ] [ -w webParent ] [ -s successWorkList ] workPath
        BashOperator(
            task_id="sync_debag",
            bash_command=f"syncOneWork.sh -A -a {str(DEST_PATH)}  -s $(mktemp) {download}",
            env=env
        ).execute(context)



with DAG(
        'sqs_sensor_dag',
        default_args=default_args,
        schedule=MY_TIME_DELTA) as gs_dag:
    msgs = get_restored_object_messages()
    downloads = download_from_messages(msgs)
    to_sync = debag_downloads(downloads)
    syncd = sync_debagged(to_sync)
    #
    # POS: can't get output
    # sqs_sensor = SqsSensor(
    #     task_id='sqs_sensor_task',
    #     #     dag=dag,
    #     sqs_queue=UNGLACIERED_QUEUE_NAME,
    #     # Lets use default,
    #     # TODO: setup aws_conn_id='my_aws_conn',
    #     max_messages=10,
    #     wait_time_seconds=10,
    #     do_xcom_push=False
    # )

    # pm = PythonOperator(
    #     task_id='process_messages',
    #     python_callable=process_messages,
    #     dag=gs_dag
    # )
    #
    # sqs_sensor >> pm

# Use taskflow
# process_task = PythonOperator(
#     task_id='process_messages',
#     python_callable=process_messages,
#     provide_context=True,
#     dag=dag
# )

# sqs_sensor >> process_task
if __name__ == '__main__':
    gs_dag.test()
