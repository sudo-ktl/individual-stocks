from requests_html import HTMLSession

def scrape_news(url):
    session = HTMLSession()
    r = session.get(url)
    r.html.render()

    news_list = []

    # ニュースの日付と本文を取得
    articles = r.html.find('.F105_News__WrapperGridItem-sc-8xbll7-8 eNdsEd')
    for article in articles:
        date = article.find('p', first=True).text
        print(date)
        link = article.find('a', first=True).attrs['href']
        print(link)
        # news = get_news_content(link)
        # news_list.append({'date': date, 'content': news})

    return news_list

def get_news_content(url):
    session = HTMLSession()
    r = session.get(url)
    r.html.render()

    # ニュースの本文を取得
    content = r.html.find('.news-content', first=True).text

    return content

# テスト
url = 'https://recruit-holdings.com/ja/newsroom/2023/'
news = scrape_news(url)
# for article in news:
#     print('日付:', article['date'])
#     print('本文:', article['content'])
#     print('---')
