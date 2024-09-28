from src.getinfo import rpatools
from fastapi import File, UploadFile,Request
from pydantic import BaseModel
import os
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends,  Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form, Query
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from src.auth.auth_service import *
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


class cve(BaseModel):
    cve: str
    rule: str
    envi : int
    accuracy_test :str
    performance_test : str



@router.post("/uploadfile/normal")
async def upload_file(response:Response,request: Request,cve: str = Form(...), file: UploadFile = File(...), client=Depends(get_supabase_client)):
    user_info = getuserinfo(client=client,response=response,request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    user_id = user_info["user"].user.id
    folder_path = f"normal_pcap/{user_id}"
    os.makedirs(folder_path, exist_ok=True)
    file_location = f"{folder_path}/{cve}.pcap"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": file_location}

@router.get("/download")
async def download_file(file_location: str = Query(..., description="The name of the file to download")):
    file_location = file_location
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location, media_type='application/octet-stream', filename=file_location)


@router.post("/uploadfile/attack")
async def upload_file(response:Response,request: Request,cve: str = Form(...), file: UploadFile = File(...), client=Depends(get_supabase_client)):
    user_info = getuserinfo(client=client,response=response,request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    user_id = user_info["user"].user.id
    folder_path = "attack_pcap/"+user_id
    os.makedirs(folder_path, exist_ok=True)
    file_location = folder_path+"/"+cve+".pcap"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": file_location}


@router.post("/test/input")
async def test(response:Response,request:Request,client=Depends(get_supabase_client)):
    data = await request.json()
    user_info = getuserinfo(client=client,response=response,request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    print(user_info)
    user_id = user_info["user"].user.id
    accuracy_test = data.get("accuracy_test", "")
    performance_test = data.get("performance_test", "")
    cve = str(data.get("cve", ""))
    envi = data.get("envi", "")[0]
    rule = str(data.get("rule", ""))

    if accuracy_test and performance_test:
        whattest = 2
    elif accuracy_test:
        whattest = 0
    else:
        whattest = 1
    if os.path.isfile("normal_pcap/"+"/"+user_id+"/"+cve+".pcap"):
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"):  #normal+attack
            test_result = await rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1= "normal_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        file_path_2="attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest,
            user_id=user_id
	        )
        else:   #only normal
            test_result = await rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1= "normal_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        file_path_2= "original/attack.pcap",
	        what_test = whattest,
            user_id=user_id
	        )
    else: 
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"): #only attack
            test_result = await rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi,  
	        file_path_1= "original/normal.pcap",
	        file_path_2= "attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest,
            user_id=user_id
	        )
        else:  #none
            test_result = await rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1="original/normal.pcap",
	        file_path_2= "original/attack.pcap",
	        what_test = whattest,
            user_id=user_id
	        )
    return JSONResponse(test_result)
