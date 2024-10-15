import requests
from bs4 import BeautifulSoup

async def news_search(keyword):
    a= []
    # Naver search URL
    url = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query='+keyword

    # Make a request to the page
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    html = response.text

    # Parse the page content
    soup = BeautifulSoup(html, 'html.parser')

    # Find news article titles and URLs
    articles = soup.find_all('a', {'class': 'news_tit'})
    descriptions = soup.find_all('div', {'class': 'dsc_wrap'})

    for article, descript in zip(articles, descriptions):
        title = article.get_text()
        link = article['href']
        description = descript.get_text()
        try:
            res = requests.get(link, headers=headers)
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            a.append({"title":title,"description":description,"link":link})

        except:
            None
    return a


