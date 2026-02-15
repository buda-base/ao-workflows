 cd /Users/jimk/dev/ao-workflows ; /usr/bin/env /Users/jimk/dev/ao-workflows/venv/bin/python /Users/jimk/.vscode/extensions/ms-python.debugpy-2025.18.0-darwin-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher 55263 -- /Users/jimk/dev/ao-workflows/airflow-docker/dags/DIP_pump.py
/Users/jimk/dev/ao-workflows/airflow-docker/dags/DIP_pump.py:30 RemovedInAirflow3Warning: Param `schedule_interval` is deprecated and will be removed in a future release. Please use `schedule` instead.
[2026-02-15T15:52:50.566-0500] {dag.py:4080} INFO - dagrun id: dip_pump_example
[2026-02-15T15:52:50.622-0500] {dag.py:4096} INFO - created dagrun <DagRun dip_pump_example @ 2026-02-15 20:52:50.111533+00:00: manual__2026-02-15T20:52:50.111533+00:00, state:running, queued_at: None. externally triggered: False>
[2026-02-15T15:52:50.681-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=get_deep_archive_task map_index=-1
[2026-02-15T15:52:50.682-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.get_deep_archive_task manual__2026-02-15T20:52:50.111533+00:00 [scheduled]>
[2026-02-15 15:52:50,880] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='get_deep_archive_task' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:50.880-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='get_deep_archive_task' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
'SPROC result for DEEP_ARCHIVE:'
[{'WorkName': 'NoWork',
  'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28),
  'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1),
  'dip_activity_type_id': 5,
  'dip_comment': 'qa service sattva Howdy from a test',
  'dip_dest_path': 'NoRealPathDest',
  'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90',
  'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302',
  'path': 'NoRealPathDest',
  'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48),
  'work_id': 50985},
 {'WorkName': 'W4JK98766',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive2/66/W4JK98766',
  'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766',
  'path': '/mnt/Archive2/66/W4JK98766',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11),
  'work_id': 48741},
 {'WorkName': 'W4JK98772',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive2/72/W4JK98772',
  'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772',
  'path': '/mnt/Archive2/72/W4JK98772',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32),
  'work_id': 48743},
 {'WorkName': 'W4JK98775',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive3/75/W4JK98775',
  'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775',
  'path': '/mnt/Archive3/75/W4JK98775',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39),
  'work_id': 48744},
 {'WorkName': 'W4JK98792',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive3/92/W4JK98792',
  'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792',
  'path': '/mnt/Archive3/92/W4JK98792',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46),
  'work_id': 48745},
 {'WorkName': 'W4JK98795',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive3/95/W4JK98795',
  'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795',
  'path': '/mnt/Archive3/95/W4JK98795',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53),
  'work_id': 48746}]
