# -*- coding: utf-8 -*-

from db.__init__ import Session
from db.stock import Stock, Stock_data, Exchange, Trend, Category

import transaction

from datetime import datetime, date, time, timedelta
from sqlalchemy import and_
from decimal import *

import os, sys


def addStock(dict, cat):
    '''
    What is given to this class
        {'name': name, "rise": change, 'price': price, 'buy': buy, 'sell': sell,
       'lowest sell': ssell, 'high': high, 'volume': volume, 'exchange': exchange, 'time': time, 'klid': klid}
    '''
       
    session = Session()  
    stock = session.query(Stock).filter(Stock.klid == dict['klid']).all()
    
    #if stock isn't in the db lets add it there
    if not stock:
        #because python didn't like finish letters, we can change them back
        if "'O'" in cat:
            cat = cat.replace("'O'", u"Ö")
            
        if "'o'" in cat:
            cat = cat.replace("'o'", u"ö")
          
        #lets see if there is already a same named category
        category = session.query(Category).filter(Category.category == cat).first()
    
        #if not lets create a category 
        if not category: 
            with transaction.manager:
                cate = Category(category = cat)
                
                session.add(cate)
                session.commit()
                
                #get category's id
                cateid = cate.id
                
        else:
            #get category's id
            cateid = category.id
            
            
        with transaction.manager:
            name = dict['name']
            #because python didn't like finish letters, we can change them back
            if "'a'" in name:
                name = name.replace("'a'", u"ä")
            if "'o'" in name:
                name = name.replace("'o'", u"ö")
            if "'OA'" in name:
                name = name.replace("'OA'", u"Å")
                
            #create new stock record
            newStock = Stock(name = name, klid = dict['klid'], category_id = cateid)
            session.add(newStock)
            session.commit()
            
            #add exchange information for the stock
            exc = Exchange(stock_id = newStock.id, exchange = dict['exchange'])
            
            session.add(exc)
            session.commit()
            
            
            
'''
saves stock data, like prices etc to db
id is kauppalehti's own id
'''            
def stockData(list, id):
    session = Session()
    
    stock = session.query(Stock).filter(Stock.klid == id).first()
    time = datetime.strptime(list[0], "%d.%m.%Y").date() #make it a date object
    
    stockData = session.query(Stock_data).filter(and_(Stock_data.stock_id == stock.id, Stock_data.date == time)).first()
    
    #if there is a record from that day we can exit this class
    if stockData:
        return False
    
    with transaction.manager:  
        newData = Stock_data(stock_id = stock.id, date = time, open = float(list[1]), high_sell =  float(list[2]), 
                            lowest_sell =  float(list[3]), close =  float(list[4]), volume =  float(list[5]))                    
                            
        session.add(newData)
        session.commit()
        
    return True
    

'''
class gets list of all stock klid's (KL's own id)
'''
def getIDList():
    session = Session()
    
    stocks = session.query(Stock).all()
    
    IDlist = []
    for stock in stocks:
        IDlist.append(stock.klid)
        
    return IDlist
    

'''
Get stocks name that belongs to that klid
'''    
def getStockname(klid):
    session = Session()
    
    stock = session.query(Stock).filter(Stock.klid == klid).first()
    
    return stock.name
    
 
'''
Add's trend data to db
''' 
def addTrend(dict, klid):
    session = Session()
    
    stock = session.query(Stock).filter(Stock.klid == klid).first()
    
    treData = session.query(Trend).filter(and_(Trend.stock_id == stock.id, Trend.time == dict['time'])).first()
    
    #check that there are no data from that day and time
    if not treData:    
        with transaction.manager:
            trend = Trend(stock_id = stock.id, time = dict['time'], value = dict['value'])
            
            session.add(trend)
            session.commit()
 
 
'''
tells how many stocks are there that doesn't have any trend data available on google 
Not used currently
prints all the info on commandline
'''
def CheckAllTheStockThatDoesntHaveTrendData():
    session = Session()
    
    counter = 0
    
    for id in range(0, 137):
        trend = session.query(Trend).filter(Trend.stock_id == id).first()
        print '\n\n'
        print trend
        print '\n\n'
        if not trend:
            counter += 1
            
    print counter
    
