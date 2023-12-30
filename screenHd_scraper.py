from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import utils
import requests
import urllib3
from urllib3.util import ssl_

ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

company_name = "shinetsu"

def get_dynamic_page_links(driver,url):

    # 指定されたURLにアクセス
    driver.get(url)

    # ページが完全にロードされるまで待機
    driver.implicitly_wait(10)

    # ページからデータを取得
    section_elements = driver.find_elements(By.CSS_SELECTOR, "#content > section.news-section._page-news > div.news-wrapp > div > div.item")
    links_dates = []
    for section in section_elements:
        a_element = section.find_element(By.CSS_SELECTOR, "div > a")
        p_element = section.find_element(By.CSS_SELECTOR, "p.date > a")
        absolute_link = a_element.get_attribute("href")
        date = utils.convert_date_format(p_element.text, '%Y.%m.%d')
        links_dates.append((absolute_link, date))

    return links_dates

def main(company_name):
    # WebDriverのセットアップ
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    session = requests.Session()

    links_dates = []
    url = "https://www.shinetsu.co.jp/jp/news/#2023"
    links_dates = get_dynamic_page_links(driver, url)

    data = []
    for link, date in links_dates:
        if link.endswith(".pdf"):
            text = utils.get_pdf_text_with_pdfplumber(session, link)
        else:
            text = text = utils.scrape_dynamic_site_text(driver, link)
        if text is not None:
            data.append({'newsDate': date, 'content': text})
    # WebDriverを終了
    driver.quit()

    print(links_dates)
    processed_data = utils.process_data(data, company_name)
    utils.save_data_to_csv(processed_data, company_name)
    # utils.write_to_csv(data, f"data/{company_name}_news.csv")

if __name__ == "__main__":
    main(company_name)