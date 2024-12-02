#!/usr/bin/env python3
"""
On the shell running docker, run 'extract-failed-runs.sh [ optional output_dir, default is run-fails-$(log_now_ish) (see ~/bin/init_sys.sh ]'

this python file does a close analysis by determining the actual item that failed
"""
import os
from pathlib import Path


# in fhe given directory return only the directory whose name  that is first in a given sequence fails = [sync, debag, wait_for_file]'
def filter_dir(dir: Path, sorts:[]):
    # dict of  { sort: [Path, Path, ...], ... }
    out_map:{} = {}
    for sort in sorts:
        for root, dirs, files in os.scandir(dir):
            for dir in dirs:
                if dir.startswith(sort):
                    out_map[sort] = dir
                    break
