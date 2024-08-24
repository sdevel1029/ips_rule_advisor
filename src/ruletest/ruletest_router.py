'''import RPATools
from fastapi import File, UploadFile,FastAPI,Request,Response
from pydantic import BaseModel
import os
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


class cve(BaseModel):
    cve: str
    rule: str
    envi : int
    accuracy_test :str
    performance_test : str


@router.post("/uploadfile/normal")
async def upload_file(request:Request,file: UploadFile = File(...),client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info["user"]["user"]["id"]
    folder_path = "uploaded_files/"+user_id+"/"+"normal"
    os.makedirs(folder_path, exist_ok=True)
    file_location = folder_path+"/"+file.filename
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@router.post("/uploadfile/attack")
async def upload_file(request:Request,file: UploadFile = File(...),client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info["user"]["user"]["id"]
    folder_path = "uploaded_files/"+user_id+"/"+"attack"
    os.makedirs(folder_path, exist_ok=True)
    file_location = folder_path+"/"+file.filename
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}


@router.post("/test/input")
async def test(cve:cve,request:Request,response: Response,file: UploadFile = File(...),client=Depends(get_supabase_client)):
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info["user"]["user"]["id"]
    if cve.accuracy_test and cve.accuracy_test:
        whattest = 2
    elif cve.accuracy_test:
        whattest = 0
    else:
        whattest = 1

    filename = cve.cve+"_"+user_id
    res = (
    client.table("testresult")
    .insert({"rule": cve.rule, "CVEnum": cve.cve,"envi": cve.envi,"whattest": whattest,"userid": user_id})
    .execute()
)
    inserted_testid = res.data[0]['testid']
    response.set_cookie(key="test", value=inserted_testid)
    return {"status": "success"}
    

@router.post("/test/result")
async def test(request:Request,client=Depends(get_supabase_client)):
    test = request.cookies.get("test")
    res = client.table("testresult").select("*").is_("testid", test).execute()
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info["user"]["user"]["id"]
    if os.path.isfile("uploaded_files/"+user_id+"/"+"normal"):
        if os.path.isfile("uploaded_files/"+user_id+"/"+"attack"):  #normal+attack
            test_result = RPATools.test(
	        cve = res["data"][0]["CVEnum"], 
            rule= res["data"][0]["rule"], 
	        envi = res["data"][0]["envi"], 
	        normal_pcap_file_path  = "uploaded_files/"+user_id+"/"+"normal",
	        attack_pacp_file_path  = "uploaded_files/"+user_id+"/"+"attack",
	        what_test = res["data"][0]["whattest"]
	        )
        else:   #only normal
            test_result = RPATools.test(
	        cve = res["data"][0]["CVEnum"], 
            rule= res["data"][0]["rule"], 
	        envi = res["data"][0]["envi"], 
	        normal_pcap_file_path  = "uploaded_files/"+user_id+"/"+"normal",
	        attack_pacp_file_path  = "original/attack",
	        what_test = res["data"][0]["whattest"]
	        )
    else: 
        if os.path.isfile("uploaded_files/"+user_id+"/"+"attack"): #only attack
            test_result = RPATools.test(
	        cve = res["data"][0]["CVEnum"], 
            rule= res["data"][0]["rule"], 
	        envi = res["data"][0]["envi"], 
	        normal_pcap_file_path  = "original/normal",
	        attack_pacp_file_path  = "uploaded_files/"+user_id+"/"+"attack",
	        what_test = res["data"][0]["whattest"]
	        )
        else:  #none
            test_result = RPATools.test(
	        cve = res["data"][0]["CVEnum"], 
            rule= res["data"][0]["rule"], 
	        envi = res["data"][0]["envi"], 
	        normal_pcap_file_path  = "original/normal",
	        attack_pacp_file_path  = "original/attack",
	        what_test = res["data"][0]["whattest"]
	        )
    response = (
    client.table("countries")
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
    .eq("testid", test)
    .execute()
)
    return test_result


@router.post("/test/accept")
async def test(request:Request,response: Response,client=Depends(get_supabase_client)):
    test = request.cookies.get("test")
    user = request.cookies.get("user")
    user_info = client.auth.get_user(user)
    user_id = user_info["user"]["user"]["id"]
    restest = client.table("testresult").select("*").is_("testid", test).execute()
    res = (
    client.table("testresult")
    .insert({"testid": test, "CVEnum": restest["data"][0]["CVEnum"],"userid": user_id})
    .execute()
)
    response.set_cookie(key="previd", value=res.data[0]['previd'])
    return {"status": "success"}
'''
