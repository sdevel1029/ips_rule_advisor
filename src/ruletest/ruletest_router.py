
from src.getinfo import rpatools
from fastapi import File, UploadFile,Request
from pydantic import BaseModel
import os
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends,  Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form


router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


class cve(BaseModel):
    cve: str
    rule: str
    envi : int
    accuracy_test :str
    performance_test : str



@router.post("/uploadfile/normal")
async def upload_file(request: Request,cve: str = Form(...), file: UploadFile = File(...), client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info.user.id
    folder_path = f"normal_pcap/{user_id}"
    os.makedirs(folder_path, exist_ok=True)
    file_location = f"{folder_path}/{cve}.pcap"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}


@router.post("/uploadfile/attack")
async def upload_file(request: Request,cve: str = Form(...), file: UploadFile = File(...), client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info.user.id
    folder_path = "attack_pcap/"+user_id
    os.makedirs(folder_path, exist_ok=True)
    file_location = folder_path+"/"+cve+".pcap"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}


@router.post("/test/input", response_class=HTMLResponse)
async def test(request:Request,client=Depends(get_supabase_client)):
    data = await request.json()
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = str(user_info.user.id)
    accuracy_test = data.get("accuracy_test", "")
    performance_test = data.get("performance_test", "")
    cve = str(data.get("cve", ""))
    envi = int(data.get("envi", ""))
    rule = str(data.get("rule", ""))
    if accuracy_test and performance_test:
        whattest = 2
    elif accuracy_test:
        whattest = 0
    else:
        whattest = 1
    
    if os.path.isfile("normal_pcap/"+"/"+user_id+"/"+cve+".pcap"):
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"):  #normal+attack
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1= "normal_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        file_path_2="attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest 
	        )
        else:   #only normal
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1= "normal_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        file_path_2= "original/attack",
	        what_test = whattest 
	        )
    else: 
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"): #only attack
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi,  
	        file_path_1= "original/normal",
	        file_path_2= "attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest 
	        )
        else:  #none
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1="original/normal",
	        file_path_2= "original/attack",
	        what_test = whattest 
	        )
        test_result
        ans = {}
        ans["cve"] = cve
        ans["envi"] = envi
        ans["rule"] = rule
        ans["created_at"] = "Asd"
        if envi == 0:
            ans["setting"] = "snort2"
        if envi == 1:
            ans["setting"] = "snort3"
        if envi == 2:
            ans["setting"] = "suricata"
        ans["total"] = test_result['공격 패킷 결과']['총 패킷 수'] + test_result['정상 패킷 결과']['총 패킷 수']
        ans["attacknum"] = test_result['공격 패킷 결과']['총 패킷 수']
        ans["normalnum"] = test_result['정상 패킷 결과']['총 패킷 수']
        ans["accuracyrate"] =(test_result['정상 패킷 결과']['오탐된 패킷 수'] +test_result['공격 패킷 결과']['미탐된 패킷 수'])/ ans["total"] 
        ans["attackrate"] = test_result['정상 패킷 결과']['오탐된 패킷 수']/ans["normalnum"]
        ans["normalrate"] = test_result['공격 패킷 결과']['미탐된 패킷 수']/ans["attacknum"]
        ans["attacktrue"] = (ans["attacknum"]-test_result['공격 패킷 결과']['미탐된 패킷 수'])/ans["attacknum"]
        ans["normaltrue"] = (ans["normalnum"]-test_result['정상 패킷 결과']['오탐된 패킷 수'])/ans["normalnum"]
        ans["normallatency"] = test_result['정상 패킷 결과']['평균 시간_룰 적용 후']-test_result['정상 패킷 결과']['평균 시간_룰 적용 전']
        ans["normalcpu_usage"] =test_result['정상 패킷 결과']['평균 cpu_룰 적용 후']-test_result['정상 패킷 결과']['평균 cpu_룰 적용 전']
        ans["normalmemory_usage"] =test_result['정상 패킷 결과']['평균 memory_룰 적용 후']-test_result['정상 패킷 결과']['평균 memory_룰 적용 전']
        ans["attacklatency"] = test_result['공격 패킷 결과']['평균 시간_룰 적용 후']-test_result['공격 패킷 결과']['평균 시간_룰 적용 전']
        ans["attackcpu_usage"] = test_result['공격 패킷 결과']['평균 cpu_룰 적용 후']-test_result['공격 패킷 결과']['평균 cpu_룰 적용 전']
        ans["attackmemory_usage"] = test_result['공격 패킷 결과']['평균 memory_룰 적용 후']-test_result['공격 패킷 결과']['평균 memory_룰 적용 전']

        

    return templates.TemplateResponse("ruletest_result.html",{"request": request, "test_result": ans})
