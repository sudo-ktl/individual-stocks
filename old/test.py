import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
from datetime import time
import pytz
import re
import csv

def isValidDate(stock_date_list,stock_date): 
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
        if(isValidDate(stock_date_list,t1ft)):
            return t1ft
        else:
            t = t1
            tDatetime = dateToDatetime(t)
    # print(current_date,tDatetime)
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

# サブのcsv読み込み
df_stock = pd.read_csv('data/fastretailing_stock20231114.csv')
stock_date_list = df_stock['日付'].tolist()
stock_list = df_stock.values.tolist() #csvの二次元配列

# メインのcsv読み込み
df_news = pd.read_csv('data/fastRetailing_news_20231114.csv')
news_list = df_news.values.tolist()

result_list = [] 
for news in news_list:
    stock_date = news[0]
    if(isValidDate(stock_date_list,stock_date)):
        print(stock_date)
        for stock in stock_list:
            if stock[0] == stock_date:
                result_list.append(stock)
            else:
                continue
    else:
        stock_date = findNextValidDate(stock_date,stock_date_list)
        print(stock_date)
        for stock in stock_list:
            if stock[0] == stock_date:
                result_list.append(stock)
            else:
                continue