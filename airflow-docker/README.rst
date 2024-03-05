.. -*- mode: rst -*-
# Airflow docker
Using the techniques in `O'Reilly "Data Pipelines with Apache Airflow" <https://read.amazon.com/?asin=B0978171QX&ref_=kwl_kr_iv_rec_1>`_

to create a docker repo for airflow.

This docker compose has to modify the ``scheduler`` container. This container runs the DAGS,
so it must contain all the DAG's dependencies (except airflow itself)

