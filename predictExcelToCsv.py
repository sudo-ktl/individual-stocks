import pandas as pd

def read_excel_to_dict_list(file_path, column_names):
    df = pd.read_excel(file_path, header=None, names=column_names)
    df['predictDate'] = pd.to_datetime(df['predictDate']).dt.strftime('%y/%m/%d')
    dict_list = df.to_dict(orient='records')
    return dict_list

def write_dict_list_to_csv(dict_list, output_file_path):
    df = pd.DataFrame(dict_list)
    df.to_csv(output_file_path, index=False)

def convert_excel_to_csv(input_file_path, output_file_path, column_names):
    dict_list = read_excel_to_dict_list(input_file_path, column_names)
    write_dict_list_to_csv(dict_list, output_file_path)

# 使用例
column_names = ['predictDate', 'predictScore']  # 列名のリストを設定します
convert_excel_to_csv('data/predictscore20231111.xlsx', 'data/predictscore20231111.csv', column_names)