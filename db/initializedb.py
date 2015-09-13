from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from __init__ import Base
from stock import Stock, Stock_data, Exchange, Trend, Category

import transaction
import os


class initialdb(): 
    #get this files path
    path = os.path.dirname(os.path.realpath(__file__))
            
    #sqlite:///:memory:
    engine = create_engine('sqlite:///'+path+'/stock.db', echo=True)
    #sqlite:///:memory:
    #engine = create_engine('sqlite:///stock.db', echo=True)
    engine.raw_connection().connection.text_factory = str

    #mapping
    Base.metadata.create_all(engine) 

    #Session
    Session = sessionmaker(bind=engine)   
    session = Session()

    '''with transaction.manager:
        ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
        print ed_user.name
        session.add(ed_user)
        session.commit()
        print ed_user.id
        
    asd = session.query(User).all()
    print asd
    for i in asd:
        print i.id'''