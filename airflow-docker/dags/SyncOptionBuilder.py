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
from pathlib import Path

import yaml

class SyncOptionsBuilder():
    """
    Transforms a yaml into a dictionary/?list? of syncOneWork.sh flags

    """


def get_sync_options(sync_config_path: Path, default_config: str) -> {}:
    """
    Parse the yaml file, merging it with the dictionary resulting from the default. values in the
    sync_config_path take precedence over the default_config, but the sync_config_path yaml need not
    be complete
    :param sync_path:
    :param default_config:
    :return:
    """
    import yaml
    base_doc = yaml.safe_load(default_config)
    if sync_config_path and os.path.exists(sync_config_path):
        override_doc = yaml.safe_load(sync_config_path.read_text())
        # +3 github copilot
        base_doc.update(override_doc)

    return base_doc