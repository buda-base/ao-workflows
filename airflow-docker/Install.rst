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

:container: The docker container that is running.

:bind mount: in a docker compose ``volumes`` stanza, this is the right hand side of the colon. Ex: ``./logs:/opt/airflow/logs`` In this expression, ``.logs`` is the *host* directory, and ``/opt/airflow/logs`` is the *container* directory

Please refer to :ref:`docker-concepts` below for a quick introduction to the docker concepts most relevant to this project. A deeper dive is count in :doc:`Development.rst`


TL,DR: Quickstart
=================
You can get this running from a typical development workstation, which is set up for `syncAnywhere` development, in a few steps:

- get this repo
- Build the image (see below) ``bdrc-docker.sh``
- Deploy to the image with ``deploy``
- cd to the ``--dest`` argument to deploy
- run ``docker-compose up -d``
- end the run with ``docker-compose down`` (in the ``--dest`` directory)

After a few minutes, open up a browser to localhost:8089 (admin/admin)

.. warning::

    Do not activate the ``sqs_scheduled_dag``in the Web UI. If you do that, works may not be sync'd.  See :ref:`Development.rst` for the DAG fuctionality.

Please see

airflow-docker project architecture
===================================
There are two phases to building the project:
- Building the base airflow image
- Deploying the runtime code into a docker environment


Building the base airflow image
===============================

Principles
----------
The base airflow image is a docker compose container with a complete apache airflow image that has this project's requirements built into it.

``Dockerfile-bdrc`` orchestrates customizing the airflow docker image. Only used in the context of the ``bdrc-docker.sh`` script, which wraps the ``Dockerfile-bdrc`` file.

You need to rebuild the base airflow image when anything **except** the DAGs change. This includes:

