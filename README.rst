=====================
AO Workflow on Docker
=====================

There are two principal components in this project:

#. Docker
#. Airflow

Docker
======

There are two steps in building docker.

Reference documentation for Airflow on Docker is found at:
`Running Airflow in Docker <https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html>`_

The code that implements this stage is in the `airflow-docker` folder in this project.
The major high-level steps are:

1.  Build a docker image from an airflow-approved source. This is accomplished in the
``build-docker-image.sh`` script. This script

    #. Prepares the requirements for the airflow dag: There are two classes:

        * What the code inside the airflow DAG needs to run.
        * What the code external to airflow needs.

    #. Launches the build of the image.

2. Build a docker :strong:`container` out of the built image.
This step provisions the various services that makeup airflow.

Building the Airflow Docker image
--------------------------------------------------------------------------------
``build-bdrc-airflow.sh``
This script:

* downloads ``audit-tool``
* acquires the ``archive-ops/scripts/syncAnywhere/deployment`` scripts
* Merges the ``archive-ops`` and ``StagingGlacierProcess`` requirements (pyPI packages) into one file.
* Invokes the Dockerfile, which:

    * Copies the ``audit-tool, deployment`` scripts into the image
    * Generates the python dependencies
    * Installs the above into the container

Note there are two sets of dependencies in use:
``airflow-docker/StagingGlacierProcess-requirements.txt`` and ``archive-ops/requirements.txt``.
The former is used by the DAGs, the latter by the ``syncOneWork.sh`` that the ``sync_debagged``
task invokes. Since all that work is done in a shell outside of airflow, airflow doesn't need
to support it, but the container does.

Building the Airflow Docker container
--------------------------------------------------------------------------------
**Operational steps**

``run-bdrc-airflow.sh`` copies credential files into a local directory that is linked to the docker container
that hosts the image.

**``docker-compose.yml``**

The ``docker-compose.yml`` file is the configuration file for the services that make up the airflow instance.
Most of it is boilerplate (from the O'Reilly "Data Pipelines in Airflow" book - the sections that support our workflow are:


..code-block:: yaml
    :caption: scheduler mount points
    :name: source: docker-compose.yml (1)
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
to the service. Note that other services **cannot** access these secrets, without access from this file

..code-block:: yaml
   :caption: secrets
   :name: source: docker-compose.yml (2)


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

Running the Airflow Docker container
--------------------------------------------------------------------------------
After the above steps, ``docker-compose up -d`` (the ``-d`` flag just launches the services in the background.

