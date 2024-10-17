import httpx
from bs4 import BeautifulSoup
import random
import time

# 여러 User-Agent를 리스트로 정의하여 랜덤으로 선택
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
]

async def get_cve_details(keyword):
    # 주어진 키워드로 URL 구성
    url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={keyword}"

    # 랜덤한 User-Agent 선택
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': 'https://cve.mitre.org/'  # 추가적인 Referer 헤더
    }
    
    results = []  # 결과 리스트 초기화

    try:
        # 비동기 클라이언트를 사용하여 요청 처리 (세션 유지)
        async with httpx.AsyncClient(timeout=20) as client:
            # 첫 번째 요청 전에 딜레이 (사람이 사이트를 사용하는 것처럼 보이도록)
            time.sleep(random.uniform(1, 3))  # 1초에서 3초 사이의 랜덤한 딜레이 추가

            response = await client.get(url, headers=headers)
            response.raise_for_status()  # 상태 코드가 200이 아닐 경우 예외 발생

            # 응답 텍스트 파싱
            html = response.text

            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(html, 'html.parser')

            # div#CenterPane > div#TableWithRules 찾기
            center_pane = soup.find('div', {'id': 'CenterPane'})
            if not center_pane:
                print("Error: div with id 'CenterPane' not found.")
                return results  # 빈 리스트 반환

            table_div = center_pane.find('div', {'id': 'TableWithRules'})
            if not table_div:
                print("Error: div with id 'TableWithRules' not found.")
                return results  # 빈 리스트 반환

            # div 안의 모든 tr 태그 찾기 (tbody가 없을 수 있으므로)
            rows = table_div.find_all('tr')[1:]  # 첫 번째 행은 헤더이므로 제외

            if not rows:
                print("Error: No rows found in the table.")
                return results  # 빈 리스트 반환

            # 각 행에서 CVE 코드와 설명 추출
            for row in rows:
                cols = row.find_all('td')

                # 열의 수가 2개일 때만 처리 (CVE 코드와 설명이 있는 행)
                if len(cols) >= 2:
                    cve_code = cols[0].find('a').text.strip() if cols[0].find('a') else cols[0].text.strip()
                    description = cols[1].text.strip()

                    # 결과에 추가
                    results.append((cve_code, description))
                else:
                    print(f"Warning: Row does not have 2 columns. Skipping: {row}")

    except httpx.HTTPStatusError as e:
        # 요청 실패 시 예외 처리 (로그나 오류 메시지)
        print(f"Error during request: {str(e)}")
    except httpx.RequestError as e:
        # 요청 과정에서 발생한 오류 처리
        print(f"Request error occurred: {str(e)}")
    except Exception as e:
        # 기타 예외 처리
        print(f"An error occurred: {str(e)}")

    return results  # 결과 반환
