from requests_html import HTMLSession
import requests
from PyPDF2 import PdfReader
from PyPDF2 import PdfFileReader
from io import BytesIO
from urllib.parse import urljoin
import re
import csv
import time
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
import pdfplumber
import hashlib
import os

def read_news_data(file_path):
    # print('read_news_data')
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def fetch_data(url):
    print('fetch_data')
    session = HTMLSession()
    try:
        response = session.get(url)
        time.sleep(1)
    except RequestException as e:
        print(f"An error occurred while getting the response from the URL: {url}")
        print(f"Error: {e}")
        return None
    return response

def get_press_releases(url,perse_function):
    print('get_press_releases')
    response = fetch_data(url)
    press_releases = perse_function(response)
    return list(reversed(press_releases))

def get_current_date():
    print('get_current_date')
    return datetime.now().strftime('%Y%m%d')


def write_to_csv(data, filename):
    """
    データをCSVファイルに書き込みます。
    逆順で書き込みます。
    

    引数:
    data (list of dict): CSVに書き込むデータ。各辞書はCSVの1行を表し、キーは列のヘッダー、値はその列のデータを表します。
    filename (str): 書き込むCSVファイルの名前。

    戻り値:
    なし

    注意:
    この関数は新しいファイルを作成し、既存のファイルは上書きします。
    """
    print('write_to_csv')
    with open(filename, "w", newline="") as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in reversed(data):
            writer.writerow(row)

def dict_list_to_csv(data, filename):
    print('dict_list_to_csv')
    with open(filename, "w", newline="", encoding='utf-8') as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def write_to_csv_not_reversed(data, filename):
    """
    データをCSVファイルに書き込みます。

    引数:
    data (list of dict): CSVに書き込むデータ。各辞書はCSVの1行を表し、キーは列のヘッダー、値はその列のデータを表します。
    filename (str): 書き込むCSVファイルの名前。

    戻り値:
    なし

    注意:
    この関数は新しいファイルを作成し、既存のファイルは上書きします。
    """
    print('write_to_csv')
    with open(filename, "w", newline="") as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def get_pdf_text(session, url, verify=True):
    """
    指定されたURLからPDFをダウンロードし、そのテキスト内容を抽出します。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): ダウンロードするPDFのURL。
    verify (bool): SSL証明書の検証を行うかどうか。デフォルトはTrue。

    戻り値:
    str: PDFのテキスト内容。PDFのダウンロードやテキストの抽出に失敗した場合はNone。

    """
    print('get_pdf_text')
    pdf_response = session.get(url, verify = verify)
    if pdf_response.status_code == 200:
        reader = PdfReader(BytesIO(pdf_response.content))
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        # 改行と空白を削除
        text = text.replace("\n", "").replace("\r", "").replace("  ", " ")
        # すべての連続する空白を単一の空白に置き換え
        text = re.sub(' +', ' ', text)
        return text
    return None


def get_pdf_text_with_pdfplumber(session, url, verify=True):
    """
    指定されたURLからPDFをダウンロードし、そのテキスト内容を抽出します。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): ダウンロードするPDFのURL。
    verify (bool): SSL証明書の検証を行うかどうか。デフォルトはTrue。

    戻り値:
    str: PDFのテキスト内容。PDFのダウンロードやテキストの抽出に失敗した場合はNone。

    """
    print('get_pdf_text_with_pdfplumber')
    pdf_response = session.get(url, verify = verify)
    if pdf_response.status_code == 200:
        if pdf_response.content[:4] != b'%PDF':
            print('The downloaded file is not a PDF.')
            return None
        with pdfplumber.open(BytesIO(pdf_response.content)) as pdf:
            text = ' '.join(page.extract_text() for page in pdf.pages)
        # 改行と空白を削除
        text = text.replace("\n", "").replace("\r", "").replace("  ", " ")
        # すべての連続する空白を単一の空白に置き換え
        text = re.sub(' +', ' ', text)
        print(f'pdfからテキストを返します:{url}')
        return text
    return None

def scrape_text(session, url, element_selector="p", is_dynamic = False ,verify=True):
    """
    指定されたURLのページからテキストを取得します。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): テキストを取得するページのURL。
    is_dynamic (bool): ページが動的に生成されるかどうかを指定します。デフォルトはFalse。
    element_selector (str): テキストを取得するHTML要素を指定するセレクタ。デフォルトは "p"。

    戻り値:
    str: 取得したテキスト。テキストが取得できなかった場合はエラーメッセージ。

    """
    print('scrape_text')
    response = session.get(url,verify = verify)
    if is_dynamic:
        response.html.render()  # JavaScriptをレンダリング
    if response is None:
        return "URLからのレスポンスの取得に失敗しました"

    text_elements = response.html.find(element_selector)

    if text_elements:
        text = " ".join([element.text.replace('\n', ' ') for element in text_elements])
    else:
        text = f"{element_selector}タグがありませんでした"

    return text

