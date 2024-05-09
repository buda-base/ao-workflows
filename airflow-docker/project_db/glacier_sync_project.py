"""
Create the DbOrm for the glacier sync project.
The project workflow is:
State 0: Unbegun
State 1: Restore requested
State 2: Restore completed
State 3: Sync completed

Project members are works. The work is instantiated
"""


from sqlalchemy.orm import Session

# create a new session
session = Session()

# get the object progress row
object_progress = session.query(ObjectProgress).filter_by(object_name='my-object').first()

# update the progress
object_progress.restore_requested = True
object_progress.restore_complete = True
# ...

# commit the changes
session.commit()