# src/getinfo/rpatools.py
import httpx
import asyncio
import os
import copy
from datetime import datetime
from ..database import supabase_client
from src.getinfo.global_var import test_wait_list


# 수집원 세팅
# 형태 : 딕셔너리로 "사이트 이름" : "cve 코드를 제외한 베이스 url"
#
base_url = {}
base_nvd = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="
base_url["nvd"] = base_nvd


supabase = supabase_client.get_supabase_client()


### 함수들


# 비동기 get 함수
async def send_get_request(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, timeout=30)
    return response


# 비동기 post 함수
async def send_post_request(url, data, files):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, files=files, timeout=30)
    return response


# site_name 에서 code 관련 정보 크롤링 해오는 함수
async def read_api(code, site_name):
    try:
        url = base_url[site_name] + code
    except:
        return {}

    res = await send_get_request(url=url)

    return res.json()


# nvd 정보수집
async def nvd(code):
    result = await read_api(code, "nvd")

    # 예외 1 : 결과 없음
    if result.get("totalResults", 0) == 0:
        return {}

    # 최종 output
    output = {}
    
    try:
        output["id"] = result["vulnerabilities"][0]["cve"]["id"]
        output["수정시간"] = result["vulnerabilities"][0]["cve"]["lastModified"]
        output["설명"] = result["vulnerabilities"][0]["cve"]["descriptions"][0]["value"]
    except (IndexError, KeyError) as e:
        return {"error": "필수 정보가 없습니다."}

    # 메트릭 처리 부분에서 예외 처리 추가
    metrics = result["vulnerabilities"][0]["cve"].get("metrics", {})
    if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
        output["점수"] = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
        output["메트릭"] = metrics["cvssMetricV31"][0]["cvssData"]["vectorString"]

        # 메트릭 세부 만들기 시작
        tmp_for_detail = {}
        try:
            tmp_for_detail["공격벡터"] = metrics["cvssMetricV31"][0]["cvssData"].get("attackVector", "정보 없음")
            tmp_for_detail["공격복잡성"] = metrics["cvssMetricV31"][0]["cvssData"].get("attackComplexity", "정보 없음")
            tmp_for_detail["필요한권한"] = metrics["cvssMetricV31"][0]["cvssData"].get("privilegesRequired", "정보 없음")
            tmp_for_detail["사용자상호작용"] = metrics["cvssMetricV31"][0]["cvssData"].get("userInteraction", "정보 없음")
            tmp_for_detail["범위"] = metrics["cvssMetricV31"][0]["cvssData"].get("scope", "정보 없음")
            tmp_for_detail["기밀성"] = metrics["cvssMetricV31"][0]["cvssData"].get("confidentialityImpact", "정보 없음")
            tmp_for_detail["무결성"] = metrics["cvssMetricV31"][0]["cvssData"].get("integrityImpact", "정보 없음")
            tmp_for_detail["가용성"] = metrics["cvssMetricV31"][0]["cvssData"].get("availabilityImpact", "정보 없음")
        except KeyError:
            tmp_for_detail = {
                "공격벡터": "정보 없음",
                "공격복잡성": "정보 없음",
                "필요한권한": "정보 없음",
                "사용자상호작용": "정보 없음",
                "범위": "정보 없음",
                "기밀성": "정보 없음",
                "무결성": "정보 없음",
                "가용성": "정보 없음"
            }

    else:
        output["점수"] = "정보 없음"
        output["메트릭"] = "정보 없음"
        tmp_for_detail = {
            "공격벡터": "정보 없음",
            "공격복잡성": "정보 없음",
            "필요한권한": "정보 없음",
            "사용자상호작용": "정보 없음",
            "범위": "정보 없음",
            "기밀성": "정보 없음",
            "무결성": "정보 없음",
            "가용성": "정보 없음"
        }

    output["메트릭세부"] = tmp_for_detail

    output["exploitability점수"] = metrics.get("cvssMetricV31", [{}])[0].get("exploitabilityScore", "정보 없음")
    output["impact점수"] = metrics.get("cvssMetricV31", [{}])[0].get("impactScore", "정보 없음")

    # metrics v3.1 - 동건
    cvssMetric_v31 = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})

    # metrics_exploitability: 'attackVector'부터 'scope'까지
    keys_exploitability = [
        "attackVector",
        "attackComplexity",
        "privilegesRequired",
        "userInteraction",
        "scope",
    ]
    metrics_exploitability = {key: cvssMetric_v31.get(key, "정보 없음") for key in keys_exploitability}

    # metrics_impact: 'confidentialityImpact'부터 'availabilityImpact'까지
    keys_impact = ["confidentialityImpact", "integrityImpact", "availabilityImpact"]
    metrics_impact = {key: cvssMetric_v31.get(key, "정보 없음") for key in keys_impact}

    output["악용가능성메트릭"] = metrics_exploitability
    output["영향메트릭"] = metrics_impact

    # 제품, cpe
    cpe_list = []
    try:
        cpe_raw_data = result["vulnerabilities"][0]["cve"]["configurations"]
        for nodes in cpe_raw_data:
            tmp_list = []
            for node in nodes["nodes"]:
                for match in node.get("cpeMatch", []):
                    cpe_info = match["criteria"]

                    # 소프트웨어 정보 추출 (vendor, product, version)
                    parts = cpe_info.split(":")
                    if len(parts) >= 5:
                        vendor = parts[3]
                        product = parts[4]
                        version = parts[5]

                        # 버전 범위가 존재하면 추출
                        version_start = match.get("versionStartIncluding", None)
                        version_end = match.get("versionEndExcluding", None)

                        # 리스트에 추가
                        tmp_list.append(
                            {"CPE": cpe_info, "포함": version_start, "비포함": version_end}
                        )
            cpe_list.append(tmp_list)
    except KeyError:
        output["제품들"] = "정보 없음"
    else:
        output["제품들"] = cpe_list

    # poc, 참고자료
    ref = []
    poc = []
    try:
        for i in range(0, len(result["vulnerabilities"][0]["cve"]["references"])):
            tmp_ref = {}
            tmp_ref["url"] = result["vulnerabilities"][0]["cve"]["references"][i]["url"]
            tmp_ref["tags"] = result["vulnerabilities"][0]["cve"]["references"][i]["tags"]

            if "Exploit" in tmp_ref["tags"]:
                poc.append(tmp_ref)
                continue
            else:
                ref.append(tmp_ref)
    except KeyError:
        output["poc"] = []
        output["참고자료"] = []
    else:
        output["poc"] = poc
        output["참고자료"] = ref

    return output



