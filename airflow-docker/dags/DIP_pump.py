from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.models.xcom_arg import XComArg
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from pprint import pprint as pp
from DIP_pump_depositIA import process_work

from staging_utils import get_db_config
def process_results(**context):
    # Example Python task logic
    print("Processing results from SQL task...")

def get_dip_candidate(dip_activity_code):
    with DrsDbContextBase(get_db_config('qa')) as drs:
        sess = drs.get_session()
        # Call a SPROC or execute a query using the session
        # Use SQLAlchmey to call a sproc with an argument

        result = sess.execute("CALL GetDIPActivityCandidates(:activity)", {"activity": dip_activity_code})
        pp(f"SPROC result for {dip_activity_code}:")
        # We're returning here, because we don't use the >> flow
        # We're assigning the result to the next task, so it can be distributed
        rows =  [dict(row) for row in result.fetchall()]
        pp(rows)
        return rows
         
with DAG(
    dag_id="dip_pump_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["example"],
) as dag:
    start = EmptyOperator(task_id="start")

    @task
    def get_deep_archive_task():
        return get_dip_candidate('DEEP_ARCHIVE')
    
    @task
    def get_ia_task():
        return get_dip_candidate('IA')  
    
    @task
    def do_one_deep_archive(row: dict):
        # Example logic for deep archive task
        print("DA" * 20)
        process_work(row['WorkName'], row['DIPDestPath'])
        print("DA" * 20)

    @task
    def do_one_ia(row: dict):        # Example logic for IA task
        print("IA" * 20)
        pp(row) 
        print("IA" * 20)

    # ia_rows = get_ia_task()
    # process_ia_rows_mapped = do_one_ia.expand(row=XComArg(ia_rows))

    # deep_archive_rows = get_deep_archive_task()
    # rocess_deep_archive_rows_mapped = do_one_deep_archive.expand(row=XComArg(deep_archive_rows))

    # # The secret sauce
    # start >> [ia_rows, deep_archive_rows]   

    #Github copilot
    do_one_ia.expand(row=get_ia_task())
    do_one_deep_archive.expand(row=get_deep_archive_task())    

    if __name__ == "__main__":
        # Airflow throws an exception here when I want to use the XComArg.PlainXComArg has no attribute 
        dag.test()