#!/usr/bin/env python3
"""
Parallelism is at the DAG level in airflow, so create a DAG that watches for file existence, then debags and syncs it
**without** removing the debagged file.

The FileSensor operator can block until a file is available, so we can start 'n' DAGS and then just dump a bunch of
files into the working area.
Since we're event based, there's no need for an external process to track files that are in progress, or move them from
an "in process" to a "done" bucket.

The names of the directories that represent the stages are:
DOWNLOAD_PATH: Where the files live before they are processed
PROCESSING_PATH: Where the files are moved to when they are in the queue to be processed.

"""

import fnmatch
# This is really stupid. SqlAlchemy can't import a pendulum.duration, so I have
# to drop back to datetime.timedelta
from datetime import timedelta
from typing import Union, List

import airflow.operators.bash
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from bag import bag_ops
from pendulum import DateTime, Timezone
from util_lib.version import bdrc_util_version

import SyncOptionBuilder as sb
from staging_utils import *

# Do Once only. Seems to survive process boundaries.
# You can also do this in the UI  (Admin -> Connections

# from airflow import settings
# from airflow.models import Connection
#
# # Create a new Connection object
# new_connection = Connection(
#     conn_id='incoming_conn_id',
#     conn_type='fs',
#     extra='{"path": "/Users/jimk/bdrc/data/Incoming"}'
# )

# session = settings.Session()
# session.add(new_connection)
# session.commit()
# session.close()
#

# -------------  CONFIG CONST  ----------------------------

ZIP_GLOB = "*.zip"
BAG_ZIP_GLOB = "*.bag.zip"
EXTRACTED_CONTEXT_KEY: str = "extracted_works"
#
# Because we use this in multiple places
DEBAG_TASK_ID: str = "debag"
UNZIP_TASK_ID: str = "unzip"
WAIT_FOR_FILE_TASK_ID: str = "wait_for_file"

# Don't modify these unless you need to - see the next section, DEV|PROD CONFIG
#
# DB for log_dip
_PROD_DB: str = 'prod'
_DEV_DB: str = 'qa'
#
# DAG parameters

# TODO: Convert to pendulum
_DEV_TIME_SCHEDULE: timedelta = timedelta(minutes=3)
_DEV_DAG_START_DATE: DateTime = DateTime(2025, 1, 12, 11, 15)
_DEV_DAG_END_DATE: DateTime = DateTime(2025, 12, 8, hour=23)

_PROD_TIME_SCHEDULE: timedelta = timedelta(minutes=15)
_PROD_DAG_START_DATE: DateTime = DateTime(2024, 11, 24, 14, 22)
_PROD_DAG_END_DATE: DateTime = _PROD_DAG_START_DATE.add(weeks=1)

# Sync parameters
_DEV_DEST_PATH_ROOT: str = str(Path.home() / "dev" / "tmp")
_DOCKER_DEST_PATH_ROOT: str = "/mnt"
_PROD_DEST_PATH_ROOT: str = _DOCKER_DEST_PATH_ROOT

# SYNC config
#
# Use this file if it is under the Work root
DEFAULT_SYNC_YAML_PATH: Path = Path("config", "sync.yml")
DEFAULT_SYNC_YAML: str = """
audit:
    # Empty means run all tests
    # Fill in with python array: [ 'test1','test2' ...]
    pre: []
    post: []
sync:
    archive: true
    web: true
    replace: false
"""

# ------------- CONFIG CONST  ----------------------------

# region ------------   CONST  ----------------------------

# For determining some file sys roots
DARWIN_PLATFORM: str = "darwin"
SYNC_TZ_LABEL: str = 'America/New_York'

#  ------------   /CONST  ----------------------------

# --------------------- DEV|PROD CONFIG  ---------------
# Loads the values set in MY_.....
# Of course, you do not want to call side effect inducing functions in setting this
# See the dev section below
DAG_TIME_DELTA: timedelta = _PROD_TIME_SCHEDULE
DAG_START_DATETIME = _PROD_DAG_START_DATE
DAG_END_DATETIME = _PROD_DAG_START_DATE.add(weeks=2)
MY_DB: str = _PROD_DB
MY_DEST_PATH_ROOT: str = _PROD_DEST_PATH_ROOT

