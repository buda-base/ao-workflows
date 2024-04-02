#!/usr/bin/env bash
 aws s3 rm s3://staging.nlm.bdrc.org/airflow/W1FPL2251.bag.zip
 aws s3 rm s3://staging.fpl.bdrc.org/airflow/W1FPL2251.bag.zip
 aws s3 cp s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip s3://staging.fpl.bdrc.org/airflow/W1FPL2251.bag.zip
 aws s3 cp s3://manifest.bdrc.org/airflow/W1FPL2251.bag.zip s3://staging.nlm.bdrc.org/airflow/W1FPL2251.bag.zip