[2026-02-15 15:52:53,420] {python.py:202} INFO - Done. Returned value was: [{'WorkName': 'NoWork', 'path': 'NoRealPathDest', 'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28), 'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1), 'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3), 'dip_activity_result_code': 0, 'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302', 'dip_dest_path': 'NoRealPathDest', 'work_id': 50985, 'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90', 'dip_comment': 'qa service sattva Howdy from a test'}, {'WorkName': 'W4JK98766', 'path': '/mnt/Archive2/66/W4JK98766', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766', 'dip_dest_path': '/mnt/Archive2/66/W4JK98766', 'work_id': 48741, 'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 rc:success'}, {'WorkName': 'W4JK98772', 'path': '/mnt/Archive2/72/W4JK98772', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772', 'dip_dest_path': '/mnt/Archive2/72/W4JK98772', 'work_id': 48743, 'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98775', 'path': '/mnt/Archive3/75/W4JK98775', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775', 'dip_dest_path': '/mnt/Archive3/75/W4JK98775', 'work_id': 48744, 'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98792', 'path': '/mnt/Archive3/92/W4JK98792', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792', 'dip_dest_path': '/mnt/Archive3/92/W4JK98792', 'work_id': 48745, 'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98795', 'path': '/mnt/Archive3/95/W4JK98795', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795', 'dip_dest_path': '/mnt/Archive3/95/W4JK98795', 'work_id': 48746, 'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 rc:success'}]
[2026-02-15T15:52:53.420-0500] {python.py:202} INFO - Done. Returned value was: [{'WorkName': 'NoWork', 'path': 'NoRealPathDest', 'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28), 'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1), 'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3), 'dip_activity_result_code': 0, 'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302', 'dip_dest_path': 'NoRealPathDest', 'work_id': 50985, 'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90', 'dip_comment': 'qa service sattva Howdy from a test'}, {'WorkName': 'W4JK98766', 'path': '/mnt/Archive2/66/W4JK98766', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766', 'dip_dest_path': '/mnt/Archive2/66/W4JK98766', 'work_id': 48741, 'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 rc:success'}, {'WorkName': 'W4JK98772', 'path': '/mnt/Archive2/72/W4JK98772', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772', 'dip_dest_path': '/mnt/Archive2/72/W4JK98772', 'work_id': 48743, 'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98775', 'path': '/mnt/Archive3/75/W4JK98775', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775', 'dip_dest_path': '/mnt/Archive3/75/W4JK98775', 'work_id': 48744, 'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98792', 'path': '/mnt/Archive3/92/W4JK98792', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792', 'dip_dest_path': '/mnt/Archive3/92/W4JK98792', 'work_id': 48745, 'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98795', 'path': '/mnt/Archive3/95/W4JK98795', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795', 'dip_dest_path': '/mnt/Archive3/95/W4JK98795', 'work_id': 48746, 'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 rc:success'}]
[2026-02-15T15:52:53.509-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=get_deep_archive_task, execution_date=20260215T205250, start_date=, end_date=20260215T205253
[2026-02-15T15:52:53.525-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=get_deep_archive_task map_index=-1
[2026-02-15T15:52:53.525-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=get_ia_task map_index=-1
[2026-02-15T15:52:53.526-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.get_ia_task manual__2026-02-15T20:52:50.111533+00:00 [scheduled]>
[2026-02-15 15:52:53,565] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='get_ia_task' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:53.565-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='get_ia_task' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
'SPROC result for IA:'
[{'WorkName': 'NoWork',
  'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28),
  'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1),
  'dip_activity_type_id': 5,
  'dip_comment': 'qa service sattva Howdy from a test',
  'dip_dest_path': 'NoRealPathDest',
  'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90',
  'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302',
  'path': 'NoRealPathDest',
  'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48),
  'work_id': 50985},
 {'WorkName': 'W1AC6',
  'create_time': datetime.datetime(2025, 1, 15, 13, 57, 35),
  'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 25, 56),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 25, 53),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W1AC6  success elapsed: 00:00:00 rc:success',
  'dip_dest_path': '/mnt/Archive0/00/W1AC6',
  'dip_external_id': '6c696575-fa08-11ef-98b2-0e7ec8e7f259',
  'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AC6',
  'path': '/mnt/Archive0/00/W1AC6',
  'update_time': datetime.datetime(2025, 3, 5, 16, 26),
  'work_id': 7735},
 {'WorkName': 'W1AO1',
  'create_time': datetime.datetime(2025, 1, 15, 13, 57, 45),
  'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 26, 11),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 26, 9),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W1AO1  success elapsed: 00:00:00 rc:success',
  'dip_dest_path': '/mnt/Archive0/00/W1AO1',
  'dip_external_id': '757c2af6-fa08-11ef-98b2-0e7ec8e7f259',
  'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AO1',
  'path': '/mnt/Archive0/00/W1AO1',
  'update_time': datetime.datetime(2025, 3, 5, 16, 26, 13),
  'work_id': 119621},
 {'WorkName': 'W23834',
  'create_time': datetime.datetime(2024, 10, 30, 12, 19, 43),
  'dip_activity_finish': datetime.datetime(2025, 3, 7, 16, 3, 27),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2025, 3, 7, 16, 3, 24),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W23834  success elapsed: 00:00:01 '
                 'rc:success',
  'dip_dest_path': '/Users/jimk/dev/tmp/Archive1/34/W23834',
  'dip_external_id': '9d1282a2-fb97-11ef-98b2-0e7ec8e7f259',
  'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-07T15:53:13/unzip/W23834',
  'path': '/Users/jimk/dev/tmp/Archive1/34/W23834',
  'update_time': datetime.datetime(2025, 3, 7, 16, 3, 29),
  'work_id': 5368},
 {'WorkName': 'W8LS68220',
  'create_time': datetime.datetime(2024, 11, 14, 11, 23, 55),
  'dip_activity_finish': datetime.datetime(2025, 3, 8, 13, 3, 3),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2025, 3, 8, 13, 3, 1),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W8LS68220  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220',
  'dip_external_id': '9426fb66-fc47-11ef-98b2-0e7ec8e7f259',
  'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-08T12:48:05/debag/W8LS68220',
  'path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220',
  'update_time': datetime.datetime(2025, 3, 8, 13, 3, 7),
  'work_id': 33192},
 {'WorkName': 'W4JK98766',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive2/66/W4JK98766',
  'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766',
  'path': '/mnt/Archive2/66/W4JK98766',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11),
  'work_id': 48741},
 {'WorkName': 'W4JK98772',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive2/72/W4JK98772',
  'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772',
  'path': '/mnt/Archive2/72/W4JK98772',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32),
  'work_id': 48743},
 {'WorkName': 'W4JK98775',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive3/75/W4JK98775',
  'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775',
  'path': '/mnt/Archive3/75/W4JK98775',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39),
  'work_id': 48744},
 {'WorkName': 'W4JK98792',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive3/92/W4JK98792',
  'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792',
  'path': '/mnt/Archive3/92/W4JK98792',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46),
  'work_id': 48745},
 {'WorkName': 'W4JK98795',
  'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50),
  'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50),
  'dip_activity_result_code': 0,
  'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49),
  'dip_activity_type_id': 5,
  'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 '
                 'rc:success',
  'dip_dest_path': '/mnt/Archive3/95/W4JK98795',
  'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259',
  'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795',
  'path': '/mnt/Archive3/95/W4JK98795',
  'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53),
  'work_id': 48746}]