def is_definitely_not_pdf(url):
    non_pdf_extensions = ['.html', '.php', '.asp', '.jpg', '.png']
    non_pdf_domains = ['facebook.com', 'twitter.com']

    if any(url.lower().endswith(ext) for ext in non_pdf_extensions):
        return True
    if any(domain in url for domain in non_pdf_domains):
        return True

    return False

def is_pdf_link(url, verify=True):
    # 明らかにPDFでないURLをチェック
    if is_definitely_not_pdf(url):
        return False

    # URLの末尾が '.pdf' で終わるかチェック
    if url.lower().endswith('.pdf'):
        return True

    try:
        response = requests.get(url, stream=True, verify=verify, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        response.close()
        return 'application/pdf' in content_type
    except requests.RequestException as e:
        print(f"リクエスト中にエラーが発生しました: {e}")
        return False


def scrape_text_and_pdf(session, url, element_selector="p", is_dynamic=False, verify=True, ignore_strings=None):
    print(f'scrape_text_and_pdf: {url}')
    
    # URLがPDFファイルを指しているか確認
    if is_pdf_link(url, verify):
        print(f"{url} はPDFファイルです")
        return get_pdf_text_with_pdfplumber(session, url, verify)

    # PDFファイルでない場合、通常のスクレイピングを行う
    try:
        print(f"{url} から通常のスクレイピングを行いテキストを取得します")
        response = session.get(url, verify=verify)
        if response.status_code != 200:
            return f"URLからのレスポンス取得に失敗しました: ステータスコード {response.status_code}"

        if is_dynamic:
            response.html.render()  # JavaScriptをレンダリング

        text_elements = response.html.find(element_selector)
        content = " ".join([element.text.replace('\n', ' ') for element in text_elements]) if text_elements else response.html.text

        # ページ内のPDFリンクを探索
        pdf_links = [urljoin(url, a.attrs['href']) for a in response.html.find('a') if 'href' in a.attrs and a.attrs['href'].endswith('.pdf') and (not any(ignore_string in a.attrs['href'] for ignore_string in ignore_strings) if ignore_strings else True)]
        for pdf_link in pdf_links:
            print(f'{pdf_link}からPDFテキストを取得します')
            pdf_text = get_pdf_text_with_pdfplumber(session, pdf_link, verify)
            if pdf_text:
                content += "\n" + pdf_text

        return content
    except Exception as e:
        return f"{url} からのテキスト取得中にエラーが発生しました: {e}"




def scrape_dynamic_text_and_pdf(driver, session, url, verify=True, ignore_strings=None):
    """
    指定されたURLの動的なWebサイトからテキストを抽出します。URLがPDFファイルの場合は、そのPDFのテキストを取得します。

    引数:
    driver (webdriver object): WebDriverのインスタンス。
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): テキストを取得するWebサイトのURL。
    verify (bool): SSL証明書の検証を行うかどうか。デフォルトはTrue。
    ignore_strings (list): PDFファイルのURLに含まれている場合に無視する文字列のリスト。

    戻り値:
    str: Webサイトから抽出したテキスト。
    """
    if is_pdf_link(url, verify):
        return get_pdf_text_with_pdfplumber(session, url, verify)
    # if url.endswith('.pdf'):
    #     return get_pdf_text_with_pdfplumber(session, url, verify)

    driver.get(url)

    # ページ内のテキストを取得
    page_text = driver.find_element(By.TAG_NAME, "body").text

    # ページ内のPDFリンクを探す
    pdf_links = []
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and href.endswith('.pdf') and (not any(ignore_string in href for ignore_string in ignore_strings) if ignore_strings else True):
            pdf_links.append(href)

    # PDFリンクからテキストを取得
    for pdf_link in pdf_links:
        pdf_text = get_pdf_text_with_pdfplumber(session, pdf_link, verify)
        if pdf_text:
            page_text += "\n" + pdf_text

    return page_text.replace(' ', '').replace('\n', '')

def scrape_text_bs4(session, url, element_selector="p", verify=True):
    """
    BeautifulSoup4を使用して指定されたURLからテキストをスクレイピングします。

    Parameters:
    url (str): スクレイピング対象のURL。
    selector (str): スクレイピングする要素を指定するCSSセレクタ。

    Returns:
    str: スクレイピングしたテキスト。指定されたセレクタに一致する要素が存在しない場合は空文字列を返します。

    Raises:
    requests.exceptions.RequestException: URLへのリクエストが失敗した場合に発生します。
    bs4.BeautifulSoup: HTMLのパースに失敗した場合に発生します。
    """
    print('scrape_text')
    response = session.get(url, verify=verify)
    response.encoding = 'utf-8'  # エンコーディングを指定
    if response is None:
        return "URLからのレスポンスの取得に失敗しました"

    soup = BeautifulSoup(response.text, 'html.parser')  # BeautifulSoupでHTMLをパース
    text_elements = soup.select(element_selector)  # CSSセレクタで要素を取得

    if text_elements:
        text = " ".join([element.text.replace('\n', ' ') for element in text_elements])
    else:
        text = f"{element_selector}タグがありませんでした"

    return text

def convert_date_format(date_string, original_format, new_format='%y/%m/%d'):
    print('convert_date_format')    
    """
    元の形式の日付文字列を新しい形式に変換します。

    引数:
    date_string (str): 変換する日付文字列。
    original_format (str): 元の日付文字列の形式。
    new_format (str): 変換後の日付文字列の形式。デフォルトは'%y/%m/%d'。

    戻り値:
    str: 変換後の日付文字列。変換に失敗した場合はNone。
    """
    try:
        date = datetime.strptime(date_string, original_format)
        return date.strftime(new_format)
    except ValueError:
        print(f"日付の変換に失敗しました。入力された日付：{date_string}、元の形式：{original_format}、新しい形式：{new_format}")
        return None
    
def scrape_dynamic_site_text(driver, url):
    """
    指定されたURLの動的なWebサイトからテキストを抽出します。

    引数:
    driver (webdriver object): WebDriverのインスタンス。
    url (str): テキストを抽出するWebサイトのURL。

    戻り値:
    str: Webサイトから抽出したテキスト。
    """
    driver.get(url)
    text = driver.find_element(By.TAG_NAME, "body").text
    text = text.replace('\n', '').replace(' ', '')
    return text

def generate_id(news_content):
    # ニュース本文からハッシュ値を生成
    hash_object = hashlib.sha256(news_content.encode())
    hex_dig = hash_object.hexdigest()

    return hex_dig

def add_unique_id(dict_list):
    print('add_unique_id')
    for dict_ in dict_list:
        content = dict_['content'] + dict_['newsDate']
        unique_id = generate_id(content)
        dict_['id'] = unique_id
    return dict_list

def remove_duplicates(list1, list2):
    combined = list1 + [d for d in list2 if d not in list1]
    return combined

def is_file_exists(file_path):
    return os.path.isfile(file_path)

def update_press_releases(old_data_path, new_data):
    """
    既存のニュースデータと新しいニュースデータを組み合わせて、重複を削除します。

    Args:
        old_data_path (str): 既存のニュースデータのファイルパス。
        new_data (list): 新しいニュースデータのリスト。各要素は辞書で、ニュースの内容を表します。
                         データは昇順（最古のニュースが最初に来る）である必要があります。

    Returns:
        list: 既存のニュースデータと新しいニュースデータを組み合わせ、重複を削除したリスト。

    注意:
        new_dataは昇順である必要があります。これは、最古のニュースがリストの最初に来るようにするためです。
    """
    print('update_press_release')
    if is_file_exists(old_data_path):
        print(f'ファイルが{old_data_path}に存在します。更新確認をします。')
        old_data = read_news_data(old_data_path)
        press_releases = remove_duplicates(old_data, new_data)
    else:
        print('ファイルが存在しません。新規に作成します')
        press_releases = new_data
    return press_releases

def create_session():
    session = HTMLSession()
    return session


def get_data(session, links_dates, ignore_strings, is_dynamic = False,verify=True, driver=None):
    """
    指定されたリンクからテキストをスクレイピングし、それらをデータリストとして返します。

    Parameters:
    session (requests.Session): requestsライブラリのSessionオブジェクト。
    links_dates (list): リンクと日付のペアのリスト。
    ignore_strings (list): リンクから除外する文字列のリスト。
    is_dynamic (bool, optional): JavaScriptをレンダリングするかどうかを指定します。デフォルトはFalse。
    verify (bool, optional): SSL証明書の検証を行うかどうかを指定します。デフォルトはTrue。
    driver (selenium.webdriver, optional): Selenium WebDriverのインスタンス。デフォルトはNone。

    Returns:
    list: スクレイピングしたテキストとその日付を含む辞書のリスト。
    """
    data = []
    for link, date in links_dates:
        print(f"{link}からテキストを取得しています")

        try:
            if driver:
                # WebDriverが提供された場合は、動的なWebサイトのスクレイピングを行う
                text = scrape_dynamic_text_and_pdf(driver, session, link, verify=verify, ignore_strings=ignore_strings)
            else:
                # WebDriverが提供されない場合は、通常のスクレイピングを行う。is_dynamicがTrueの場合はJavaScriptをレンダリングする
                text = scrape_text_and_pdf(session, link, ignore_strings=ignore_strings, verify=verify,is_dynamic=is_dynamic)
        except Exception as e:
            print(f"{link}からのデータ取得中にエラーが発生しました: {e}")
            text = None
            
        if text is not None:
            data.append({'newsDate': date, 'content': text})
        time.sleep(2)
    return data

def process_data(data,company_name):
    data_with_id = add_unique_id(data)
    sorted_data = list(reversed(data_with_id)) #データを昇順に並び替え
    updated_data = update_press_releases(f"data/{company_name}_news.csv", sorted_data)
    return updated_data

def save_data_to_csv(data, company_name):
    dict_list_to_csv(data, f"data/{company_name}_news.csv")