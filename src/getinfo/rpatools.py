# src/getinfo/rpatools.py
import httpx
import asyncio
import os
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
    # 결과값 받기
    result = {}
    result = await read_api(code, "nvd")

    # 예외 1 : 결과 없음
    if result["totalResults"] == 0:
        return {}

    # 최종 output
    output = {}
    output["id"] = result["vulnerabilities"][0]["cve"]["id"]
    output["수정시간"] = result["vulnerabilities"][0]["cve"]["lastModified"]
    output["설명"] = result["vulnerabilities"][0]["cve"]["descriptions"][0]["value"]
    output["점수"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"]
    output["메트릭"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"]
    # 메트릭 세부 만들기 시작
    tmp_for_detail = {}
    tmp_for_detail["공격벡터"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["attackVector"]
    tmp_for_detail["공격복잡성"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["attackComplexity"]
    tmp_for_detail["필요한권한"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["privilegesRequired"]
    tmp_for_detail["사용자상호작용"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["userInteraction"]
    tmp_for_detail["범위"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["scope"]
    tmp_for_detail["기밀성"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["confidentialityImpact"]
    tmp_for_detail["무결성"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["integrityImpact"]
    tmp_for_detail["가용성"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["availabilityImpact"]

    # 끝
    output["메트릭세부"] = tmp_for_detail
    output["exploitability점수"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["exploitabilityScore"]
    output["impact점수"] = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["impactScore"]

    ###############################################################
    # 메트릭 v3.1 - 동건
    cvssMetric_v31 = result["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]

    # metrics_exploitability: 'attackVector'부터 'scope'까지
    keys_exploitability = [
        "attackVector",
        "attackComplexity",
        "privilegesRequired",
        "userInteraction",
        "scope",
    ]
    metrics_exploitability = {key: cvssMetric_v31[key] for key in keys_exploitability}

    # metrics_impact: 'confidentialityImpact'부터 'availabilityImpact'까지
    keys_impact = ["confidentialityImpact", "integrityImpact", "availabilityImpact"]
    metrics_impact = {key: cvssMetric_v31[key] for key in keys_impact}

    output["악용가능성메트릭"] = metrics_exploitability
    output["영향메트릭"] = metrics_impact
    ###############################################################
    # 제품, cpe
    cpe_list = []

    cpe_raw_data = result["vulnerabilities"][0]["cve"]["configurations"]

    for nodes in cpe_raw_data:
        tmp_list = []
        for node in nodes["nodes"]:
            for match in node.get("cpeMatch", []):
                cpe_info = match["criteria"]

                # 소프트웨어 정보 추출 (vendor, product, version)
                # 예: 'cpe:2.3:a:vendor:product:version:*:*:*:*:*:*:*'
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

    output["제품들"] = cpe_list

    # poc, 참고자료
    # 참고자료 중에서 tag 에 Exploit 있는것들을 poc에 넣음
    ref = []
    poc = []
    for i in range(0, len(result["vulnerabilities"][0]["cve"]["references"])):
        tmp_ref = {}
        tmp_ref["url"] = result["vulnerabilities"][0]["cve"]["references"][i]["url"]
        tmp_ref["tags"] = result["vulnerabilities"][0]["cve"]["references"][i]["tags"]

        if "Exploit" in tmp_ref["tags"]:
            poc.append(tmp_ref)
            continue
        else:
            ref.append(tmp_ref)

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
        # await test_func1()
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
            test_id = test_wait_list.pop(0)
            server_id = tmp_flag[0]["id"]
            supabase.table("test_server_status").update({"able": False}).eq(
                "id", server_id
            ).execute()
            test_server_url = tmp_flag[0]["server_url"]

            # db에서 정보 들고오기
            first_test_info = (
                supabase.table("test_all")
                .select("rule, envi, what_test, file_path_1, file_path_2")
                .eq("id", test_id)
                .execute()
            )
            data = first_test_info.data[0]

            file_paths = [data["file_path_1"], data["file_path_2"]]

            del data["file_path_1"]
            del data["file_path_2"]

            # server 에 요청하기
            files = [
                ("files", (file_path, open(file_path, "rb")))
                for file_path in file_paths
            ]
            test_res = await send_post_request(
                url=test_server_url, data=data, files=files
            )
            output = test_res.json()

            # 서버 다시 사용 가능으로 수정
            supabase.table("test_server_status").update({"able": True}).eq(
                "id", server_id
            ).execute()

            # 정상 수행 됐으면 test 결과 넣기
            if test_res.status_code == 200:
                supabase.table("test_all").update(
                    {
                        "done": True,
                        "result_normal": output["정상 패킷 결과"],
                        "result_attack": output["공격 패킷 결과"],
                    }
                ).eq("id", test_id).execute()
                ### 여기 추가해야됨
            else:  # 비정상이면 다시 대기열 맨 앞에 넣기
                test_wait_list.insert(0, test_id)

            return output
        return {"server": "is full"}
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
    tmp_dict_1 = {
        "user_id": user_id,
        "cve": cve,
        "rule": rule,
        "envi": envi,
        "what_test": what_test,
    }
    tmp_dict_2 = {"file_path_1": file_path_1, "file_path_2": file_path_2}
    tmp_dict = {**tmp_dict_1, **tmp_dict_2}

    # test 정보 테이블에 저장
    tmp_data = supabase.table("test_all").insert(tmp_dict).execute()
    id = tmp_data.data[0]["id"]
    created_time = tmp_data.data[0]["created_at"]

    # 대기열 리스트에 넣기
    test_wait_list.append(id)

    # 수행하기
    output = await test_func1()
    output["test_id"] = id
    output["created_time"] = created_time

    return output