[2026-02-15 15:52:54,694] {python.py:202} INFO - Done. Returned value was: [{'WorkName': 'NoWork', 'path': 'NoRealPathDest', 'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28), 'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1), 'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3), 'dip_activity_result_code': 0, 'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302', 'dip_dest_path': 'NoRealPathDest', 'work_id': 50985, 'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90', 'dip_comment': 'qa service sattva Howdy from a test'}, {'WorkName': 'W1AC6', 'path': '/mnt/Archive0/00/W1AC6', 'create_time': datetime.datetime(2025, 1, 15, 13, 57, 35), 'update_time': datetime.datetime(2025, 3, 5, 16, 26), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 25, 53), 'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 25, 56), 'dip_activity_result_code': 0, 'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AC6', 'dip_dest_path': '/mnt/Archive0/00/W1AC6', 'work_id': 7735, 'dip_external_id': '6c696575-fa08-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W1AC6  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W1AO1', 'path': '/mnt/Archive0/00/W1AO1', 'create_time': datetime.datetime(2025, 1, 15, 13, 57, 45), 'update_time': datetime.datetime(2025, 3, 5, 16, 26, 13), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 26, 9), 'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 26, 11), 'dip_activity_result_code': 0, 'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AO1', 'dip_dest_path': '/mnt/Archive0/00/W1AO1', 'work_id': 119621, 'dip_external_id': '757c2af6-fa08-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W1AO1  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W23834', 'path': '/Users/jimk/dev/tmp/Archive1/34/W23834', 'create_time': datetime.datetime(2024, 10, 30, 12, 19, 43), 'update_time': datetime.datetime(2025, 3, 7, 16, 3, 29), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 7, 16, 3, 24), 'dip_activity_finish': datetime.datetime(2025, 3, 7, 16, 3, 27), 'dip_activity_result_code': 0, 'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-07T15:53:13/unzip/W23834', 'dip_dest_path': '/Users/jimk/dev/tmp/Archive1/34/W23834', 'work_id': 5368, 'dip_external_id': '9d1282a2-fb97-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W23834  success elapsed: 00:00:01 rc:success'}, {'WorkName': 'W8LS68220', 'path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220', 'create_time': datetime.datetime(2024, 11, 14, 11, 23, 55), 'update_time': datetime.datetime(2025, 3, 8, 13, 3, 7), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 8, 13, 3, 1), 'dip_activity_finish': datetime.datetime(2025, 3, 8, 13, 3, 3), 'dip_activity_result_code': 0, 'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-08T12:48:05/debag/W8LS68220', 'dip_dest_path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220', 'work_id': 33192, 'dip_external_id': '9426fb66-fc47-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W8LS68220  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98766', 'path': '/mnt/Archive2/66/W4JK98766', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766', 'dip_dest_path': '/mnt/Archive2/66/W4JK98766', 'work_id': 48741, 'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 rc:success'}, {'WorkName': 'W4JK98772', 'path': '/mnt/Archive2/72/W4JK98772', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772', 'dip_dest_path': '/mnt/Archive2/72/W4JK98772', 'work_id': 48743, 'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98775', 'path': '/mnt/Archive3/75/W4JK98775', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775', 'dip_dest_path': '/mnt/Archive3/75/W4JK98775', 'work_id': 48744, 'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98792', 'path': '/mnt/Archive3/92/W4JK98792', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792', 'dip_dest_path': '/mnt/Archive3/92/W4JK98792', 'work_id': 48745, 'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98795', 'path': '/mnt/Archive3/95/W4JK98795', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795', 'dip_dest_path': '/mnt/Archive3/95/W4JK98795', 'work_id': 48746, 'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 rc:success'}]
[2026-02-15T15:52:54.694-0500] {python.py:202} INFO - Done. Returned value was: [{'WorkName': 'NoWork', 'path': 'NoRealPathDest', 'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28), 'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1), 'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3), 'dip_activity_result_code': 0, 'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302', 'dip_dest_path': 'NoRealPathDest', 'work_id': 50985, 'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90', 'dip_comment': 'qa service sattva Howdy from a test'}, {'WorkName': 'W1AC6', 'path': '/mnt/Archive0/00/W1AC6', 'create_time': datetime.datetime(2025, 1, 15, 13, 57, 35), 'update_time': datetime.datetime(2025, 3, 5, 16, 26), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 25, 53), 'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 25, 56), 'dip_activity_result_code': 0, 'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AC6', 'dip_dest_path': '/mnt/Archive0/00/W1AC6', 'work_id': 7735, 'dip_external_id': '6c696575-fa08-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W1AC6  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W1AO1', 'path': '/mnt/Archive0/00/W1AO1', 'create_time': datetime.datetime(2025, 1, 15, 13, 57, 45), 'update_time': datetime.datetime(2025, 3, 5, 16, 26, 13), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 26, 9), 'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 26, 11), 'dip_activity_result_code': 0, 'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AO1', 'dip_dest_path': '/mnt/Archive0/00/W1AO1', 'work_id': 119621, 'dip_external_id': '757c2af6-fa08-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W1AO1  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W23834', 'path': '/Users/jimk/dev/tmp/Archive1/34/W23834', 'create_time': datetime.datetime(2024, 10, 30, 12, 19, 43), 'update_time': datetime.datetime(2025, 3, 7, 16, 3, 29), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 7, 16, 3, 24), 'dip_activity_finish': datetime.datetime(2025, 3, 7, 16, 3, 27), 'dip_activity_result_code': 0, 'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-07T15:53:13/unzip/W23834', 'dip_dest_path': '/Users/jimk/dev/tmp/Archive1/34/W23834', 'work_id': 5368, 'dip_external_id': '9d1282a2-fb97-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W23834  success elapsed: 00:00:01 rc:success'}, {'WorkName': 'W8LS68220', 'path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220', 'create_time': datetime.datetime(2024, 11, 14, 11, 23, 55), 'update_time': datetime.datetime(2025, 3, 8, 13, 3, 7), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2025, 3, 8, 13, 3, 1), 'dip_activity_finish': datetime.datetime(2025, 3, 8, 13, 3, 3), 'dip_activity_result_code': 0, 'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-08T12:48:05/debag/W8LS68220', 'dip_dest_path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220', 'work_id': 33192, 'dip_external_id': '9426fb66-fc47-11ef-98b2-0e7ec8e7f259', 'dip_comment': 'archive sync for W8LS68220  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98766', 'path': '/mnt/Archive2/66/W4JK98766', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766', 'dip_dest_path': '/mnt/Archive2/66/W4JK98766', 'work_id': 48741, 'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 rc:success'}, {'WorkName': 'W4JK98772', 'path': '/mnt/Archive2/72/W4JK98772', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772', 'dip_dest_path': '/mnt/Archive2/72/W4JK98772', 'work_id': 48743, 'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98775', 'path': '/mnt/Archive3/75/W4JK98775', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775', 'dip_dest_path': '/mnt/Archive3/75/W4JK98775', 'work_id': 48744, 'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98792', 'path': '/mnt/Archive3/92/W4JK98792', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792', 'dip_dest_path': '/mnt/Archive3/92/W4JK98792', 'work_id': 48745, 'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 rc:success'}, {'WorkName': 'W4JK98795', 'path': '/mnt/Archive3/95/W4JK98795', 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50), 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53), 'dip_activity_type_id': 5, 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49), 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50), 'dip_activity_result_code': 0, 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795', 'dip_dest_path': '/mnt/Archive3/95/W4JK98795', 'work_id': 48746, 'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259', 'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 rc:success'}]
[2026-02-15T15:52:54.712-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=get_ia_task, execution_date=20260215T205250, start_date=, end_date=20260215T205254
[2026-02-15T15:52:54.724-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=get_ia_task map_index=-1
[2026-02-15T15:52:54.725-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=start map_index=-1
[2026-02-15T15:52:54.725-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.start manual__2026-02-15T20:52:50.111533+00:00 [scheduled]>
[2026-02-15 15:52:54,763] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='start' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:54.763-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='start' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:54.769-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=start, execution_date=20260215T205250, start_date=, end_date=20260215T205254
[2026-02-15T15:52:54.778-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=start map_index=-1
[2026-02-15T15:52:54.927-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=6
[2026-02-15T15:52:54.928-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=6 [scheduled]>
[2026-02-15 15:52:54,977] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:54.977-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W4JK98772',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive2/72/W4JK98772',
 'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772',
 'path': '/mnt/Archive2/72/W4JK98772',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32),
 'work_id': 48743}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:54,979] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:54.979-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:54.984-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=6, execution_date=20260215T205250, start_date=, end_date=20260215T205254
[2026-02-15T15:52:54.994-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=6
[2026-02-15T15:52:54.994-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=5
[2026-02-15T15:52:54.995-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=5 [scheduled]>
[2026-02-15 15:52:55,042] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.042-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W4JK98766',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive2/66/W4JK98766',
 'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766',
 'path': '/mnt/Archive2/66/W4JK98766',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11),
 'work_id': 48741}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,044] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.044-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.050-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=5, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.059-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=5
[2026-02-15T15:52:55.059-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=8
[2026-02-15T15:52:55.060-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=8 [scheduled]>
[2026-02-15 15:52:55,106] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.106-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W4JK98792',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive3/92/W4JK98792',
 'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792',
 'path': '/mnt/Archive3/92/W4JK98792',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46),
 'work_id': 48745}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,108] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.108-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.113-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=8, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.123-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=8
[2026-02-15T15:52:55.124-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_deep_archive map_index=4
[2026-02-15T15:52:55.124-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_deep_archive manual__2026-02-15T20:52:50.111533+00:00 map_index=4 [scheduled]>
[2026-02-15 15:52:55,171] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.171-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
DADADADADADADADADADADADADADADADADADADADA
{'WorkName': 'W4JK98792',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 43),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 43),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 42),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98792  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive3/92/W4JK98792',
 'dip_external_id': 'b29ba460-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98792',
 'path': '/mnt/Archive3/92/W4JK98792',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 46),
 'work_id': 48745}
DADADADADADADADADADADADADADADADADADADADA
[2026-02-15 15:52:55,173] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.173-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.179-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_deep_archive, map_index=4, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.197-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_deep_archive map_index=4
[2026-02-15T15:52:55.198-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=4
[2026-02-15T15:52:55.199-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=4 [scheduled]>
[2026-02-15 15:52:55,251] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.251-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W8LS68220',
 'create_time': datetime.datetime(2024, 11, 14, 11, 23, 55),
 'dip_activity_finish': datetime.datetime(2025, 3, 8, 13, 3, 3),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2025, 3, 8, 13, 3, 1),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W8LS68220  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220',
 'dip_external_id': '9426fb66-fc47-11ef-98b2-0e7ec8e7f259',
 'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-08T12:48:05/debag/W8LS68220',
 'path': '/Users/jimk/dev/tmp/Archive0/20/W8LS68220',
 'update_time': datetime.datetime(2025, 3, 8, 13, 3, 7),
 'work_id': 33192}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,252] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.252-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.258-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=4, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.269-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=4
