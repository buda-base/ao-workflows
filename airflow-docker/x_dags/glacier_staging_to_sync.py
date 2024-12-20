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

import shutil
import airflow.operators.bash

from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowFailException, AirflowException
from datetime import datetime, timedelta
from bag import bag_ops
from botocore.exceptions import ClientError
from util_lib.version import bdrc_util_version

from staging_utils import *

#  ------------   local types----------------------------
Download_Map = collections.namedtuple('Download_Map', ['region_name', 'bucket', 'queue_name', 'config_section_name'])
#  ------------   /local types----------------------------


# -------------  CONFIG CONST  ----------------------------

BAG_ZIP_PATTERN="*.bag.zip"

# Don't modify these unless you need to - see the next section, DEV|PROD CONFIG
#
# DB for log_dip
_PROD_DB: str = 'prod'
_DEV_DB: str = 'qa'
#
# DAG parameters

_DEV_TIME_SCHEDULE: timedelta =  timedelta(hours=6)
_DEV_DAG_START_DATE: datetime = datetime(2024, 11, 12, 11, 15)
_DEV_DAG_END_DATE: datetime = datetime(2024, 12, 8, hour=23)
_DEV_DL_PER_DAG=5


_PROD_TIME_SCHEDULE: timedelta = timedelta(minutes=15)
_PROD_DAG_START_DATE: datetime = datetime(2024, 5, 18, 17, 22)
_PROD_DAG_END_DATE: datetime = datetime(2024, 7, 8, hour=23)
_PROD_DL_PER_DAG=15

# Sync parameters
_DEV_DEST_PATH_ROOT: str = str(Path.home() / "dev" / "tmp" )
_PROD_DEST_PATH_ROOT: str = "/mnt"

# ------------- CONFIG CONST  ----------------------------

# region ------------   CONST  ----------------------------

UNGLACIERED_QUEUE_NAME: str = 'ManifestReadyToIntake'

# See AWSIntake.setup-aws.py for the queue names
# See 'deploy' for the config section names
_PROD_DOWNLOAD_MAP: [Download_Map] = [
    Download_Map('ap-northeast-2', 'glacier.staging.fpl.bdrc.org', 'FplReadyToIntake', 'ap_northeast'),
    Download_Map('ap-northeast-2', 'glacier.staging.nlm.bdrc.org', 'NlmReadyToIntake', 'ap_northeast'),
]
_DEV_DOWNLOAD_MAP: [Download_Map] = [
    Download_Map('us-east-1', 'manifest.bdrc.org', UNGLACIERED_QUEUE_NAME, 'default')
]

# For determining some file sys roots
DARWIN_PLATFORM: str = "darwin"

REQUESTED_AWS_EVENTS: [str] = ['ObjectRestore:Completed', 'ObjectCreated:*']

# our buckets and SQS queues are in these sections of the config
REQUESTED_AWS_SECTIONS: [str] = ['default', 'ap_northeast']

#  ------------   /CONST  ----------------------------

# --------------------- DEV|PROD CONFIG  ---------------
# Loads the values set in MY_.....
# Of course, you do not want to call side-effect inducing functions in setting this
# See the dev section below
DAG_TIME_DELTA: timedelta = _PROD_TIME_SCHEDULE
DAG_START_DATETIME = _PROD_DAG_START_DATE
DAG_END_DATETIME = _PROD_DAG_END_DATE
MY_DB: str = _PROD_DB
download_map: [Download_Map] = _PROD_DOWNLOAD_MAP
MY_DEST_PATH_ROOT: str = _PROD_DEST_PATH_ROOT
MY_DL_PER_DAG = _PROD_DL_PER_DAG


DAG_TIME_DELTA = _DEV_TIME_SCHEDULE
DAG_START_DATETIME = _DEV_DAG_START_DATE
DAG_END_DATETIME = _DEV_DAG_END_DATE
MY_DB = _DEV_DB
download_map = _DEV_DOWNLOAD_MAP
# OK tp leave local - $ARCH_ROOT in the .env makes this safe
# MY_DEST_PATH_ROOT = _DEV_DEST_PATH_ROOT
MY_DL_PER_DAG = _DEV_DL_PER_DAG

# --------------------- /DEV|PROD CONFIG  ---------------

# --------------- SETUP DAG    ----------------
#
# this section configures the DAG filesystem. Coordinate with bdrc-docker-compose.yml
#  scheduler:
#       ...
#       volumes:
#          ....

