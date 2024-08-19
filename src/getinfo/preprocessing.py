import re

#전처리기능
def normalize_cve_format(input_code):
    code = input_code.strip().upper()

    if code.startswith("CVE-"):
        return code

    code = re.sub(r"[\s-]", "", code)  #공백이나 -가 있으면 제거

    #년도
    year_match = re.match(r"(\d{2}|\d{4})", code)
    if not year_match:
        raise ValueError("Invalid CVE formate")

    year = year_match.group(0)

    #두자리로 입력하는 경우 -> 네자리로 변환
    #ex) 20 -> 2020
    if len(year) == 2:
        year = "20" + year

    num = code[len(year):]

    return f"CVE-{year}-{number_part}"

# test
test_inputs = [
    "2021-44228",
    "2021 44228",
    "21-44228",
    "21 44228",
    "cve-2021-44228",
    "CVE-21-44228"
]

for test_input in test_inputs:
    try:
        normalized_code = normalize_cve_format(test_input)
        print(f"Input: {test_input} -> Normalized: {normalized_code}")
    except ValueError as e:
        print(f"Input: {test_input} -> Error: {e}")

# RPATools.info()에 적용
info_result = RPATools.info(normalize_cve_format("21 44228"))   

