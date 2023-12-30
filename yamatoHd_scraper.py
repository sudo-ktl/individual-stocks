from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import utils
from companies import company_dict

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

def main(company_name,url,ignore_strings):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    session = utils.create_session()
    links_dates = []
    try:
        for page in range(1, 8):
            page_url = f"{url}{page}"
            links_dates.extend(get_dynamic_page_links(driver, page_url))
        data = utils.get_data(session, links_dates, ignore_strings,driver=driver)
        processed_data = utils.process_data(data, company_name)
        utils.save_data_to_csv(processed_data, company_name)
    finally:
        driver.quit()


if __name__ == "__main__":
    company_name = company_dict['yamatoHd']['name']
    url = company_dict['yamatoHd']['newsUrl']
    ignore_strings = ['.pdf']
    main(company_name,url,ignore_strings)