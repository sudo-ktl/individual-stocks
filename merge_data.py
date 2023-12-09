import csv
from datetime import datetime




def read_news_data(file_path):
    print('read_news_data')
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)
    
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

    fieldnames = ['newsDate', 'content', 'stockDate', 'start', 'end', 'flag', 'nikkeiFlag','predictScore']

    # press_releases = list(press_releases)

    # データを追記する
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # if not existing_data:
        writer.writeheader()
        writer.writerows(press_releases)
    
def main(company_name):

    press_releases = read_news_data(f'data/{company_name}_news.csv')

    stock_data = read_stock_data(f'data/{company_name}_stock.csv') #企業の株価データを読み込む
    merged_data = merge_press_releases_with_stock_data(press_releases, stock_data, ['stockDate','start', 'end', 'flag'])
    print('merged_dataを準備しました')

    nikkei_data = read_stock_data('data/nikkei225_stock.csv') #日経平均株価データを読み込む
    merged_data_with_nikkei = merge_press_releases_with_stock_data(merged_data, nikkei_data, ['nikkeiFlag'])
    print('merged_data_with_nikkeiを準備しました')    

    predict_data = read_stock_data('data/predictscore20231111.csv') #予測データを読み込む
    merged_data_with_predict = merge_press_releases_with_stock_data(merged_data_with_nikkei, predict_data, ['predictScore'], False)
    print('merged_data_with_predictを準備しました')

    dt_now = datetime.now().strftime('%Y%m%d')
    print(type(merged_data_with_predict))

    merged_data_to_csv(merged_data_with_predict, f"result/{company_name}_{dt_now}.csv")

if __name__ == '__main__':
    main('keisei')