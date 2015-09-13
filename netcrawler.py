# -*- coding: utf-8 -*-
'''
class main handless almost everything, it's on bottom of this file
'''
import requests
import sys, os
from decimal import *
from random import randint
from datetime import datetime, date, time
from time import sleep

from dbconnector import addStock, stockData, getIDList, addTrend, getStockname

#functio kirjoittaa kaiken tiedostoon
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

    f.write(text)
    f.close()
   
'''
used to parse html file
Text is a list that has only lines that belong to 1 stock
Class returns lots of stuff in dict, only few are needed currently
'''    
def parser(text):

    for index, line in enumerate(text):
        i = 1 #all the lines are always in same order, so increasing i is only thing what we have to do
        #starting point might be bit unknown at first
        if '<td><a' in line:
            #klid is kauppalehti's own id, that we are used to mine their day that from that specific stock
            klid = line[line.rfind('klid='):]
            klid = klid[:klid.rfind('"')]
            klid = int(klid.replace('klid=', ''))
            
            print klid
            
            #name is stocks name
            name = line[line.rfind('">'):]
            name = name.replace('</a></td>', '')
            name = name.replace('">', '')
            
            #sometimes there are few stocks that don't have a name
            if name == '-':
                name = None
                
            #python doesn't like always Finnish letters, so lets cheat a little    
            if '\xc3\xa4' in name:
                name = name.replace('\xc3\xa4', "'a'")
            if '\xc3\xb6' in name:
                name = name.replace('\xc3\xb6', "'o'")
            if '\xc3\x85' in name:
                name = name.replace('\xc3\x85', "'OA'")
            print name
            
            #price line is next thing in a list
            priceLine = text[index+i]
            i += 1
            
            price = priceLine[priceLine.rfind('">'):]
            price = price.replace('</td>', '')
            price = price.replace('">', '')
            if price == '-':
                price = None
            else:
                price = Decimal(price)
            print price
            
            changeLine = text[index+i]
            i += 1
            #sometimes there is only newline in here, so we have to try nest list item
            if not changeLine.isalpha():
                changeLine = text[index+i]
                i += 1
                
            change = changeLine[changeLine.rfind('">'):]
            change = change.replace('</td>', '')
            change = change.replace('">', '')
            if change == '-':
                change = None
            print change
            
            timeLine = text[index+i]
            i += 1
            
            time = timeLine[timeLine.rfind('">'):]
            time = time.replace('</td>', '')
            time = time.replace('">', '')
            if time == '-':
                time = None
            print time
            
            buyLine = text[index+i]
            i += 1
            
            buy = buyLine[buyLine.rfind('tasot">'):]
            buy = buy.replace('</a></td>', '')
            buy = buy.replace('tasot">', '')
            if buy == '-':
                buy = None
            else:
                buy = Decimal(buy)
            print buy
            
            sellLine = text[index+i]
            i += 1
            
            sell = sellLine[sellLine.rfind('tasot">'):]
            sell = sell.replace('</a></td>', '')
            sell = sell.replace('tasot">', '')
            if sell == '-':
                sell = None
            else:
                sell = Decimal(sell)
            print sell
            
            highLine = text[index+i]
            i += 1
            
            high = highLine[highLine.rfind('">'):]
            high = high.replace('</td>', '')
            high = high.replace('">', '')
            if high == '-':
                high = None
            else:
                high = Decimal(high)
            print high
            
            ssellLine = text[index+i]
            i += 1
            
            ssell = ssellLine[ssellLine.rfind('">'):]
            ssell = ssell.replace('</td>', '')
            ssell = ssell.replace('">', '')
            if ssell == '-':
                ssell = None
            else:
                ssell = Decimal(ssell)
            print ssell
            
            volumeLine = text[index+i]
            i += 1
            
            volume = volumeLine[volumeLine.rfind('t">'):]
            volume = volume.replace('</a></td>', '')
            volume = volume.replace('t">', '')
            if volume == '-':
                volume = None
            else:
                volume = int(volume)
            print volume
            
            exchangeLine = text[index+i]
            i += 1
            
            exchange = exchangeLine[exchangeLine.rfind('">'):]
            exchange = exchange.replace('</td>', '')
            exchange = exchange.replace('">', '')
            if exchange == '-':
                exchange = None
            print exchange
            
            
            return {'name': name, "rise": change, 'price': price, 'buy': buy, 'sell': sell,
                    'lowest sell': ssell, 'high': high, 'volume': volume, 'exchange': exchange, 'time': time, 'klid': klid}   
                    
    
