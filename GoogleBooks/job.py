"""
Defines the job of creating and updating the worklist
for google books
Going in with Apache Airflow

to debug:
https://stackoverflow.com/questions/58931845/debugging-airflow-tasks-with-ide-tools
Just add a new run configuration of type "Python Debug Server".
Can be local or remote!
Use any spare port (e.g. 9091)

Documentation: This Dag is the ETL for the works that are to be Google Booked.

Style is from [Working with taskflow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
Steps:
1. Extract current set from BUDA
2. Transform
3. Load into drs.GB_ToDo, excluding duplicates
"""
import json

import pendulum
from GbWorkflowUtils import get_gb_candidates

from airflow.decorators import dag, task


@dag(
    description="Google Books work list ETL",
    schedule=None,
    tags=["Google Books"],
)
def tutorial_taskflow_api():
    """
### TaskFlow API Tutorial Documentation
This is a simple data pipeline example which demonstrates the use of
the TaskFlow API using three simple tasks for Extract, Transform, and Load.
Documentation that goes along with the Airflow TaskFlow API tutorial is
located
[here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html)
    :return:
    """
    @task
    def extract() -> []:
            """
            Fetch list of works from BUDA
            :return:
            """
            return get_gb_candidates()

    @task
    def transform() -> []:
        """
        Extracts workIds from work members
        :return:
        """