- the sync script (``archive-ops/scripts/syncAnywhere/syncOneWork.sh``, or its python dependencies
- the audit tool user properties changes.
- Different bind mounts change.

There may be other cases where you need to rebuild the base airflow image.

Operations
----------

Building an image
^^^^^^^^^^^^^^^^^

- Git pull ``buda-base/ao-workflows`` into ``WORKFLOW_DEV_DIR``.
- Git pull ``buda-base/archive-ops`` into ``AO_DEV_DIR``.
- Start the Desktop Docker (or the docker daemon on Linux)
- run `bdrc-docker.sh` with your choice of options:

.. code-block:: bash

    ./bdrc-docker.sh -h
    Usage: bdrc-docker.sh  [ -h|--help ]  [ -m|--requirements <dag-requirements-file> ] [ -d|--build_dir <build-dir> ]
    Invokes the any_service:build target in bdrc-docker-compose.yml
      -c|--config_dir <config_dir>: the elements of the 'bdrc' folder under .config. the config dir must contain at least folder 'bdrc'
      -h|--help
      -m|--requirements <dag-requirements-file>: default: ./StagingGlacierProcess-requirements.txt
      -d|--build_dir <build-dir>: default: ~/tmp/compose-build

    ** CAUTION: ONLY COPY config what is needed. db_apps is NOT needed.**
    ** DO NOT COPY the entire bdrc config tree!

The results of this operation is a docker image named ``bdrc-airflow`` that the docker runtime installs in its cache.

Details
^^^^^^^

:StagingGlacierProcess-requirements.txt: specifies the python libraries that are required for the ``StagingGlacierProcess`` DAG to run.

:syncAnywhere/requirements.txt: specifies the python libraries that are required for the internal shell script that the glacier_staging_dag runs. (This what a native Linux user would use when provisioning their environment using ``archive-ops/scripts/deployments/copyLinksToBin``) This value is hard coded. The current active GitHub branch of ``archive-ops`` is the source.

:config_dir: specifies the directory that contains the configuration files that the DAGs use. The contents of this directory are built into the image. These are values that are not necessarily secret, but must be built into the image (because they cannot be bind mounted, or accessed from secrets. BDRC developers are familiar with this content, and not much more needs can safely be said. In the first writing, the only content is the ``bdrc/auditTool`` directory.


Deploying the Runtime: ``deploy``
---------------------------------

This  ``deploy`` script step creates **or updates**  the environment that the docker compose container runs in.
The ``--dest`` argument becomes the directory that is the context in which the ``bdrc-airflow`` image runs. So, in a ``docker-compose.yaml`` statement like:

.. code-block:: yaml

    volumes:
      - ./logs:/opt/airflow/logs    # bind mount for logs

the ``.`` in ``./logs`` is the ``--dest`` directory of the ``deploy`` command.

.. code-block:: bash

    ./deploy -h
    Usage: deploy [-h|--help] -s|--source <source-dir> -d|--dest <deploy-dir> [-i|--init-env <deploy-dir>]
    Create and deployment directory for the airflow docker compose service
      -h|--help
      -s|--source <source-dir>: source directory
      -d|--dest <deploy-dir>: deployment directory
      -i|--init-env <deploy-dir>: initialize test environment AFTER creating it with --s and --d

the ``-i|--init-env`` is used standalone to build an empty tree of the RS archive for testing.
You need to manually reference its output in the bdrc-docker-compose.yaml scheduler:volumes:
The ``scheduler`` service executes the airflow DAGS, and manages the logs. Therefore,
it is the service that needs access to the host platform. The ``deploy`` script
creates this.

It creates directories in the ``build_dir`` directory:

.. code-block:: bash

    ./dags/  ./logs/ ./docker-secrets/ docker-compose.yml .env


It also:

- populates the secrets that the scheduler service needs.
      - database passwords
- AWS credentials

Note that secrets are used exclusively by Python code - other applications, such as the bash sync script need specific additions that are built into the ``bdrc-airflow`` image.


How to use deploy
-----------------

You need to deploy the runtime code into a docker environment when:
- the structure of user identity of the docker services in `bdrc-docker-compose.yml` changes
- parameters or secrets change
- you change the output of syncs (for testing)

You don't generally need to deploy the runtime code when the DAGs change. You
can update the DAGs in the running environment by copying them into the docker environment
that ``deploy`` created.

Running
-------
This section contains summaries of the scripts that run the docker environment.

#. ``bdrc-docker.sh`` builds the base airflow image. This is the image that the scheduler service runs in. This script is run when the base image needs to be rebuilt. You specify a **BUILD** directory, the script assembles prerequisites into that directory, builds the image, which the local docker platform caches. Once this is done, the build directory can be deleted.

    - Use cases:
       - Installing a new version of:
            - audit tool
            - syncAnywhere script library
            - syncAnywhere python dependencies
            - DAG code needs new Python dependencies
        - creating new volumes in the image.

#.  ``deploy`` creates  or updates a docker compose container from the image and other environmental variables. The  the runtime environment. If you are simply updating the code in a DAG, you can simply run ``deploy`` against the running container.

    - Use cases:
        - Changing the code in a DAG
        - Changing the environment variables in .env
        - Changing secrets

Once you have completed the ``deploy`` step, you can ``cd <dest>`` and run ``docker-compose up -d`` to start the docker image.

.. warning::

    The ``deploy`` script either creates or updates the directory named in the ``--dest`` argument. Once the docker compose is running, if you remove the directory, the docker compose will break.

.. tip::

    If you want to update the DAGs, you can simply make your changes in the development archive, and run ``deploy`` into the running container. Airflow can automatically re-scan the DAGS and update changes. You do not need to restart the container.



.. _docker-concepts:

Docker concepts
===============

This platform was developed with reference to:
Reference documentation for Airflow on Docker is found at:
`Running Airflow in Docker <https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html>`_

The code that implements this stage is in the `airflow-docker` folder in this project.

Volumes
-------

The most significant interface between docker and its host (one of our Linux servers, where
the output of the process lands) is in ``airflow-docker/bdrc-docker-compose.yml`` :

.. code-block:: yaml

    volumes:
      # System logs
      - ./logs:/opt/airflow/logs
      # bind mount for download sink. Needed because 1 work's bag  overflows
      # the available "space" in the container.
      # See dags/glacier_staging_to_sync.py:download_from_messages
      #
      # IMPORTANT: Use local storage for download and work. For efficiency
      - ${ARCH_ROOT:-.}/AO-staging-Incoming/bag-download:/home/airflow/bdrc/data
      # For testing on local mac. This is a good reason for not
      # using files, but a service. Note this folder has to match test_access_permissions.py
      #  - /mnt/Archive0/00/TestArchivePermissions:/home/airflow/extern/Archive0/00/TestArchivePermissions
      # ao-workflows-18 - dip_log match fs
      - ${ARCH_ROOT:-/mnt}:/mnt


The above fragment links **host (real world)** directories to **container (internal to scheduler service)** directories.

Secrets
-------

This segment specifies secrets handling. Note that bdrc utilities Python modules had to be changed
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

Persistent data
---------------
You can use volumes to create areas in docker that store persistent data. this data
persists across container lifecycles. This is useful for the airflow database and the
work files, but is only available to docker.

You use **bind mount points** to map a host platform
directory to a container directory.
This is how to export data (such as files) from a docker container. This project does not use any persistent data