'''
Calculated trend values, returns the list of day's mean value
Last item of the list is latest value
''' 
def getTrendValues(id, days):
    session = Session()
    
    stockTrending = session.query(Trend).filter(Trend.stock_id == id).all()
    
    if stockTrending:
        #lets transfer the time to UTC+0 to get more accurate day to day data
        #time is stored in UTC-7
        #for i in stockTrending:
        #    i.time = i.time + timedelta(hours=7)
        
        #get latest day number that has trending record 
        latestDate = stockTrending[-1]
        latestDate = latestDate.time
        
        Lyear = latestDate.year
        Lmonth = latestDate.month
        LDay = latestDate.day
        
        #time is stored in UTC-7
        fdate = datetime.strptime(str(Lyear)+str(Lmonth)+str(LDay), "%Y%m%d") #make it a date object
        #lets include utc-7 time difference to date object.
        fdate = fdate - timedelta(hours=7)
        
        #lets get earlier day
        sdate = fdate - timedelta(hours=24)
        
        #empty list for storing trending data
        trendList = []
        
        #lets get trend data from specified range. starts at 0
        for i in range(int(days)+1):
            #date object includes utc-7 time difference 
            fdate = fdate - timedelta(hours=i*24)
            sdate = sdate - timedelta(hours=i*24)
        
            #lets query db for 24 datapoints where we can calculate days mean value
            trending = session.query(Trend).filter(and_
                        (Trend.stock_id == id, Trend.time >= sdate, Trend.time < fdate)
                        ).all()
            if trending:            
                totalValue = 0
                
                for j in trending:
                    totalValue += j.value
                
                #if there are missing data points for that day, dividing it always with 24 guarantees accuracy 
                mean = totalValue/24
                
                trendList.append(mean)
            
        #lets reserve list item order, so that newest value is last    
        return trendList[::-1]


'''
Not so complicated analyser.
That is trying to determining if stock has grown interest 
Doesn't currently have any science behind 
'''
def analyse(list):
    #lets only analyse 7 days
    analList = list[-7:]
 
    if list:     
        a1 = list[-1]
        a2 = list[-2]
        
        #checks if interest has grown from yesterday. If it has more than 10 points then it should be significant 
        if (a1 -a2) > 10:
            return True
        
        #check if there has been growing interest from longer time period(7days), compared to latest data point        
        elif list[-1] > ((sum(list[:-2])/len(list[:-2])) +10):
            return True
         
        #since sometimes there is only few values added to mean
        elif (list[-2] - list[-3]) > 10:
            return True
            
        elif list[-2] > ((sum(list[:-3])/len(list[:-3])) +10):
            return True
            
        else:
            return False
            
      
'''
Get all normal stock id's
'''                
def getIDS():
    session = Session()    
    stocks = session.query(Stock).all()
    
    list = []
    for i in stocks:
        list.append(i.id)
        
    return list
 
'''
Get stock name by it's normal db id
''' 
def getnamesbyid(id):
    session = Session()
    
    stock = session.query(Stock).filter(Stock.id == id).first()
    
    return stock.name

'''
Save stuff to file
text is string
name is files name that is created or opened
'''    
def writer(text, name):
    filename = name + '.txt'
    
    #get current script execution path
    path = sys.argv[0]
    #remove scrip file name
    path = path[:path.rfind('\\')] 
    
    #creating a file if needed and accessing to it
    file = os.path.join(path, filename) 
    f = open (file, 'a')
    #text = text.encode(encoding='UTF-8',errors='ignore')
    #text = text.decode().encode('utf-8')
    text = text.encode("utf8") + '\n'
    
    f.write(text)
    f.close()
            
  
def main(argv):
    ids = getIDS()
    
    if len(argv) == 2:
        days = argv[1]
        
        if not days.isdigit():
            days = 15
            
    else:
        days = 15
    
    for id in ids:
        data = getTrendValues(id, days)
        #print data[1]
        if data:
            anal = analyse(data)
            
            name = getnamesbyid(id)
            #write all the information to text file, if user has written 'all' to arguments
            if 'all' in argv:
                writer(name + '  ' + str(data), 'all')
            
            #only write promising stock to text file for further analysis 
            if anal:
                name = getnamesbyid(id)
                writer(name + '  ' + str(data), 'buy')
            

        
if __name__ == "__main__":
    #sys.argv first argument should be number of days we are inspecting.
    #other argument can be 'all'. in that case script prints all of the stock informations to text file
    main(sys.argv)
    
    
    