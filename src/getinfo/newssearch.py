import httpx
from bs4 import BeautifulSoup

async def news_search(keyword):
    a = []
    # Naver search URL
    url = f'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query={keyword}'

    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        # 비동기 클라이언트를 사용하여 요청 처리
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # 상태 코드가 200이 아닐 경우 예외 발생

            html = response.text

            # Parse the page content
            soup = BeautifulSoup(html, 'html.parser')

            # Find news article titles and URLs
            articles = soup.find_all('a', {'class': 'news_tit'})
            descriptions = soup.find_all('div', {'class': 'dsc_wrap'})

            # 각 기사에 대해 제목, 설명, 링크를 추출
            for article, descript in zip(articles, descriptions):
                try:
                    title = article.get_text()
                    link = article['href']
                    description = descript.get_text()
                    res = await client.get(link, headers=headers)
                    res.raise_for_status()
                    a.append({"title": title, "description": description, "link": link})
                except:
                    pass

    except httpx.HTTPStatusError as e:
        # 요청 실패 시 예외 처리 (로그나 오류 메시지)
        print(f"Error during request: {str(e)}")
    except Exception as e:
        # 기타 예외 처리
        print(f"An error occurred: {str(e)}")

    return a


