import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
from datetime import time
import pytz
import re
import csv

# ニュースを日付と本文のリストで取得する
news_src = 'https://www.fastretailing.com/jp/about/news/2023.html'
response = requests.get(news_src)
soup = BeautifulSoup(response.content, 'lxml')
elem = soup.find('dl',class_ = 'about-newsrelease pkg')

date_elems = elem.find_all('dt')
date_list = []
for date_elem in date_elems:
    stock_date = date_elem.get_text().replace('.','/')[2:]
    date_list.append(stock_date)

url_elems = elem.find_all('a')
url_list = []
for url_elem in url_elems:
    url_list.append('https://www.fastretailing.com' + url_elem.attrs['href'])

text_list = []
for url in url_list:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    elem = soup.find('div',class_ = 'entry-content pkg')
    text_list.append(elem.getText().replace('\n',''))

news_list = list(zip(date_list,text_list))

# print(news_list[0])

dt_now = datetime.datetime.now().strftime('%Y%m%d')
file_name = 'fastRetailing_news_' + dt_now + '.csv'

with open(f"data/{file_name}",'w') as csv_file:
    fieldnames = ['newsDate','content']
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)
    writer.writerows(news_list)