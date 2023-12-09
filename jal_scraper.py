from requests_html import HTMLSession
from datetime import datetime, timedelta
from requests.exceptions import RequestException
import utils
import csv

# グローバルスコープでURLを定義
# URL = "https://press.jal.co.jp/ja/index.html"


# 記事のテキストを取得
def scrape_text(url):
    print('scrape_text')
    response = utils.fetch_data(url)
    if response is None:
        return "URLからのレスポンスの取得に失敗しました"

    text_elements = response.html.find("p")

    if text_elements:
        text = " ".join([element.text.replace('\n', ' ') for element in text_elements])
    else:
        text = "pタグがありませんでした"

    return text

# ニュースサイトの日付のフォーマットを変換
def convert_date_format(date):
    print('convert_date_format')
    try:
        dt = datetime.strptime(date, '%Y年%m月%d日')
        return dt.strftime('%Y/%m/%d')[2:]
    except ValueError:
        print(f"Error: The date '{date}' does not match the format '%Y年%m月%d日'")
        return None

# 各記事のurl情報と日付を取得
def parse_article(article):
    print('parse_article')
    link_element = article.find("a", first=True)
    if link_element is None:
        print(f"An error occurred while parsing the article: 'a' element not found. Article content: {article.text[:100]}")
        return None

    link = link_element.attrs["href"]

    date_element = article.find("time", first=True)
    if date_element is None:
        print(f"An error occurred while parsing the article at {link}: 'time' element not found.")
        return None

    date = date_element.text
    formatted_date = convert_date_format(date)
    text = scrape_text(link)

    return {"newsDate": formatted_date, "content": text}

# html構造から日付と記事urlの含まれた辞書の配列を取得して各関数に渡す
def parse_press_releases(response):
    print('parse_press_releases')
    if response is None:
        return []

    press_releases = []
    articles = response.html.find("li.c-news-list__item", first=False)
    for article in articles:
        press_release = parse_article(article)
        if press_release is not None:
            press_releases.append(press_release)

    return press_releases

def main():
    print('スクレイピングを開始します')
    dt_now = utils.get_current_date()
    press_releases = []
    for i in range(1, 18):
        if(i == 1):
            URL = "https://press.jal.co.jp/ja/index.html"
        else:
            URL = f"https://press.jal.co.jp/ja/index_{i}.html"

        press_releases += utils.get_press_releases(URL, parse_press_releases)
    print('press_releasesを準備しました')

    print(press_releases)

    with open(f'data/jal_news.csv', 'w', newline='') as csvfile:
        fieldnames = press_releases[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for press_release in reversed(press_releases):
            writer.writerow(press_release)

if __name__ == '__main__':
    main()