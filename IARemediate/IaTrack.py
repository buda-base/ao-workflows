"""
SqlAlchemy ORM for tracking IA
"""
import configparser
import logging
import os.path
import sys

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, text, select, insert, Table
from sqlalchemy.orm import declarative_base, relationship, Session

from config.config import DBConfig

Base = declarative_base()

# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
# Use the qa section, which is an authorized user - only if you want to create things
# for reading, use 'prod'
cnf: DBConfig = DBConfig('prod', '~/.config/bdrc/db_apps.config')

# We need to reach through the DBApps config into the underlying [mysql] config
# parser
engine_cnf = configparser.ConfigParser()
engine_cnf.read(os.path.expanduser(cnf.db_cnf))

conn_str = "mysql+pymysql://%s:%s@%s:%d/%s" % (
    engine_cnf.get(cnf.db_host, "user"),
    engine_cnf.get(cnf.db_host, "password"),
    engine_cnf.get(cnf.db_host, "host"),
    engine_cnf.getint(cnf.db_host, "port", fallback=3306),
    engine_cnf.get(cnf.db_host, "database"))

engine = create_engine(conn_str, echo=True, future=True)


class IATrack(Base):
    __table__ = Table('IATrack', Base.metadata, autoload_with=engine)
    # workId: int, ia_id : str , task_id:str
    def __init__(self, *args, **kwargs ):
        """
        reflect constructor orgs attempt
        :param workId:
        :param ia_id:
        :param task_id:
        """
        super().__init__(*args, **kwargs)


class Works(Base):
    __table__ = Table('Works', Base.metadata, autoload_with=engine)


class IATracker():
    # Just in case we need works
    _work_table: Base

    @property
    def work_table(self):
        return self._work_table

    @work_table.setter
    def work_table(self, value):
        self._work_table = value

    def __init__(self):
        """
        Initiates connection and instantiates mapped table objects
        """

        try:
            # self.ia_track = Table("IATrack", Base.metadata, autoload_with=self._engine)
            # self.work_table = Table("Works", Base.metadata, autoload_with=self._engine)
            self.work_table = Works()

        except:
            ee = sys.exc_info()
            logging.info(ee)

    def add_track(self, ia_item_id: str, work_name: str, task_id: int):
        """
        Adds a record to tracking
        :param ia_item_id: the IA identifier
        :param work_name: the work referenced by the identifier
        :return: the ID of the newly created tracking item
        """

        # Get the work Name
        work_id: int = -1

        conn = engine.raw_connection()
        cursor = conn.cursor()
        results: []

        try:
            cursor.callproc("AddWork", [work_name, 0])
        finally:
            cursor.close()
            conn.commit()
            conn.close()
        work_id = 0

        with Session(engine) as session:
            get_work_id = select(Works.workId).where(Works.WorkName == work_name)

            # We get back a unitary tuple with the workID
            one = session.execute(get_work_id).first()
            if one is None:
                raise ValueError(f"Could not locate work with name {work_name}")
            work_id = one[0]

            # It would be nice if reflected ORMS could use __init__ **kwargs
            # work_id=work_id, ia_id=ia_item_id, task_id=task_id
            new_ia = IATrack( workId=work_id, ia_id=ia_item_id, task_id=task_id)
#             new_ia = IATrack()
#             new_ia.workId = work_id
#             new_ia.ia_id = ia_item_id
#             new_ia.task_id = task_id

            session.add(new_ia)
            session.flush()
            session.commit()


if __name__ == '__main__':
    iat: IATracker = IATracker()
    iat.add_track("bdrc-Blarg", "HoopstyFreen", 42)
