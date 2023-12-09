import requests
import time
import csv
from requests_html import HTMLSession
from PyPDF2 import PdfReader
from io import BytesIO
from datetime import datetime
from urllib.parse import urljoin
import re
import utils

company_name = 'keio'

def get_page_links(session, url):
    print('get_page_links')
    response = session.get(url)
    links_dates = []
    dl_elements = response.html.find("dl")
    for dl in dl_elements:
        a_elements = dl.find("dd > a")
        p_elements = dl.find("dt > p")
        for a, p in zip(a_elements, p_elements):
            relative_link = a.attrs.get("href", "")
            # 相対URLを絶対URLに変換
            absolute_link = urljoin(url, relative_link)
            date = utils.convert_date_format(p.text, '%Y. %m. %d')
            if absolute_link.endswith(".pdf"):
                links_dates.append((absolute_link, date))
    return links_dates


def main(company_name):
    url = "https://www.keio.co.jp/news/update/news_release/news_all.html"
    session = HTMLSession()
    links_dates = get_page_links(session, url)
    print(links_dates)
    data = []
    for link, date in links_dates:
        text = utils.get_pdf_text(link)
        if text is not None:
            data.append({'newsDate': date, 'content': text})
        time.sleep(2)
    utils.write_to_csv(data, f"data/{company_name}_news.csv")


if __name__ == "__main__":
    main(company_name)