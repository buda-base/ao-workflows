#!/usr/bin/env bash
# Get failed runs from the Airflow logs
set -e
. ~/bin/init_sys.sh
#
# Where airflow is writing the logs - on sattva
export LOG_SRC=~jimk/prod/docker-containers/debag-sync/logs/dag_id=down_scheduled
# make a run-log dir:
export LOG_TARGET=${1:-run-fails-$(log_now_ish)}
# Query docker for failed dag runs
# sed out the color ansi escape sequence
docker exec -it   debag-sync-scheduler-1 airflow dags list-runs --dag-id down_scheduled --state failed --output plain | sed  's/\x1B\[[0-9;]*[a-zA-Z]//g' > down-scheduled-fails
# Copy all the tasks for the failed runs.
cat down-scheduled-fails  | grep 'scheduled__' | awk '{print $2}' | parallel 'cp -rv $LOG_TARGET/"run_id={}" $LOG_TARGET'
cat << EOF > /dev/null
You still have to know which failed.
Print the last task in the failed run - it will be the one that fails.
The task labels are:
wait_for_file
debag
sync
EOF

for task_fails in sync debag wait_for_file ; do
    echo "Task: $task_fails"
    # find $task_fails int the 'task_id='
    find $LOG_TARGET -type d -name task_id=$task_fail
done
#
# next task:

