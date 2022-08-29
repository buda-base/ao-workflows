
# Metadata
# let's build us some Core shit
import sqlalchemy
from sqlalchemy import MetaData, create_engine, ForeignKey, text


def show_samples():
    """
    It's the punk soul brother, check it out
    :return:
    """

    # with engine.begin() as conn:
    #     conn.execute(
    #         text("INSERT INTO user_account (id, name, fullname) VALUES (:i, :n, :f)"),
    #         [
    #             {"i": 6, "n": "Fred", "f": "Fred Dushinksy"},
    #             {"i": 9, "n": "Dyy", "f": "Dyy Kul"},
    #             {"i": 3000, "n": "blort", "f": "blort Hoerk"}
    #         ]
    #     )
    #
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM user_account"))
        for row in result:
            print(f"i: {row.id}  n: {row.name} f:{row.fullname}")
        print ('*******************')
        result = conn.execute(text("SELECT * FROM address"))
        for row in result:
            print(f"i: {row.id}  u: {row.user_id} f:{row.email_address}")

metadata_obj = MetaData()

from sqlalchemy import Table, Column, Integer, String
user_table = Table(
    "user_account",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(30)),
    Column('fullname', String)
)

print(sqlalchemy.__version__)

address_table = Table(
    "address",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('user_account.id'), nullable=False),
    Column('email_address', String, nullable=False)
)

# Let's persist these bad boys
# Not so fast, but hee's how
# engine = create_engine("sqlite+pysqlite:////Users/jimk/tmp/user-orm.db", echo=True, future=True)
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)

metadata_obj.create_all(engine)

#
# New in this tutorial
from sqlalchemy import insert, select
stmt = insert(user_table).values(name='spongebob', fullname="Spongebob Squarepants")

#

# Nothing to see here
print('--------------   what''s up doc ------------------')
result = None
show_samples()
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()

# or, this alt
with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"}
        ]
    )
    conn.commit()

# Insert ... from select
select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt
)
print(insert_stmt)

# Not in sqlite
insert_stmt_return = insert(address_table).returning(address_table.c.id, address_table.c.email_address)
print(insert_stmt_return)

# Run the statements
with engine.begin() as conn:
    result = conn.execute(insert_stmt)
    print(result)
print('--------------   now?  ------------------')
show_samples()



