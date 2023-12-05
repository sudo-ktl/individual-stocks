import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from datetime import time
import pytz
import re
import csv

target_date = '2023.11.11'
year = int(target_date[0:4])
month = int(target_date[5:7])
day = int(target_date[8:10])
stock_date = target_date.replace('.','/')[2:] #yy/mm/ddの形
df = pd.read_csv('fastretailing_stock20231109.csv')
stock_date_list = df['日付'].tolist()


# yy/mm/ddの形で渡している
def isValidDate(list,stock_date): 
    if(stock_date in stock_date_list):
        return True
    else:
        return False
    
# yy/mm/ddの形で返す
# 株価の日時リストにニュースの日時が無い場合、直近の株価日時を返す
def findNextValidDate(stock_date,stock_date_list):
    current_date = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    t = stockDateToDateObject(stock_date)
    tDatetime = dateToDatetime(t)
    while(current_date >= tDatetime):
        t1 = t + datetime.timedelta(days=1)
        t1ft = t1.strftime('%y/%m/%d')
        print(t1ft)
        if(isValidDate(stock_date_list,t1ft)):
            return t1ft
        else:
            t = t1
            tDatetime = dateToDatetime(t)
    print(current_date,tDatetime)
    return current_date #株価リストにまだ日時が登録されていない事を表したい

# yy/mm/ddの形で渡してdateオブジェクトを返す
def stockDateToDateObject(stock_date):
    y = stock_date[0:2]
    year = int(f"20{y}")
    month = int(stock_date[3:5])
    day = int(stock_date[6:8])
    return datetime.date(year,month,day)

def dateToDatetime(dateObject):
    dt_native = datetime.datetime.combine(dateObject, time())
    return pytz.timezone('Asia/Tokyo').localize(dt_native)


print(findNextValidDate(stock_date,stock_date_list))



# print(year,month,day)

# findNextDate(year,month,day)