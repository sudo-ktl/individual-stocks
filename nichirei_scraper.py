import time
from requests_html import HTMLSession
from urllib.parse import urljoin
import utils

company_name = 'nichirei'

def get_page_links(session, url):
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
    response.encoding = 'utf-8'
    links_dates = []
    section_elements = response.html.find("section.p-block__small")
    for section in section_elements:
        a_elements = section.find("ul > li > a")
        p_elements = section.find("ul > li > a > p > span")
        for a, p in zip(a_elements, p_elements):
            relative_link = a.attrs.get("href", "")
            # 相対URLを絶対URLに変換
            absolute_link = urljoin(url, relative_link)
            print(absolute_link)
            date = utils.convert_date_format(p.text, '%Y年%m月%d日')
            print(date)
            links_dates.append((absolute_link, date))
    return links_dates


def main(company_name):
    url = "https://www.nichirei.co.jp/news/2023"
    session = HTMLSession()
    links_dates = get_page_links(session, url)
    print(links_dates)
    data = []
    for link, date in links_dates:
            if link.endswith(".pdf"):
                text = utils.get_pdf_text(session,link,verify=False)
            else:
                text = utils.scrape_text(session,link,verify=False)
            if text is not None:
                data.append({'newsDate': date, 'content': text})
            time.sleep(2)
    utils.write_to_csv(data, f"data/{company_name}_news.csv")


if __name__ == "__main__":
    main(company_name)