[2026-02-15T15:52:55.269-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_deep_archive map_index=1
[2026-02-15T15:52:55.270-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_deep_archive manual__2026-02-15T20:52:50.111533+00:00 map_index=1 [scheduled]>
[2026-02-15 15:52:55,316] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.316-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
DADADADADADADADADADADADADADADADADADADADA
{'WorkName': 'W4JK98766',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 4),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 8),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 3),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98766  success elapsed: 00:00:01 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive2/66/W4JK98766',
 'dip_external_id': '9b5871b3-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98766',
 'path': '/mnt/Archive2/66/W4JK98766',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 11),
 'work_id': 48741}
DADADADADADADADADADADADADADADADADADADADA
[2026-02-15 15:52:55,318] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.318-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.323-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_deep_archive, map_index=1, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.333-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_deep_archive map_index=1
[2026-02-15T15:52:55.334-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=1
[2026-02-15T15:52:55.334-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=1 [scheduled]>
[2026-02-15 15:52:55,380] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.380-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W1AC6',
 'create_time': datetime.datetime(2025, 1, 15, 13, 57, 35),
 'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 25, 56),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 25, 53),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W1AC6  success elapsed: 00:00:00 rc:success',
 'dip_dest_path': '/mnt/Archive0/00/W1AC6',
 'dip_external_id': '6c696575-fa08-11ef-98b2-0e7ec8e7f259',
 'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AC6',
 'path': '/mnt/Archive0/00/W1AC6',
 'update_time': datetime.datetime(2025, 3, 5, 16, 26),
 'work_id': 7735}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,381] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.381-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.387-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=1, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.396-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=1
