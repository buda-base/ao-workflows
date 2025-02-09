#!/usr/bin/env python3
"""
Utilities to generate sync options for syncOneWork.sh
/Users/jimk/bin/syncOneWork.sh: illegal option -- -
Synopsis:syncOneWork.sh  [ -h ] [-A] [-W] [ -a archiveParent ] [ -w webParent ] [ -s successWorkList ] workPath
  Options:
      -h help:            This message
      -A:                 Overwrite entire archive tree with source
      -W:                 Overwrite entire web tree with source
      -h help:            This message
      -a archiveParent:   sync to file system, under archiveParent
      -w webParent:       sync images/ to S3 bucket at webParent. Requires -s
      -s successWorkPath  path to a file which contains work RIDS for which the operations(s) have succeeded.
                          Required when -w is given
      workPath:           path to text to sync (e.g. /mnt/audit-Incoming/W666)

      If -a and -w are not given, only runs audit tool.

      this module populates the -A -a -W -w flags, and declares any environment variables represented by the parser
      (such as
"""
import os
from pathlib import Path
import yaml
from pendulum import DateTime
import logging
LOG = logging.getLogger("airflow.task")

from staging_utils import get_db_config


class SyncOptionsBuilder:
    """
    Transforms a yaml into a dictionary/?list? of syncOneWork.sh flags

    """


# ---------------   CONSTS  --------------------------------
# See docker-compose.yml for the location of the system logs. Should be a bind mount point
# ./bdr.log:/mnt/processing/logs
APP_LOG_ROOT = Path.home() / "bdrc" / "log"

util_ver: str
from util_lib.version import bdrc_util_version

# noinspection PyBroadException
try:
    util_ver: str = bdrc_util_version()
except:
    util_ver = "Unknown"

# SYNC config
#
# Use this file if it is under the Work root
DEFAULT_SYNC_YAML_PATH: Path = Path("config", "sync.yml")
DEFAULT_SYNC_YAML: str = """
audit:
    # Empty means run all tests, no extra args
    # Fill in with python array: [ '-D','Bladdbla=yyssw' ,'-T','Test1,Test2,Test3' ...]
    pre: []
    post: []
sync:
    archive: true
    web: true
    replace: false
    update_web: true
"""

# map the AYAML to syncOneWork environment variables
DEFAULT_YAML_ENVS: {} = {'pre': 'LOCAL_AUDIT_OPTIONS',
                         'post': 'REPO_AUDIT_OPTIONS',
                         # special case - see syncAnywhere_options
                         'update_web': 'NO_REFRESH_WEB'
                         }

# Example yaml. this is the mapping of yaml defaults to environment variables and command arguments
#     test = """
# audit:
#     # Empty means run all tests
#     # Fill in with python array: [ '-D' 'bladd'test1','test2' ...]
#     pre: [] -> env: LOCAL_AUDIT_OPTIONS
#     post: [] -> env: REPO_AUDIT_OPTIONS
# sync:
#     archive: true -> "-a"
#     web: true -> "-w"
#     replace: false -> "-A -W" if true
#    special case hack
#     update_web: false -> env: NO_REFRESH_WEB=True
# """
# N.B. depends on syncOneWork
SYNC_COMMAND_ARG_MAP: {} = {
    '-a': None,
    '-w': None
}


# ---------------   /CONSTS --------------------------------

def build_arg_map(archive_dest: os.PathLike, web_dest: str, arg_map: {}):
    """
    Fill in defaults from caller
    :param archive_dest: where archives go
    :param web_dest: where web images go
    :param arg_map: dictionary to update
    :return:
    """
    arg_map['-a'] = str(archive_dest)
    arg_map['-w'] = str(web_dest)


deep_search_results: object = None


