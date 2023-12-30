import re
import csv

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def split_text_by_delimiter(text, delimiter):
    return re.split(delimiter, text)

def convert_list_to_dict_list(parts, flags):
    result = []
    dict = {}
    for i,v in enumerate(parts):
        if(i%2==0):
            dict['content'] = v.replace('\n', '')
        else:
            for flag in flags:
                if flag in v:
                    start = v.index(flag)
                    end = v.index('\n', start)
                    dict[flag] = v[start + len(flag)+1:end].strip().replace('\n', '')
            result.append(dict)
            dict = {}
    return result


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

def main(read_data_path,output_csv_path):
    text = read_text_file(read_data_path).replace('\r', '').replace('  ', ' ')
    delimiter = '--------------------------------------------------'
    parts = split_text_by_delimiter(text, delimiter)
    parts = [part for part in parts if part]
    results = convert_list_to_dict_list(parts, flags)
    dict_list_to_csv(results, output_csv_path)

flags = [
    '喜びを感じた',
    '恐怖を感じた', 
    '驚きを感じた', 
    '信頼できる情報と感じた', 
    '曖昧な情報と感じた', 
    '何かの意図をもって書かれたと感じた', 
    '経済に期待がもてると感じた'
]

if __name__ == '__main__':
    main('data/jal-preds.txt', 'data/jal_preds.csv')
