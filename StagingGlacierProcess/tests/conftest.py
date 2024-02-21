import datetime

import pytest
from airflow.models import DAG, BaseOperator
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task

pytest_plugins = ["helpers_namespace"]


@pytest.fixture
def test_dag():
    return DAG(
        "test_dag",
        default_args={"owner": "airflow", "start_date": datetime.datetime(2015, 1, 1)},
        schedule_interval="@daily",
    )


@pytest.helpers.register
def run_airflow_task(task: BaseOperator, dag: DAG):
    dag.clear()
    task.run(
        start_date=dag.default_args["start_date"],
        end_date=dag.default_args["start_date"],
        ignore_ti_state=True,
    )





def test_this(test_dag):
    task = EmptyOperator(task_id="my_task", dag=test_dag)
    pytest.helpers.run_airflow_task(task, test_dag)
