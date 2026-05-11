from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
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
    access = Column(String, nullable=False)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    user = relationship("User", backref="customer")
    rentals = relationship("Rental", backref="customer")

class Equipment(Base):
    __tablename__ = "equipments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    rentals = relationship("Rental", backref="equipment")

class Rental(Base):
    __tablename__ = "rentals"
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipments.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)