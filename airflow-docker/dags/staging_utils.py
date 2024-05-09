#!/usr/bin/env python3
"""
Utilities for glacier staging
"""
import pprint
import sys
from pathlib import Path
import configparser
import boto3
import dateutil
import pendulum


# iterate over a list of classes and return if any of them satisfies the match_class function
def match_any_event_class(subject: str, event_classes: [str]) -> bool:
    """
    match_class for a list of classes
    """
    # Iterate over the list of classes
    for class_ in event_classes:
        # If the subject matches the class, return True
        if match_class(subject, class_):
            return True
    return False

def match_class(subject: str, class_: str) -> bool:
    """
    Test to see if a colon separated tuple is a member of a class,
    defined by a colon separated tuple.
    The second element of the class_ tuple is either a token or a wildcard character,
    defined using the character *.
    In this case, if the subject's first token matches the class' first token, the subject matches.
    Otherwise, the whole second token must match
    :param subject: colon separated tuple to test
    :param class_: colon separated tuple - definition of possible matches
    :return: True if the subject matches the class
    """
    # Split the subject and class into tokens
    subject_tokens = subject.split(':')
    class_tokens = class_.split(':')

    # If the first token of the subject matches the first token of the class, the subject matches the class
    return ((subject_tokens[0] == class_tokens[0])
            and ( class_tokens[1] == '*'
                  or subject_tokens[1] == class_tokens[1]))



def create_session(creds_section_name: str) -> boto3.Session:
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


class DipOpCodes():
    RESTORED: int = 0
    DOWNLOADED: int = 1
    DEBAGGED: int = 2
    SYNCD: int = 3

def db_phase(op_code: str, work_rid: str, user_data:{} = None):
    """
    record the operation in the progress db
    :param record: work_rid: search term of item to updatekey
    """
    from GlacierSyncProgress import GlacierSyncProgress
    from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
    from sqlalchemy.exc import NoResultFound

    op_time: pendulum.DateTime = pendulum.now()

    gsp: GlacierSyncProgress = GlacierSyncProgress()
    gsp_found:bool = False

    with DrsContextBase() as drs:
        gsp: GlacierSyncProgress
        try:
            gsp = drs.query(GlacierSyncProgress).filter(GlacierSyncProgress.work_rid == work_rid).one()
            gsp_found = True
        except NoResultFound:
            gsp = GlacierSyncProgress()
            gsp.object_name = work_rid
            gsp.user_data = list(user_data)
            drs.add(gsp)
            drs.commit()

        if op_code == DipOpCodes.RESTORED:
            gsp.restore_complete_on = op_time
        elif op_code == DipOpCodes.DOWNLOADED:
            gsp.download_complete_on = op_time
        elif op_code == DipOpCodes.DEBAGGED:
            gsp.download_debagged_on = op_time
        elif op_code == DipOpCodes.SYNCD:
            gsp.sync_complete_on = op_time

        # Concatenate user data to existing, if given
        if gsp_found and user_data:
            gsp.phase_data = user_data
        drs.commit()


# DEBUG: Local
if __name__ == '__main__':
    #     sqs = create_session('default').client('s3')
    #     print(sqs.list_buckets())
    path_to_credentials = Path(sys.argv[1])
    section = sys.argv[2] if len(sys.argv) > 2 else 'default'
    o_section = get_aws_credentials(path_to_credentials, section)
    for x in o_section.keys():
        pprint.pprint(f"{section}[{x}]={o_section[x]}")
