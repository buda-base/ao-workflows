"""
These are outside of the dags. These are one-time routines that use GlacierSyncProgress
"""
import argparse
import csv
from pprint import pp
# dont add to docker
# from tqdm import tqdm
from time import sleep

import boto3
import pendulum
from sqlalchemy import true
from sqlalchemy.future import Engine
from BdrcDbLib.SqlAlchemy_get_or_create import get_or_create

from GlacierSyncProgress import GlacierSyncProgress
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from sqlalchemy.orm.exc import NoResultFound


def make_a_glacier_sync_progress():
    """
    Strictly for first article testing. No use in production
    :return:
    """
    import pendulum
    import random
    o_id = int(divmod(random.random() * 100, 100)[1])
    # object_name: str = str(o_id)
    object_name: str = 'ud = dict'

    ud_list_data: [] = [{'d1k1': 'd1v1', 'd1k2': 'd1v2'}, {'d2k1': 'd2v1', 'd2k2': 'd2v2'}]
    ud_dict_data: {} = {'d1k1': 'd1v1', 'd1k2': 'd1v2', 'd2k1': 'd2v1', 'd2k2': 'd2v2'}

    with DrsDbContextBase() as drs:
        sess = drs.get_session()
        try:
            gsp = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == object_name).one()
        except NoResultFound:
            gsp = GlacierSyncProgress()
            gsp.object_name = object_name
            gsp.update_user_data(pendulum.now().to_rfc3339_string(), ud_dict_data)
            sess.add(gsp)
            sess.commit()
        gsp.update_user_data(pendulum.now().to_rfc3339_string(),
                             {f'd{o_id}k1': f'd{o_id}v1', f'd{o_id}k2': f'd{o_id}v2'})
        sess.commit()


def glacier_sync_catchup():
    """
    Transform all the syncs done by airflow into GlacierSyncProgress records
    :return:
    """
    done_already: [] = ['W1NLM4700', 'W1NLM4800', 'W1NLM4900', 'W1NLM5000', 'W1NLM5100', 'W1NLM5300', 'W1NLM5400',
                        'W1NLM5500', 'W1NLM5800', 'W1NLM7363']
    with DrsDbContextBase() as drs:
        sess = drs.get_session()
        for work in done_already:
            sleep(1)
            import pendulum
            xnow = pendulum.now()
            gsp = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work).one()
            gsp.restore_complete_on = xnow
            gsp.download_complete_on = xnow
            gsp.debag_complete_on = xnow
            gsp.sync_complete_on = xnow
            gsp.update_user_data(xnow.to_rfc3339_string(), {'work_rid': work, 'provider': 'manual'})
            sess.add(gsp)
            sess.commit()
            print(f"{work} done")


