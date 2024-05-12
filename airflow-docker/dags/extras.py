"""
These are outside of the dags. These are one-time routines that use GlacierSyncProgress
"""
import argparse
from datetime import time
from time import sleep

import pendulum

from GlacierSyncProgress import GlacierSyncProgress
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from sqlalchemy.orm.exc import NoResultFound

def make_a_glacier_sync_progress():
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
            gsp.update_user_data( pendulum.now().to_rfc3339_string(), ud_dict_data)
            sess.add(gsp)
            sess.commit()
        gsp.update_user_data( pendulum.now().to_rfc3339_string(), {f'd{o_id}k1': f'd{o_id}v1', f'd{o_id}k2': f'd{o_id}v2'})
        sess.commit()

def glacier_sync_catchup():
    """
    Transform all the syncs done by airflow into GlacierSyncProgress records
    :return:
    """
    done_already:[] = ['W1NLM4700','W1NLM4800','W1NLM4900','W1NLM5000','W1NLM5100','W1NLM5300','W1NLM5400','W1NLM5500','W1NLM5800','W1NLM7363']
    with DrsDbContextBase() as drs:
        sess = drs.get_session()
        for work in done_already:
            sleep(1)
            import pendulum
            xnow = pendulum.now()
            gsp_w = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work).one()
            gsp.restore_complete_on = xnow
            gsp.download_complete_on = xnow
            gsp.debag_complete_on = xnow
            gsp.sync_complete_on = xnow
            gsp.update_user_data(xnow.to_rfc3339_string() ,{'work_rid': work, 'provider': 'manual'})
            sess.add(gsp)
            sess.commit()
            print(f"{work} done")

def add_works_to_project():
    """
    read a list from a csv and add them to the GlacierSyncProgress table, with NO activities logged
    :return:
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('work_list', help='a csv file with a list of works to add to the GlacierSyncProgress table',type=args.FileType('r'))

    args = ap.parse_args()
    with args.work_list as f:
        csvr = csv.reader(f)
        with DrsDbContextBase() as drs:
                sess = drs.get_session()
                # Open a csv reader from f
                # read each line and add it to the GlacierSyncProgress table
                for row in csvr:
                    work = row[0]
                    aws_s3_path=row[1]
                    gsp = GlacierSyncProgress()
                    gsp.object_name = work
                    gsp.update_user_data( pendulum.now().to_rfc3339_string(), {'aws_s3_path': aws_s3_path})
                    sess.add(gsp)
                    sess.commit()
                    print(f"{work=}, {aws_s3_path=} added")

if __name__ == '__main__':
    add_works_to_project()