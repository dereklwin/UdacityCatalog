import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

    # <script src="//apis.google.com/js/platform.js?onload=start" async defer> </script>


Base = declarative_base()

class Userdb(Base):
  __tablename__ = 'userdb'

  id = Column(Integer, primary_key = True)
  name = Column(String(250), nullable = False)
  email = Column(String(250), nullable= False)
  picture = Column(String(250))

class Cities(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    image = Column(String(250))
    user_id = Column(Integer, ForeignKey('userdb.id'))
    user = relationship(Userdb)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            
        }


class Destinations(Base):
    __tablename__ = 'destinations'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    price = Column(String(250))
    city_id = Column(Integer, ForeignKey('cities.id'))
    cities = relationship(Cities)
    image = Column(String(250))
    user_id = Column(Integer, ForeignKey('userdb.id'))
    user = relationship(Userdb)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image': self.image,
        }


engine = create_engine('postgresql+psycopg2://catalog:drowssap@localhost/cities')

Base.metadata.create_all(engine)
