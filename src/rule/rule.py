from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

@router.get("/ruletest", response_class=HTMLResponse)
async def ruletest(request: Request):
    return templates.TemplateResponse("ruletest.html", {"request": request})

@router.get("/ruletest/result", response_class=HTMLResponse)
async def ruletest(request: Request,testid:str, client=Depends(get_supabase_client)):
    restest = client.table("test_all").select("*").eq("id", int(testid)).execute()
    content=restest.data[0]
    ans = {}
    ans["cve"] = content['cve']
    ans["rule"] = content['rule']
    ans["user_id"] = content['user_id']
    ans["created_at"] = datetime.fromisoformat(content['created_at']).date().isoformat()
    if content['envi'] == 0:
        ans["setting"] = "snort2"
    if content['envi'] == 1:
        ans["setting"] = "snort3"
    if content['envi'] == 2:
        ans["setting"] = "suricata"
    ans["total"] = content['result_attack']['총 패킷 수'] + content['result_normal']['총 패킷 수']
    ans["attacknum"] = content['result_attack']['총 패킷 수']
    ans["normalnum"] = content['result_normal']['총 패킷 수']

    if content["what_test"] == 0:
        ans["accuracyrate"] =format(((content['result_normal']['오탐된 패킷 수'] +content['result_attack']['미탐된 패킷 수'])/ ans["total"]) *100,".2f")
        ans["attackrate"] = format((content['result_normal']['오탐된 패킷 수']/ans["normalnum"])*100,".2f")
        ans["normalrate"] = format((content['result_attack']['미탐된 패킷 수']/ans["attacknum"])*100,".2f")
        ans["attacktrue"] = format(((ans["attacknum"]-content['result_attack']['미탐된 패킷 수'])/ans["attacknum"])*100,".2f")
        ans["normaltrue"] = format(((ans["normalnum"]-content['result_normal']['오탐된 패킷 수'])/ans["normalnum"])*100,".2f")
        ans["normallatency"] = "정오탐 테스트만 하였습니다"
        ans["normalcpu_usage"] = "정오탐 테스트만 하였습니다"
        ans["normalmemory_usage"] = "정오탐 테스트만 하였습니다"
        ans["attacklatency"] = "정오탐 테스트만 하였습니다"
        ans["attackcpu_usage"] = "정오탐 테스트만 하였습니다"
        ans["attackmemory_usage"] = "정오탐 테스트만 하였습니다"

    if content["what_test"] == 1:
        ans["accuracyrate"] = "성능 테스트만 하였습니다"
        ans["attackrate"] = "성능 테스트만 하였습니다"
        ans["normalrate"] = "성능 테스트만 하였습니다"
        ans["attacktrue"] = "성능 테스트만 하였습니다"
        ans["normaltrue"] = "성능 테스트만 하였습니다"
        ans["normallatency"] = format(content['result_normal']['평균 시간_룰 적용 후']-content['result_normal']['평균 시간_룰 적용 전'],".2f")
        ans["normalcpu_usage"] = format(content['result_normal']['평균 cpu_룰 적용 후']-content['result_normal']['평균 cpu_룰 적용 전'],".2f")
        ans["normalmemory_usage"] = format(content['result_normal']['평균 memory_룰 적용 후']-content['result_normal']['평균 memory_룰 적용 전'],".2f")
        ans["attacklatency"] = format(content['result_attack']['평균 시간_룰 적용 후']-content['result_attack']['평균 시간_룰 적용 전'],".2f")
        ans["attackcpu_usage"] = format(content['result_attack']['평균 cpu_룰 적용 후']-content['result_attack']['평균 cpu_룰 적용 전'],".2f")
        ans["attackmemory_usage"] = format(content['result_attack']['평균 memory_룰 적용 후']-content['result_attack']['평균 memory_룰 적용 전'] ,".2f")

    if content["what_test"] == 2:
        ans["accuracyrate"] =format(((content['result_normal']['오탐된 패킷 수'] +content['result_attack']['미탐된 패킷 수'])/ ans["total"]) *100,".2f")
        ans["attackrate"] = format((content['result_normal']['오탐된 패킷 수']/ans["normalnum"])*100,".2f")
        ans["normalrate"] = format((content['result_attack']['미탐된 패킷 수']/ans["attacknum"])*100,".2f")
        ans["attacktrue"] = format(((ans["attacknum"]-content['result_attack']['미탐된 패킷 수'])/ans["attacknum"])*100,".2f")
        ans["normaltrue"] = format(((ans["normalnum"]-content['result_normal']['오탐된 패킷 수'])/ans["normalnum"])*100,".2f")
        ans["normallatency"] = format(content['result_normal']['평균 시간_룰 적용 후']-content['result_normal']['평균 시간_룰 적용 전'],".2f")
        ans["normalcpu_usage"] = format(content['result_normal']['평균 cpu_룰 적용 후']-content['result_normal']['평균 cpu_룰 적용 전'],".2f")
        ans["normalmemory_usage"] = format(content['result_normal']['평균 memory_룰 적용 후']-content['result_normal']['평균 memory_룰 적용 전'],".2f")
        ans["attacklatency"] = format(content['result_attack']['평균 시간_룰 적용 후']-content['result_attack']['평균 시간_룰 적용 전'],".2f")
        ans["attackcpu_usage"] = format(content['result_attack']['평균 cpu_룰 적용 후']-content['result_attack']['평균 cpu_룰 적용 전'],".2f")
        ans["attackmemory_usage"] = format(content['result_attack']['평균 memory_룰 적용 후']-content['result_attack']['평균 memory_룰 적용 전'] ,".2f")
    client.table("test_result").insert(ans).execute()

    cvecontentcli = client.table("info").select("*").eq("cve", content['cve']).execute()
    if cvecontentcli.count != None:
        cvecontent=cvecontentcli.data[0]
        ans["type"] = cvecontent["vuln_type"]
        ans["description"] = cvecontent["description"]
    else:
        ans["type"] = "이 cve에 대한 정보 수집을 아직 하지 않았습니다"
        ans["description"] = "이 cve에 대한 정보 수집을 아직 하지 않았습니다"
    return templates.TemplateResponse("ruletest_result.html", {"request": request, "test_result": ans})
