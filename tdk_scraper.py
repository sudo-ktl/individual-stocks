from requests_html import HTMLSession
import os
import csv
import time
import glob
from datetime import datetime, timedelta
from requests.exceptions import RequestException

# グローバルスコープでURLを定義
URL = "https://www.tdk.com/ja/news_center/press/index.html?f%5B0%5D=news_center_press_releases_display_date%3A2023"

def fetch_data(url):
    session = HTMLSession()
    try:
        response = session.get(url)
    except RequestException as e:
        print(f"An error occurred while getting the response from the URL: {url}")
        print(f"Error: {e}")
        return None
    return response

def scrape_text(url):
    response = fetch_data(url)
    if response is None:
        return "URLからのレスポンスの取得に失敗しました"

    text_elements = response.html.find("p")

    if text_elements:
        text = " ".join([element.text.replace('\n', ' ') for element in text_elements])
    else:
        text = "pタグがありませんでした"

    return text

def parse_article(article):
    link_element = article.find("a", first=True)
    if link_element is None:
        print(f"An error occurred while parsing the article: 'a' element not found. Article content: {article.text[:100]}")
        return None

    link = link_element.attrs["href"]

    date_element = article.find("time", first=True)
    if date_element is None:
        print(f"An error occurred while parsing the article at {link}: 'time' element not found.")
        return None

    date = date_element.text
    formatted_date = convert_date_format(date)
    text = scrape_text(link)

    return {"newsDate": formatted_date, "content": text}

def parse_press_releases(response):
    if response is None:
        return []

    press_releases = []
    articles = response.html.find(".views-row", first=False)
    for article in articles:
        press_release = parse_article(article)
        if press_release is not None:
            press_releases.append(press_release)

    return press_releases

def get_press_releases():
    # グローバルスコープで定義したURLを使用
    response = fetch_data(URL)
    time.sleep(1)
    return parse_press_releases(response)

def read_stock_data(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return {row['stockDate']: row for row in reader}
    
def find_nearest_date(stock_data, target_date):
    date_format = "%y/%m/%d"
    target_date = datetime.strptime(target_date, date_format)
    future_dates = {k: v for k, v in stock_data.items() if datetime.strptime(k, date_format) >= target_date}
    if not future_dates:
        raise ValueError("No future dates available")
    nearest_date = min(future_dates.keys(), key=lambda d: abs(datetime.strptime(d, date_format) - target_date))
    return stock_data[nearest_date]


def merge_press_releases_with_stock_data(press_releases, stock_data, merge_keys):
    merged_press_releases = []
    for press_release in press_releases:
        date = press_release['newsDate']
        if date in stock_data:
            press_release.update({k: stock_data[date][k] for k in (merge_keys)})
            merged_press_releases.append(press_release)
        else:
            try:
                nearest_data = find_nearest_date(stock_data, date)
                press_release.update({k: nearest_data[k] for k in (merge_keys)})
                merged_press_releases.append(press_release)
            except ValueError:
                continue
    return merged_press_releases


def export_to_csv(press_releases, filepath):

    fieldnames = ['newsDate', 'content', 'stockDate', 'start', 'end', 'flag', 'nikkeiFlag']

    # データを逆順に並べ替える
    press_releases = list(reversed(press_releases))

    # データを追記する
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # if not existing_data:
        writer.writeheader()
        writer.writerows(press_releases)

def convert_date_format(date):
    try:
        dt = datetime.strptime(date, '%Y年%m月%d日')
        return dt.strftime('%Y/%m/%d')[2:]
    except ValueError:
        print(f"Error: The date '{date}' does not match the format '%Y年%m月%d日'")
        return None

def get_current_date():
    return datetime.now().strftime('%Y%m%d')

dt_now = get_current_date()
press_releases = get_press_releases()

stock_data = read_stock_data('data/tdk_stock.csv') #企業の株価データを読み込む
merged_data = merge_press_releases_with_stock_data(press_releases, stock_data, ['stockDate','start', 'end', 'flag'])

nikkei_data = read_stock_data('data/nikkei225_stock.csv') #日経平均株価データを読み込む
merged_data_with_nikkei = merge_press_releases_with_stock_data(merged_data, nikkei_data, ['nikkeiFlag'])    

# pridict_data = read_stock_data('data/predictscore20231111.csv') #予測データを読み込む
# merged_data_with_predict = merge_press_releases_with_stock_data(merged_data_with_nikkei, pridict_data, ['predictScore'])

export_to_csv(merged_data_with_nikkei, f"result/tdk_{dt_now}.csv")

