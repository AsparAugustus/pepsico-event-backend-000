from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create a SQLite database called Admin
engine = create_engine('sqlite:///admin.db')
Base = declarative_base()

# Define a User class with attributes id, username, and password
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

# Create the table
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Add a user to the database
user = User(username='pepsi', password='pop')
session.add(user)
session.commit()
