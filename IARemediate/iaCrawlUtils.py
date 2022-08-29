"""
Replicate in python the command:
cat $UPLOAD_WORK_LIST| parallel --group 'ia tasks {} -p "cmd=derive.php" -p "submittime>=2022-04-01" | jq . '  > work-tasks

Only tasks which have failed have a status. so one cannot discriminate based on status alone whether work's last derive
task succeeded.

We need the IA identifiers for the succeeded derive tasks to check their collections.
"""

from internetarchive import get_session, ArchiveSession
from pathlib import Path

from internetarchive.catalog import CatalogTask


class ia_lib():
    ia_session: ArchiveSession
    config: {} = {'logging': {'level': 'INFO', 'file': f'{str(Path(Path.home() / "tmp" / "ia.log"))}'}}

    def __init__(self):
        """
        Create a session we can use
        """
        self.ia_session = get_session(config=self.config)

    def get_last_work_derive_task(self, id: str) -> CatalogTask:
        """
        Get the most recent derive task for the id
        This is a little subtle because you can't count on an error state always. The if a task
        fails, it has a color red, but if a subsequent try succeeds, the color comes back none.
        :param id: work to search
        :return:
        """

        tasks = self.ia_session.get_tasks(id, params={'cmd': 'derive.php'})
        last_derive_task_time = max([x.submittime for x in tasks])
        return [x for x in tasks if x.submittime == last_derive_task_time][0]


class ia_report_log():
    """
    Transforms the report log into a data structure"
    [ {'mismatch_type': str , 'works_mismatched' : [ str,....] }
    """

    _log_source: Path
    _log_lines:[str] = []

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
        self.log_source = log_source
        self.load()

    def load(self):
        """
        Rebuilds structure from the file
        """
        log_buf:[str] = []
        with open (self.log_source, 'r') as ibuf:
            log_buf = ibuf.readlines()
        self.raw_lines = [x.strip() for x in log_buf if x.strip()]


if __name__ == '__main__':
    # xx = ia_lib().get_last_work_derive_task("")
    yy = ia_report_log(Path(Path.home() / "dev" / "ao-workflows" / "data" / "ia-mismatch.report.txt"))
