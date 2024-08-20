import requests

# 수집원 세팅
# 형태 : 딕셔너리로 "사이트 이름" : "cve 코드를 제외한 베이스 url"
# 
base_url = {}
base_nvd = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="
base_url["nvd"] = base_nvd


# 동작
def read_api(code, site_name):
    try :
        url = base_url[site_name] + code
    except :
        return {}

    res = requests.get(url=url)
    res.close()

    return res.json()

def nvd(code) :
    # 결과값 받기
    result = {}
    result = read_api(code, "nvd")

    # 예외 1 : 결과 없음
    if(result["totalResults"] == 0) :
        return {}

    # 최종 output
    output = {}

    # id
    output["id"] = result["vulnerabilities"][0]["cve"]["id"]

    # 설명
    output["설명"] = result["vulnerabilities"][0]["cve"]["descriptions"][0]["value"]

    # cvss 3 메트릭
    output["cvss_3.x_점수"] = result["vulnerabilities"][0]["cve"]["metrics"]['cvssMetricV31'][0]["cvssData"]["baseScore"]
    output["cvss_3.x_메트릭"] = result["vulnerabilities"][0]["cve"]["metrics"]['cvssMetricV31'][0]["cvssData"]["vectorString"]

    # 제품, cpe
    cpe_list = []

    cpe_raw_data = result["vulnerabilities"][0]["cve"]["configurations"]

    for nodes in cpe_raw_data:
        tmp_list = []
        for node in nodes['nodes']:
            for match in node.get('cpeMatch', []):
                cpe_info = match['criteria']
                
                # 소프트웨어 정보 추출 (vendor, product, version)
                # 예: 'cpe:2.3:a:vendor:product:version:*:*:*:*:*:*:*'
                parts = cpe_info.split(':')
                if len(parts) >= 5:
                    vendor = parts[3]
                    product = parts[4]
                    version = parts[5]
                    
                    # 버전 범위가 존재하면 추출
                    version_start = match.get('versionStartIncluding', None)
                    version_end = match.get('versionEndExcluding', None)
                    
                    # 리스트에 추가
                    tmp_list.append({
                        'CPE' : cpe_info,
                        '이버전부터(포함)': version_start,
                        '이버전까지(비포함)': version_end
                    })
        cpe_list.append(tmp_list)

    output["영향 받는 제품들 CPE"] = cpe_list

    # poc, 참고자료
    # 참고자료 중에서 tag 에 Exploit 있는것들을 poc에 넣음
    ref = []
    poc = []
    for i in range(0,len(result["vulnerabilities"][0]["cve"]["references"])) :
        tmp_ref = {}
        tmp_ref["url"] = result["vulnerabilities"][0]["cve"]["references"][i]["url"]
        tmp_ref["tags"] = result["vulnerabilities"][0]["cve"]["references"][i]["tags"]

        if "Exploit" in tmp_ref["tags"] :
            poc.append(tmp_ref)
            continue
        else :
            ref.append(tmp_ref)
    
    output["poc"] = poc
    output["참고자료"] = ref

    return output

def github_poc(code):
    output = {}

    return output

def snort_coummunity_rule(code):
    output = {}

    return output


def info(code) :
    # 결과값 받기
    output = {}

    # 수집원 nvd
    res_nvd = nvd(code)
    output["nvd"] = res_nvd

    # 수집원 github poc 모음집
    res_github_poc = github_poc(code)
    output["github_poc"] = res_github_poc

    # 수집원 snort community rule
    res_snort_community_rule = snort_coummunity_rule(code)
    output["snort_community_rule"] = res_snort_community_rule

    return output

# 테스트
test_server_url = ""

def test(id, rule, prog : int, file_1, file_2):
    output = {}
    data = {}

    test_res = requests.post(url=test_server_url, data=data)
    test_res.close()



    return output