[2026-02-15T15:52:55.397-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=7
[2026-02-15T15:52:55.397-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=7 [scheduled]>
[2026-02-15 15:52:55,442] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.442-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W4JK98775',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive3/75/W4JK98775',
 'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775',
 'path': '/mnt/Archive3/75/W4JK98775',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39),
 'work_id': 48744}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,443] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.443-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.448-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=7, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.458-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=7
[2026-02-15T15:52:55.458-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_deep_archive map_index=0
[2026-02-15T15:52:55.458-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_deep_archive manual__2026-02-15T20:52:50.111533+00:00 map_index=0 [scheduled]>
[2026-02-15 15:52:55,504] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.504-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
DADADADADADADADADADADADADADADADADADADADA
{'WorkName': 'NoWork',
 'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28),
 'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1),
 'dip_activity_type_id': 5,
 'dip_comment': 'qa service sattva Howdy from a test',
 'dip_dest_path': 'NoRealPathDest',
 'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90',
 'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302',
 'path': 'NoRealPathDest',
 'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48),
 'work_id': 50985}
DADADADADADADADADADADADADADADADADADADADA
[2026-02-15 15:52:55,505] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.505-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.510-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_deep_archive, map_index=0, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.521-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_deep_archive map_index=0
[2026-02-15T15:52:55.522-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=0
[2026-02-15T15:52:55.522-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=0 [scheduled]>
[2026-02-15 15:52:55,567] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.567-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'NoWork',
 'create_time': datetime.datetime(2021, 7, 16, 17, 15, 28),
 'dip_activity_finish': datetime.datetime(2001, 3, 3, 0, 0, 3),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2001, 1, 1, 0, 0, 1),
 'dip_activity_type_id': 5,
 'dip_comment': 'qa service sattva Howdy from a test',
 'dip_dest_path': 'NoRealPathDest',
 'dip_external_id': 'f1c5954e-e67a-11eb-ad57-0673343fbb90',
 'dip_source_path': '/mnt/rs5Archive0/02/W8LS19302',
 'path': 'NoRealPathDest',
 'update_time': datetime.datetime(2025, 2, 12, 14, 0, 48),
 'work_id': 50985}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,568] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.568-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.573-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=0, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.583-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=0
[2026-02-15T15:52:55.584-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_deep_archive map_index=3
[2026-02-15T15:52:55.584-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_deep_archive manual__2026-02-15T20:52:50.111533+00:00 map_index=3 [scheduled]>
[2026-02-15 15:52:55,629] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.629-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
DADADADADADADADADADADADADADADADADADADADA
{'WorkName': 'W4JK98775',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 36),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 36),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 35),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98775  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive3/75/W4JK98775',
 'dip_external_id': 'ae69e55b-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98775',
 'path': '/mnt/Archive3/75/W4JK98775',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 39),
 'work_id': 48744}
