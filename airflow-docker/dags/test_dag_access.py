#!/usr/bin/env python3
"""
Test dag access to archives
"""

import os
from datetime import timedelta
from pathlib import Path
from pprint import pp
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

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


def _test_access():
    """
    Touch something on the archive. See bdrc-docker-compose.yml for the
    mapping.
    This shouldn't work when bdrc-airflow build with <user> uid,
    but should with "sync"
    """
    # Must match bdrc-docker-compose.yml:
    #     scheduler:
    #          ...
    #          volumes:
    #               - /mnt/Archive0/00/TestArchivePermissions:/home/airflow/extern/Archive0/00/TestArchivePermissions
    test_perms_path: Path = Path("/mnt") /  "Archive0" / "00" / "TestArchivePermissions"
    tested_string: str = os.makedirs(test_perms_path,exist_ok=True)
    test_perms_instance = test_perms_path /  "add_multiples"
    with open(Path.joinpath(test_perms_instance), 'a') as test_perms_file:
        msg:str =f"Howdy from :{str(test_perms_instance)}:  on {pendulum.now().to_iso8601_string()}"
        pp(msg)
        test_perms_file.writelines([msg])
        test_perms_file.write('\n')
        
    pp(f"Tested: {test_perms_instance=}")
    for dentry in  os.scandir(test_perms_path):
        pp(f"found: {dentry.name} {dentry=}")

            # Debug test - write to the bind mount
            
            # import pendulum
            # current_date = pendulum.now()
            # with open(DOWNLOAD_PATH / "test_file", 'w') as tf:    
            #     tf.writelines([f"Howdy at {current_date.to_iso8601_string()}"])
            # # test what's in the bind mount?
            # with os.scandir(DOWNLOAD_PATH) as dentries:
            #     for dentry in dentries:
            #         pp(f"{dentry.name=} type={'f' if dentry.is_file() else 'd' if dentry.is_dir() else '?'}")
            # maybe a use for this later
            # hash = s3_record['s3']['object']['eTag']


with DAG('test_access_permissions_dag', schedule=None, tags=['bdrc', 'test']) as tp_dag:
    tp = PythonOperator(python_callable=_test_access, task_id='test_access_permissions')

from airflow import DAG
from airflow.operators.python import task
from airflow.utils.dates import days_ago

dag = DAG(
    'my_dag',
    schedule=None,
    #    start_date=days_ago(2),
    tags=['example'],
)

@task(dag=dag, retries=3, retry_delay=timedelta(minutes=1))
def my_task():
    from airflow.exceptions import AirflowException
    raise AirflowException("allowing to fail with retry")

my_task()
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
    #    gs_dag.test()
    dag.cli()

    