# +3 GitHub Copilot
def deep_search(dictionary, key) -> object:
    """
    Recursively search for a key in a dictionary or in dictionaries contained in the values.
    :param dictionary: The dictionary to search.
    :param key: The key to search for.
    :return: the first value found for the key
    """

    global deep_search_results

    def search(d):
        global deep_search_results
        if isinstance(d, dict):
            for k, v in d.items():
                if deep_search_results:
                    break
                if k == key:
                    deep_search_results = v
                    return
                if isinstance(v, dict):
                    search(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            search(item)

    deep_search_results = None
    search(dictionary)
    return deep_search_results
    # return results


def get_sync_options(sync_config_path: Path, default_config: str) -> {}:
    """
    Parse the yaml file, merging it with the dictionary resulting from the default. values in the
    sync_config_path take precedence over the default_config, but the sync_config_path yaml need not
    be complete
    :param sync_config_path: Path to user provided sync overrides
    :param default_config: the default yaml as a string
    :return: the default_config dictionary with the sync_config_path values merged in
    """
    import yaml
    base_doc = yaml.safe_load(default_config)
    if sync_config_path and os.path.exists(sync_config_path):
        override_doc = yaml.safe_load(sync_config_path.read_text())
        merge_yaml(base_doc, override_doc)

    return base_doc


def merge_yaml(base: {}, override: {}):
    """
    Merge two yaml files, base and override. If a value appears in override, replace it in base.
    Do this search recursivley through all levels of the yaml files
    :param base: base yaml
    :param override: override yaml
    :return: merged yaml file in :param base
    """
    for key, value in override.items():
        if isinstance(value, dict):
            # get node from base
            node = base.setdefault(key, {})
            # merge recursively
            merge_yaml(node, value)
        else:
            # replace or add value
            base[key] = value


def build_sync_env(execution_date, prod_level: str, db_config: os.PathLike) -> dict:
    """
    See sync task
       You have to emulate this stanza in bdrcSync.sh to set logging paths correctly
    # tool versions
    export logDipVersion=$(log_dip -v)
    export auditToolVersion=$(audit-tool -v)

    # date/time tags
    export jobDateTime=$(date +%F_%H.%M.%S)
    export jobDate=$(echo $jobDateTime | cut -d"_" -f1)
    export jobTime=$(echo $jobDateTime | cut -d"_" -f2)

    # log dirs
    # NOTE: these are dependent on logDir which is declared in the config file
    export syncLogDateTimeDir="$logDir/sync-logs/$jobDate/$jobDateTime"
    export syncLogDateTimeFile="$syncLogDateTimeDir/sync-$jobDateTime.log"
    export syncLogTempDir="$syncLogDateTimeDir/tempFiles"

    export auditToolLogDateTimeDir="$logDir/audit-test-logs/$jobDate/$jobDateTime"
    """

    # set up times
    year, month, day, hour, minute, second, *_ = execution_date.timetuple()

    # sh: $(date +%F_%H.%M.%S)
    job_time: str = f"{hour:0>2}.{minute:0>2}.{second:0>2}"
    # sh: $(date +%F)
    job_date: str = f"{year}-{month:0>2}-{day:0>2}"
    # $(date +%F_%H.%M.%S)
    job_date_time: str = f"{job_date}_{job_time}"

    # DEBUG: make local while testing
    # _root: Path = Path.home() / "dev" / "tmp" / "Projects" / "airflow" / "glacier_staging_to_sync" / "log"
    logDir: Path = APP_LOG_ROOT
    sync_log_home: Path = logDir / "sync-logs" / job_date / job_date_time
    sync_log_file = sync_log_home / f"sync-{job_date_time}.log"
    audit_log_home: Path = logDir / "audit-test-logs" / job_date / job_date_time
    os.makedirs(sync_log_home, exist_ok=True)
    os.makedirs(audit_log_home, exist_ok=True)

    env: {} = {
        "DEBUG_SYNC": "true",
        "DB_CONFIG": get_db_config(prod_level),
        "hostName": "airflow_platform",
        "userName": "airflow_platform_user",
        "logDipVersion": util_ver,
        "auditToolVersion": "unknown",
        "jobDateTime": job_date_time,
        "jobDate": job_date,
        "jobTime": job_time,
        "auditToolLogDateTimeDir": str(audit_log_home),
        "syncLogDateTimeDir": str(sync_log_home),
        "syncLogDateTimeFile": str(sync_log_file),
        "syncLogTempDir": str(sync_log_home / "tempFiles"),
        "PATH": os.getenv("PATH")

    }

    # jimk aow32: provide aws credentials only under docker
    if os.path.exists("/run/secrets/aws"):
        env['AWS_SHARED_CREDENTIALS_FILE'] = '/run/secrets/aws'



    LOG.info(f" sync environment: {env}")

    return env


def syncAnywhere_options(sync_options: {}, yaml_map) -> {}:
    """
    Build environment variables implied in the map. Returns a yaml parsed like dictionary
    { 'env': { 'LOCAL_AUDIT_OPTIONS': 'value', 'REPO_AUDIT_OPTIONS': 'value', 'NO_REFRESH_WEB': 'value' },
    'sync': [ '-a' , '-w' , '-A -W''}
    """

    rd: {} = {}
    env = {}

    # Look in directive_map (user input or default) for the keys in the yaml_map
    # you have to do an in depth search
    for target_key, value in yaml_map.items():
        # tearget_key_values holds the user input, crated in sync_options
        target_key_values: [] = deep_search(sync_options, target_key)
        if not target_key_values:
            continue
        # if the value is empty, we don't want to emit it.
        # We only want to emit a scalar value
        # And we want it to be a str, otherwise the Python subprocess parser:
        #     env_list.append(k + b'=' + os.fsencode(v))
        #             ^^^^^^^^^^^^^^
        # File "<frozen os>", line 812, in fsencode
        # TypeError: expected str, bytes or os.PathLike object, not bool
        #
        # HACK ALERT: the 'update_web' key is a special case - it should
        # set the NO_REFRESH_WEB only if its value is 'False'
        # yaml should be   update_web: { true | false }
        if target_key == 'update_web':
            if not target_key_values:
                env[DEFAULT_YAML_ENVS[value]] = 'Yes'
        else:
            # if len(target_key_values) == 1 and target_key_values[0]:
            env[value] = flatten_list(target_key_values)

    # Create the env key
    rd['env'] = env

    # Get the archive command value
    _ = deep_search(sync_options, 'archive')
    if _:
        rd['sync'] = ['-a']
    else:
        rd['sync'] = []
    _ = deep_search(sync_options, 'web')
    if _:
        rd['sync'].append('-w')

    # The relpace key has a boolean arg
    _ = deep_search(sync_options, 'replace')
    if _:
        rd['sync'].append('-A -W')
    return rd


# flatten a possibly nested list of lists into a single string, with a space between every detected list element, but the list elemnts preserverd
def flatten_list(nested_list: []) -> str:
    """
    Flatten a possibly nested list of lists into a single string, space separated
    :param nested_list: list of lists
    :return: flattened list
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            # flat_list.extend(flatten_list(item))
            flat_list.append(flatten_list(item))
        else:
            flat_list.append(item)
    return ' '.join(str(x) for x in flat_list)


def build_dest_args(cmd_params: [], cmd_param_map: {}) -> str:
    """
    Build destinations arguments to syncOneWork.sh
    :param cmd_params: given parameters
    :param cmd_param_map: maps parameters to arguments
    :return: assembled proper command string
    """
    base: str = ''
    for cmd_arg in cmd_params:
        # Not all possible commands have argumentsm so use .get()
        # If any of the keys would result in multiple token in bash, wrap them up
        cmd_arg_value = cmd_param_map.get(cmd_arg, None)
        base += f" {cmd_arg} "
        if cmd_arg_value:
            base += f"{encode_for_bash(cmd_arg_value)}"
    return base


def encode_for_bash(string):
    import shlex
    return shlex.quote(string) if string else string


def build_sync(start_time: DateTime, prod_level, src: os.PathLike, archive_dest: os.PathLike,
               web_dest: str) -> ():
    """
    Build command and environment for airflow BashOperator
    :return: (environment, command_string
    """
    build_arg_map(archive_dest, web_dest, SYNC_COMMAND_ARG_MAP)
    directives_dict = get_sync_options(Path(src, DEFAULT_SYNC_YAML_PATH), DEFAULT_SYNC_YAML)
    # rebuild the env for each work - the local config file may have something to add
    env: {} = build_sync_env(start_time, prod_level, get_db_config(prod_level))

    # Get extra environment and command strings from the sync config
    command_extras: [] = syncAnywhere_options(directives_dict, DEFAULT_YAML_ENVS)
    if command_extras.get('env'):
        env.update(command_extras['env'])
    # Build the sync command
    # Build the sync destination strings
    dest_cmd_args: str = build_dest_args(command_extras.get('sync'), SYNC_COMMAND_ARG_MAP)
    # HACK ALERT: do not quote {dest_cmd_args} the constants have to take care of this
    #
    # Unneded diagnostics you can insert into the command string
    # set -vx
    # pip show bdrc-util
    # pip show bdrc-db-lib
    # which syncOneWork.sh
    # echo $PATH
    #
    # The moustaches {{}} inject a literal { or }, not an fString resolution
    bash_command = f"""
#!/usr/bin/env bash
syncOneWork.sh -s $(mktemp) {dest_cmd_args} "{src}" 2>&1 | tee $syncLogDateTimeFile
rc=${{PIPESTATUS[0]}}
exit $rc
"""
    return env, bash_command


if __name__ == '__main__':
    # Just test stubs here
    # pp(f"Empty string: {encode_for_bash('')}")
    # pp(f"Live string {encode_for_bash('helloWorld')}")
    # pp(f"space string {encode_for_bash('hello World')}")
    pass
#     MSY: str = """
# sync:
#     web: false
#     bladd: true
# """
#     dsy: {} = yaml.safe_load(DEFAULT_SYNC_YAML)
#     msy: {} = yaml.safe_load(MSY)
#     merge_yaml(dsy, msy)
#
#     sync_options: {} = {'audit': {'post': ['-T', 'ImageFileNameFormat'], 'pre': ['-T', 'NoFilesInFolder']},
#                         'sync': {'archive': False, 'replace': False, 'update_web': True, 'web': True}}
#     ff = deep_search(sync_options, 'pre')
#
#     l1: [] = ['a', 'b']
#     l2: [] = ['c', ['d12', 'e34']]
#     cc = flatten_list([l1, l2])
#     print(cc)
#     example_dict = {
#         'a': 1,
#         'b': {'c': 2, 'd': {'e': 3}},
#         'f': [{'g': 4}, {'h': {'i': 5}}],
#         'j': {'k': [{'l': 6}, {'m': 7}]}
#     }
#
#     print(deep_search(example_dict, 'e'))  # Output: [3]
#     print(deep_search(example_dict, 'g'))  # Output: [4]
#     print(deep_search(example_dict, 'l'))  # Output: [6]
