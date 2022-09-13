"""
Library which creates and maintains a sqlAlchemy ORM
"""
from sqlalchemy import create_engine, text

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
# engine = create_engine("sqlite+pysqlite:///:file:/Users/jimk/tmp/iafix.sqlite", echo=True, future=True)

with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
    )
    conn.commit()

# Begin once
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}]
    )
#
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT x, y FROM some_table"))
#     for row in result:
#         x = row.x
#         y = row.y
#         print(f"x: {x}  y: {y}")


# with engine.connect() as conn:
#     result = conn.execute(
#         text("SELECT x, y FROM some_table WHERE y > :y"),
#         {"y": 2}
#     )
#     for row in result:
#        print(f"x: {row.x}  y: {row.y}")
#

# Bundling Parameters with a Statement
stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6)
with engine.connect() as conn:
    result = conn.execute(stmt)
    for row in result:
       print(f"x: {row.x}  y: {row.y}")

# Executing with an ORM Session
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=-42)
with Session(engine) as session:
    result = session.execute(stmt)
    for row in result:
       print(f"x: {row.x}  y: {row.y}")

# Commit as you go
with Session(engine) as session:
    result = session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y":11}, {"x": 13, "y": 15}]
    )
    session.commit()





