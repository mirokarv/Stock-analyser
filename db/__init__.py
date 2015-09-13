from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

#get this files path
path = os.path.dirname(os.path.realpath(__file__))
        
#sqlite:///:memory:
engine = create_engine('sqlite:///'+path+'/stock.db', echo=True)

engine.raw_connection().connection.text_factory = str


#mapping
Base = declarative_base()
Base.metadata.create_all(engine) 

#Session
Session = sessionmaker(bind=engine)
