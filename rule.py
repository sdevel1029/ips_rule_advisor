from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

@router.get("/ruletest", response_class=HTMLResponse)
async def ruletest(request: Request):
    return templates.TemplateResponse("ruletest.html", {"request": request})

@router.get("/ruletest/result", response_class=HTMLResponse)
async def ruletest(request: Request,testid:str, client=Depends(get_supabase_client)):
    restest = client.table("test_all").select("*").eq("testid", testid).execute()
    content=restest.data[0]
    ans = {}
    ans["cve"] = content['cve']
    ans["envi"] = content['envi']
    ans["rule"] = content['rule']
    ans["created_at"] = content['created_at']
    if content['envi'] == 0:
        ans["setting"] = "snort2"
    if content['envi'] == 1:
        ans["setting"] = "snort3"
    if content['envi'] == 2:
        ans["setting"] = "suricata"
    ans["total"] = content['result_attack']['총 패킷 수'] + content['result_normal']['총 패킷 수']
    ans["attacknum"] = content['result_attack']['총 패킷 수']
    ans["normalnum"] = content['result_normal']['총 패킷 수']
    ans["accuracyrate"] =(content['result_normal']['오탐된 패킷 수'] +content['result_attack']['미탐된 패킷 수'])/ ans["total"] 
    ans["attackrate"] = content['result_normal']['오탐된 패킷 수']/ans["normalnum"]
    ans["normalrate"] = content['result_attack']['미탐된 패킷 수']/ans["attacknum"]
    ans["attacktrue"] = (ans["attacknum"]-content['result_attack']['미탐된 패킷 수'])/ans["attacknum"]
    ans["normaltrue"] = (ans["normalnum"]-content['result_normal']['오탐된 패킷 수'])/ans["normalnum"]
    ans["normallatency"] = content['result_normal']['평균 시간_룰 적용 후']-content['result_normal']['평균 시간_룰 적용 전']
    ans["normalcpu_usage"] =content['result_normal']['평균 cpu_룰 적용 후']-content['result_normal']['평균 cpu_룰 적용 전']
    ans["normalmemory_usage"] =content['result_normal']['평균 memory_룰 적용 후']-content['result_normal']['평균 memory_룰 적용 전']
    ans["attacklatency"] = content['result_attack']['평균 시간_룰 적용 후']-content['result_attack']['평균 시간_룰 적용 전']
    ans["attackcpu_usage"] = content['result_attack']['평균 cpu_룰 적용 후']-content['result_attack']['평균 cpu_룰 적용 전']
    ans["attackmemory_usage"] = content['result_attack']['평균 memory_룰 적용 후']-content['result_attack']['평균 memory_룰 적용 전'] 
    return templates.TemplateResponse("rulecontent.html", {"request": request, "content": ans})

