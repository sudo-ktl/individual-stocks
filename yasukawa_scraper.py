from requests_html import HTMLSession
from urllib.parse import urljoin
import utils
from companies import company_dict

def get_page_links(session, url): #ページごとに変更が必要
    """
    指定されたURLのページからリンクと日付を取得します。この関数はHTMLの構造に依存します。
    HTMLの構造が異なる場合は、適切に調整する必要があります。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): リンクと日付を取得するページのURL。

    戻り値:
    list of tuple: 各タプルは(URLのリンク, 日付)を表します。日付はデフォルトで'%y/%m/%d'の形式で表されます。

    注意:
    この関数は特定のHTML構造を前提としています。HTMLのセクション要素、リンク要素、日付要素のセレクタは、
    対象となるウェブページの構造に合わせて適切に調整する必要があります。
    """
    print('get_page_links')
    response = session.get(url)
    links_dates = []
    section_elements = response.html.find(" #contents > div.news_list ") #構造に合わせて変更
    for section in section_elements:
        a_elements = section.find(" dl > dd > a ") #構造に合わせて変更
        p_elements = section.find(" dl > dt > b ") #構造に合わせて変更
        for a, p in zip(a_elements, p_elements):
            relative_link = a.attrs.get("href", "")
            absolute_link = urljoin(url, relative_link)
            print(absolute_link)
            date = utils.convert_date_format(p.text, '%Y年%m月%d日') #日付の形式に合わせて変更
            print(date)
            links_dates.append((absolute_link, date))
    return links_dates

def get_page_links2(session, url): #ページごとに変更が必要
    """
    指定されたURLのページからリンクと日付を取得します。この関数はHTMLの構造に依存します。
    HTMLの構造が異なる場合は、適切に調整する必要があります。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): リンクと日付を取得するページのURL。

    戻り値:
    list of tuple: 各タプルは(URLのリンク, 日付)を表します。日付はデフォルトで'%y/%m/%d'の形式で表されます。

    注意:
    この関数は特定のHTML構造を前提としています。HTMLのセクション要素、リンク要素、日付要素のセレクタは、
    対象となるウェブページの構造に合わせて適切に調整する必要があります。
    """
    print('get_page_links')
    response = session.get(url)
    links_dates = []
    section_elements = response.html.find(" #businessmain_2_latestProductList > ul.m-list-news ") #構造に合わせて変更
    for section in section_elements:
        a_elements = section.find(" li > div.m-list-news_text > a ") #構造に合わせて変更
        p_elements = section.find(" li > div.m-list-news_information > time ") #構造に合わせて変更
        for a, p in zip(a_elements, p_elements):
            relative_link = a.attrs.get("href", "")
            absolute_link = urljoin(url, relative_link)
            print(absolute_link)
            date = utils.convert_date_format(p.text, '%Y/%m/%d') #日付の形式に合わせて変更
            print(date)
            links_dates.append((absolute_link, date))
    return links_dates

    
def get_links_dates(session, params,get_page_links_func):
    """
    指定されたURLからリンクと日付を取得します。

    Parameters:
    session (requests.Session): requestsライブラリのSessionオブジェクト。
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
            links_dates.extend(get_page_links_func(session, page_url))
    else:
        links_dates.extend(get_page_links_func(session, url))
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
    session = utils.create_session()
    all_links_dates = []
    for params in params_list:
        all_links_dates.extend(get_links_dates(session, params,params['get_page_links_func']))
    data = utils.get_data(session, all_links_dates, ignore_strings)
    processed_data = utils.process_data(data, company_name)
    utils.save_data_to_csv(processed_data, company_name)

if __name__ == "__main__":
    key = 'yasukawa' #keyをcompany_dictのkeyに変更
    company_name = company_dict[key]['name'] #keyを変更
    ignore_strings = ['.pdf'] #リンク先にpdfがある場合、除外する文字列を追加
    params_list = [
        {'url': company_dict[key]['newsUrl'],'get_page_links_func': get_page_links},
    ]
    main(company_name, ignore_strings, params_list)