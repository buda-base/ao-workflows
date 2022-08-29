from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, text, select, insert
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)


class User(Base):
    __tablename__ = 'user_account'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'))
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


#
# Create the tables
Base.metadata.create_all(engine)

# Add some users
squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")
#
# boilerplate
session = Session(engine)

# Add some data
session.add(squidward)
session.add(krabs)
session.flush()

# define a select statement
stmt = select(User)

# and run it
with Session(engine) as session:
    for row in session.execute(stmt):
        print(row)

# Now try the insert select from, but in ORM style

# Insert ... from select
    select_u_email = select(User.id, User.name + "@aol.com")
    insert_stmt = insert(Address).from_select(
        ["user_id", "email_address"], select_u_email
    )
    result = session.execute(select_u_email)
    print(result)

    session.execute(insert_stmt)
    session.flush()

    get_addrs_stmt = select(Address)
    for row in session.execute(get_addrs_stmt):
        print(row)
