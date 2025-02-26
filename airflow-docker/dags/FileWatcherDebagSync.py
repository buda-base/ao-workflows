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
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
# bag is in pyPI bdrc-bag
from bag import bag_ops
from pendulum import DateTime
from sqlalchemy import text

import SyncOptionBuilder as sb
from staging_utils import *

# Do Once only. Seems to survive process boundaries.
# 2025 update - this is no longer necessary. Levin in place
# You can also do this in the UI  (dac_specialAdmin -> Connections

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
SYNC_DATA_KEY: str = "synced_data"
#
# Because we use this in multiple places
WAIT_FOR_FILE_TASK_ID: str = "wait_for_file"
DEBAG_TASK_ID: str = "debag"
UNZIP_TASK_ID: str = "unzip"
SYNC_TASK_ID: str = "sync"
DEEP_ARCHIVE_TASK_ID: str = "deep_archive"

# Don't modify these unless you need to - see the next section, DEV|PROD CONFIG
#
# DB for log_dip
_PROD_DB: str = 'prod'
_DEV_DB: str = 'qa'
#
# DAG parameters

# TODO: Convert to pendulum
_DEV_TIME_SCHEDULE: timedelta = timedelta(minutes=3)
_DEV_DAG_START_DATE: DateTime = DateTime(2025, 2, 24, 11, 15)
_DEV_DAG_END_DATE: DateTime = DateTime(2025, 12, 8, hour=23)

_PROD_TIME_SCHEDULE: timedelta = timedelta(minutes=30)
_PROD_DAG_START_DATE: DateTime = DateTime(2025,2, 24, 10,45)
_PROD_DAG_END_DATE: DateTime = _PROD_DAG_START_DATE.add(months=1)

# Sync parameters
# Under docker, /mnt is linked to a local directory, not the real /mnt. See bdrc-docker-compose.yml
_DEV_DEST_PATH_ROOT: str = str(Path.home() / "dev" / "tmp") if not os.path.exists('/run/secrets') else "/mnt"
#
# Use S3Path, if we ever use this var. For now, but this layer is just passing it on
_DEV_DEEP_ARCHIVE_DEST: str = "s3://manifest.bdrc.org"
_DEV_WEB_DEST: str = f"{_DEV_DEEP_ARCHIVE_DEST}/Works"

# dev or test invariant
MY_FEEDER_HOME: Path = Path(_DEV_DEST_PATH_ROOT, "sync-transfer")

_DOCKER_DEST_PATH_ROOT: str = "/mnt"
_PROD_DEST_PATH_ROOT: str = _DOCKER_DEST_PATH_ROOT
#
# See ~/dev/archive-ops/scripts/syncAnywhere/sample.config
_PROD_WEB_DEST: str = "s3://archive.tbrc.org/Works"
_PROD_DEEP_ARCHIVE_DEST: str = "s3://glacier.archive.bdrc.org"
# ------------- CONFIG CONST  ----------------------------

# region ------------   CONST  ----------------------------

# For determining some file sys roots
DARWIN_PLATFORM: str = "darwin"
SYNC_TZ_LABEL: str = 'America/New_York'

#  ------------   /CONST  ----------------------------

# -------------   LOGGING ----------------------------
# Hope this spans tasks
LOG = logging.getLogger("airflow.task")
# --------------------- DEV|PROD CONFIG  ---------------
# Loads the values set in MY_.....
# Of course, you do not want to call side effect inducing functions in setting this
# See the dev section below
DAG_TIME_DELTA: timedelta = _PROD_TIME_SCHEDULE
DAG_START_DATETIME = _PROD_DAG_START_DATE
DAG_END_DATETIME = _PROD_DAG_START_DATE.add(weeks=2)
MY_DB: str = _PROD_DB
MY_DEST_PATH_ROOT: str = _PROD_DEST_PATH_ROOT
MY_WEB_DEST: str = _PROD_WEB_DEST
MY_DEEP_ARCHIVE_DEST: str = _PROD_DEEP_ARCHIVE_DEST

# When debugging in an IDE, always set a breakpoint here,
# just to ensure you're not running in production
# Of course, you have to set the env var PYDEV_DEBUG
# you can set it in the docker-compose.yaml, after


