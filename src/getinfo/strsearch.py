import requests
from bs4 import BeautifulSoup

def get_cve_details(keyword):
    # 주어진 키워드로 URL 구성
    url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={keyword}"
    
    # 웹 페이지 요청
    response = requests.get(url)
    
    # 응답 상태 코드 확인
    if response.status_code != 200:
        print(f"Error: Unable to fetch data, status code {response.status_code}")
        return []
    
    # 페이지를 BeautifulSoup으로 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # div#CenterPane > div#TableWithRules 찾기
    center_pane = soup.find('div', {'id': 'CenterPane'})
    if not center_pane:
        print("Error: div with id 'CenterPane' not found.")
        return []

    table_div = center_pane.find('div', {'id': 'TableWithRules'})
    if not table_div:
        print("Error: div with id 'TableWithRules' not found.")
        return []

    # div 안의 모든 tr 태그를 찾기 (tbody가 없을 수 있으므로)
    rows = table_div.find_all('tr')[1:]  # 첫 번째 행은 헤더이므로 제외

    if not rows:
        print("Error: No rows found in the table.")
        return []

    results = []  # 결과 리스트 초기화

    # 각 행에서 CVE 코드와 설명을 추출
    for row in rows:
        cols = row.find_all('td')

        # 열의 수가 2개일 때만 처리 (CVE 코드와 설명이 있는 행)
        if len(cols) >= 2:
            # 첫 번째 열에서 <a> 태그 안의 텍스트 추출 (CVE 코드)
            cve_code = cols[0].find('a').text.strip() if cols[0].find('a') else cols[0].text.strip()

            # 설명 추출
            description = cols[1].text.strip()

            # 결과에 추가
            results.append((cve_code, description))
        else:
            print(f"Warning: Row does not have 2 columns. Skipping: {row}")
    
    return results
