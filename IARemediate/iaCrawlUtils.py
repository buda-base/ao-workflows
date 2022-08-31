"""Replicate in python the command: cat $UPLOAD_WORK_LIST| parallel --group 'ia tasks {} -p "cmd=derive.php" -p
"submittime>=2022-04-01" | jq . '  > work-tasks

Only tasks which have failed have a status. so one cannot discriminate based on status alone whether work's last derive
task succeeded.

We need the IA identifiers for the succeeded derive tasks to check their collections.
"""
import json
import os.path
from typing import Tuple, Any

from internetarchive import get_session, ArchiveSession
from pathlib import Path

from internetarchive.catalog import CatalogTask

_s3: str = 's3'
platform_ia_config_map: {} = {
    'Darwin': os.path.expanduser('~/.config/ia.ini'),
    'Linux': os.path.expanduser('~/.ia'),
    'Windows': os.path.expanduser('~\.config\internetarchive\ia.ini')
}


class ia_lib:
    ia_session: ArchiveSession
    config: {} = {'logging': {'level': 'INFO', 'file': f'{str(Path(Path.home() / "tmp" / "ia.log"))}'}}

    def __init__(self):
        """
        Create a session we can use
        """
        self.ia_session = get_session(config=self.config)

    def get_last_work_derive_task(self, ia_id: str) -> CatalogTask:
        """
        Get the most recent derive task for the id
        This is a little subtle because you can't count on an error state always. The if a task
        fails, it has a color red, but if a subsequent try succeeds, the color comes back none.
        :param ia_id: work to search
        :return:
        """

        tasks = self.ia_session.get_tasks(ia_id, params={'cmd': 'derive.php'})
        last_derive_task_time = max([x.submittime for x in tasks])
        return [x for x in tasks if x.submittime == last_derive_task_time][0]

    def submit_rederive_task(self, ia_id: str) -> Tuple[Any, Any]:
        """
        Submit a rederive task
        :type ia_id: str
        :param ia_id: Internet Archive Item id
        :return: task id if successful
        """

        # https://archive.org/services/docs/api/tasks.html
        # Requests doc https://requests.readthedocs.io/en/latest/

        task_url = "https://archive.org/services/tasks.php"

        req_data_dict: {} = {'identifier': ia_id,
                             'cmd': 'derive.php',
                             'args': ['remove_derived=*']
                             }

        req_json: str = json.dumps(req_data_dict)
        import requests

        auth = self.ia_auth()
        headers: {} = {
            'Authorization': f"LOW {auth[0]}:{auth[1]}"
        }

        r: requests.Response = requests.post(url=task_url, data=req_json, headers=headers)
        if not r.ok:
            raise ValueError(f"Rederive request for {ia_id} failed  ")
        resp_dict = r.json()
        print(resp_dict)
        if resp_dict['success']:
            return resp_dict['value']['task_id'], resp_dict['value']['log']
        else:
            raise ValueError(f"item {ia_id} request failed {resp_dict['error']} ")

    # try:
    #     with request.urlopen(req) as response:
    def ia_auth(self) -> (str, str):
        """
        Returns the S3 link access and security keys from the user's auth file
        :return:
        """
        import platform
        from configparser import ConfigParser

        ps: str = platform.system()
        try:
            cnf: ConfigParser = ConfigParser()
            cnf.read(platform_ia_config_map[ps])

            if _s3 not in cnf:
                raise NotImplementedError("Config requires an s3 section")
            return cnf[_s3]['access'], cnf[_s3]['secret']

        except KeyError:
            raise ValueError(f"{ps} is not a supported platform for BDRC Internet Archive operations")


class IaReportLog:
    """
    Transforms the report log into a data structure"
    [ {'mismatch_type': str , 'works_mismatched' : [ str,....] }
    """

    _log_source: Path
    _log_lines: [str] = []

    @property
    def raw_lines(self):
        return self._raw_lines

    @raw_lines.setter
    def raw_lines(self, value):
        self._raw_lines = value

    @property
    def log_source(self):
        return self._log_source

    @log_source.setter
    def log_source(self, value):
        self._log_source = value
        self.load()

    @log_source.deleter
    def log_source(self):
        pass

    def __init__(self, log_source: Path):
        """
        :param log_source: file containing list of mismatches.
        log file Structure
        1..* ['reason:'  1..n [ blank line | IA item id ] ]
        where 'reason is an arbitrary string
        """
        self._raw_lines = None
        self.log_source = log_source
        self.load()

    def load(self):
        """
        Rebuilds structure from the file
        """

        with open(self.log_source, 'r') as ibuf:
            log_buf = ibuf.readlines()
        # Believe it or not, this actually works, if the file was read
        self.raw_lines = [x.strip() for x in log_buf if x.strip()]


if __name__ == '__main__':
    # xx = ia_lib().get_last_work_derive_task("")
    yy = IaReportLog(Path(Path.home() / "dev" / "ao-workflows" / "data" / "ia-mismatch.report.txt"))
