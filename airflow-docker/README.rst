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
- run `bdrc-docker.sh` with your choice of options:

.. code-block:: bash

    ❯ ./bdrc-docker.sh  --help
    Usage: bdrc-docker.sh [-b|--build] [-r|--run] [-h|--help] [ -r|--refresh_build ] [-m|--requirements <dag-requirements-file>] [-l|--build_dir <build-dir>]
      -b|--build: build a replacement airflow image
      -r|--run: run the composed container ** default action if no flags given
      -h|--help
      -r|--refresh_build: if building, purge all built material and start over
      -m|--requirements <dag-requirements-file>: default: ./StagingGlacierProcess-requirements.txt
      -l|--build_dir <build-dir>: default: ~/tmp/compose-build

You can use multiple options. (although  --run and --down only provide a smoke test)
The default ``build_dir`` is created if it doesn't exist
Details
-------
:StagingGlacierProcess-requirements.txt: specifies the python libraries that are required for the ``StagingGlacierProcess`` DAG to run.

:syncAnywhere/requirements.txt: specifies the python libraries that are required for the internal shell script that the glacier_staging_dag runs. (This what a native Linux user would use when provisioning their environment using ``archive-ops/scripts/deployments/copyLinksToBin``)

:secrets handling: It's well, a saucerful of secret. Code warriors are invited to examine.

docker-compose architecture
---------------------------


Docker
======

There are two steps in building docker.

Reference documentation for Airflow on Docker is found at:
`Running Airflow in Docker <https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html>`_

The code that implements this stage is in the `airflow-docker` folder in this project.
The major high-level steps are:

.. code-block:: yaml

        volumes:
          # DEV/TEST use bind mounts
          # System logging - /opt/airflow/logs is the airflow system default
          # TODO: Migrate to debian
          - /Users/jimk/dev/tmp/Projects/airflow/syslog:/opt/airflow/logs
          # TODO: Migrate to debian
          # App logging. Replicate in glacier_staging_to_sync.py
          - /Users/jimk/dev/tmp/Projects/airflow/log:/home/airflow/log
          # We don't need to persist stating in a resource shared between containers
          # - staging:/home/airflow/staging
          # Export actual sync product - this is wrto bodhi/sattva
          #      - /mnt/Archive0:/var/mnt/Archive0
          #      - /mnt/Archive1:/var/mnt/Archive1
          #      - /mnt/Archive2:/var/mnt/Archive2
        #      - /mnt/Archive3:/var/mnt/Archive3
        # For testing on local mac. This is a good reason for not
        # using files, but a service
          - /Users/jimk/dev/tmp/Archive0:/home/airflow/extern/Archive0
          - /Users/jimk/dev/tmp/Archive1:/home/airflow/extern/Archive1
          - /Users/jimk/dev/tmp/Archive2:/home/airflow/extern/Archive2
          - /Users/jimk/dev/tmp/Archive3:/home/airflow/extern/Archive3
        # Provision secrets for the scheduler service:
        secrets:
          - db_apps
          - drs_cnf
          - aws

The above fragment links **host** directories to **container** directories, and ``secrets`` mounts
to the service. Note that other services **cannot** access these secrets, without access from this file.

.. code-block:: yaml

    secrets:
      db_apps:
        file:
          .secrets/db_apps.config
      drs_cnf:
        file:
          .secrets/drs.config
      aws:
        file:
          .secrets/aws-credentials

This stanza maps the host files (which were created in ``build-docker-compose.sh``) to the
scheduler service **only**. The entire scheduler accesses these as ``/run/secrets/<secret_name>``
(e.g. ``/run/secrets/aws``), not the actual file name under ``.secrets``.

The ``.secrets`` directory **must never** be checked into the repository.


