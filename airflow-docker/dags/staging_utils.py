#!/usr/bin/env python3
"""
Utilities for glacier staging
"""
import os
import shutil
import fcntl

from airflow.sensors.filesystem import FileSensor
from pathlib import Path
import configparser
import re
import logging
LOG = logging.getLogger("airflow.task")

import boto3
import pendulum

from sqlalchemy import desc

# ------------------    CONST --------------------
RUN_SECRETS: Path = Path("/run/secrets")
LOCK_FILE: str = '/tmp/CollectingWatcherLock.lock'

COLLECTED_FILE_KEY: str = 'collected_file'




# ------------------    /CONST --------------------


class CollectingSingleFileSensor(FileSensor):
    """
    Returns a single file from a pool of readies. downstream users have to delete this file
    """

    def acquire_lock(self):
        lock_file = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        LOG.info(f"got lock on {LOCK_FILE=}")
        return lock_file

    def release_lock(self, lock_file):
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        LOG.info(f"released lock on {LOCK_FILE=}")

    def __init__(self, processing_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_dir: Path = Path(kwargs['filepath']).parent
        self.processing_path = processing_path

    def poke(self, context):
        import glob
        lock_file = self.acquire_lock()
        try:
            matched_files = glob.glob(self.filepath)
            if matched_files:
                # First, pick one, hide it from other sensors by moving it to in process.
                # Return the in_process version

                target_match = Path(matched_files[0])
                # Fully qualify target path. YGNI (You're going to need it)
                target_path = self.processing_path / target_match.name
                shutil.move(target_match, target_path)
                # push the moved file onto the response stack
                context['ti'].xcom_push(key=COLLECTED_FILE_KEY, value=str(target_path))
                LOG.info(f"Located {target_match} and moved to {target_path}")
                return True
            else:
                LOG.info(f"Nothing found for {self.filepath}")
                return False
        finally:
            self.release_lock(lock_file)


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


def db_phase(op_code: str, work_rid: str,  db_config: str, user_data: {} = None) -> None:
    """
    record the operation in the progress db
    :param op_code: operation (See GlacierSyncOpCodes
    :param work_rid: object to track
    :param db_config: database
    :param user_data: details of the operation
    """
    from GlacierSyncProgress import GlacierSyncProgress
    from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
    from sqlalchemy.exc import NoResultFound

    op_time: pendulum.DateTime = pendulum.now()

    gsp: GlacierSyncProgress = GlacierSyncProgress()
    gsp_found: bool = False

    with DrsDbContextBase(get_db_config(db_config)) as drs:
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

        LOG.info(f"Updating {gsp.object_name} with {op_code} at {op_time}")
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



# -----------------  mocks for testing / debugging ------------------------
# Set up this copy for mock objects, because debagging is destructive
# removed - just set a bag zip file in AWS s3 and set up mock_message to get it
# mock_downloads: [str] = [
#     str(shutil.copy(BASE_PATH / "save-W1FPL2251.bag.zip", DOWNLOAD_PATH / "miniW1FPL2251.bag.zip"))]

mock_message: [] = [
    dict(
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "ap-northeast-2",
            "eventTime": "2024-04-06T00:11:23.730Z",
            "eventName": "ObjectRestore:Completed",
            "userIdentity": {
                "principalId": "AmazonCustomer:A1JPP2WW1ZYN4F"
            },
            "requestParameters": {
                "sourceIPAddress": "s3.amazonaws.com"
            },
            "responseElements": {
                "x-amz-request-id": "439897F6741FD9BA",
                "x-amz-id-2": "MF0oW9le+g8K5/R/uUks1QuFbZxNuSmZDWQ5utu8ZTcHEKSGFHzdFBEtebICzrPtG3YL1YVmffxhRw4nDPTZ1w=="
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "BagCreatedNotification",
                "bucket": {
                    "name": "glacier.staging.nlm.bdrc.org",
                    "ownerIdentity": {
                        "principalId": "A1JPP2WW1ZYN4F"
                    },
                    "arn": "arn:aws:s3:::glacier.staging.nlm.bdrc.org"
                },
                "object": {
                    "key": "Archive0/00/W1NLM4700/W1NLM4700.bag.zip",
                    "size": 17017201852,
                    "eTag": "41654cbd2a8f2d3c0abc83444fde825b-2029",
                    "sequencer": "00638792A45B638391"
                }
            },
            "glacierEventData": {
                "restoreEventData": {
                    "lifecycleRestorationExpiryTime": "2024-04-12T00:00:00.000Z",
                    "lifecycleRestoreStorageClass": "DEEP_ARCHIVE"
                }
            }
        }
    )]

mock_message1: [] = [
    dict(eventVersion="2.1", eventSource="aws:s3", awsRegion="us-east-1", eventTime="2024-02-24T08:47:18.267Z",
         eventName="ObjectRestore:Completed", userIdentity={
            "principalId": "AmazonCustomer:A1JPP2WW1ZYN4F"},
         requestParameters={
             "sourceIPAddress": "s3.amazonaws.com"
         },
         responseElements={
             "x-amz-request-id": "6E5A5E04B1CFFAC5",
             "x-amz-id-2": "Tt/6gfwuhCu9X06urpzaVuNBhSv4EW47BlmS2WrViVZ+MNDLo/ckEgLqLGi02IV6L3vshvP++ps1iPp9Zl3tPQ=="
         },
         s3={
             "s3SchemaVersion": "1.0",
             "configurationId": "MGU5Zjk3MzItMjQ4Yi00MTU0LTk4ZGItNDBjYjU1MzhjMGU3",
             "bucket": {
                 "name": "manifest.bdrc.org",
                 "ownerIdentity": {
                     "principalId": "A1JPP2WW1ZYN4F"
                 },
                 "arn": "arn:aws:s3:::manifest.bdrc.org"
             },
             "object": {
                 "key": "ao1060/W1FPL2251.bag.zip",
                 "size": 78668981,
                 "eTag": "405202973fc17c6f4b26cb56022c6201-10",
                 "versionId": "vwfO4VqvGTlWeuSAtXDOhPzFhl.6YrSG",
                 "sequencer": "0065C3D18445E403D5"
             }
         },
         glacierEventData={
             "restoreEventData": {
                 "lifecycleRestorationExpiryTime": "2024-03-06T00:00:00.000Z",
                 "lifecycleRestoreStorageClass": "DEEP_ARCHIVE"
             }
         }
         )
]