DADADADADADADADADADADADADADADADADADADADA
[2026-02-15 15:52:55,631] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.631-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.637-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_deep_archive, map_index=3, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.647-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_deep_archive map_index=3
[2026-02-15T15:52:55.647-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=3
[2026-02-15T15:52:55.648-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=3 [scheduled]>
[2026-02-15 15:52:55,693] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.693-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W23834',
 'create_time': datetime.datetime(2024, 10, 30, 12, 19, 43),
 'dip_activity_finish': datetime.datetime(2025, 3, 7, 16, 3, 27),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2025, 3, 7, 16, 3, 24),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W23834  success elapsed: 00:00:01 rc:success',
 'dip_dest_path': '/Users/jimk/dev/tmp/Archive1/34/W23834',
 'dip_external_id': '9d1282a2-fb97-11ef-98b2-0e7ec8e7f259',
 'dip_source_path': '/Users/jimk/bdrc/data/work/down_scheduled_2025-03-07T15:53:13/unzip/W23834',
 'path': '/Users/jimk/dev/tmp/Archive1/34/W23834',
 'update_time': datetime.datetime(2025, 3, 7, 16, 3, 29),
 'work_id': 5368}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,694] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.694-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.699-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=3, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.708-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=3
[2026-02-15T15:52:55.709-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=9
[2026-02-15T15:52:55.709-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=9 [scheduled]>
[2026-02-15 15:52:55,754] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.754-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W4JK98795',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive3/95/W4JK98795',
 'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795',
 'path': '/mnt/Archive3/95/W4JK98795',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53),
 'work_id': 48746}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,755] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.755-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.760-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=9, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.771-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=9