# github_poc 정보수집
async def github_poc(code):
    output = {}

    return output


# snort_community_rule 정보수집
async def snort_coummunity_rule(code):
    output = {}
    result_list = []

    # rule 탐색할 폴더 경로, 탐색할 cve 코드 숫자부분
    folder_path = "./src/getinfo/rule_files/snort_rule"
    keyword = code[4:]

    # 폴더 안 모든 .rules 파일 읽으며 탐색 후 저장
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".rules"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    content = content.split("\n")
                    for i in content:
                        if keyword in i:
                            result_list.append(i)

    output["rules"] = result_list
    return output


# emerging_rule 정보수집
async def emerging_rule_download():
    tmp_url = "https://rules.emergingthreatspro.com/open/snort-2.9.0/emerging-all.rules"
    res = await send_get_request(url=tmp_url)
    data = res.text

    ttmp_fd = open("./src/getinfo/rule_files/emerging-all.rules.txt", "w")
    ttmp_fd.write(data)
    ttmp_fd.close()

    return data


async def emerging_rule(code):
    output = {}
    # rule 파일 읽기
    try:
        tmp_fd = open("./src/getinfo/rule_files/emerging-all.rules.txt", "r")
        data = tmp_fd.read()
        tmp_fd.close()
    except:  # 없으면 다운로드
        data = await emerging_rule_download()

    # 데이터 처리
    data = data.split("\n")

    search_key = code[4:]
    result_list = []
    for i in data:
        if search_key in i:
            result_list.append(i)

    output["rules"] = result_list

    return output


# 정보수집 메인 함수
async def info(code):
    # 결과값 받기
    output = {}

    # 수집원 nvd
    res_nvd = await nvd(code)
    output["nvd"] = res_nvd

    # 수집원 github poc 모음집
    res_github_poc = await github_poc(code)
    output["github_poc"] = res_github_poc

    # 수집원 snort community rule
    res_snort_community_rule = await snort_coummunity_rule(code)
    output["snort_community_rule"] = res_snort_community_rule

    # 수집원 emerging_rule
    res_emerging_rule = await emerging_rule(code)
    output["emerging_rule"] = res_emerging_rule

    return output


############### 테스트 ###############
######################################
######################################
######################################


# 대기열에 있는 것들을 가능한 테스트 서버에 매칭 시켜주는 함수
async def do_remainning_test():
    # db에서 아직 수행 안된것들 있었으면 대기열에 추가하기
    # check_db = supabase.table("test_all").select("id").eq("done", False).execute()
    # tmp_list = check_db.data
    # for i in tmp_list:
    #     test_wait_list.append(i["id"])

    while True:
        await test_func1()
        await asyncio.sleep(1)


