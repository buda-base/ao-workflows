"""
Defines the job of creating and updating the worklist
for google books
Going in with Apache Airflow

to debug:
https://stackoverflow.com/questions/58931845/debugging-airflow-tasks-with-ide-tools
Just add a new run configuration of type "Python Debug Server".
Can be local or remote!
Use any spare port (e.g. 9091)

Using Sensors:
https://marclamberti.com/blog/airflow-sensors/

"""
import json
import logging
from pprint import pprint

import pendulum
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor

from GbWorkflowUtils import gb_proj_candidates, gb_transform, gb_project_load

from airflow.models import DAG

import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=9091, stdoutToServer=True, stderrToServer=True)


def _dump_list(**kwargs):
    """
    Downstream task
    :param thing:
    :return:
    """
    ti = kwargs['ti']
    book_list = ti.xcom_pull(task_ids='get-to-gb-upload')

    if book_list:
        logging.info(f"book_list! {len(book_list)}")
    else:
        logging.info("NO book_list")


DAG_GET_LIMIT = 10
with DAG(
        dag_id="google-books-content-upload",
        schedule=None,
        start_date=pendulum.datetime(2023, 2, 23, tz="EST"),
        catchup=False,
        tags=["Google Books"],
) as dag:
    # If I ever want to put this in an external SQL, do this:
    # https://stackoverflow.com/questions/52688757/how-to-pass-sql-as-file-with-parameters-to-airflow-operator
    books_needing_upload = SqlSensor(task_id='get-to-gb-upload', conn_id='drs_af_conn', sql=f"select V.label from pm_project_members pmm \
left join GB_Content_Track GCT on GCT.volume_id = pmm.pm_volume_id \
inner join pm_member_states pms on pms.id = pmm.pm_project_state_id \
               inner join Volumes V on V.volumeId = pmm.pm_volume_id \
where GCT.volume_id is null \
and pmm.pm_volume_id is not null \
and pms.m_state_name = \'Not started\' \
limit {DAG_GET_LIMIT}", poke_interval=5, mode="reschedule")

    dump_books = PythonOperator(task_id='dump_list', python_callable=_dump_list)

    books_needing_upload >> dump_books


@task(task_id="dump_volume_names")
def dump_list(raw_list: [str]):
    """
    Extracts workIds from work members
    :return:
    """
    pprint(raw_list)


@task
def get_volumes(work_ids: [int]):
    pass


@task
def work_project_load(works: [str]):
    """
    Loads works into a hardwired project
    :param works: list of workRIDs in the DRS normalized schema (no BUDA decorator e.g. bdr:)
    :return:
    """
    desc = """
        Google Books Metadata is the project that represents uploading all the MARC
        records of works into Google Books.
        """
    gb_project_load(works, "Google Books Metadata", )


# extract >> transform >> get_volumes >>
# proj_candidates = extract()
# norm_works = transform()
