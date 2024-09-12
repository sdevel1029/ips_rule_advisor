from src.getinfo import rpatools
from fastapi import File, UploadFile,Request
from pydantic import BaseModel
import os
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends,  Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
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


@router.post("/test/input")
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
	        file_path_2= "original/attack",
	        what_test = whattest,
            user_id=user_id
	        )
    else: 
        if os.path.isfile("attack_pcap/"+"/"+user_id+"/"+cve+".pcap"): #only attack
            test_result = await rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi,  
	        file_path_1= "original/normal",
	        file_path_2= "attack_pcap/"+"/"+user_id+"/"+cve+".pcap",
	        what_test = whattest,
            user_id=user_id
	        )
        else:  #none
            test_result = await rpatools.test(
	        cve = cve, 
            rule= rule, 
	        envi = envi, 
	        file_path_1="original/normal",
	        file_path_2= "original/attack",
	        what_test = whattest,
            user_id=user_id
	        )


    return JSONResponse(test_result)
