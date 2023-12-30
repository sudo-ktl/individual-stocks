import csv
import sys
from datetime import datetime
import os
import glob
from companies import company_dict


def remove_nul_characters(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    content = content.replace('\x00', '')  # NUL文字を置換
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_news_data(file_path):
    print('read_news_data')
    csv.field_size_limit(sys.maxsize)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except csv.Error as e:
        if 'line contains NUL' in str(e):
            # NUL文字を削除して再試行
            remove_nul_characters(file_path)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                return list(reader)
        else:
            raise  # 他のエラーは再発生させる


    
def read_stock_data(filepath):
    print('read_stock_data')
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return {row['stockDate']: row for row in reader}
    
def find_nearest_date(stock_data, target_date):
    print('find_nearest_date')
    date_format = "%y/%m/%d"
    target_date = datetime.strptime(target_date, date_format)
    future_dates = {k: v for k, v in stock_data.items() if datetime.strptime(k, date_format) >= target_date}
    if not future_dates:
        raise ValueError("No future dates available")
    nearest_date = min(future_dates.keys(), key=lambda d: abs(datetime.strptime(d, date_format) - target_date))
    return stock_data[nearest_date]
    
def merge_press_releases_with_stock_data(press_releases, stock_data, merge_keys, use_nearest_date=True):
    print('merge_press_releases_with_stock_data')
    merged_press_releases = []
    for press_release in press_releases:
        date = press_release['newsDate']
        if date in stock_data:
            print("日付が一致しました")
            press_release.update({k: stock_data[date][k] for k in merge_keys})
            merged_press_releases.append(press_release)
        else:
            print("日付が一致しませんでした")
            if use_nearest_date:
                try:
                    nearest_data = find_nearest_date(stock_data, date)
                    press_release.update({k: nearest_data[k] for k in merge_keys})
                    merged_press_releases.append(press_release)
                except ValueError:
                    continue
            else:
                press_release.update({k: 'none' for k in merge_keys})
                merged_press_releases.append(press_release)
    return merged_press_releases
    
def merged_data_to_csv(press_releases, filepath):
    print('merged_data_to_csv')

    fieldnames = ['newsDate', 'content', 'id','stockDate', 'start', 'end', 'flag', 'nikkeiFlag','predictScore']

    # press_releases = list(press_releases)

    # データを追記する
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # if not existing_data:
        writer.writeheader()
        writer.writerows(press_releases)


def cleanup_directory(directory):
    # ディレクトリ内の全てのCSVファイルをリストアップ
    files = glob.glob(os.path.join(directory, '*.csv'))

    # 各会社の最新の日付を保存する辞書
    latest_dates = {}

    for file in files:
        # ファイル名から会社名と日付を抽出
        basename = os.path.basename(file)
        company_name, date_str = basename.split('_')
        date_str = date_str.replace('.csv', '')

        # 日付をdatetimeオブジェクトに変換
        date = datetime.strptime(date_str, '%Y%m%d')

        # 会社の最新の日付を更新
        if company_name not in latest_dates or date > latest_dates[company_name][1]:
            latest_dates[company_name] = (file, date)

    # 最新でないファイルを削除
    for file in files:
        company_name = os.path.basename(file).split('_')[0]
        if file != latest_dates[company_name][0]:
            os.remove(file)
    
def get_names(company_dict):
    return [info['name'] for info in company_dict.values()]
    
    
def main(company_name):
    print(f'company_name: {company_name}')
    press_releases = read_news_data(f'data/{company_name}_news.csv')

    stock_data = read_stock_data(f'data/{company_name}_stock.csv') #企業の株価データを読み込む
    merged_data = merge_press_releases_with_stock_data(press_releases, stock_data, ['stockDate','start', 'end', 'flag'])
    print('merged_dataを準備しました')

    nikkei_data = read_stock_data('data/nikkei225_stock.csv') #日経平均株価データを読み込む
    merged_data_with_nikkei = merge_press_releases_with_stock_data(merged_data, nikkei_data, ['nikkeiFlag'])
    print('merged_data_with_nikkeiを準備しました')    

    predict_data = read_stock_data('data/predictscore20231218.csv') #予測データを読み込む
    merged_data_with_predict = merge_press_releases_with_stock_data(merged_data_with_nikkei, predict_data, ['predictScore'], False)
    print('merged_data_with_predictを準備しました')

    dt_now = datetime.now().strftime('%Y%m%d')
    print(type(merged_data_with_predict))

    merged_data_to_csv(merged_data_with_predict, f"result/{company_name}_{dt_now}.csv")
    
if __name__ == '__main__':
    company_names = get_names(company_dict)
    for company_name in company_names:
        main(company_name)
    cleanup_directory('result')