.. -*- mode: rst -*-

==============
Airflow docker
==============

Using the techniques in `O'Reilly "Data Pipelines with Apache Airflow" <https://read.amazon.com/?asin=B0978171QX&ref_=kwl_kr_iv_rec_1>`_

to create a docker repo for airflow.

This docker compose has to modify the ``scheduler`` container. This container runs the DAGS,
so it must contain all the DAG's dependencies (except airflow itself)

Persistent data
===============
You can use volumes to create areas in docker that store persistent data. this data
persists across container lifecycles. This is useful for the airflow database and the
work files.

You use **bind mount points** to map a host platform
directory to a container directory.
This is how to export data (such as files) from a docker container.

``airflow-docker`` project architecture
=======================================

Building ``airflow-docker``
---------------------------
1. Modifying the base airflow image: The distributed airflow image needs
to have the BDRC environment installed before the DAGs can run. It needs two classes of additions:

- The BDRC sycning utilities, environment, which is installed from the ``buda-base/archive-ops`` repo.
- Python libraries that support the ``StagingGlacierProcess`` workflow.

2. Operational steps

- Git pull ``buda-base/ao-workflows`` into ``WORKFLOW_DEV_DIR``.
- Git pull ``buda-base/archive-ops`` into ``AO_DEV_DIR``.
- Start the Desktop Docker (or the docker daemon on Linux)
- Edit ``build-bdrc-airflow.sh`` to locate ``AO_DEV_DIR`` This script installs:
     - Audit tool
     - The BDRC environment:
         - credentials
         - scripts
         - Python packages
- Run ``build-bdrc-airflow.sh`` to build the modified image. This deposits the image in the local docker repo.

When you are done, you should have an image that ``docker compose`` can use.

Building the airflow container.
-------------------------------
This step prepares to run the ``docker compose`` command.
Running ``airflow-docker``
--------------------------

Using the modified image, which is installed in the native ``docker`` environment,
``cd DEV_DIR/ao-workflows/airflow-docker``
``docker-compose up -d`` To start the container.


``docker-compose.yml`` defines the containers that comprise the airflow platform.
Typically, you would use the ``docker-compose up-d`` command to start the containers.

StagingGlacierProcess
=====================