DAG_TIME_DELTA = _DEV_TIME_SCHEDULE
DAG_START_DATETIME = _DEV_DAG_START_DATE
DAG_END_DATETIME = _DEV_DAG_END_DATE
MY_DB = _DEV_DB
# OK to leave local - $ARCH_ROOT in the .env makes this safe
MY_DEST_PATH_ROOT = _DEV_DEST_PATH_ROOT

# --------------------- /DEV|PROD CONFIG  ---------------

# --------------- SETUP DAG    ----------------
#
# this section configures the DAG filesystem. Coordinate with bdrc-docker-compose.yml
#  scheduler:
#       ...
#       volumes:
#          ....

#
# Use an environment variable to set the base path
# See docker-compose.yml for the roots/home/a
#
BASE_PATH = Path.home() / "bdrc" / "data"
# This was when we were local
DOWNLOAD_PATH: Path = BASE_PATH / "Incoming"

# Processing resources
#
# Feeder DAG moves files here.
READY_PATH: Path = DOWNLOAD_PATH / "ready"
# wait_for_files task moves files here for them to work on
PROCESSING_PATH: Path = DOWNLOAD_PATH / "in_process"
# debag copies them here before destroying the original
RETENTION_PATH: Path = DOWNLOAD_PATH / "save"
# debag destination
STAGING_PATH = BASE_PATH / "work"

# Number of files that triggers the feeder dag
PROCESSING_LOW_LIMIT: int = 2
# Maximum number of files to be in the processing queue
PROCESSING_HIGH_LIMIT: int = 20

os.makedirs(READY_PATH, exist_ok=True)
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(STAGING_PATH, exist_ok=True)
os.makedirs(PROCESSING_PATH, exist_ok=True)
os.makedirs(RETENTION_PATH, exist_ok=True)

# See docker-compose.yml for the location of the system logs. Should be a bind mount point
# ./bdr.log:/mnt/processing/logs
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
# noinspection PyBroadException
try:
    util_ver: str = bdrc_util_version()
except:
    util_ver = "Unknown"


def add_if_work(unz: Path, works: [Path]) -> None:
    """
    Add a directory to an output buffer it contains a work structure
    :param unz:
    :param works:
    :return:
    """
    if WorkStructureVersion.detect_work(unz) >= WorkStructureVersion.V1:
        works.append(unz)
    else:
        for subdir in os.scandir(unz):
            # Transform dirEntry into Path
            if subdir.is_dir() and WorkStructureVersion.detect_work(Path(subdir)) >= WorkStructureVersion.V1:
                # transform a dir entry into a Path
                works.append(Path(subdir))


# Write a method that can take either a list of Paths or a single PathLike parameter
# and return a list of Paths
def get_extract_downs(unzipped: Union[List[Path], os.PathLike]) -> [Path]:
    """
    the input directory is the result of either an unzip or a debag operation.
    Test its structure, to see if it is:
    - a work,
    - a parent of one or more work
    :param unzipped: List of unzipped directories
    :return:
    """
    # if unzipped is a list, iterate over it, else operate on it
    works: [Path] = []
    for unz in iter_or_return(unzipped):
        # If the directory contains a 'work' directory, then this is a parent directory
        # of one or more works. We need to return the list of works
        add_if_work(unz, works)
    return works


def stage(detected) -> Path:
    """
    put the input article into the staging path
    :param detected:
    :return:
    """
    pp(f"Copying {detected} to {RETENTION_PATH}. Using {STAGING_PATH} as the staging area")
    shutil.copy(detected, RETENTION_PATH)
    #    pp(f"Copied {detected} to {RETENTION_PATH}. Using {STAGING_PATH} as the staging area")
    os.makedirs(STAGING_PATH, exist_ok=True)
    return STAGING_PATH


