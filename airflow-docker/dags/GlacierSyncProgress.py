"""
Model for tracking Glacier Sync process
"""
import random

from BdrcDbLib.DbOrm.models.drs import TimestampMixin
from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
import pendulum
from sqlalchemy.ext.mutable import MutableDict, MutableList

Base = declarative_base()


class GlacierSyncProgress(Base, TimestampMixin):
    __tablename__ = 'glacier_sync_progress'

    id = Column(Integer, primary_key=True)
    object_name = Column(String(255))
    restore_requested_on = Column(TIMESTAMP, nullable=True)
    restore_complete_on = Column(TIMESTAMP, nullable=True)
    download_complete_on = Column(TIMESTAMP, nullable=True)
    debag_complete_on = Column(TIMESTAMP, nullable=True)
    sync_complete_on = Column(TIMESTAMP, nullable=True)

    #https://stackoverflow.com/questions/42559434/updates-to-json-field-dont-persist-to-db
    user_data = Column(MutableList.as_mutable(JSON),
                       comment='format:[ {"time_stamp" : <current_time>, "user_data" : provided_user_data object}... ]')



    def update_user_data(self, when: str, provided_user_data: object):
        """
        User data is a list of lists of dictionaries. Each new entry is a list that contains:
        [ 'time_stamp' : <current_time>, 'user_data' : provided_user_data object ]
        :param when: time stamp of update
        :param provided_user_data: user data to log - must be None, or serializable
        :return:
        """
        #
        if not provided_user_data:
            provided_user_data = {'provided_user_data': False}

        new_ud = {'time_stamp': when, 'user_data': provided_user_data}
        if not self.user_data:
            self.user_data = [new_ud]
        else:
            self.user_data.append(new_ud)
            # exist_ud = self.user_data
            # exist_ud.append(new_ud)
            # self.user_data = exist_ud


    def __repr__(self):
        return f"""
        <{self.id}: {self.object_name=}
        {self.restore_requested_on=} 
        {self.restore_complete_on=}
        {self.download_complete_on=}
        {self.debag_complete_on=}
        {self.sync_complete_on=}
        {self.user_data=}>
        """


if __name__ == '__main__':
    # Create the table
    with DrsDbContextBase(context_str='prodsa:~/.config/bdrc/db_apps.config') as ctx:
        engine: Engine = ctx.get_engine()
        inspector = inspect(engine)
        if inspector.has_table(GlacierSyncProgress.__tablename__):
            GlacierSyncProgress.__table__.drop(engine)
        GlacierSyncProgress.metadata.create_all(engine, checkfirst=True, tables=[GlacierSyncProgress().__table__])

