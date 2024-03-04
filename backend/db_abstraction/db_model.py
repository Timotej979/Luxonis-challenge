from sqlalchemy import MetaData, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from datetime import datetime


metadata = MetaData()
Base = declarative_base(metadata = metadata)

class Flats_on_sale(Base):
    __tablename__ = 'Flats_on_sale'

    ID = Column(Integer, primary_key = True, unique = True, autoincrement = True)
    created = Column(DateTime, default = datetime.now)
    last_updated = Column(DateTime, default = datetime.now, onupdate = datetime.now)
    title = Column(String(1000))
    price = Column(Float)
    location = Column(String(100))