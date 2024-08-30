from src.getinfo import rpatools
from fastapi import File, UploadFile,FastAPI,Request,Response
from pydantic import BaseModel
import os
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse


router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


class cve(BaseModel):
    cve: str
    rule: str
    envi : int
    accuracy_test :str
    performance_test : str


@router.post("/uploadfile/normal")
async def upload_file(cve:str,request:Request,file: UploadFile = File(...),client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info.user.id
    folder_path = "normal_pcap/"+"/"+user_id
    os.makedirs(folder_path, exist_ok=True)
    file_location = folder_path+"/"+cve+".pcap"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@router.post("/uploadfile/attack")
async def upload_file(cve:str,request:Request,file: UploadFile = File(...),client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info.user.id
    folder_path = "attack_pcap/"+"/"+user_id
    os.makedirs(folder_path, exist_ok=True)
    file_location = folder_path+"/"+cve+".pcap"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}


@router.post("/test/input")
async def test(request:Request,response: Response,client=Depends(get_supabase_client)):
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
    res = (
    client.table("testresult_duplicate")
    .insert({"rule": rule, "CVEnum": cve,"envi": envi,"whattest": whattest,"userid": user_id})
    .execute()
)
    '''
    if os.path.isfile("normal_pcap/"+"/"+user_id+"/"+cve+".pcap"):
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"):  #normal+attack
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        normal_pcap_file_path  = "normal_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        attack_pacp_file_path  = "attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest 
	        )
        else:   #only normal
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        normal_pcap_file_path  = "normal_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        attack_pacp_file_path  = "original/attack",
	        what_test = whattest 
	        )
    else: 
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"): #only attack
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi,  
	        normal_pcap_file_path  = "original/normal",
	        attack_pacp_file_path  = "attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest 
	        )
        else:  #none
            test_result = rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        normal_pcap_file_path  = "original/normal",
	        attack_pacp_file_path  = "original/attack",
	        what_test = whattest 
	        )'''
    inserted_testid = res.data[0]['testid']
    print(inserted_testid)
    '''
    res1 = (
    client.table("testresult")
    .update({"normalnum": test_result["정상 패킷 결과"]["정상 패킷 수"],
             "normalfalse": test_result["정상 패킷 결과"]["오탐된 패킷 수"]
             ,"normalfalsepac": test_result["정상 패킷 결과"]["오탐된 패킷"]
             ,"normaltimebefore": test_result["정상 패킷 결과"]["평균 시간_룰 적용 전"]
             ,"normaltimeafter": test_result["정상 패킷 결과"]["평균 시간_룰 적용 후"]
             ,"attacknum": test_result["공격 패킷 결과"]["공격 패킷 수"]
             ,"attackfalse": test_result["공격 패킷 결과"]["미탐된 패킷 수"]
             ,"attackfalsepac": test_result["공격 패킷 결과"]["미탐된 패킷"]
             ,"attacktiembefore": test_result["공격 패킷 결과"]["평균 시간_룰 적용 전"]
             ,"attacktiemafter": test_result["공격 패킷 결과"]["평균 시간_룰 적용 후"]})
    .eq("testid", inserted_testid)
    .execute()
)'''

    res1 = (
    client.table("testresult_duplicate")
    .update({"normalnum": 123,
             "normalfalse": 123
             ,"normalfalsepac": 12
             ,"normaltimebefore": 12
             ,"normaltimeafter": 12
             ,"attacknum": 12
             ,"attackfalse": 12
             ,"attackfalsepac": 12
             ,"attacktiembefore": 12
             ,"attacktiemafter": 12})
    .eq("testid", inserted_testid)
    .execute()
)

    response.set_cookie(key="test", value=inserted_testid)
    return {"testid": inserted_testid}


@router.post("/test/show")
async def test(request:Request,response: Response,client=Depends(get_supabase_client)):
    body = await request.json()  # Get JSON data from the request body
    test = body.get("testid")
    restest = client.table("testresult_duplicate").select("*").eq("testid", test).execute()
    if restest.data:
        content=restest.data[0]
        result = {}
        envi = content["envi"]
        if envi ==0:
            result["setting"] = "snort2"
        if envi ==1:
            result["setting"] = "snor3"
        if envi ==2:
            result["setting"] = "suricata"
        result["text"] = content["rule"]
        result["cve"] = content["CVEnum"]
        result["created_at"] = content["created_at"]
        result["attacklatency"] = float(content['attacktiemafter']) - float(content['attacktiembefore'])
        result["normallatency"] = float(content['normaltimeafter']) - float(content['normaltimebefore'])
        result["total"] = content['normalnum'] + content['attacknum']
        result["attacknum"] = content['attacknum'] + content['attackfalse']
        result["normalnum"] = content['normalnum'] + content['normalfalse']
        result["accuracy"] = (content['normalnum']+content['attacknum'])/(content['normalnum'] + content['attacknum'])
        result["attackrate"] = content['attackfalse']/(content['attacknum'])
        result["normalrate"] = content['normalfalse']/(content['normalnum'])
        result["attacktrue"] = (content['attacknum']-content['attackfalse'])/(content['attacknum'])
        result["normaltrue"] = (content['normalnum']-content['normalfalse'])/(content['normalnum'])
        result["envi"] = envi
        return JSONResponse(result)
    else:
        return JSONResponse(content={"error": "No data found"}, status_code=404)



@router.post("/test/accept")
async def test(request:Request,response: Response,client=Depends(get_supabase_client)):
    test = request.cookies.get("test")
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info.user.id
    restest = client.table("testresult").select("*").eq("testid", test).execute()
    res = (
    client.table("testresult_duplicate")
    .insert({"testid": test, "CVEnum": restest["data"][0]["CVEnum"],"userid": user_id})
    .execute()
)
    res 
    response.set_cookie(key="previd", value=res.data[0]['previd'])
    return {"status": "success"}
