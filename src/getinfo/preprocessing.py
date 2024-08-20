import re

def normalize_cve_format(cve: str) -> str:
    # 정규식으로 숫자만 추출
    match = re.match(r"(?i)(?:CVE[\s-]*)?(\d{2}|\d{4})[\s-]*(\d{4,})", cve)
    if match:
        year, id_part = match.groups()
        # 연도가 두 자릿수인 경우 처리
        if len(year) == 2:
            if year == "99":
                year = "1999"
            else:
                year = "20" + year
        return f"CVE-{year}-{id_part}"
    else:
        # 유효한 형식이 아닌 경우 None 반환
        return None