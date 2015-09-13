#Stock data miner and analyser for Finish stocks README

##Getting Started

### Requirements
- Python 2.7 used
- 4 spaces used for indenting
#### Packages used
- Sqlalchemy, transaction, requests

### Instructions

#### Netcrawler.py:
-Mines all the data
- optional arguments: int. Int is related to stocks ids, if script stops in middle of running you can restart it where it stopped

#### dbconnector.py 
- Saves data to db
- When started it does all the data analysis 
- optional agruments: 
-- first: int, number that tell how many days we should analyse
-- Second. "all" keyword that prints every stock information to text file

#### db/initializedb.py
- initializes the database, if you want clean start    