'''
text is list that contains a lines from raw text. Raw text is originally html file
cat is category (string)
Text has lines from part that belongs to specific category
Class parses the lines and after that calls db class that saves data to db 
'''    
def textCutter(text, cat):
    #used to find list items that have the stock data
    startIndex, endIndex = None, None

    for index, line in enumerate(text):
        #each stock is inside of tr class html element
        #find the line that has the stock information
        if '<tr class="' in line and not startIndex:
            startIndex = index
            
        if startIndex:
            
            #fins last item in the list that has specific stock data
            if '</tr>' in line:
                if not startIndex == index:
                    endIndex = index
                    
            if endIndex:
                #Now we know all the list items that have stock data, lest parse it
                output = parser(text[startIndex-1:endIndex])
                startIndex, endIndex = None, None #reset the helper atributes
                print output
                if output:
                    #db connector class that saves data to db
                    addStock(output, cat)
                
                #checks if </tr> and start of the new stock data block are on same line
                if '<tr class="' in line:
                    startIndex = index


'''
Other links, just in case
http://porssi.taloussanomat.fi/startel/ajax_startel_const_list.html?BLOCKSIZE=200&OFFSET=0&NAVI_RANGE=0&VERSION=1&FORMAT=0&ID_NOTATION_INDEX=9174280&SORT=NAME_SECURITY&WITH_QUOTES=DLY&BLOCK_NR=4&FROM_TOOL=markets&FROM_NAME=index&ID_CLIST=7426&INCLUDE_INSTRUMENTS_WITHOUT_COMPANY_DATA=1&TAB=Day&ID_NOTATION=9174280&AJAX_TARGET_NR=_1
http://www.kauppalehti.fi/5/i/porssi/porssikurssit/lista_gen.jsp?listIds=kaikki&gics=0&refresh=60&markets=XHEL&currency=euro&volume=cur&selected=&p=1&psize=50&order=alpha&reverse=false&rdc=14e63be4496&AjaxRequestUniqueId=14361925503802
http://www.kauppalehti.fi/5/i/porssi/porssikurssit/lista_gen.jsp?listIds=kaikki&gics=0&refresh=60&markets=XHEL&currency=euro&volume=kpl&selected=&p=1&psize=50&order=alpha&reverse=false&rdc=14e63be4496&AjaxRequestUniqueId=143619285132112
'''

'''
Makes get request and gets all the stock names in id that are currently listed in helsinki's stock markets
Return huge string
'''
def getStockData():
    r = requests.get('http://www.kauppalehti.fi/5/i/porssi/porssikurssit/lista_gen.jsp?listIds=kaikki&gics=0&refresh=60&markets=XHEL&currency=euro&volume=kpl&selected=&p=1&psize=50&order=alpha&reverse=false&rdc=14e63be4496&AjaxRequestUniqueId=143619285132312')

    text = r.text
    text = text.encode('utf8')
    
    return text


'''
used to get stock data, names and id's
Kauppalehti also uses stock categories, we are also stealing those 
'''    
def mainData():
    #make request, from kauppalehti. Gets stock names and id's
    text = getStockData()
    
    #used tp get stock categories
    indexList = []
    indexName = []

    #get category names
    for index, line in enumerate(text.splitlines()):
        if 'colspan' in line:
            name = line[line.rfind('<h3>'):]
            name = name.replace('<h3>', '')
            name = name.replace('</h3></td>', '')
            
            #python doesn't like Finnish letters, lets cheat little in here
            if '\xc3\x96' in name:
                name = name.replace('\xc3\x96', "'O'")
                
            if '\xc3\xb6' in name:
                name = name.replace('\xc3\xb6', "'o'")
                
            indexList.append(index-1)
            indexName.append(name)
            
            print name, index
         
    #creates list, based in newline(\n) in the text 
    splitText = text.splitlines() 

    lenght = len(indexList)
    
    #we are splitting text by kauppalehti's categories, and all the stock in that category are sent to text cutter
    for i in range(len(indexList)):
        if not i == lenght-1:
            newText = splitText[indexList[i]-2:indexList[i+1]+2]  
            textCutter(newText, indexName[i])

        else:
            #last category
            newText = splitText[indexList[i]:]    
            textCutter(newText, indexName[i])
            


# http://www.kauppalehti.fi/5/i/amstock/historydata.jsp?klid=1901&period=1&turnover=false&1438409686722

def getData(id):
    randomID = randint(409686722,1000000000)
    url = 'http://www.kauppalehti.fi/5/i/amstock/historydata.jsp?klid=' + str(id) + '&period=1&turnover=false&1438' +str(randomID)
    r = requests.get(url)

    text = r.text
    text = text.encode('utf8')
    
    return text
    
    