def build_sync_env(execution_date) -> dict:
    """
    See sync task
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
def _which_file(**context):
    """
    Extracts the ZIP from the bag
    :param context:
    :return: Task id of handler
    """
    # Same as in the step debag
    detected = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key='collected_file')

    if fnmatch.fnmatch(detected, BAG_ZIP_GLOB):
        return DEBAG_TASK_ID
    else:
        return UNZIP_TASK_ID


@task(retries=0)
def debag(**context) -> [str]:
    """
    Saves each download, then debags it
    :return: list of **path names** of  unbagged work archives
    so returning strings
    """

    # DEBUG_DEV
    # return ["/home/airflow/bdrc/data/work/W1NLM4700"]
    # Get the file
    detected = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key='collected_file')

    # TODO: Figure out why FileSensor returns empty
    if not detected:
        raise AirflowException("No file detected, but wait_for_file returned true")
    staging_path: Path = stage(detected)
    empty_contents(staging_path)

    # Remove any contents of staging_path
    # Debag returns [pathlib.Path] - supports multiple works per bag
    debagged_downs = bag_ops.debag(detected, str(staging_path))

    # Get a list of all the possible works that could be in the debagged directory.
    debagged_downs = get_extract_downs(debagged_downs)
    # Use some secret badass knowledge about how bag_ops.debag works
    # to know that the bag_ops creates a dir "bags" under
    # STAGING_PATH, and that contains a directory named <workname>.bag
    # We want to copy some data in the bag into the work to sync.
    # Add the bag description to the archive that is to be sync'd
    #
    # In the case of a multi-work bag, the bag_ops.debag treats all the works
    # in a bag as a unitary bag, which makes it impossible to separate out the bags
    # for each work.
    #
    # This turns out to be problematic for future bagging, because debag sees
    # Work/Work.bag as a bag, but without any contents in the 'data/'
    # so only copy the manifest and tag files
    for db_down in debagged_downs:
        work_name: str = Path(db_down).stem
        bag_target: str = f"{work_name}.bag"
        dest_bag: Path = db_down / bag_target
        src_bag_path: Path = staging_path / "bags" / bag_target
        if not os.path.exists(src_bag_path):
            pp(f"Could not find {src_bag_path} for {work_name}")
            continue
        save_glob: str = f"*manifest*.txt"
        for fd in os.scandir(src_bag_path):
            if fd.is_file() and fnmatch.fnmatch(fd, save_glob):
                os.makedirs(dest_bag, exist_ok=True)
                target: Path = dest_bag / fd.name
                if target.exists():
                    target.unlink()
                shutil.move(fd.path, target)
        pp(f"{work_name=} {db_down=} {src_bag_path=}")
        db_phase(GlacierSyncOpCodes.DEBAGGED, work_name, db_config=MY_DB, user_data={'debagged_path': str(db_down)})
    context['ti'].xcom_push(key=EXTRACTED_CONTEXT_KEY, value=[str(d.absolute()) for d in debagged_downs])


@task(retries=0)
def unzip(**context):
    """
    Unzip file into the same directory that debag would
    :param context:
    :return: pushes into context['ti'](task_id DEBAG_TASK_ID, key EXTRACTED_CONTEXT_KEY)
    """
    detected = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key='collected_file')

    # TODO: Figure out why FileSensor returns empty
    if not detected:
        raise AirflowException("No file detected, but wait_for_file returned true")
    staging_path: Path = stage(detected)

    try:
        # Unzip detected into STAGING_PATH
        import zipfile
        with zipfile.ZipFile(detected, 'r') as z:
            z.extractall(staging_path)

        staging_paths: [Path] = get_extract_downs(staging_path)
        context['ti'].xcom_push(key=EXTRACTED_CONTEXT_KEY, value=[str(sp.absolute()) for sp in staging_paths])
    except Exception as e:
        raise AirflowException(f"Error unzipping {detected}: {str(e)}")


# Downstream of a branching operator
@task(retries=0, trigger_rule='none_failed')
def sync(**context):
    """
    Syncs each work in a bag.
    :param context: airflow context
    """
    from pendulum import DateTime
    # DEBUG_DEV
    # return 0
    utc_start: DateTime = context['data_interval_start']
    local_start: DateTime = utc_start.in_tz(SYNC_TZ_LABEL)

    downs = context['ti'].xcom_pull(task_ids=[DEBAG_TASK_ID, UNZIP_TASK_ID], key=EXTRACTED_CONTEXT_KEY)

    env: {} = build_sync_env(local_start)

    pp(env)

    pp(downs)
    # downs could be a list of lists, if a bag or a zip file contained multiple works
    for a_down in iter_or_return(downs):
        # need an extra layer of indirection, for multi-zip or multi-bag-entries
        for down in iter_or_return(a_down):
            directives_dict = sb.get_sync_options(Path(down, DEFAULT_SYNC_YAML_PATH), DEFAULT_SYNC_YAML)
            # Build the sync command
            # The moustaches {{}} inject a literal, not an fString resolution
            bash_command = f"""
            #!/usr/bin/env bash
            set -vx
            which syncOneWork.sh
            echo $PATH
            syncOneWork.sh -a "{str(DEST_PATH)}"  -s $(mktemp) "{down}" 2>&1 | tee $syncLogDateTimeFile
            rc=${{PIPESTATUS[0]}}
            exit $rc
            """

            airflow.operators.bash.BashOperator(
                task_id="sync_debag",
                bash_command=bash_command,
                env=env
            ).execute(context)

            db_phase(GlacierSyncOpCodes.SYNCD, Path(down).stem, db_config=MY_DB, user_data={'synced_path': down})


@task
def cleanup(**context):
    """
    Cleans up the work area that was sync'd. Of course, you only run after sync has succeeded
    """
    # Use the same paths that were input to 'sync'
    # p_to_rm: [Path] = context['ti'].xcom_pull(task_ids=DEBAG_TASK_ID, key=EXTRACTED_CONTEXT_KEY)
    p_to_rm = context['ti'].xcom_pull(task_ids=[DEBAG_TASK_ID, UNZIP_TASK_ID], key=EXTRACTED_CONTEXT_KEY)

    for a_down in iter_or_return(p_to_rm):
        # need an extra layer of indirection, for multi-zip or multi-bag-entries
        for p in iter_or_return(a_down):
            pp(f"removing {str(p)}")
            shutil.rmtree(p)


# DAG args for all DAGs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    #    'start_date': DateTime(2024, 2, 20),
    #    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    # Noisy in debug. Different dags will have to handle their own way.
    # 'retries': 22,
    # 'retry_delay': timedelta(minutes=1),
    'catchup': False
}

with DAG('down_scheduled',
         # These are for rapid file testing
         schedule=timedelta(seconds=30),
         start_date=DateTime(2024, 11, 21, 15, 30, tzinfo=Timezone('America/New_York')),
         end_date=DAG_END_DATETIME,
         tags=['bdrc'],
         catchup=False,  # SUPER important. Catchups can confuse the Postgres DB
         default_args=default_args,
         max_active_runs=6
         ) as get_one:
    start = EmptyOperator(
        task_id='start'
    )

    wait_for_file = CollectingSingleFileSensor(
        processing_path=PROCESSING_PATH,
        task_id=WAIT_FOR_FILE_TASK_ID,
        filepath=f"{str(READY_PATH)}/{ZIP_GLOB}",
        poke_interval=10,
        # Needed for fs? timeout=5,
        # Apparently, having this on returns true
        # mode='reschedule'
    )

    which_file = BranchPythonOperator(
        task_id='which_file',
        python_callable=_which_file)

    start >> wait_for_file >> which_file >> [debag(), unzip()] >> sync() >> cleanup()

with DAG('feeder',
         schedule=timedelta(hours=2),
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
         tags=['bdrc'],
         catchup=False,  # SUPER important. Catchups can confuse the Postgres DB
         default_args=default_args,
         max_active_runs=1) as feeder:
    @task
    def feed_files(src_path: Path, dest_path: Path):
        """
        Replenishes the ready directory
        :return:
        """

        in_process_queue_bag_count: int = 0
        with os.scandir(dest_path) as _process:
            for _p in _process:
                if _p.is_file() and fnmatch.fnmatch(_p.name, ZIP_GLOB):
                    in_process_queue_bag_count += 1

        pp(f"Looking for {ZIP_GLOB} in {dest_path=} found {in_process_queue_bag_count=} {PROCESSING_LOW_LIMIT=} "
           f"PROCESSING_HIGH_LIMIT={PROCESSING_HIGH_LIMIT}")
        if in_process_queue_bag_count < PROCESSING_LOW_LIMIT:
            n_to_feed: int = PROCESSING_HIGH_LIMIT - in_process_queue_bag_count
            to_move: [] = []
            with os.scandir(src_path) as _dir:
                for _d in _dir:
                    if _d.is_file() and fnmatch.fnmatch(_d.name, ZIP_GLOB):
                        to_move.append(_d.path)
                        n_to_feed -= 1
                        if n_to_feed == 0:
                            break
            # _m is str
            for _m in to_move:
                pp(f"Moving {_m} to {dest_path}/{Path(_m).name}")
                shutil.move(_m, dest_path)
        else:
            pp("No need to feed")


    feed_files(DOWNLOAD_PATH, READY_PATH)

if __name__ == '__main__':
    # noinspection PyArgumentList
    # feeder.test()

    test_yaml = """
    
    """
    get_one.test()
    # gs_dag.cli()
