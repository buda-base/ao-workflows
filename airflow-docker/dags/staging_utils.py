#!/usr/bin/env python3
"""
Utilities for glacier staging
"""
import pprint
from pathlib import Path
import configparser
import boto3
import pendulum
from pprint import pp

from sqlalchemy import desc

# ------------------    CONST --------------------
RUN_SECRETS: Path = Path("/run/secrets")


# ------------------    /CONST --------------------


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
            and (class_tokens[1] == '*'
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
    if not Path.exists(RUN_SECRETS):
        print('No secrets found, using local credentials')
        ases = boto3.Session(profile_name=creds_section_name)
    else:
        print('using secrets')
        # See ../airflow-docker/docker-compose.yml
        #        creds_section = get_aws_credentials(Path('/run/secrets/aws'), creds_section_name)
        creds_section = get_aws_credentials(RUN_SECRETS / "aws", creds_section_name)
        ases = boto3.Session(aws_access_key_id=creds_section['aws_access_key_id'],
                             aws_secret_access_key=creds_section['aws_secret_access_key'],
                             region_name=creds_section['region_name'])
    return ases


def get_db_config(prefix: str = 'prod') -> str:
    """
    Get the config path for db
    :return:
    """
    if not Path.exists(RUN_SECRETS):
        return f"{prefix}:~/.config/bdrc/db_apps.config"
    else:
        print('using secrets')
        return f"{prefix}:/run/secrets/db_apps"


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


class GlacierSyncOpCodes():
    RESTORED: int = 0
    DOWNLOADED: int = 1
    DEBAGGED: int = 2
    SYNCD: int = 3


def db_phase(op_code: str, work_rid: str, user_data: {} = None):
    """
    record the operation in the progress db
    :param op_code: operation (See GlacierSyncOpCodes
    :param work_rid: object to track
    :param user_data: details of the operation
    """
    from GlacierSyncProgress import GlacierSyncProgress
    from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
    from sqlalchemy.exc import NoResultFound

    op_time: pendulum.DateTime = pendulum.now()

    gsp: GlacierSyncProgress = GlacierSyncProgress()
    gsp_found: bool = False

    with DrsDbContextBase(get_db_config('qa')) as drs:
        sess = drs.get_session()

        gsp = sess.query(GlacierSyncProgress).filter(GlacierSyncProgress.object_name == work_rid).order_by(
            desc(GlacierSyncProgress.update_time)).first()
        if not gsp:
            gsp = GlacierSyncProgress()
            gsp.object_name = work_rid
            sess.add(gsp)

        if op_code == GlacierSyncOpCodes.RESTORED:
            gsp.restore_complete_on = op_time
        elif op_code == GlacierSyncOpCodes.DOWNLOADED:
            gsp.download_complete_on = op_time
        elif op_code == GlacierSyncOpCodes.DEBAGGED:
            gsp.debag_complete_on = op_time
        elif op_code == GlacierSyncOpCodes.SYNCD:
            gsp.sync_complete_on = op_time

        # Concatenate user data to existing
        gsp.update_user_data(op_time.to_rfc3339_string(), user_data)
        sess.commit()


def work_rid_from_aws_key(aws_key: str) -> str:
    """
    Extract the work_rid from an aws key
    :param aws_key: aws key to extract from can be {parent/.../}*Work_rid.any.number.suffixes
    :return: work_rid
    """
    basename: Path = Path(aws_key.split('/')[-1])
    while basename.suffix:
        basename = basename.with_suffix('')
    return basename.name


# DEBUG: Local
if __name__ == '__main__':
    #     sqs = create_session('default').client('s3')
    #     print(sqs.list_buckets())
    # path_to_credentials = Path(sys.argv[1])
    # section = sys.argv[2] if len(sys.argv) > 2 else 'default'
    # o_section = get_aws_credentials(path_to_credentials, section)
    # for x in o_section.keys():
    #     pprint.pprint(f"{section}[{x}]={o_section[x]}")

    pp(work_rid_from_aws_key('freem/bladd/bla'))
    pp(work_rid_from_aws_key('bla'))
    pp(work_rid_from_aws_key('bla.goy.evitch'))
    pp(work_rid_from_aws_key('s3:/lsdfsdf/bla.goy.evitch'))
