
# Airflow on docker

## sources

### See	Trello
https://trello.com/c/YFL70YiJ
### Docker
[Installing Docker on Debian using the repository](https://docs.docker.com/engine/install/debian/#install-using-the-repository)

See also [Docker post-install](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
about creating the docker group, so you can 

### Airflow
[Apache install Airflow on Docker](https://airflow.apache.org/docs/apache-airflow/2.0.1/start/docker.html)

`curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.0.1/docker-compose.yaml`
Also, the 'Installing Docker' page (above) is wrong.
It results in the install spewing
```shell
airflow-airflow-init-1  | ValueError: Unable to configure handler 'processor': [Errno 13] Permission denied: '/opt/airflow/logs/scheduler'
```

Because the page doesn't tell you about the 'Docker post-install' docker group.
Also, its directive to
```shell
mkdir ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```
doesn't say that the full paths to `dags` `logs` and `plugins` has to be in the yaml\
(TOTH to [stackOverflow](https://stackoverflow.com/questions/59412917/errno-13-permission-denied-when-airflow-tries-to-write-to-logs) )

```shell
  volumes:
    - /home/Hargulatrix/airflow/dags:/opt/airflow/dags
    -  /home/Hargulatrix/airflow/logs:/opt/airflow/logs
    -  /home/Hargulatrix/airflow/plugins:/opt/airflow/plugins
```
(I also made these dirs 775 so the docker group, to which I added myseld)

```shell
docker compose up airflow-init
....
airflow-airflow-init-1  | Admin user airflow created
airflow-airflow-init-1  | 2.0.1
airflow-airflow-init-1 exited with code 0
```

then check:

```shell
❯ docker images
REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
redis            latest    2f66aad5324a   36 hours ago    117MB
postgres         13        b7424fa040a0   38 hours ago    373MB
apache/airflow   2.0.1     369caa46a074   12 months ago   881MB
hello-world      latest    feb5d9fea6a5   16 months ago   13.3kB

```