def addStockDatatoDB(text, id):
    data = text.splitlines()
    for line in data[1:]:
        #date, open, high, close, volume
        list = line.split(';')
        
        nlist= []
        for i in list:
            if ',' in i:
                j = i.replace(',', '.')
                nlist.append(j)
                
            else:
                nlist.append(i)
                
        
        stockData(nlist, id)
        
'''
class to get stock specific data from google trend
Only fetches data from last 7 days
Takes in name (String)
Returns huge string 
'''        
def getTrendData(stock):
    #check if stock name has LP(Liquidity Provider), and removes it if found. To get better results
    stock = stock.replace(' (LP)', '')
    
    url = 'http://www.google.com/trends/fetchComponent?q=' + stock + '&date=today%207-d&cid=TIMESERIES_GRAPH_0&export=3'
    
    #make the request
    r = requests.get(url)
    
    text = r.text 
    text = text.encode('utf8') # format the string to utf-8
    
    return text
 
 
'''
Method used to parse war text data from google trend
Currently only works if google things you are from sweden or finland
Finally class calls db connector class that saves all the data to db
Data:
    time = Datetime (standard python date object. yyyymmddhhmm )
    value = int
''' 
def parseTrendText(text, id):
    #transfers ascii months to string numbers
    #currently supports only finnish or swedish ascii months
    def getMonth(m):
        m = m.lower()
        if 'tammi' in m or 'janu' in m:
            return '01'
        if 'helmi' in m or 'feb' in m:
            return '02'
        if 'maalis' in m or 'mars' in m:
            return '03'
        if 'huhti' in m or 'april' in m:
            return '04'
        if 'touko' in m or 'maj' in m:
            return '05'
        if 'kes' in m or 'juni' in m:
            return '06'
        if 'hein' in m or 'juli' in m:
            return '07'
        if 'elo' in m or 'aug' in m:
            return '08'
        if 'syys' in m or 'sep' in m:
            return '09'
        if 'loka' in m or 'okt' in m:
            return '10'
        if 'marras' in m or 'novem' in m:
            return '11'
        if 'joulu' in m or 'decem' in m:
            return '12'
     
    #chops the raw text to parts    
    #Removes useless stuff from beginning of the raw text 
    text = text[text.rfind('"rows":'):]
    #remove that rows words
    text = text.replace('"rows":', '')
    #chops the raw text to parts by keywords "c", it's unique identifier for each data 'row'
    list = text.split('"c":') #creates a list
    #first item/line in a list is pointless
    list = list[1:]
    
    for i in list:
        #sometimes there might be "c" column but it's empty, checks that
        if not '"v":null' in i:
            #find the value
            value = i[i.rfind('"f":"'):]
            value = value.replace('"f":"', '')
            value = int(value[:value.rfind('"')])
            
            #finds the date part
            date = i[:i.rfind('"v":')]
            date = date[date.rfind('"f":'):]
            date = date.replace('"f":"', '')

            date = date.split(' ') #creates a list

            num = date[0] #get day
            num = num.replace('.', '') 
            #if num is 2, pythons strptime would make this to 20, so adding extra 0 is needed
            if int(num) < 10:
                num = '0' + str(num)
            
            month = date[1]
            year = date[2]
            #in Finnish on time string part has klo on it. in swedish there is only date items
            if 'klo' in date:
                time = date[4]
            else:
                #if raw text is in swedish
                time = date[3]
            
            mm = getMonth(month)
            dtime = str(num)+mm+str(year)+str(time)
            #time still has gtm in it, lets remove it
            dtime = dtime[:dtime.rfind('GTM')]
            time = datetime.strptime(dtime, "%d%m%Y%H:%M") #make it a date object
            
            #save data to db
            addTrend({'time': time, 'value': value}, id)

  
def main(startID):
    #get stock names and id's
    mainData()
    
    #get klid list
    ids = getIDList()

    for id in ids[int(startID):]:
        #get day data from stocks
        textData = getData(id)
        #add them to db
        asd = addStockDatatoDB(textData, id)
            
        #get trend data
        stockName = getStockname(id)    
        trendData = getTrendData(stockName)
        #parse and add to db
        parseTrendText(trendData, id)
        
        #anti doss
        sleep(2)
 
 
if __name__ == "__main__":
    #if script stopping running middle of data mining 
    #user can specify stock id where to start the data mining process
    #by giving a command line argument the last processed stock's id-1 
    if len(sys.argv) < 2:
        main(0)
    else:
        main(sys.argv[1])
    

    
    