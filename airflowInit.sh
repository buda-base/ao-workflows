#!/usr/bin/env bash
#
# After installing airflow 2, you have to run this once to initialize the database
# Get airflow into the path
. ~/dev/ao-workflows/venv/bin/activate
echo Checking connection to Airflow
if [[ ! "airflow db check" ]] ; then
airflow db migrate --yes
echo UPGRADE DONE -------------------------------------------
airflow db reset --yes
echo RESET DONE "********************************************"
airflow users create --username admin --password admin --firstname Anonymous --lastname Admin --role Admin --email jimk@tbrc.org
echo USER CREATED "********************************************"
else
  echo okely dokely
fi

