import datetime

import pytest
from airflow.models import DAG, BaseOperator, DagRun
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from airflow.utils.state import DagRunState

pytest_plugins = ["helpers_namespace"]


@pytest.fixture
def test_dag():
    """
    this doesnt work outside of the context of a webserver and scheduler setup
    :return:
    """
    return DAG(
        "fixture_dag",
        default_args={"owner": "airflow", "start_date": datetime.datetime(2015, 1, 1)},
        schedule_interval="@daily",
    )


@pytest.helpers.register
def run_airflow_task(task: BaseOperator, dag: DAG):
    """
this doesnt work outside of the context of a webserver and scheduler setup
:return:
"""
    dag.clear()
    task.run(
        start_date=dag.default_args["start_date"],
        end_date=dag.default_args["start_date"],
        ignore_ti_state=True,
    )


@pytest.mark.skip("doesnt run standalone")
def test_this(test_dag):
    """test_dag is the pytest fixture in __file__"""
    task = BashOperator(task_id="test_task", dag=test_dag, bash_command="echo 'hello!'")
    pytest.helpers.run_airflow_task(task, test_dag)


def test_circular():
    dag = DAG(dag_id='kyklops')
    task1 = EmptyOperator(task_id="task1", dag=dag)
    task2 = EmptyOperator(task_id="task2", dag=dag)
    task3 = EmptyOperator(task_id="task3", dag=dag)
    task1 >> task2 >> task3 >> task1
    dr: DagRun = dag.test()
    assert dr.state == DagRunState.FAILED


def test_linear():
    dag = DAG(dag_id='direct')
    task1 = EmptyOperator(task_id="task1", dag=dag)
    task2 = EmptyOperator(task_id="task2", dag=dag)
    task3 = EmptyOperator(task_id="task3", dag=dag)
    task1 >> task2 >> task3
    dr: DagRun = dag.test()
    assert dr.state == DagRunState.SUCCESS