regional_queue_buckets: [()]
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
DEST_PATH: Path = Path(MY_DEST_PATH_ROOT, "Archive")
# Non docker
_DB_CONFIG: Path = Path.home() / ".config" / "bdrc" / "db_apps.config" if not Path.exists(
    Path("/run/secrets/db_apps")) else Path("/run/secrets/db_apps")

# select a level (used in syncing)

prod_level: str = MY_DB
# used in syncing
util_ver: str
try:
    util_ver: str = bdrc_util_version()
except:
    util_ver = "Unknown"

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


@task(retries=10, retry_delay=timedelta(hours=6))
def get_restored_object_messages():
    """
    Pull a message from SQS
    :return:
    """
    # DEBUG_DEV
    # return mock_message

    # output buffer
    s3_records: [] = []

    # read from an SQS Queue
    # map of sessions, keyed by region
    try:
        session_dict: {} = create_fetch_sessions(download_map)

        for dm_entry in download_map:
            region_name: str = dm_entry.region_name
            sqs = session_dict[region_name].client('sqs')

            queue_url = f"https://sqs.{region_name}.amazonaws.com/170602929106/{dm_entry.queue_name}"
            pp(f"Polling  {queue_url}")
            # Receive message from SQS queue
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],

                # SEVERE WARNING ALERT  YOU MUST ONLY GET 1 MESSAGE AT A TIME.
                # If there is a failure, and multiple messages are received, and one fails,
                # special code will have to be written to fetch others
                MaxNumberOfMessages=1,
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
                        # Add to log
                        for m in msg_s3_records:
                            work_rid: str = work_rid_from_aws_key( m['s3']['object']['key'])
                            db_phase(GlacierSyncOpCodes.RESTORED, work_rid, db_config=MY_DB, user_data=m)

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

    pp(f"Returning {len(s3_records)}")
    if not s3_records:
        raise AirflowException("No restore requests available")
    return s3_records



def send_retry_if(bucket: str, key: str, e: ClientError):
    """
    :param bucket:
    :param key:
    :param specific Exception
    :return:
    """
    error_code = e.response['Error']['Code']
    if error_code == 'InvalidObjectState':
        print("Caught an InvalidObjectState error")


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

            # DEBUG_DEV
            # Overwrite to simulate a failure - a key that can never appear
            # key += "simulate_failureHack"

            download_full_path: Path = DOWNLOAD_PATH / key
            dfp_str: str = str(download_full_path)
            pp(f"{download_full_path=} {dfp_str=}")
            os.makedirs(download_full_path.parent, exist_ok=True)

            s3 = get_cached_session(get_download_map_for_region(awsRegion).config_section_name).client('s3')
            # DEBUG Just keep using the same file. Externally, copy from a source
            # before a run, because debag will delete the source
            # DEBUG_DEV
            s3.download_file(bucket, key, dfp_str)
            # DEBUG_DEV
            # return [dfp_str]

            pp(f"Downloaded S3://{bucket}/{key} to {dfp_str}")
            downloaded_paths.append(dfp_str)
            # Some exceptions, trigger retry

            work_rid: str = work_rid_from_aws_key(key)
            db_phase(GlacierSyncOpCodes.DOWNLOADED, work_rid,   db_config=MY_DB, user_data={'download_path': dfp_str})

        except KeyError as e:
            err: str = f'KeyError: {e}'
            pp(err)
            raise ValueError(err)
        except ClientError as e:
            err = f"Could not retrieve S3://{bucket}/{key}:"
            pp(err)
            pp(e)
            send_retry_if(bucket, key)
            raise ValueError(err)
        # General exception fails
        except:
            import sys
            ei = sys.exc_info()
            pp(ei)
            raise AirflowFailException(str(ei[1]))

    else:
        pp('No messages')

    return downloaded_paths


@task
def get_downloads() -> [str]:
    """
    Get the list of paths that are ready to debag
    :return:
    """
    import fnmatch
    # For proof of concept, just use hardwired dir
    matches = []
    pattern = "*.bag.zip"
    pp(f"Looking for {pattern} in {DOWNLOAD_PATH}")
    for root, dirnames, filenames in os.walk(DOWNLOAD_PATH):
        pp(f"{root=} {dirnames=} {filenames=}")
        for filename in fnmatch.filter(filenames, BAG_ZIP_PATTERN):
            matches.append(os.path.join(root, filename))
    return matches[:MY_DL_PER_DAG]


