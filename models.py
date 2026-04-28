from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os

Base = declarative_base()

if os.path.exists("/home"):
    db_path = "sqlite:////home/users.db"  # Azure
else:
    db_path = "sqlite:///users.db"        # Local

engine = create_engine(db_path)
Session = sessionmaker(bind=engine)
db_session = Session()

def get_session():
    
    return db_session

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)