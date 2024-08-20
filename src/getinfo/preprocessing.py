import re

#전처리기능
def normalize_cve_format(input_code):
    code = input_code.strip().upper()

    #이미 형식이 맞는경우
    if code.startswith("CVE-"):
        return code

    if re.match(r'^CVE-\d{4}-\d+$', code):
        return code
    
    code = re.sub(r"[\s-]", "", code)  #공백이나 -가 있으면 제거

    #년도추출
    year_match = re.match(r"(\d{2}|\d{4})", code)
    if not year_match:
        raise ValueError("Invalid CVE formate")

    year = year_match.group(0)

    # 나머지 부분 추출
    num = code[len(year):]

    # 2자리 년도 처리
    if len(year) == 2:
        year = "20" + year
    return f"CVE-{year}-{num}"

'''
# 테스트
test_inputs = [
    "2021-44228", => o
    "2021 44228", => 결과 : CVE-2020-2144228 
    "21-44228", => o
    "21 44228", => o
    "cve-2021-44228", => o
    "CVE-21-44228" => 결과 : CVE-21-44228
]
'''