import utils
import pandas as pd

def read_csv_to_dict_list(csv_file_path):
    # CSVファイルをDataFrameに読み込む
    df = pd.read_csv(csv_file_path)

    # 日付形式を変更する
    df['stockDate'] = pd.to_datetime(df['stockDate']).dt.strftime('%y/%m/%d')

    # DataFrameを辞書のリストに変換
    dict_list = df.to_dict(orient='records')

    return dict_list

dict_list = read_csv_to_dict_list('data/actionvsg20231218-cp.csv')
utils.dict_list_to_csv(dict_list, 'data/predictscore20231218.csv')

# 使用例
# この関数は外部のCSVファイルを読み込むため、実際のファイルパスを指定する必要があります。
# 以下の例では 'path/to/your/csvfile.csv' を実際のCSVファイルパスに置き換えてください。
# csv_file_path = 'path/to/your/csvfile.csv'
# dict_list = read_csv_to_dict_list(csv_file_path)
# print(dict_list[:5])  # 最初の5つの要素を表示
