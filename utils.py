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
    return press_releases

def get_current_date():
    print('get_current_date')
    return datetime.now().strftime('%Y%m%d')


def write_to_csv(data, filename):
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
        for row in reversed(data):
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

def scrape_all_text(session, url, is_dynamic = False ,verify=True):
    """
    指定されたURLのページから全てのテキストを取得します。

    引数:
    session (requests_html.HTMLSession): リクエストを送信するためのセッション。
    url (str): テキストを取得するページのURL。
    is_dynamic (bool): ページが動的に生成されるかどうかを指定します。デフォルトはFalse。
    verify (bool): SSL証明書の検証を行うかどうかを指定します。デフォルトはTrue。

    戻り値:
    str: 取得したテキスト。テキストが取得できなかった場合はエラーメッセージ。

    """
    response = session.get(url, verify=verify)
    if is_dynamic:
        response.html.render()  # JavaScriptをレンダリング
    if response is None:
        return "URLからのレスポンスの取得に失敗しました"

    text_elements = response.html.find('*')
    text = " ".join([element.text.replace('\n', ' ') for element in text_elements if element.text])

    return text

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