==============
Airflow docker
==============

Overview
========
Using the techniques in `O'Reilly "Data Pipelines with Apache Airflow" <https://read.amazon.com/?asin=B0978171QX&ref_=kwl_kr_iv_rec_1>`_

to create a docker repo for airflow.

This docker compose has to modify the ``scheduler`` container. This container runs the DAGS,
so it must contain all the DAG's dependencies (except airflow itself)

Definitions
-----------
:host: The physical machine that the docker containers run on  (real world). in a docker compose
``volumes`` stanza, this is the left hand side of the colon. In a ``secrets:`` stanza, it's the terminal node.

:container: The docker container that is running. in a docker compose
``volumes`` stanza, this is the right hand side of the colon.


Persistent data
---------------
You can use volumes to create areas in docker that store persistent data. this data
persists across container lifecycles. This is useful for the airflow database and the
work files.

You use **bind mount points** to map a host platform
directory to a container directory.
This is how to export data (such as files) from a docker container.

airflow-docker project architecture
===================================
There are two phases to building the project:
- Building the base airflow image
- Deploying the runtime code into a docker environment

You need to rebuild the base airflow image when:
- the sync script, or its python dependencies change (these must be injected into the shell environment that the airflow BashOperator uses)
- the resources that the airflow DAG code needs are changed.

You need to deploy the runtime code into a docker environment when:
- the structure of user identity of the docker services in `bdrc-docker-compose.yml` changes
- parameters or secrets change
- you change the output of syncs (for testing)

You don't generally need to deploy the runtime code when the DAGs change. You
can update the DAGs in the running environment by copying them into the docker environment
that ``deploy`` created.

Building the base airflow image
===============================
The base airflow image contains an apache airflow image that has this project's
requirements built into it. This is specified in in ``bdrc-docker-compose.yml``

1. Modifying the base airflow image: The distributed airflow image needs
to have the BDRC environment installed before the DAGs can run. It needs two classes of additions:

- The BDRC synching utilities, environment, which is installed from the ``buda-base/archive-ops`` repo.
- Python libraries that support the ``StagingGlacierProcess`` workflow (the DAG)

2. Operational steps

- Git pull ``buda-base/ao-workflows`` into ``WORKFLOW_DEV_DIR``.
- Git pull ``buda-base/archive-ops`` into ``AO_DEV_DIR``.
- Start the Desktop Docker (or the docker daemon on Linux)
- run `bdrc-docker.sh` with your choice of options:

.. code-block:: bash

    ❯ ./bdrc-docker.sh  --help
    Usage: bdrc-docker.sh  [ -h|--help ]  [ -m|--requirements <dag-requirements-file> ] [ -l|--build_dir <build-dir> ]
    Invokes the any_service:build target in bdrc-docker-compose.yml
      -h|--help
      -m|--requirements <dag-requirements-file>: default: ./StagingGlacierProcess-requirements.txt
      -l|--build_dir <build-dir>: default: ~/tmp/compose-build. Temporary directory for staging materials.


Details
-------

:StagingGlacierProcess-requirements.txt: specifies the python libraries that are required for the ``StagingGlacierProcess`` DAG to run.

:syncAnywhere/requirements.txt: specifies the python libraries that are required for the internal shell script that the glacier_staging_dag runs.
(This what a native Linux user would use when provisioning their environment using ``archive-ops/scripts/deployments/copyLinksToBin``)
This value is hard coded. The current active GitHub branch of ``archive-ops`` is the source.


Deploying the Runtime
=====================
This step creates the environment that the docker service ``scheduler`` runs in.
The ``scheduler`` service executes the airflow DAGS, and manages the logs. Therefore,
it is the service that needs access to the host platform. The ``deploy`` script
creates this.

It creates in the ``build_dir`` directory:

.. code-block:: bash

    ./dags     ./logs ./plugins ./docker-secrets docker-compose.yml


This is sufficient to launch airflow in docker.

Docker background
=================

This platform was developed with reference to:
Reference documentation for Airflow on Docker is found at:
`Running Airflow in Docker <https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html>`_

The code that implements this stage is in the `airflow-docker` folder in this project.

The most significant interface between docker and its host (one of our Linux servers, where
the output of the process lands) is in ``airflow-docker/bdrc-docker-compose.yml`` :

.. code-block:: yaml

      volumes:
      - ./logs:/opt/airflow/logs
      # For testing on local mac. This is a good reason for not
      # using files, but a service. Note this folder has to match test_access_permissions.py
      #  - /mnt/Archive0/00/TestArchivePermissions:/home/airflow/extern/Archive0/00/TestArchivePermissions
      - ${ARCH_ROOT:-/mnt}/Archive0:/home/airflow/extern/Archive0
      - ${ARCH_ROOT:-/mnt}/Archive1:/home/airflow/extern/Archive1
      - ${ARCH_ROOT:-/mnt}/Archive2:/home/airflow/extern/Archive2
      - ${ARCH_ROOT:-/mnt}/Archive3:/home/airflow/extern/Archive3
      # This allows us to dynamically add or modify dags without restarting the scheduler
      - ./dags:/opt/airflow/dags


The above fragment links **host (real world)** directories to **container (internal to scheduler service)** directories.

This segment specifies secrets handling. Note that bdrc utilities had to be changed
to detect the existence of ``/run/secrets`` and use it if it exists.

.. code-block:: yaml

    secrets:
      db_apps:
        file:
          .docker-secrets/db_apps.config
      drs_cnf:
        file:
          .docker-secrets/drs.config
      aws:
        file:
          .docker-secrets/aws-credentials

This stanza maps the host files (which were created in ``deploy``) to the
scheduler service **only**. The scheduler  services accesses these as ``/run/secrets/<secret_name>``
(e.g. ``/run/secrets/aws``), not the actual file name under ``.secrets``.

The ``.secrets`` directory **must never** be checked into the repository.