# 테스트 요청 보내는 함수
async def test_func1():
    # 대기열(=리스트)에 원소 존재하면
    if test_wait_list:
        able_server_list = (
            supabase.table("test_server_status")
            .select("id, server_url")
            .eq("able", True)
            .execute()
        )
        tmp_flag = able_server_list.data

        # 사용 가능한 서버 있으면
        if tmp_flag:
            # 대기열 리스트, 서버 able 수정
            data_origin = test_wait_list.pop(0)
            data = copy.deepcopy(data_origin)
            del data["id"]
            server_id = tmp_flag[0]["id"]
            supabase.table("test_server_status").update({"able": False}).eq(
                "id", server_id
            ).execute()
            test_server_url = tmp_flag[0]["server_url"]

            # 파일 경로 처리?
            file_paths = [data["normalpacket"], data["attackpacket"]]

            # server 에 요청하기
            return_output = {}
            try :
                files = [
                    ("files", (file_path, open(file_path, "rb")))
                    for file_path in file_paths
                ]

                data_to_server = {}
                data_to_server["rule"] = data_origin["rule"]
                data_to_server["envi"] = data_origin["envi"]
                data_to_server["what_test"] = data_origin["what_test"]

                test_res = await send_post_request(
                    url=test_server_url, data=data_to_server, files=files
                )
                output = test_res.json()
                return_output["server"] = 1

                # 정상 수행 됐으면 test 결과 넣기
                if test_res.status_code == 200:
                    print("=== 200 ===")
                    data["result_normal"] = output["정상 패킷 결과"]
                    data["result_attack"] = output["공격 패킷 결과"]

                    ans = {}

                    if data['envi'] == 0:
                        ans["setting"] = "snort2"
                    if data['envi'] == 1:
                        ans["setting"] = "snort3"
                    if data['envi'] == 2:
                        ans["setting"] = "suricata"
                    
                    ans["total"] = data['result_attack']['총 패킷 수'] + data['result_normal']['총 패킷 수']
                    ans["attacknum"] = data['result_attack']['총 패킷 수']
                    ans["normalnum"] = data['result_normal']['총 패킷 수']

                    if data["what_test"] == 0:
                        ans["accuracyrate"] =format(((data['result_normal']['오탐된 패킷 수'] +data['result_attack']['미탐된 패킷 수'])/ ans["total"]) *100,".2f")
                        ans["attackrate"] = format((data['result_normal']['오탐된 패킷 수']/ans["normalnum"])*100,".2f")
                        ans["normalrate"] = format((data['result_attack']['미탐된 패킷 수']/ans["attacknum"])*100,".2f")
                        ans["attacktrue"] = format(((ans["attacknum"]-data['result_attack']['미탐된 패킷 수'])/ans["attacknum"])*100,".2f")
                        ans["normaltrue"] = format(((ans["normalnum"]-data['result_normal']['오탐된 패킷 수'])/ans["normalnum"])*100,".2f")
                        ans["normalpacket_num"] = data['result_normal']["오탐된 패킷"]
                        ans["attackpacket_num"] = data['result_attack']["미탐된 패킷"]
                        ans["normallatency"] = "정오탐 테스트만 하였습니다"
                        ans["normalcpu_usage"] = "정오탐 테스트만 하였습니다"
                        ans["normalmemory_usage"] = "정오탐 테스트만 하였습니다"
                        ans["attacklatency"] = "정오탐 테스트만 하였습니다"
                        ans["attackcpu_usage"] = "정오탐 테스트만 하였습니다"
                        ans["attackmemory_usage"] = "정오탐 테스트만 하였습니다"

                    if data["what_test"] == 1:
                        ans["accuracyrate"] = "성능 테스트만 하였습니다"
                        ans["attackrate"] = "성능 테스트만 하였습니다"
                        ans["normalrate"] = "성능 테스트만 하였습니다"
                        ans["attacktrue"] = "성능 테스트만 하였습니다"
                        ans["normaltrue"] = "성능 테스트만 하였습니다"
                        ans["normalpacket_num"] = "성능 테스트만 하였습니다"
                        ans["attackpacket_num"] = "성능 테스트만 하였습니다"
                        ans["normallatency"] = format(data['result_normal']['평균 시간_룰 적용 후']-data['result_normal']['평균 시간_룰 적용 전'],".2f")
                        ans["normalcpu_usage"] = format(data['result_normal']['평균 cpu_룰 적용 후']-data['result_normal']['평균 cpu_룰 적용 전'],".2f")
                        ans["normalmemory_usage"] = format(data['result_normal']['평균 memory_룰 적용 후']-data['result_normal']['평균 memory_룰 적용 전'],".2f")
                        ans["attacklatency"] = format(data['result_attack']['평균 시간_룰 적용 후']-data['result_attack']['평균 시간_룰 적용 전'],".2f")
                        ans["attackcpu_usage"] = format(data['result_attack']['평균 cpu_룰 적용 후']-data['result_attack']['평균 cpu_룰 적용 전'],".2f")
                        ans["attackmemory_usage"] = format(data['result_attack']['평균 memory_룰 적용 후']-data['result_attack']['평균 memory_룰 적용 전'] ,".2f")

                    if data["what_test"] == 2:
                        ans["accuracyrate"] =format(((data['result_normal']['오탐된 패킷 수'] +data['result_attack']['미탐된 패킷 수'])/ ans["total"]) *100,".2f")
                        ans["attackrate"] = format((data['result_normal']['오탐된 패킷 수']/ans["normalnum"])*100,".2f")
                        ans["normalrate"] = format((data['result_attack']['미탐된 패킷 수']/ans["attacknum"])*100,".2f")
                        ans["attacktrue"] = format(((ans["attacknum"]-data['result_attack']['미탐된 패킷 수'])/ans["attacknum"])*100,".2f")
                        ans["normaltrue"] = format(((ans["normalnum"]-data['result_normal']['오탐된 패킷 수'])/ans["normalnum"])*100,".2f")
                        ans["normalpacket_num"] = data['result_normal']["오탐된 패킷"]
                        ans["attackpacket_num"] = data['result_attack']["미탐된 패킷"]
                        ans["normallatency"] = format(data['result_normal']['평균 시간_룰 적용 후']-data['result_normal']['평균 시간_룰 적용 전'],".2f")
                        ans["normalcpu_usage"] = format(data['result_normal']['평균 cpu_룰 적용 후']-data['result_normal']['평균 cpu_룰 적용 전'],".2f")
                        ans["normalmemory_usage"] = format(data['result_normal']['평균 memory_룰 적용 후']-data['result_normal']['평균 memory_룰 적용 전'],".2f")
                        ans["attacklatency"] = format(data['result_attack']['평균 시간_룰 적용 후']-data['result_attack']['평균 시간_룰 적용 전'],".2f")
                        ans["attackcpu_usage"] = format(data['result_attack']['평균 cpu_룰 적용 후']-data['result_attack']['평균 cpu_룰 적용 전'],".2f")
                        ans["attackmemory_usage"] = format(data['result_attack']['평균 memory_룰 적용 후']-data['result_attack']['평균 memory_룰 적용 전'] ,".2f")
                    
                    try:
                        print("=== 5 ===")
                        supabase.table("test_result").update(ans).eq("id", data_origin["id"]).execute()
                    except:
                        print("=== 4 ===")
                        test_wait_list.insert(0, data_origin)
                        return_output["server"] = 4 # 마지막 저장에서 에러

                else:  # 비정상이면 다시 대기열 맨 앞에 넣기
                    print("=== 3 ===")
                    test_wait_list.insert(0, data_origin)
                    return_output["server"] = 3

            except :
                print("=== 2 ===")
                test_wait_list.insert(0, data_origin)
                return_output["server"] = 2 # 서버와 통신 중 에러

            # 서버 다시 사용 가능으로 수정
            supabase.table("test_server_status").update({"able": True}).eq(
                "id", server_id
            ).execute()

            return return_output
        return {"server": 0}
    return {"wait_list": "is empty"}


# 대기열에 등록하고 수행하는 함수
async def test(
    user_id: str,
    cve: str,
    rule: str,
    envi: int,
    what_test: int,
    file_path_1: str,
    file_path_2: str,
):
    now = datetime.now()
    now = datetime.fromisoformat(str(now)).date().isoformat()
    tmp_dict_1 = {
        "user_id": user_id,
        "created_at": now,
        "cve": cve,
        "rule": rule,
        "envi": envi,
        "what_test": what_test,
        "normalpacket" : file_path_1,
        "attackpacket" : file_path_2
    }

    # test 정보 테이블에 저장
    tmp_data = supabase.table("test_result").insert(tmp_dict_1).execute()
    id = tmp_data.data[0]["id"]

    # 대기열 리스트에 넣기
    tmp_dict_1["id"] = id
    test_wait_list.append(tmp_dict_1)

    # 수행하기
    output = await test_func1()
    output["test_id"] = id
    
    # 서버 부족 등 문제 있었으면, 대기열 추가해주기
    if output["server"] != 1 : 
        wait_num = 0
        id = int(id)
        for i in test_wait_list:
            wait_num += 1
            if i["id"] == id:
                break
        output["wait_num"] = wait_num

    return output