is_debug = os.getenv("PYDEV_DEBUG", "NO")
if is_debug == "YES":
    DAG_TIME_DELTA = _DEV_TIME_SCHEDULE
    DAG_START_DATETIME = _DEV_DAG_START_DATE
    DAG_END_DATETIME = _DEV_DAG_END_DATE
    MY_DB = _DEV_DB
    # OK to leave local - $ARCH_ROOT in the .env makes this safe
    MY_DEST_PATH_ROOT = _DEV_DEST_PATH_ROOT
    MY_WEB_DEST = _DEV_WEB_DEST
    MY_DEEP_ARCHIVE_DEST: str = _DEV_DEEP_ARCHIVE_DEST

LOG.info(f"{is_debug=}")
LOG.info(f"{DAG_TIME_DELTA=}")
LOG.info(f"{DAG_START_DATETIME=}")
LOG.info(f"{DAG_END_DATETIME=}")
LOG.info(f"{MY_DB=}")
# OK to leave MY_DEST_PATH_ROOT  local - $ARCH_ROOT in the .env makes this safe pp(f"{MY_DEST_PATH_ROOT=}")pp(f"{MY_WEB_DEST=}")
LOG.info(f"{MY_DEST_PATH_ROOT=}")
LOG.info(f"{MY_FEEDER_HOME=}")
LOG.info(f"{MY_WEB_DEST=}")
LOG.info(f"{MY_DEEP_ARCHIVE_DEST=}")

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
# Where feeder gets its work from
DOWNLOAD_PATH: Path = BASE_PATH / "Incoming"

# This was when we were local
# Bse of all processing done here
WORK_PATH = BASE_PATH / "work"

# Processing resources
#
# Feeder DAG moves files here.
READY_PATH: Path = WORK_PATH / "ready"
# wait_for_files task moves files here for them to work on
PROCESSING_PATH: Path = WORK_PATH / "in_process"

# jimk: changed preservaton task to feeder, which moves and then copies.
# feeder copies them here before destroying the original
RETENTION_PATH: Path = MY_FEEDER_HOME / "save"
# debag destination
STAGING_PATH = BASE_PATH / "work"

# This constant is both the number of instances of the sync dag, and the number of files that
# the Feeder dag needs to replenish.
SYNC_DAG_NUMBER_INSTANCES: int = 3
# Number of files that triggers the feeder dag
PROCESSING_LOW_LIMIT: int = 1
# Maximum number of files to be in the processing queue
PROCESSING_HIGH_LIMIT: int = SYNC_DAG_NUMBER_INSTANCES

READY_PATH.mkdir(parents=True, exist_ok=True)
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
STAGING_PATH.mkdir(parents=True, exist_ok=True)
PROCESSING_PATH.mkdir(parents=True, exist_ok=True)


# This value is a docker Bind Mount to a local dir - see ../airflow-docker/bdrc-docker-compose.yml
DEST_PATH: Path = Path(MY_DEST_PATH_ROOT, "Archive")

# select a level for db ops (see staging_utils.get_db_config)
prod_level: str = MY_DB


# ----------------------   /SETUP DAG      -------------------------

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


def stage_in_task(**context) -> (Path, Path):
    """
    Stages the Wait for file for unzipping
    :param context: airflow task context
    :return: tuple containing the path of the detected file, and the path to the location it is to be moved
    to for work. Creates the location it is to be moved to if it does not exist
    """

    # sanity check
    detected: str = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key=COLLECTED_FILE_KEY)
    if not detected:
        raise AirflowException("No file detected, but wait_for_file returned true")

    # Stage into
    from pendulum import DateTime
    dis: DateTime = context['data_interval_start']
    run_data_path: str = f"{context['dag'].dag_id}_{dis.in_tz('local').strftime('%Y-%m-%dT%H:%M:%S')}"
    task_id: str = context['task'].task_id

    LOG.info(f"Run ID: {run_data_path}, Task ID: {task_id}")

    staging_path: Path = Path(STAGING_PATH, run_data_path, task_id)

    empty_contents(staging_path)
    return detected, staging_path


