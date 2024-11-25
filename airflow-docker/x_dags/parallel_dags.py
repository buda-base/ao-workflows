import pendulum
from airflow import DAG, settings
from airflow.models import DagBag, DagRun, TaskInstance, DagModel
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import os
from pprint import pp

from airflow.utils.state import DagRunState

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def list_files(directory, **context):
    files = os.listdir(directory)
    pp(files)
    context['ti'].xcom_push(key='file_list', value=files)

def process_file(file):
    print(f"Processing file: {file}")
def trigger_subdag(file, parent_dag_name, child_dag_name,default_args):
    subdag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=default_args,
        # schedule_interval=schedule_interval,
        # start_date=start_date,
    )

    with subdag:
        # Add tasks to your subdag here
        # Example:
        task = PythonOperator(
            task_id='process_file',
            python_callable=process_file,
            op_kwargs={'file': file},
        )

    return subdag

def create_subdag_tasks(parent_dag_id: str, **context):
    files = context['ti'].xcom_pull(key='file_list', task_ids='list_files')
    pp(files)
    # start_date = pendulum.today('UTC').add(days=-1)
    # schedule = None   # Manual trigger only

    dag_bag: DagBag = DagBag()
    triggers:[] = []
    for file in files:
        subdag_id = f"process_{os.path.splitext(file)[0]}"
        pp(f"Building {subdag_id}")
        # subdag = trigger_subdag(file, parent_dag_name, subdag_id, start_date, schedule, default_args)
        # Without start_date and schedule. Triggered only
        subdag = trigger_subdag(file, parent_dag_id, subdag_id, default_args)
        dag_bag.bag_dag(subdag,parent_dag_id)

        trigger = TriggerDagRunOperator(
            task_id=subdag_id,
            trigger_dag_id=subdag.dag_id,
            execution_date=pendulum.now('UTC'),
            wait_for_completion=False,
        )

        # Probably not async
        session = settings.Session()
        if not session.query(DagModel).filter(DagModel.dag_id == subdag.dag_id).first():
            session.add(DagModel(dag_id=subdag.dag_id))
        session.commit()
        session.close()
        dag_bag.sync_to_db()
        triggers.append(trigger)

    context['ti'].xcom_push(key='triggers', value=triggers)



with DAG(
    'file_sensor_trigger_subdags',
    default_args=default_args,
    description='Trigger subDAGs for each detected file',
    schedule=timedelta(hours=1),
    start_date=pendulum.today('UTC').add(days=-1),
    catchup=True,
    tags=['example'],
) as FS_subdag:
    list_files_task = PythonOperator(
        task_id='list_files',
        python_callable=list_files,
        op_kwargs={'directory': '/Users/jimk/bdrc/data/Incoming'},
        provide_context=True,
    )

    create_subdags_task = PythonOperator(
        task_id='create_subdag_tasks',
        python_callable=create_subdag_tasks,
        provide_context=True,
        op_kwargs={'parent_dag_id': 'file_sensor_trigger_subdags'},
    )

    list_files_task >> create_subdags_task >> trigger_subdags_task




if __name__ == '__main__':
    #    dag.clear(dag_run_state=DagRunState.QUEUED)
    FS_subdag.test()
    # ss = settings.Session()
    # r_dags = ss.query(DagRun).filter(DagRun.state == DagRunState.RUNNING).all()
    # for dd in r_dags:
    #     pp(dd.dag_id)
    # ss.close()