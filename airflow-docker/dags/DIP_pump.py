from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from pprint import pprint as pp

from staging_utils import get_db_config
def process_results(**context):
    # Example Python task logic
    print("Processing results from SQL task...")

with DAG(
    dag_id="dip_pump_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["example"],
) as dag:

    def call_sproc(**context):
         with DrsDbContextBase(get_db_config('qa')) as drs:
            sess = drs.get_session()
            # Call a SPROC or execute a query using the session
            # Use SQLAlchmey to call a sproc with an argument

            result = sess.execute("CALL GetDIPActivityCandidates(:activity)", {"activity": 'DEEP_ARCHIVE'})
            pp("SPROC result:")
            pp(result.fetchall())            

    sql_task = PythonOperator(
        task_id="call_sproc",
        python_callable=call_sproc,
        provide_context=True,
    )

    python_task = PythonOperator(
        task_id="process_sql_results",
        python_callable=process_results,
        provide_context=True,
    )

    sql_task >> python_task

    if __name__ == "__main__":
        dag.test()