# enum to contain v1 work type and v2 work type
class WorkStructureVersion():
    V0 = 0 # none
    V1 = 1
    V2 = 2

    @staticmethod
    def detect_work(w_path: Path) -> int:
        """
        Check if the directory structure matches either of the two specified types.
        :param w_path: Path to the top level folder 'WorkName'
        :return: True if the directory structure matches either type, False otherwise
        """
        if not w_path.is_dir():
            return WorkStructureVersion.V0

        # Define the possible child folder names
        possible_folders = {'archive', 'sources', 'images', 'eBooks', 'sync-inventory'}

        # Check for the first structure type
        for child in w_path.iterdir():
            if child.is_dir() and child.name in possible_folders:
                return WorkStructureVersion.V1

        # Check for the second structure type
        image_group_name_re = re.compile(rf"{w_path.name}-I.*")
        for child in w_path.iterdir():
            if child.is_dir() and image_group_name_re.fullmatch(child.name):
                for sub_child in child.iterdir():
                    if sub_child.is_dir() and sub_child.name in possible_folders:
                        return WorkStructureVersion.V2

        return WorkStructureVersion.V0

def empty_contents(path: Path) -> None:
    """
    Empty the contents of a directory
    :param path:
    :return:
    """
    if os.path.exists(path) and os.path.isdir(path):
        for p in os.scandir(path):
            if p.is_dir():
                shutil.rmtree(p)
            elif p.is_file():
                os.remove(p.path)
    else:
        path.mkdir(parents=True, exist_ok=True)

def iter_or_return(obj):
    """
    Github Copilot suggestion to return an object or the next
    iteration
    :param obj: onput
    :return: input of input is not iterable, else next iteration
    """
    try:
        iter(obj)
    except TypeError:
        yield obj
    else:
        yield from obj


def atomic_copy(targets:[(Path, Path)]):
    """Copies a set of filessaving the renames until the all the copies is complete
    :param targets: tuples of source and destination pairsSource file to copy
    :param dst: Destination file to copy to
    """
    import tempfile
    import sys
    # Create a temporary file in the same directory as the destination
    to_rename:[] = []
    for src, dst in targets:

        dir_name, base_name = os.path.split(dst)
        with tempfile.NamedTemporaryFile(dir=dir_name, delete=False) as tmp_file:
            temp_name = tmp_file.name

        try:
            # Copy the source file to the temporary file
            LOG.info(f"Copying {src} to {temp_name}")
            shutil.copyfile(src, temp_name)
            # Rename the temporary file to the destination file
            LOG.info(f"Renaming {temp_name} to {dst}")
            to_rename.append((temp_name, dst))
            LOG.info("atomic copy complete")
        except Exception as e:
            # Clean up the temporary file in case of an error
            LOG.exception(f"Error copying {src} to {dst}", exc_info=sys.exc_info())
            os.remove(temp_name)
            raise e

    # Now that all are copied, rename them all
    rename_exceptions: bool = False
    for temp_name, dst in to_rename:
        try:
            os.rename(temp_name, dst)
        except Exception as e:
            rename_exceptions = True
            LOG.exception(f"Error moving {str(temp_name)} to {str(dst)}", exc_info=sys.exc_info())
            try:
                os.remove(temp_name)
            except Exception as e:
                LOG.exception(f"Error removing {str(temp_name)}", exc_info=sys.exc_info())
            # Clean up the temporary file in case of an error

    if rename_exceptions:
        raise IOError("Error atomic copy renamed files. See log.")




# GitHub Copilot suggestion to get around "directory not empty" error

def remove_readonly(func, path, _):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


def pathable_airflow_run_id(possible: str) -> str:
    """
    transforms a run if into a path that can be used in a shell, by removing characters which could be operands
    :param possible:
    :return: the predecessor of any "+" in the string
    """
    parseable: str =  possible.replace("+", "Z")
    #
    # remove the "scheduled__" or "manual__" prefix
    skip_path= r"^.*__"
    return re.sub(skip_path, "", parseable)

# DEBUG: Local
if __name__ == '__main__':
    pass
    #     sqs = create_session('default').client('s3')
    #     print(sqs.list_buckets())
    # path_to_credentials = Path(sys.argv[1])
    # section = sys.argv[2] if len(sys.argv) > 2 else 'default'
    # o_section = get_aws_credentials(path_to_credentials, section)
    # for x in o_section.keys():
    #     pprint.pprint(f"{section}[{x}]={o_section[x]}")
    #
    # pp(work_rid_from_aws_key('freem/bladd/bla'))
    # pp(work_rid_from_aws_key('bla'))
    # pp(work_rid_from_aws_key('bla.goy.evitch'))
    # pp(work_rid_from_aws_key('s3:/lsdfsdf/bla.goy.evitch'))


