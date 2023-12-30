import time
from requests_html import HTMLSession
from urllib.parse import urljoin
import utils

company_name = 'keisei'

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
    article_elements = response.html.find("div.article__wrap")
    if len(article_elements) >= 2:
        a_elements = article_elements[1].find("a")
        p_elements = article_elements[1].find("a > p.dateTxt >time")
        for a, p in zip(a_elements, p_elements):
            relative_link = a.attrs.get("href", "")
            # 相対URLを絶対URLに変換
            absolute_link = urljoin(url, relative_link)
            # print(absolute_link)
            date = utils.convert_date_format(p.text, '%Y.%m.%d')
            # print(date)
            links_dates.append((absolute_link, date))
    return links_dates

def get_pdf_link(session, url, selector, verify=True):
    """
    指定されたURLのページから指定されたセレクタに一致する要素のhref属性を取得します。

    引数:
    session (requests.Session): requests.Sessionのインスタンス。
    url (str): href属性を取得するWebサイトのURL。
    selector (str): href属性を取得する要素のCSSセレクタ。
    verify (bool): SSL証明書の検証を行うかどうか。

    戻り値:
    str: 指定されたセレクタに一致する要素のhref属性。該当する要素がない場合はNone。
    """
    response = session.get(url, verify=verify)
    response.encoding = 'utf-8'
    element = response.html.find(selector, first=True)
    if element is not None:
        relative_link = element.attrs.get("href", "")
        # 相対URLを絶対URLに変換
        absolute_link = urljoin(url, relative_link)
        return absolute_link
    return None

def main(company_name):
    url = "https://www.keisei.co.jp/news/"
    session = HTMLSession()
    links_dates = get_page_links(session, url)
    # print(links_dates)
    data = []
    for link, date in links_dates:
        pdf_link = get_pdf_link(session, link, "article > div.newsBlock > div.pdfBtn > a", verify=False)
        print(pdf_link)
        if pdf_link is not None and pdf_link.endswith(".pdf"):
            text = utils.get_pdf_text_with_pdfplumber(session,pdf_link,verify=False)
            if text is not None:
                data.append({'newsDate': date, 'content': text})
        else:
            text = utils.scrape_text(session,link,verify=False)
        time.sleep(2)

    processed_data = utils.process_data(data, company_name)
    utils.save_data_to_csv(processed_data, company_name)
    # utils.write_to_csv(data, f"data/{company_name}_news.csv")


if __name__ == "__main__":
    main(company_name)