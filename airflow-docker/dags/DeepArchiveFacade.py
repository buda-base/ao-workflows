#!/usr/bin/env python3
"""This is needed to simulate the main loop of archive_ops.DeepArchive
"""
from archive_ops.DeepArchiveParser import DeepArchiveArgs
import archive_ops.DeepArchive as da
from collections import namedtuple
from pathlib import Path
from staging_utils import get_db_config



# write a sqlalchemy command in the context of DrsDbContextBase that gets the results of a SQL text query
def get_dip_id(db_config: str, work_rid: str, src_folder: str):
    """
    Returns the dip_external_id for a work at a path - use the newest one
    :param db_config: full db config in the form db_handle:/path/to/config
    :param work_rid:
    :param src_folder: the source folder for the sync we are trying to deep archive. the actual destination
    is what get's deep archived, as the source is not assumed to exist on the calling machine
    :return:
    """
    from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
    from sqlalchemy import text

    with DrsDbContextBase(db_config) as ctx:
        from sqlalchemy.orm import Session
        xs: Session = ctx.get_session()
        # get the latest
        query = text("select dip_external_id from dip_activity_work where  dip_activity_types_label = 'ARCHIVE'"
                     " and WorkName = :work_rid "
                     "and dip_source_path = :src "
                     "and dip_activity_finish is not null and dip_activity_result_code = 0 "
                     "order by dip_activity_finish desc limit 1")

        # write a direct sql query in SqlAlchemy to select dip_external_id from dip_activity_work where WorkName = work_rid and SourcePath = down
        result = xs.execute(query, {'work_rid': work_rid, 'src': src_folder})
        rows = result.fetchall()
        for row in rows:
            return row[0]


args: DeepArchiveArgs = None
record_t: namedtuple = namedtuple('record', ['dip_external_id', 'WorkName', 'path'])
record: record_t = None

def setup(db_config: str, log_root: str, bucket: str, work_rid: str, src_path: Path):
    """
    This is needed to simulate the main loop of archive_ops.DeepArchive
    """

    global args
    args = DeepArchiveArgs()
    args.log_level = "info"
    args.drsDbConfig = get_db_config(db_config)
    args.incremental = True
    args.complete = False
    args.bucket = bucket
    args.log_root = log_root
    #
    # Given the work_rid and the path, get the sync's dip_id
    global record
    dip_id: str = get_dip_id(args.drsDbConfig, work_rid, src_path)
    record = record_t(dip_external_id=dip_id, WorkName=work_rid, path=src_path)
    da.setup(args)

def do_one():
    """Copied from DeepArchive:deep_archive_shell. Assumes """
    inventory_path: Path = None
    try:
        if args.incremental:
            # Get the inventory path from the database. If none, do a complete deep archive
            inventory_path = da.get_inventory_path(record.dip_external_id, args.drsDbConfig)
            if not inventory_path:
                args.complete = True
                args.incremental = False
                da._log.warn(f"No inventory found for {record.WorkName} archive record: {record.dip_external_id[:6]}...  Running complete")

        if args.complete:
            image_group_list = da.get_igs_for_invert(record.WorkName)
            da.do_deep_archive_complete(record.WorkName, Path(record.path), image_group_list, args.bucket)
        else:  # args.incremental
            da.do_deep_archive_incremental(record.WorkName, Path(record.path), inventory_path, args.bucket)
            # image_group_list = get_igs_for_invert(record.WorkName, record.path, record.dip_external_id)

        # if there was a comment, we're only doing the image groups that were designated in the comment.
        # Otherwise, segment the work into:
        # - imagegroup + media tuples to be inverted and zipped separately
        # - everything else
        da._log.info(f"Processing {record}")
    except Exception as e:
        dip_id = da.open_log_dip(record.WorkName, record.path)
        error_string: str = f"Failed to process {record=} {dip_id=} Exception {e=}"
        da._log.error(error_string)
        da.update_log_dip(dip_id, 1, error_string)

if __name__ == "__main__":
    print(get_dip_id(get_db_config('prod'), "W1NLM6833",
                     "/home/airflow/bdrc/data/work/down_scheduled_2025-02-19T20:45:00/unzip/W1NLM6833"))