@task
def debag_downloads(downs: [str]) -> [str]:
    """
    Debags each unload
    :param downs: list of downloaded files
    :return: list of **path names** of  unbagged work archives. path object is not serializable,
    so returning strings
    """
    # DEBUG_DEV
    # return ['/home/airflow/bdrc/data/work/W1NLM4700']
    os.makedirs(STAGING_PATH, exist_ok=True)
    debagged: [Path] = []

    # BUG  Not everything that gets here is a bag.
    # Fixed: in bucket event notification configuration (see AWSIntake.setup-aws.py)
    # BUG - can have multiple entries for same zip. Deduplicate

    unique_downs = list(set(downs))

    pp(unique_downs)
    pp(STAGING_PATH)

    for down in unique_downs:
        # DEBUG_DEV - bypass debagging - just use what's there
        # debagged_downs:[] = ['/home/airflow/bdrc/data/work/W1NLM4700']
        debagged_downs: [] = [str(d) for d in bag_ops.debag(down, str(STAGING_PATH))]
        debagged.extend(debagged_downs)

        # Add the bad manifest to the work to archive
        for db_down in debagged_downs:
            work_name: str = Path(db_down).stem

            # Use some secret badass knowledge about how bag_ops.debag works
            # to know that the bag_ops creates a dir "bags" under
            # STAGING_PATH, and that contains a directory named <workname>.bag
            bag_path: Path = STAGING_PATH / "bags" / f"{work_name}.bag"
            pp(f"{work_name=} {db_down=} {bag_path=}")
            shutil.move(bag_path, db_down)
            db_phase(GlacierSyncOpCodes.DEBAGGED, work_name,  db_config=MY_DB, user_data={'debagged_path': db_down})
    return debagged


@task
def sync_debagged(downs: [str], **context):
    """
    Syncs each debagged work
    :param downs:
    :param context: airflow context
    """

    # DEBUG_DEV
    # return 0
    env: {} = build_sync_env(context['execution_date'])

    pp(env)

    for download in downs:
        # Build the sync command
        # The moustaches {{}} inject a literal, not an fString resolution
        bash_command = f"""
        #!/usr/bin/env bash
        ls -l /mnt
        syncOneWork.sh -a "{str(DEST_PATH)}"  -s $(mktemp) "{download}" 2>&1 | tee $syncLogDateTimeFile
        rc=${{PIPESTATUS[0]}}
        exit $rc
        """


        airflow.operators.bash.BashOperator(
            task_id="sync_debag",
            bash_command=bash_command,
            env=env
        ).execute(context)

        # If we got here, the sync succeeded, otherwise, the task raised "fail"
        # jimk ao-workflows-24: remove the sync source
        shutil.rmtree(download)

        db_phase(GlacierSyncOpCodes.SYNCD, Path(download).stem,   db_config=MY_DB, user_data={'synced_path': download})


# Not used: but you could pass it in to DAG constructor
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

with DAG('sqs_scheduled_dag',
         schedule=DAG_TIME_DELTA,
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
         tags=['bdrc'],
         catchup=False,  # SUPER important. Catchups can confuse the Postgres DB
         # DEBUG_DEV
         # max_active_runs=1,
         # This kills when rsyncing
         # max_active_runs=4,
         max_active_runs=2,


         # Note we don't want to specify a retries argument for each/all tasks in the DAG.
         # Except for the looking for SQS messages for retry: that should retry if there are no messages.
         #
         # retries = 5,
         # retry_delay = timedelta(hours=6)

         ) as sync_dag:
    msgs = get_restored_object_messages()
    downloads = download_from_messages(msgs)
    to_sync = debag_downloads(downloads)
    sync_debagged(to_sync)

with DAG('down_scheduled_dag',
         schedule=DAG_TIME_DELTA,
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
         tags=['bdrc'],
         catchup=False,  # SUPER important. Catchups can confuse the Postgres DB
         # DEBUG_DEV
         # max_active_runs=1,
         # This kills when rsyncing
         # max_active_runs=4,
         max_active_runs=4


         # Note we don't want to specify a retries argument for each/all tasks in the DAG.
         # Except for the looking for SQS messages for retry: that should retry if there are no messages.
         #
         # retries = 5,
         # retry_delay = timedelta(hours=6)

         ) as dl_dag:
    downloads = get_downloads()
    to_sync = debag_downloads(downloads)
    sync_debagged(to_sync)

if __name__ == '__main__':
    # noinspection PyArgumentList
    dl_dag.test()
    # gs_dag.cli()