# ----------------------   airflow task declarations  -------------------------
def _which_file(**context):
    """
    Extracts the ZIP from the bag
    :param context:
    :return: Task id of handler
    """
    # Same as in the step debag
    detected = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key=COLLECTED_FILE_KEY)

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

    # stage_in_task creates everything it returns
    detected, staging_path = stage_in_task(**context)

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
            LOG.info(f"Could not find {src_bag_path} for {work_name}")
            continue
        save_glob: str = f"*manifest*.txt"
        for fd in os.scandir(src_bag_path):
            if fd.is_file() and fnmatch.fnmatch(fd, save_glob):
                os.makedirs(dest_bag, exist_ok=True)
                target: Path = dest_bag / fd.name
                if target.exists():
                    target.unlink()
                shutil.move(fd.path, target)
        LOG.info(f"{work_name=} {db_down=} {src_bag_path=}")
        db_phase(GlacierSyncOpCodes.DEBAGGED, work_name, db_config=MY_DB, user_data={'debagged_path': str(db_down)})
    context['ti'].xcom_push(key=EXTRACTED_CONTEXT_KEY, value=[str(d.absolute()) for d in debagged_downs])


@task(retries=0)
def unzip(**context):
    """
    Unzip file into the same directory that debag would
    :param context:
    :return: pushes into context['ti'](task_id DEBAG_TASK_ID, key EXTRACTED_CONTEXT_KEY)
    """
    detected, staging_path = stage_in_task(**context)
    os.makedirs(staging_path, exist_ok=True)

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
    xcom_list:[] = []

    downs = context['ti'].xcom_pull(task_ids=[DEBAG_TASK_ID, UNZIP_TASK_ID], key=EXTRACTED_CONTEXT_KEY)
    # downs could be a list of lists, if a bag or a zip file contained multiple works
    for a_down in iter_or_return(downs):
        # need an extra layer of indirection, for multi-zip or multi-bag-entries
        for down in iter_or_return(a_down):
            work_rid: str = Path(down).stem
            env, bash_command = sb.build_sync(start_time=local_start, prod_level=MY_DB, src=down,
                                              archive_dest=DEST_PATH, web_dest=MY_WEB_DEST)
            LOG.info(f"syncing {down}")

            airflow.operators.bash.BashOperator(
                task_id="sync_debag",
                bash_command=bash_command,
                env=env
            ).execute(context)

            db_phase(GlacierSyncOpCodes.SYNCD, work_rid, db_config=MY_DB, user_data={'synced_path': down})
            # report on each syncd work
            xcom_list.append((work_rid, down))

    context['ti'].xcom_push(key=SYNC_DATA_KEY, value=xcom_list)





@task
def cleanup(**context):
    """
    Cleans up the work area that was sync'd. Of course, you only run after sync, or sync's succeeded
    """
    # Use the same paths that were input to 'sync'
    # p_to_rm: [Path] = context['ti'].xcom_pull(task_ids=DEBAG_TASK_ID, key=EXTRACTED_CONTEXT_KEY)
    p_to_rm = context['ti'].xcom_pull(task_ids=[DEBAG_TASK_ID, UNZIP_TASK_ID], key=EXTRACTED_CONTEXT_KEY)

    # aow-36 remove the collected file
    collected_file = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key=COLLECTED_FILE_KEY)
    if collected_file:
        Path(collected_file).unlink(missing_ok=True)


    # aow-36 remove the collected file
    collected_file = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key=COLLECTED_FILE_KEY)
    if collected_file:
        Path(collected_file).unlink(missing_ok=True)

    r_ip_paths: set = set()
    # remove in_process/work_name and work directory for this run id
    for a_down in iter_or_return(p_to_rm):
        for p in iter_or_return(a_down):
            # The unzipped or debagged directory is two down from the parent of all extracted
            # works in this run
            dd = Path(p).parent.parent
            r_ip_paths.add(dd)
    for r_i_p in r_ip_paths:
        LOG.info(f"removing {str(r_i_p)}")
        shutil.rmtree(r_i_p, onerror=remove_readonly)


