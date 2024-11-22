from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime
from airflow.decorators import task

from time import sleep
import random as r

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

def msg(op: str, s: int):
    print(f'{op} and sleeping {s=}')
    sleep(s)

def generate_list(**kwargs):
    return ['object1', 'object2', 'object3']

def process_object(obj, **kwargs):
    msg(f'Processing {obj}',r.randint(3,20))
    return obj

with DAG('dynamic_parallel_tasks_dag', default_args=default_args, schedule_interval='@daily') as dag:
    generate_task = PythonOperator(
        task_id='generate_list',
        python_callable=generate_list,
        provide_context=True
    )

    def create_dynamic_tasks(**kwargs):
        ti = kwargs['ti']
        objects = ti.xcom_pull(task_ids='generate_list')
        with TaskGroup(group_id='dynamic_tasks') as tg:
            for obj in objects:
                PythonOperator(
                    task_id=f'process_{obj}',
                    python_callable=process_object,
                    op_args=[obj],
                    provide_context=True
                )
        return tg

    dynamic_tasks = PythonOperator(
        task_id='create_dynamic_tasks',
        python_callable=create_dynamic_tasks,
        provide_context=True
    )

    generate_task >> dynamic_tasks


# Can do it this way, too


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('taskflow_with_task_groups', default_args=default_args, schedule_interval='@daily') as at_task_dag:

    @task
    def task1():
        msg('Task 1 executed', r.randint(1,5))

    @task
    def task2():
        msg('Task 2 executed', r.randint(2,9))

    @task
    def task3():
        print('Task 3 executed')

    with TaskGroup(group_id='group1') as group1:
        t1 = task1()

    with TaskGroup(group_id='group2') as group2:
        t2 = task2()

    with TaskGroup(group_id='group3') as group3:
        t3 = task3()

    group1 >> group2 >> group3

from airflow import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}


with DAG('taskflow_with_xcom', default_args=default_args, schedule_interval='@daily') as g_dag:

    @task
    def task1():
        return ['arg1', 'arg2', 'arg3']

    @task
    def task2(arg):
        # Process the argument and return a new value
        return f'processed_{arg}'

    @task
    def task3(arg):
        print(f'Task 3 processing: {arg}')

    t1 = task1()

    with TaskGroup(group_id='group2') as group2:
        processed_args = [task2(arg) for arg in t1.output]

    with TaskGroup(group_id='group3') as group3:
        for arg in processed_args:
            task3(arg)

    t1 >> group2 >> group3

if __name__ == '__main__':
    # dag.test()
    g_dag.test()