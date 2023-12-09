from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import utils

company_name = "yamatoHd"

def get_dynamic_page_links(driver,url):

    # 指定されたURLにアクセス
    driver.get(url)

    # ページが完全にロードされるまで待機
    driver.implicitly_wait(10)

    # ページからデータを取得
    section_elements = driver.find_elements(By.CSS_SELECTOR, "article.news__article")
    links_dates = []
    for section in section_elements:
        a_element = section.find_element(By.CSS_SELECTOR, "a")
        p_element = section.find_element(By.CSS_SELECTOR, "a > div > div.news__property > time")
        absolute_link = a_element.get_attribute("href")
        date = utils.convert_date_format(p_element.text, '%Y年%m月%d日')
        links_dates.append((absolute_link, date))

    return links_dates

def main(company_name):
    # WebDriverのセットアップ
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    links_dates = []
    for page in range(1, 8):  # ページ1から7までループ
        url = f"https://www.yamato-hd.co.jp/news/?year=2023&cate=&label=all&page={page}"
        links_dates.extend(get_dynamic_page_links(driver, url))

    data = []
    for link, date in links_dates:
        if link.endswith(".pdf"):
            text = utils.get_pdf_text(driver, link)
        else:
            text = text = utils.scrape_dynamic_site_text(driver, link)
        if text is not None:
            data.append({'newsDate': date, 'content': text})
    # WebDriverを終了
    driver.quit()

    print(links_dates)
    utils.write_to_csv(data, f"data/{company_name}_news.csv")

if __name__ == "__main__":
    main(company_name)