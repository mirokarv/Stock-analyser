from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date

from sqlalchemy.orm import relationship

from __init__ import Base

class Stock(Base):
    __tablename__ = 'Stocks'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    klid = Column(Integer)
    category_id = Column(Integer, ForeignKey('Category.id'))
    
    category = relationship("Category", backref='Stocks', foreign_keys=[category_id])
    
    data = relationship("Stock_data")
    exchange = relationship("Exchange")
    trend = relationship("Trend")
    #category = relationship("Category")
    
class Category(Base):
    __tablename__ = 'Category'
    
    id = Column(Integer, primary_key=True)
    category = Column(String)
    
    stock = relationship("Stock")
    
    
    
'''class StockCat(Base):
    __tablename__ = 'StockCat'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('Stocks.id'))
    category_id = Column(Integer, ForeignKey('Category.id'))
    
    #stock = relationship("Stock", backref='Category', foreign_keys=[stock_id])'''

class Stock_data(Base):
    __tablename__ = 'Stock_data'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('Stocks.id'))
    date = Column(Date)
    open = Column(Integer)    
    high_sell = Column(Integer)
    lowest_sell = Column(Integer)
    close = Column(Integer)
    volume = Column(Integer)
    
    stock = relationship("Stock", backref='Stock_data', foreign_keys=[stock_id])
    
    
class Exchange(Base):
    __tablename__ = 'Exchange'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('Stocks.id'))
    exchange = Column(String)   
    
    stock = relationship("Stock", backref='Exchange', foreign_keys=[stock_id])
    
    
class Trend(Base):
    __tablename__ = 'Trend'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('Stocks.id'))
    time = Column(DateTime)
    value = Column(Integer)    
    
    stock = relationship("Stock", backref='Trend', foreign_keys=[stock_id])
    