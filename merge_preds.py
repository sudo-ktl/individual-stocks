import csv

# 感情解析の結果をニュースデータにマージする

def read_news_data(file_path):
    print('read_news_data')
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def merge_base_and_pred(base_data, preds):
    for base, pred in zip(base_data, preds):
        # predsの'content'以外のキーを取得
        keys_except_content = [key for key in pred.keys() if key != 'content']
        # 'content'以外のキーとその値をbaseに追加
        for key in keys_except_content:
            base[key] = pred[key]
    return base_data

def dict_list_to_csv(dict_list, csv_file_path):
    # フィールド名（列名）のリストを作成
    fieldnames = dict_list[0].keys()

    # CSVファイルに書き出し
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # ヘッダー（列名）を書き出し
        writer.writeheader()

        # 各辞書を行として書き出し
        for dict in dict_list:
            writer.writerow(dict)
    
base_data = read_news_data('result/jal_20231207.csv')
# print(base_data[0])
    
preds = read_news_data('data/jal_preds.csv')
# print(preds[0])

# print(is_content_match(base_data, preds))
merged_data = merge_base_and_pred(base_data, preds)


print(merged_data[0])

dict_list_to_csv(merged_data, 'result/jal_20231207_merged.csv')