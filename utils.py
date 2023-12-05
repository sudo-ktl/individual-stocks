from requests_html import HTMLSession
import csv
import time
from datetime import datetime, timedelta
from requests.exceptions import RequestException


def fetch_data(url):
    session = HTMLSession()
    try:
        response = session.get(url)
    except RequestException as e:
        print(f"An error occurred while getting the response from the URL: {url}")
        print(f"Error: {e}")
        return None
    return response

def get_press_releases(url,perse_function):
    # グローバルスコープで定義したURLを使用
    response = fetch_data(url)
    time.sleep(1)
    press_releases = perse_function(response)
    return press_releases

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