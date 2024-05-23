"""
These are outside of the dags. These are one-time routines that use GlacierSyncProgress
"""
import argparse
import csv
from datetime import  timedelta
from pprint import pp
# dont add to docker
# from tqdm import tqdm
from time import sleep

import boto3
import pendulum

from GlacierSyncProgress import GlacierSyncProgress
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from sqlalchemy.orm.exc import NoResultFound

# -----------------     CONST  -----------------
# Number of days to restore
RESTORE_DAY_COUNT: int = 5
SAFETY_FACTOR: float = 0.8
# -----------------     /CONST -----------------

def _make_a_glacier_sync_progress():
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


def _glacier_sync_catchup():
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
        with DrsDbContextBase('prodsa:~/.config/bdrc/db_apps.config') as drs:
            sess = drs.get_session()
            # Open a csv reader from f
            # read each line and add it to the GlacierSyncProgress table
            sess = drs.get_session()
            for row in csvr:
                work = row[0]
                aws_s3_bucket = row[1]
                aws_s3_key = row[2]
                gsp = drs.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work).one()
                _aws_path_data = gsp.user_data
                gsp.update_user_data(pendulum.now().to_rfc3339_string(),
                                     {'aws_s3_bucket': aws_s3_bucket, 'aws_s3_key': aws_s3_key})
                sess.add(gsp)
                iadd += 1
                if iadd % 10 == 0:
                    sess.commit()
                    iadd = 0


# Calculate from GlacierSyncProgress records the number of syncs we perform per day, using SqlAlchemy GroupBy
def calculate_syncs_per_day_groupby():
    from sqlalchemy import func
    syncs_per_day = 0.0
    with DrsDbContextBase('prodcli:~/.config/bdrc/db_apps.config') as drs:
        sess = drs.get_session()
        result = sess.query(func.date(GlacierSyncProgress.sync_complete_on), func.count(GlacierSyncProgress.sync_complete_on)) \
            .group_by(func.date(GlacierSyncProgress.sync_complete_on)) \
            .all()
        for day, count in result:
            pp(f"{day=}: {count=}")
        sum_second_elements = sum([t[1] for t in result])
        syncs_per_day = (sum_second_elements  / len(result))
    return syncs_per_day


def launch_restore_requests(days_to_refill:int):
    """
    Make sure there are enough restores to process calculate_syncs_per_day_groupby() * days_to_refill
    do this by getting:
    - the number of items with no restore_requested_on
    - the number of
    :param days_to_refill:
    :return:
    """

    average_count: float = calculate_syncs_per_day_groupby()
    total_to_restore = int(average_count * (RESTORE_DAY_COUNT /ntimes_per_day_called)  * SAFETY_FACTOR)


# TODO: Get n unrestored, don't get from list
def launch_restore_request():
    ap = argparse.ArgumentParser()
    ap.add_argument('work_list', help='a csv file with no header, containing a list of work RIDs to restore',
                    type=argparse.FileType('r'))

    args = ap.parse_args()
    s3 = boto3.client('s3')
    with args.work_list as f:
        csvr = csv.reader(f)
        with DrsDbContextBase('prodcli:~/.config/bdrc/db_apps.config') as drs:
            sess = drs.get_session()
            for row in csvr:
                work = row[0]
                launch_one_request(s3, RESTORE_DAY_COUNT, sess, work)


def launch_one_request(work: str, restore_len: int, s3: object = None, sess = None):
    """
    :param work: work to restore
    :param restore_len: number of days to restore
    :param s3: boto client
    :param sess: s3 session
    :return:
    """
    gsp = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work
                                                 ).filter(GlacierSyncProgress.restore_requested_on == None).one()
    _aws_path_data = gsp.user_data
    # The user data we're looking for is:
    # [
    #   {'user_data':
    #       {'aws_s3_key': 'Archive0/00/W1FPL11000/W1FPL11000.bag.zip', 'aws_s3_bucket': 'glacier.staging.fpl.bdrc.org'},
    #    'time_stamp': '2024-05-13T15:25:56.717146-04:00'
    #    }
    # ]
    get_user_data = lambda k, data: [b['user_data'][k] for b in data if k in b['user_data']][0]
    aws_s3_bucket = get_user_data('aws_s3_bucket', gsp.user_data)
    aws_s3_key = get_user_data('aws_s3_key', gsp.user_data)
    from botocore.exceptions import ClientError
    try:
        restore_data = s3.restore_object(Bucket=aws_s3_bucket, Key=aws_s3_key, RestoreRequest={'Days': restore_len,
                                                                                               'GlacierJobParameters': {
                                                                                                   'Tier': 'Standard'}})
        gsp.restore_requested_on = pendulum.now()
        gsp.update_user_data(pendulum.now().to_rfc3339_string(), {'restore_request_results': restore_data})
        sess.commit()
    except ClientError as e:
        if e.response['Error']['Code'] == 'RestoreAlreadyInProgress':
            print(f"{work} restore already in progress. Skipping and continuing")
        else:
            raise e

# calculate the number of timedelta objects in a day
def times_per_day(time_delta: timedelta):
    """
    Calculate the number of timedeltas in a day
    :return:
    """

    # 1 day in seconds
    seconds_per_day = 24 * 60 * 60
    n_deltas = seconds_per_day /  time_delta.total_seconds()
    return n_deltas

if __name__ == '__main__':
    # add_works_to_project()
    # launch_restore_request()
    # calculate the number of pendulum timedelta objects in a day
    pp(f"5 hours {times_per_day(timedelta(hours=5))}")

