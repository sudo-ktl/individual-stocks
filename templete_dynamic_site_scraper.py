from requests_html import HTMLSession
from urllib.parse import urljoin
import utils
from companies import company_dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re

def fetch_dynamic_page_links(driver, url):
    driver.get(url)
    driver.implicitly_wait(10)

    section_elements = driver.find_elements(By.CSS_SELECTOR, "#ad2023 dl > a")
    links_dates = []
    for a_element in section_elements:
        dt_element = a_element.find_element(By.XPATH,'./dt')
        
        # デバッグ情報の出力
        print("Text in dt element:", dt_element.text)
        
        match = re.search(r'\d{4}年\d{1,2}月\d{1,2}日', dt_element.text)
        if match:
            date_text = match.group()  # '2023年12月28日' を抽出
        else:
            date_text = None  # 日付形式が見つからない場合

        absolute_link = a_element.get_attribute("href")
        print(absolute_link)
        date = utils.convert_date_format(date_text, '%Y年%m月%d日')
        print(date)
        links_dates.append((absolute_link, date))


    return links_dates

def fetch_links_dates_from_dynamic_site(driver, params,get_page_links_func):
    """
    指定されたURLからリンクと日付を取得します。

    Parameters:
    url (str): スクレイピングするWebページのURL。
    get_page_links_func (function): ページからリンクを取得するための関数。この関数は特定のHTML構造に依存します。
    verify (bool, optional): SSL証明書の検証を行うかどうかを指定します。デフォルトはTrue。

    Returns:
    list: リンクと日付のペアのリスト。
    """
    url = params['url']
    is_multi_page = params.get('is_multi_page', False)
    total_page = params.get('total_page', 1) if is_multi_page else 1

    links_dates = []
    if is_multi_page: #ページごとに変更が必要
        for page in range(1, total_page + 1):
            page_url = f"{url}{page}"
            links_dates.extend(get_page_links_func(driver, page_url))
    else:
        links_dates.extend(get_page_links_func(driver, url))
    return links_dates

def main(company_name, ignore_strings, params_list):
    """
    指定された会社のウェブサイトからデータをスクレイピングし、CSVファイルに保存します。

    Parameters:
    company_name (str): 会社の名前。
    ignore_strings (list): リンクから除外する文字列のリスト。
    params_list (list): 各URLのパラメータと対応するget_page_links_funcを含む辞書のリスト。各辞書は以下のキーを持つべきです：
        - 'url' (str): スクレイピングするWebページのURL。
        - 'get_page_links_func' (function): ページからリンクを取得するための関数。この関数は特定のHTML構造に依存します。
        - 'is_multi_page' (bool, optional): ページが複数ある場合はTrue、一ページのみの場合はFalse。デフォルトはFalse。
        - 'total_page' (int, optional): 'is_multi_page'がTrueの場合、スクレイピングするページ数を指定します。

    Returns:
    None
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    session = utils.create_session()
    all_links_dates = []
    for params in params_list:
        all_links_dates.extend(fetch_links_dates_from_dynamic_site(driver, params,params['get_page_links_func']))
    data = utils.get_data(session, all_links_dates, ignore_strings,driver=driver)
    processed_data = utils.process_data(data, company_name)
    utils.save_data_to_csv(processed_data, company_name)

if __name__ == "__main__":
    key = 'suzuki' #keyをcompany_dictのkeyに変更
    company_name = company_dict[key]['name'] #keyを変更
    ignore_strings = ['.pdf'] #リンク先にpdfがある場合、除外する文字列を追加
    params_list = [
        {'url': company_dict[key]['newsUrl'],'get_page_links_func': fetch_dynamic_page_links}
    ]
    main(company_name, ignore_strings, params_list)