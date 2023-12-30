import utils
import hashlib

def generate_id(news_content):
    # ニュース本文からハッシュ値を生成
    hash_object = hashlib.sha256(news_content.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

def add_unique_id_if_not_exists(dict_list):
    for dict_ in dict_list:
        if 'id' not in dict_:
            content = dict_['content'] + dict_['newsDate']
            unique_id = generate_id(content)
            dict_['id'] = unique_id
    return dict_list

def main(path):
    dict_list = utils.read_news_data(path)
    dict_list_with_id = add_unique_id_if_not_exists(dict_list)
    utils.write_to_csv_not_reversed(dict_list_with_id, path)

if __name__ == '__main__':
    main('data/test/news_new.csv')