#!/usr/bin/env bash
aws s3 rm s3://glacier.staging.nlm.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 rm s3://glacier.staging.fpl.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 rm s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip
#
# This is a small subset of a whole work.
aws s3 cp ~/dev/tmp/Projects/airflow/glacier_staging_to_sync/ao1060/save-W1FPL2251.bag.zip s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 cp s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip s3://glacier.staging.fpl.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 cp s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip s3://glacier.staging.nlm.bdrc.org/airflow/W1FPL2251.bag.zip