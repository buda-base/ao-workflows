from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.sqs import SqsSensor
from airflow.utils.dates import days_ago

def _process_messages(messages,**kwargs):

    fff = kwargs['ti'].xcom_pull(task_ids='wait_for_sqs_message')
    if not messages:
        print(kwargs['messages'])
    else:
        for message in messages:
            print(f"Processing message: {message}")

@dag(default_args={'owner': 'airflow'}, schedule_interval=None, start_date=days_ago(2), dag_id='HowdyDag')
def my_dag():

    wait_for_sqs_message = SqsSensor(
        task_id='wait_for_sqs_message',
        sqs_queue='ManifestReadyToIntake',
        max_messages=10,
        delete_message_on_reception=False,
        do_xcom_push=True
    )

    @task
    def decorated_process_messages(**kwargs):

        fff = kwargs['ti'].xcom_pull(task_ids='wait_for_sqs_message')
        if not fff:
            print('no fff')
        else:
            for message in fff['messages']:
                print(f"Processing message: {message}")

    # From github copilot v2
    # process_messages_op = PythonOperator(
    #     task_id='process_messages',
    #     python_callable=_process_messages
    # )

    chain(wait_for_sqs_message, decorated_process_messages(wait_for_sqs_message.output))
    # blarg = wait_for_sqs_message.output
    # decorated_process_messages(blarg)
    # wait_for_sqs_message >> process_messages
    # End github

    # vluhurg = process_messages(wait_for_sqs_message.output)
    #


my_dag = my_dag()
my_dag.test()