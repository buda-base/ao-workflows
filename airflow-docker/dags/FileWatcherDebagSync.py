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
import logging

import airflow.operators.bash
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from bag import bag_ops
from pendulum import DateTime, Timezone

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
_DEV_DAG_START_DATE: DateTime = DateTime(2025, 2, 7, 16, 15)
_DEV_DAG_END_DATE: DateTime = DateTime(2025, 12, 8, hour=23)

_PROD_TIME_SCHEDULE: timedelta = timedelta(minutes=15)
_PROD_DAG_START_DATE: DateTime = DateTime(2024, 11, 24, 14, 22)
_PROD_DAG_END_DATE: DateTime = _PROD_DAG_START_DATE.add(weeks=1)

# Sync parameters
# Under docker, /mnt is linked to a local directory, not the real /mnt. See bdrc-docker-compose.yml
_DEV_DEST_PATH_ROOT: str = str(Path.home() / "dev" / "tmp") if not os.path.exists('/run/secrets') else "/mnt"
#
# Use S3Path, if we ever use this var. For now, but this layer is just passing it on
_DEV_WEB_DEST: str = "s3://manifest.bdrc.org/Works"

_DOCKER_DEST_PATH_ROOT: str = "/mnt"
_PROD_DEST_PATH_ROOT: str = _DOCKER_DEST_PATH_ROOT
#
# See ~/dev/archive-ops/scripts/syncAnywhere/sample.config
_PROD_WEB_DEST: str = "s3://archive.tbrc.org/Works"

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

# When debugging in an IDE, always set a breakpoint here,
# just to ensure you're not running in production
# Of course, you have to set the env var PYDEV_DEBUG
# you can set it in the docker-compose.yaml, after


is_debug=os.getenv("PYDEV_DEBUG","NO")
if is_debug == "YES":
    DAG_TIME_DELTA = _DEV_TIME_SCHEDULE
    DAG_START_DATETIME = _DEV_DAG_START_DATE
    DAG_END_DATETIME = _DEV_DAG_END_DATE
    MY_DB = _DEV_DB
    # OK to leave local - $ARCH_ROOT in the .env makes this safe
    MY_DEST_PATH_ROOT = _DEV_DEST_PATH_ROOT
    MY_WEB_DEST = _DEV_WEB_DEST

LOG.info(f"{is_debug=}")
LOG.info(f"{DAG_TIME_DELTA=}")
LOG.info(f"{DAG_START_DATETIME=}")
LOG.info(f"{DAG_END_DATETIME=}")
LOG.info(f"{MY_DB=}")
LOG.info(f"{MY_DEST_PATH_ROOT=}")
LOG.info(f"{MY_WEB_DEST=}")
    # OK to leave local - $ARCH_ROOT in the .env makes this safepp(f"{MY_DEST_PATH_ROOT=}")pp(f"{MY_WEB_DEST=}")

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
    Stages the Wait for file file for unzipping
    :param context: airflow task context
    :return:
    """
    run_id_path: str = pathable_airflow_run_id(context['run_id'])
    task_id: str = context['task'].task_id

    LOG.info(f"Run ID: {run_id_path}, Task ID: {task_id}")

    detected: str = context['ti'].xcom_pull(task_ids=WAIT_FOR_FILE_TASK_ID, key='collected_file')
    # TODO: Figure out why FileSensor returns empty
    if not detected:
        raise AirflowException("No file detected, but wait_for_file returned true")
    staging_path: Path = Path(STAGING_PATH, run_id_path, task_id)
    LOG.info(f"Copying incoming {detected} to {RETENTION_PATH}. Using {staging_path} as the staging area")
    shutil.copy(detected, RETENTION_PATH)

    empty_contents(staging_path)
    return detected, staging_path


def stage(detected, RETENTION_PATH: Path) -> Path:
    """
    put the input article into the staging path
    :param detected: to move
    :param RETENTION_PATH: destination
    :return:
    """
    #    LOG.info(f"Copied {detected} to {RETENTION_PATH}. Using {STAGING_PATH} as the staging area")
    os.makedirs(STAGING_PATH, exist_ok=True)
    return STAGING_PATH


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

    detected, staging_path = stage_in_task(**context)
    os.makedirs(staging_path, exist_ok=True)

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
    
    downs = context['ti'].xcom_pull(task_ids=[DEBAG_TASK_ID, UNZIP_TASK_ID], key=EXTRACTED_CONTEXT_KEY)
    # downs could be a list of lists, if a bag or a zip file contained multiple works
    for a_down in iter_or_return(downs):
        # need an extra layer of indirection, for multi-zip or multi-bag-entries
        for down in iter_or_return(a_down):
            env, bash_command = sb.build_sync(start_time=local_start, prod_level=MY_DB, src=down,
                                              archive_dest=DEST_PATH, web_dest=MY_WEB_DEST)
            LOG.info(f"syncing {down}")

            airflow.operators.bash.BashOperator(
                    task_id="sync_debag",
                    bash_command=bash_command,
                    env=env
                ).execute(context)

            db_phase(GlacierSyncOpCodes.SYNCD, Path(down).stem, db_config=MY_DB, user_data={'synced_path': down})

# Github Copilot suggestion to get around "directory not empty" error

def remove_readonly(func, path, _):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


def pathable_airflow_run_id(possible: str) -> str:
    """
    transforms a run if into a path that can be used in a shell, by removing characters which could be operands
    :param possible:
    :return: the predecessor of any "+" in the strin
    """
    return possible.replace("+", "Z" )


@task
def cleanup(**context):
    """
    Cleans up the work area that was sync'd. Of course, you only run after sync, or sync's succeeded
    """
    # Use the same paths that were input to 'sync'
    # p_to_rm: [Path] = context['ti'].xcom_pull(task_ids=DEBAG_TASK_ID, key=EXTRACTED_CONTEXT_KEY)
    p_to_rm = context['ti'].xcom_pull(task_ids=[DEBAG_TASK_ID, UNZIP_TASK_ID], key=EXTRACTED_CONTEXT_KEY)
    run_id = pathable_airflow_run_id(context['run_id'])

    # deduplicate
    run_id_paths: set = set()

    for a_down in iter_or_return(p_to_rm):
        for p in iter_or_return(a_down):
            # Find the run id, if it is in the path
            dd = Path(p)
            if run_id in dd.parts:
                while dd.name != run_id:
                    dd = dd.parent
            run_id_paths.add(dd)
    for r_i_p in run_id_paths:
        LOG.info(f"removing {str(r_i_p)}")
        shutil.rmtree(r_i_p,onerror=remove_readonly)



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
         schedule=timedelta(minutes=1),
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
         # try using feeds settings
         default_args=default_args,
         max_active_runs=5
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

    start >> wait_for_file >> which_file >> [debag(), unzip()] >> sync() >> cleanup()

with DAG('feeder',
         schedule=timedelta(minutes=3),
         # schedule=timedelta(minutes=3),
         start_date=DAG_START_DATETIME,
         end_date=DAG_END_DATETIME,
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
            if not to_move:
                LOG.info(f"No  {ZIP_GLOB} in {src_path=}")
            for _m in to_move:
                LOG.info(f"Moving {_m} to {dest_path}/{Path(_m).name}")
                shutil.move(_m, dest_path)
        else:
            LOG.info("No need to feed")

    feed_files(DOWNLOAD_PATH, READY_PATH)

if __name__ == '__main__':
    # noinspection PyArgumentList
    # feeder.test()

    get_one.test()
    # gs_dag.cli()
