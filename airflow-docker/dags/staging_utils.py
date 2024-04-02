#!/usr/bin/env python3
"""
Utilities for glacier staging
"""
import pprint
import sys
from pathlib import Path
import configparser
import boto3


def create_session(creds_section_name: str = 'default') -> boto3.Session:
    """
    Determine where aws credentials come from - if local, use it.
    if docker, use that
    :param creds_section_name: Section name to read
    :return: Session using the credentials
    """
    # Open a secrets file and pour it into a config object
    # if /run/secrets exists, it is a docker secret
    # Otherwise, just open from whatever the system is
    ppfx: Path = Path("/run/secrets")
    # DEBUG local - See ../airflow-docker/build-xxx
    # ppfx: Path = Path("/Users/jimk/dev/ao-workflows/airflow-docker/.secrets")
    if not Path.exists(ppfx):
        print('No secrets found, using local credentials')
        ases = boto3.Session(profile_name=creds_section_name)
    else:
        print('using secrets')
        # See ../airflow-docker/docker-compose.yml
        #        creds_section = get_aws_credentials(Path('/run/secrets/aws'), creds_section_name)
        creds_section = get_aws_credentials(ppfx / "aws", creds_section_name)
        ases = boto3.Session(aws_access_key_id=creds_section['aws_access_key_id'],
                             aws_secret_access_key=creds_section['aws_secret_access_key'],
                             region_name=creds_section['region_name'])
    return ases


# TODO: Left off here, change this to creating a connection (See ao-workflows!14 comment)
def create_aws_conn(creds_section_name: str = 'default') -> boto3.Session:
    """
    Determine where aws credentials come from - if local, use it.
    if docker, use that
    :param creds_section_name: Section name to read
    :return: Session using the credentials
    """
    # Open a secrets file and pour it into a config object
    # if /run/secrets exists, it is a docker secret
    # Otherwise, just open from whatever the system is
    ppfx: Path = Path("/run/secrets")
    # DEBUG local - See ../airflow-docker/build-xxx
    # ppfx: Path = Path("/Users/jimk/dev/ao-workflows/airflow-docker/.secrets")
    if not Path.exists(ppfx):
        print('No secrets found, using local credentials')
        ases = boto3.Session(profile_name=creds_section_name)
    else:
        print('using secrets')
        # See ../airflow-docker/docker-compose.yml
        # and ../airflow-docker/deploy (which creates the secrets file
        #        creds_section = get_aws_credentials(Path('/run/secrets/aws'), creds_section_name)
        creds_section = get_aws_credentials(ppfx / "aws", creds_section_name)
        ases = boto3.Session(aws_access_key_id=creds_section['aws_access_key_id'],
                             aws_secret_access_key=creds_section['aws_secret_access_key'],
                             region_name=creds_section['region_name'])
    return ases


def get_aws_credentials(cred_file: Path, section: str = 'default') -> {}:
    """
    Get AWS credentials from a file
    :param cred_file: Path to an ini file thatr configparser can read
    :param section: Section to read
    :type section: object
    :type cred_file: pathlib.Path
    """

    # DEBUG:
    # with open(cred_file, 'r') as f:
    #     print(f.read())

    _configParser = configparser.ConfigParser()
    _configParser.read(cred_file)
    print(f"{section=}   {_configParser.sections()}")
    return _configParser[section]


# DEBUG: Local
if __name__ == '__main__':
    #     sqs = create_session('default').client('s3')
    #     print(sqs.list_buckets())
    path_to_credentials = Path(sys.argv[1])
    section = sys.argv[2] if len(sys.argv) > 2 else 'default'
    o_section = get_aws_credentials(path_to_credentials, section)
    for x in o_section.keys():
        pprint.pprint(f"{section}[{x}]={o_section[x]}")
