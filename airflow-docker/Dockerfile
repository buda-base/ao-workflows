# create custom container for bdrc airflow scheduler
# +5 Github Copilot
# Use the original image as a base
FROM apache/airflow:2.8.1-python3.11
ARG SYNC_SCRIPTS_HOME
# Install pip - DNA on some macos dockers
# RUN apt-get update && apt-get install -y python3-pip


# Copy specific scripts for the sync operation
RUN echo "Copying sync scripts from $SYNC_SCRIPTS_HOME"
RUN mkdir -p /opt/airflow/sync-scripts
COPY $SYNC_SCRIPTS_HOME /opt/airflow/sync-scripts
COPY  ./StagingGlacierProcess-requirements.txt /opt/airflow/sync-scripts
# RUN chown -R airflow:airflow /opt/airflow/sync_scripts
# Install sync dependencies
RUN pip3 install -r /opt/airflow/sync-scripts/sync-requirements.txt

# Install Glacier staging dependencies
RUN pip3 install -r /opt/airflow/sync-scripts/StagingGlacierProcess-requirements.txt

# Make the sync_scripts accessible.
ENV PATH="${PATH}:/opt/airflow/sync_scripts"