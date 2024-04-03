#!/usr/bin/env bash
aws s3 rm s3://glacier.staging.nlm.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 rm s3://glacier.staging.fpl.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 cp s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip s3://glacier.staging.fpl.bdrc.org/airflow/W1FPL2251.bag.zip
aws s3 cp s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip s3://glacier.staging.nlm.bdrc.org/airflow/W1FPL2251.bag.zip