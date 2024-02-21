#!/usr/bin/env python3
"""
Creates and airflow DAG to process unglaciered bag files. The process is:
- unbag
- (optionally) validate
Sync to Archive, using `syncOneWork.sh` (must be installed on host)
This initiates the DIP-pump workflow (see github://bdua-base/archive-ops/scripts/dip-pump
"""
from airflow.decorators import task
from pendulum import datetime

from airflow import DAG
from airflow.providers.amazon.aws.sensors.sqs import SqsSensor
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 20),
    #    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

@task()
def process_messages(messages, **context):
    # Use taskflow API instead
    # messages = context['ti'].xcom_pull(task_ids='sqs_sensor_task')
    for message in messages:
        # Add your logic here to decide whether to keep or put back each message
        pass


with DAG(
        'sqs_sensor_dag',
        default_args=default_args,
        schedule=timedelta(hours=1)) as gs_dag:

    sqs_sensor = SqsSensor(
        task_id='sqs_sensor_task',
        #     dag=dag,
        sqs_queue='my_sqs_queue',
        aws_conn_id='my_aws_conn',
        max_messages=10
    )


    process_messages(sqs_sensor.output)


# Use taskflow
# process_task = PythonOperator(
#     task_id='process_messages',
#     python_callable=process_messages,
#     provide_context=True,
#     dag=dag
# )

# sqs_sensor >> process_task
if __name__ == '__main__':
    gs_dag.test_cycle()
