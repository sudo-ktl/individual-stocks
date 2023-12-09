import requests
from bs4 import BeautifulSoup
import datetime
import csv
import time
import os

# src = 'https://kabutan.jp/stock/kabuka?code=0000&ashi=day&page='
# company_name = 'nikkei225'
# src = 'https://kabutan.jp/stock/kabuka?code=6762&ashi=day&page='
# company_name = 'tdk'
src = 'https://kabutan.jp/stock/kabuka?code=9983&ashi=day&page='
company_name = 'fastRetailing'


TABLE_INDEX = 5


def get_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def extract_table(html_content):
    table = html_content.find_all('table')[TABLE_INDEX]
    return table

def set_flag(open_price, close_price):
    if close_price > open_price:
        return 2
    elif close_price < open_price:
        return 1
    else:
        return 0
    
def extract_data(table):
    data = []
    dates = [header.text.strip() for header in table.find_all('th') if header.find_parent('tbody')]

    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 0:
            row_data = [col.text.strip() for col in cols]
            # 始値と終値を判断し、フラグを設定
            open_price = float(row_data[0].replace(',', ''))  # 始値を取得
            close_price = float(row_data[3].replace(',', ''))  # 終値を取得
            flag = set_flag(open_price, close_price)
            row_data = [val if i in [4, 5] else float(val.replace(',', '')) if val.replace(',', '').isdigit() else val for i, val in enumerate(row_data)]  # 数値に変換可能なデータを浮動小数点数に変換
            row_data.insert(0, dates.pop(0))
            row_data.append(flag)  # フラグを追加
            data.append(row_data)
    return data

def scrape_stock_data(src):
    data = []
    for page in range(1, 11):
        stock_src = f'{src}{page}'
        html_content = get_html(stock_src)
        table = extract_table(html_content)
        page_data = extract_data(table)
        data.extend(page_data)
    return data

def remove_duplicates(new_data, old_data):
    # 既存のデータの日付を取得
    old_dates = [row[0] for row in old_data if row]

    # 新しいデータの中で、既存のデータと日付が重複していないものだけを取得
    unique_data = [row for row in new_data if row[0] not in old_dates]

    return unique_data

def main(company_dict):
    for company_name, src in company_dict.items():
        time.sleep(1)
        new_data = scrape_stock_data(src)

        file_name = f"{company_name}_stock.csv"
        # ファイルが存在する場合、既存のデータを読み込む
        file_path = os.path.join("data", file_name)
        file_exists = os.path.isfile(file_path)
        old_data = []
        if file_exists:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                old_data = list(reader)

        # 重複を除いたデータを取得
        unique_data = remove_duplicates(new_data, old_data)

        if company_name == 'nikkei225':
            flag_name = 'nikkeiFlag'
        else:
            flag_name = 'flag'

        # ファイルが存在する場合、新しいデータを追記
        if file_exists:
            with open(f"data/{file_name}", 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(reversed(unique_data))
        # ファイルが存在しない場合、ヘッダーと新しいデータを書き込む
        else:
            with open(f"data/{file_name}", 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                header = ['stockDate', 'start', 'high', 'low', 'end', '前日比', '前日比%', 'volume', f'{flag_name}']
                writer.writerow(header)  # ヘッダー行を書き込む
                writer.writerows(reversed(unique_data))

        print(file_name)


# 実行するとsrcとcompany_nameの組み合わせを受け取ってループするようにしたい
if __name__ == "__main__":
    company_dict = {
        'nikkei225': 'https://kabutan.jp/stock/kabuka?code=0000&ashi=day&page=',
        'tdk': 'https://kabutan.jp/stock/kabuka?code=6762&ashi=day&page=',
        'fastRetailing': 'https://kabutan.jp/stock/kabuka?code=9983&ashi=day&page=',
        'jal':'https://kabutan.jp/stock/kabuka?code=9201&ashi=day&page=',
        'keio':'https://kabutan.jp/stock/kabuka?code=9008&ashi=day&page=',
        'nichirei':'https://kabutan.jp/stock/kabuka?code=2871&ashi=day&page=',
        'renesasElectronics':'https://kabutan.jp/stock/kabuka?code=6723&ashi=day&page=',
        'yamatoHd':'https://kabutan.jp/stock/kabuka?code=9064&ashi=day&page=',
        'keisei':'https://kabutan.jp/stock/kabuka?code=9009&ashi=day&page=',
    }
    main(company_dict)