[2026-02-15T15:52:55.771-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_deep_archive map_index=2
[2026-02-15T15:52:55.772-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_deep_archive manual__2026-02-15T20:52:50.111533+00:00 map_index=2 [scheduled]>
[2026-02-15 15:52:55,816] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.816-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
DADADADADADADADADADADADADADADADADADADADA
{'WorkName': 'W4JK98772',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 29),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 29),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 28),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98772  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive2/72/W4JK98772',
 'dip_external_id': 'aa34707a-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98772',
 'path': '/mnt/Archive2/72/W4JK98772',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 32),
 'work_id': 48743}
DADADADADADADADADADADADADADADADADADADADA
[2026-02-15 15:52:55,818] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.818-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.823-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_deep_archive, map_index=2, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.834-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_deep_archive map_index=2
[2026-02-15T15:52:55.834-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_ia map_index=2
[2026-02-15T15:52:55.835-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_ia manual__2026-02-15T20:52:50.111533+00:00 map_index=2 [scheduled]>
[2026-02-15 15:52:55,880] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.880-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_ia' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
{'WorkName': 'W1AO1',
 'create_time': datetime.datetime(2025, 1, 15, 13, 57, 45),
 'dip_activity_finish': datetime.datetime(2025, 3, 5, 21, 26, 11),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2025, 3, 5, 21, 26, 9),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W1AO1  success elapsed: 00:00:00 rc:success',
 'dip_dest_path': '/mnt/Archive0/00/W1AO1',
 'dip_external_id': '757c2af6-fa08-11ef-98b2-0e7ec8e7f259',
 'dip_source_path': '/home/airflow/bdrc/data/work/down_scheduled_2025-02-24T12:05:00/unzip/W1AO1',
 'path': '/mnt/Archive0/00/W1AO1',
 'update_time': datetime.datetime(2025, 3, 5, 16, 26, 13),
 'work_id': 119621}
IAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIA
[2026-02-15 15:52:55,882] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.882-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.887-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_ia, map_index=2, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.896-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_ia map_index=2
[2026-02-15T15:52:55.897-0500] {dag.py:4042} INFO - [DAG TEST] starting task_id=do_one_deep_archive map_index=5
[2026-02-15T15:52:55.898-0500] {dag.py:4045} INFO - [DAG TEST] running task <TaskInstance: dip_pump_example.do_one_deep_archive manual__2026-02-15T20:52:50.111533+00:00 map_index=5 [scheduled]>
[2026-02-15 15:52:55,943] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
[2026-02-15T15:52:55.943-0500] {taskinstance.py:2513} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER='airflow' AIRFLOW_CTX_DAG_ID='dip_pump_example' AIRFLOW_CTX_TASK_ID='do_one_deep_archive' AIRFLOW_CTX_EXECUTION_DATE='2026-02-15T20:52:50.111533+00:00' AIRFLOW_CTX_TRY_NUMBER='1' AIRFLOW_CTX_DAG_RUN_ID='manual__2026-02-15T20:52:50.111533+00:00'
DADADADADADADADADADADADADADADADADADADADA
{'WorkName': 'W4JK98795',
 'create_time': datetime.datetime(2026, 2, 13, 21, 41, 50),
 'dip_activity_finish': datetime.datetime(2026, 2, 13, 21, 41, 50),
 'dip_activity_result_code': 0,
 'dip_activity_start': datetime.datetime(2026, 2, 13, 21, 41, 49),
 'dip_activity_type_id': 5,
 'dip_comment': 'archive sync for W4JK98795  success elapsed: 00:00:00 '
                'rc:success',
 'dip_dest_path': '/mnt/Archive3/95/W4JK98795',
 'dip_external_id': 'b6c7bd5e-094e-11f1-a97e-0e7ec8e7f259',
 'dip_source_path': '/home/jimk/prod/aow42-replace-dip-pump/source/W4JK98795',
 'path': '/mnt/Archive3/95/W4JK98795',
 'update_time': datetime.datetime(2026, 2, 13, 21, 41, 53),
 'work_id': 48746}
DADADADADADADADADADADADADADADADADADADADA
[2026-02-15 15:52:55,944] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.944-0500] {python.py:202} INFO - Done. Returned value was: None
[2026-02-15T15:52:55.949-0500] {taskinstance.py:1149} INFO - Marking task as SUCCESS. dag_id=dip_pump_example, task_id=do_one_deep_archive, map_index=5, execution_date=20260215T205250, start_date=, end_date=20260215T205255
[2026-02-15T15:52:55.958-0500] {dag.py:4056} INFO - [DAG TEST] end task task_id=do_one_deep_archive map_index=5
[2026-02-15T15:52:55.967-0500] {dagrun.py:795} INFO - Marking run <DagRun dip_pump_example @ 2026-02-15 20:52:50.111533+00:00: manual__2026-02-15T20:52:50.111533+00:00, state:running, queued_at: None. externally triggered: False> successful
[2026-02-15T15:52:55.968-0500] {dagrun.py:846} INFO - DagRun Finished: dag_id=dip_pump_example, execution_date=2026-02-15 20:52:50.111533+00:00, run_id=manual__2026-02-15T20:52:50.111533+00:00, run_start_date=2026-02-15 20:52:50.111533+00:00, run_end_date=2026-02-15 20:52:55.968002+00:00, run_duration=5.856469, state=success, external_trigger=False, run_type=manual, data_interval_start=2026-02-15 20:52:50.111533+00:00, data_interval_end=2026-02-15 20:52:50.111533+00:00, dag_hash=None