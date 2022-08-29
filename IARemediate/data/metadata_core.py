
# Metadata
# let's build us some Core shit
import sqlalchemy
from sqlalchemy import MetaData, create_engine, ForeignKey, text

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

def show_samples():
    """
    It's the punk soul brother, check it out
    :return:
    """

    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO user_account (id, name, fullname) VALUES (:i, :n, :f)"),
            [
                {"i": 6, "n": "Fred", "f": "Fred Dushinksy"},
                {"i": 9, "n": "Dyy", "f": "Dyy Kul"},
                {"i": 3000, "n": "blort", "f": "blort Hoerk"}
            ]
        )
    #
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM user_account"))
        for row in result:
            print(f"i: {row.id}  n: {row.name} f:{row.fullname}")