@task
def deep_archive(**context):
    """Deep archive a sync'd work"""
    from DeepArchiveFacade import setup, do_one, get_dip_id

    # set up deep archive
    dis: DateTime = context['data_interval_start']
    da_log_path: str = f"{context['dag'].dag_id}_{dis.in_tz('local').strftime('%Y-%m-%dT%H:%M:%S')}"

    da_log_dir: Path = Path( sb.APP_LOG_ROOT, "deep-archive",  da_log_path)
    da_log_dir.mkdir(parents=True, exist_ok=True)
    # Get the sync task's pushed return data
    syncs:[] = context['ti'].xcom_pull(task_ids=SYNC_TASK_ID, key=SYNC_DATA_KEY)


    #
    # Given the work_rid and the path, get the sync's dip_id
    for sync_data in syncs:
        work_rid, down = sync_data

    # set up deep archive args
        setup(MY_DB, da_log_dir, MY_DEEP_ARCHIVE_DEST, work_rid, Path(down))
        do_one()



# DAG args for all DAGs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': DAG_START_DATETIME,
    'end_date': DAG_END_DATETIME,
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
         schedule=timedelta(minutes=10),
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
         # try using feeds settings
         default_args=default_args,
         max_active_runs=SYNC_DAG_NUMBER_INSTANCES
         ) as get_one:
    start = EmptyOperator(
        task_id='start'
    )

    wait_for_file = CollectingSingleFileSensor(
        processing_path=PROCESSING_PATH,
        task_id=WAIT_FOR_FILE_TASK_ID,
        filepath=f"{str(READY_PATH)}/{ZIP_GLOB}",
        poke_interval=10,
        mode='poke'
        # TODO: How can I avoid failures when no files for a long time?
        # timeout=3600,
        # Apparently, having this on returns true
        # mode='reschedule'
    )

    which_file = BranchPythonOperator(
        task_id='which_file',
        python_callable=_which_file)

    start >> wait_for_file >> which_file >> [debag(), unzip()] >> sync() >> deep_archive() >> cleanup()

with DAG('feeder',
         schedule=timedelta(minutes=100),
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
         default_args=default_args,
         max_active_runs=1) as feeder:
    @task
    def feed_files(src_path: Path, save_path: Path, dest_path: Path):
        """
        Replenishes the ready directory
        :return:
        """

        in_process_queue_bag_count: int = 0
        with os.scandir(dest_path) as _process:
            for _p in _process:
                if _p.is_file() and fnmatch.fnmatch(_p.name, ZIP_GLOB):
                    in_process_queue_bag_count += 1

        LOG.info(f"Looking for {ZIP_GLOB} in {dest_path=} found {in_process_queue_bag_count=} {PROCESSING_LOW_LIMIT=} "
                 f"PROCESSING_HIGH_LIMIT={PROCESSING_HIGH_LIMIT}")
        if in_process_queue_bag_count < PROCESSING_LOW_LIMIT:
            n_to_feed: int = PROCESSING_HIGH_LIMIT - in_process_queue_bag_count
            to_move: [] = []
            LOG.info(f"Looking for {ZIP_GLOB} in {src_path=}")
            with os.scandir(src_path) as _dir:
                for _d in _dir:
                    if _d.is_file() and fnmatch.fnmatch(_d.name, ZIP_GLOB):
                        to_move.append(_d.path)
                        n_to_feed -= 1
                        if n_to_feed == 0:
                            break
            # _m is str
            # Collect up the works to move. Moving and renaming them one at a time causes
            # enormous contention, because, as each one is renamed, it is automatically being unzipped
            # and syncd. So, collect them all, then move them all.
            to_copy:[] = []
            if not to_move:
                LOG.info(f"No  {ZIP_GLOB} in {src_path=}")
            else:
                save_path.mkdir( parents=True, exist_ok=True)
            for _m in to_move:
                _f = Path(_m).name
                save_f: Path = save_path / _f
                LOG.info(f"Moving {_m} to {save_f}")
                # if save_path exists, remove it
                if save_f.exists():
                    LOG.warning(f"existing sync transfer being removed: {save_f}")
                    save_f.unlink()
                LOG.info(f"Moving {_m} to {save_f}")
                shutil.move(_m, save_path)
                LOG.info(f"Moved.")
                to_copy.append((save_f, dest_path / _f))
        else:
            LOG.info("No need to feed")

        atomic_copy(to_copy)


    feed_files(MY_FEEDER_HOME, RETENTION_PATH,  READY_PATH)


if __name__ == '__main__':
    pass
    # noinspection PyArgumentList


    feeder.test()
    # get_one.test()
    # gs_dag.cli()