def add_works_to_project():
    """
    read a list from a csv and add them to the GlacierSyncProgress table, with NO activities logged
    :return:
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('work_list',
                    help='a csv file with a list of works, and AWS path info to add to the GlacierSyncProgress table',
                    type=argparse.FileType('r'))

    args = ap.parse_args()
    with args.work_list as f:
        csvr = csv.reader(f)
        with DrsDbContextBase('qa:~/.config/bdrc/db_apps.config') as drs:
            sess = drs.get_session()

            # Open a csv reader from f
            # read each line and add it to the GlacierSyncProgress table
            for row in csvr:
                work = row[0]
                aws_s3_bucket = row[1]
                aws_s3_key = row[2]
                # gsp = drs.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work).one()
                gsp = get_gsp(work, sess)
                _aws_path_data = gsp.user_data
                gsp.update_user_data(pendulum.now().to_rfc3339_string(),
                                     {'aws_s3_bucket': aws_s3_bucket, 'aws_s3_key': aws_s3_key})
                sess.add(gsp)
                iadd += 1
                if iadd % 10 == 0:
                    sess.commit()
                    iadd = 0


def get_gsp(object_name: str, drs_session) -> GlacierSyncProgress:
    """
    retrieve or create a GlacierSyncProgress record
    :param object_name:
    :param drs_session: drs db context session
    :return: newly created or existing record.
    """

    #
    # required to construct, might not be given in input
    defaults = {"user_data": [{}]}
    o, newly_made = get_or_create(drs_session, GlacierSyncProgress, defaults, object_name=object_name)
    if newly_made:
        pp(f"Newly made {object_name}")
        pp(o)
        drs_session.commit()
    return o


def get_user_data(k: str, data: []) -> str:
    """
    get user data for a key, if it exists
    :param k: search key
    :param data: list of dicts
    :return:
    """
    _user_data = lambda k, data: [b['user_data'][k] for b in data if k in b['user_data']]
    _ud = _user_data(k, data)
    return _ud[0] if _ud else ""


def work_restore_request(gsp_object_key: str, db_session: object, s3_client: boto3.client):
    """
    Do one work restore request, with handling
    :param gsp_object_key:
    :param db_session:
    :param s3_client:
    :return:
    """
    try:
        gsp = get_gsp(gsp_object_key, db_session)
        # gsp = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work
        #                                              ).filter(
        #     GlacierSyncProgress.restore_requested_on == None).one()
        _aws_path_data = gsp.user_data

        if len(_aws_path_data) == 1 and not _aws_path_data[0]:
            pp(f"{gsp_object_key} has no aws path data. Skipping")
            pp(gsp, indent=4, sort_dicts=True, width=80)
            return

        # The user data we're looking for is:
        # [
        #   {'user_data':
        #       {'aws_s3_key': 'Archive0/00/W1FPL11000/W1FPL11000.bag.zip', 'aws_s3_bucket': 'glacier.staging.fpl.bdrc.org'},
        #    'time_stamp': '2024-05-13T15:25:56.717146-04:00'
        #    }
        # ]

        aws_s3_bucket = get_user_data('aws_s3_bucket', gsp.user_data)
        aws_s3_key = get_user_data('aws_s3_key', gsp.user_data)

        if not aws_s3_bucket or not aws_s3_key:
            pp(f"{gsp_object_key} has no aws path data. Skipping")
            pp(gsp.user_data, indent=4, sort_dicts=True, width=80)
            return

        # jimk: raise days to 14, which is how long the notification persists
        from botocore.exceptions import ClientError
        try:
            restore_data = s3_client.restore_object(Bucket=aws_s3_bucket, Key=aws_s3_key,
                                                    RestoreRequest={'Days': 14,
                                                                    'GlacierJobParameters': {
                                                                        'Tier': 'Standard'}})
            gsp.restore_requested_on = pendulum.now()
            gsp.restore_complete_on = None
            gsp.update_user_data(pendulum.now().to_rfc3339_string(),
                                 {'restore_request_results': restore_data})
            db_session.commit()
        except ClientError as e:
            if e.response['Error']['Code'] == 'RestoreAlreadyInProgress':
                print(f"{gsp_object_key} restore already in progress. Skipping and continuing")
            else:
                raise e
    except NoResultFound:
        print(f"{gsp_object_key} not found or already requested in GlacierSyncProgress")


def get_unbegun_fpl_two_ups(engine: Engine, n_get: int):
    """
    Get the two up work rids for FPL
    :param engine:
    :param db_session:
    :return:
    """
    # sql = """
    # select distinct work_rid from work where work_rid like 'W1FPL2%' order by work_rid
    # """
    # with engine.connect() as conn:
    #     res = conn.execute(sql)
    #     for row in res:
    #         print(row[0])

    from sqlalchemy import MetaData, Table, select, or_, and_
    from sqlalchemy.dialects import mysql
    metadata = MetaData()

    with engine.connect() as connection:
        table = Table('glacier_sync_progress', metadata, autoload_with=engine)

        stmt = select(table.c.object_name).where((table.c.object_name.op('REGEXP')('W1FPL2[8-9].*')
                                   | table.c.object_name.op('REGEXP')('W1FPL3[0-7].*'))
                                   & (table.c.restore_requested_on.is_(None) )
                                   ).limit(n_get)
        print(stmt.compile(dialect=mysql.dialect()))
        result = connection.execute(stmt)
        outr:[] = []
        for row in result:
            outr.append(row[0])
        return outr



# find GlacierSyncProgress records that have not had their restore requested
def unbegun_restore_requests():
    """
    Emits restore requests for a number of GlacierSyncProgress records in -n/--num-restores
    :return:
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--num-restores',
                    help='number of works to restore (should be processable in 14 days)',
                    type=int, default=10)
    args = ap.parse_args()
    s3 = boto3.client('s3')
    with DrsDbContextBase('testprod:~/.config/bdrc/db_unit_test.config') as drs:
        sess = drs.get_session()

        # this stanza gets them all
        # gsp = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.restore_requested_on == None).limit(
        #     args.num_restores)
        # for g in gsp:
        #     print(g.object_name)
        works_to_restore:[] = get_unbegun_fpl_two_ups(drs.get_engine(), args.num_restores)
        # from functools import partial
        # emit_restore_work = partial(work_restore_request, db_session=sess, s3_client=s3)
        # result = map(emit_restore_work, works_to_restore)
        # pp(result)
        for work in works_to_restore:
            work_restore_request(work, sess, s3)


def launch_restore_request():
    """
    Get n unrestored from args --work_list file, don't get from list
    :return:
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('work_list', help='a csv file with no header, containing a list of work RIDs to restore',
                    type=argparse.FileType('r'))

    args = ap.parse_args()
    s3 = boto3.client('s3')
    with args.work_list as f:
        csvr = csv.reader(f)
        with DrsDbContextBase('prodsa:~/.config/bdrc/db_apps.config') as drs:
            sess = drs.get_session()
            for row in csvr:
                work = row[0]
                work_restore_request(work, sess, s3)


def launch_restore_on_command():
    """
    Get specific works from the command line 'extras.py W1FPL28000 W1FPL28001 ...'
    :return:
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('work_list', help='space separated list of work RIDs to restore',
                    type=str, nargs='+')

    args = ap.parse_args()
    s3 = boto3.client('s3')
    with DrsDbContextBase('prodsa:~/.config/bdrc/db_apps.config') as drs:
        sess = drs.get_session()
        for work in args.work_list:
            work_restore_request(work, sess, s3)

if __name__ == '__main__':
    # add_works_to_project()
    # launch_restore_request()
    unbegun_restore_requests()
    # launch_restore_on_command()
