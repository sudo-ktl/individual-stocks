from requests_html import HTMLSession
from urllib.parse import urljoin
import utils
import requests
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

def get_page_links(session, url): #ページごとに変更が必要
    """
    指定されたURLのページからリンクと日付を取得します。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): リンクと日付を取得するページのURL。

    戻り値:
    list of tuple: 各タプルは(URLのリンク, 日付)を表します。日付はデフォルトで'%y/%m/%d'の形式で表されます。

    """
    print('get_page_links')
    response = session.get(url)
    links_dates = []
    section_elements = response.html.find("#content > section.news-section._page-news > div.news-wrapp > div > div.item")
    print(section_elements)
    for section in section_elements:
        a_elements = section.find("div > a")
        p_elements = section.find("p.date > a")
        for a, p in zip(a_elements, p_elements):
            relative_link = a.attrs.get("href", "")
            absolute_link = urljoin(url, relative_link)
            print(absolute_link)
            date = utils.convert_date_format(p.text, '%Y.%m.%d')
            print(date)
            links_dates.append((absolute_link, date))
    return links_dates

def main(company_name, url, ignore_strings):
    session = utils.create_session()
    links_dates = get_page_links(session, url)
    data = utils.get_data(session, links_dates, ignore_strings)
    processed_data = utils.process_data(data, company_name)
    utils.save_data_to_csv(processed_data, company_name)

if __name__ == "__main__":
    company_name = 'shinetsu'
    url = "https://www.shinetsu.co.jp/jp/news/#2023"
    ignore_strings = ['.pdf']
    main(company_name,url,ignore_strings)