"""
DAOs for Google Books. When stable, import into models
"""
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase
from BdrcDbLib.DbOrm.models.drs import *



class GB_ToDo(TimestampMixin, Base):
    """
    Google Books worklist
    """
    __tablename__ = "GB_To_Do"
    work_id = Column(Integer, ForeignKey('Works.workId'))
    work = relationship('Works')



def create_tables():
    with DrsDbContextBase() as drs:
        bobby_tables: [] = [
            GB_ToDo().__table__
        ]
        Base.metadata.create_all(drs.get_engine(), checkfirst=True, tables=bobby_tables)

if __name__ == '__main__':
    """
    Have to update config
    """
    create_tables()