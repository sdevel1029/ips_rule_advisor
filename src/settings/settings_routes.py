from fastapi import APIRouter, Request, Depends, responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.mypage.mypage_service import *
from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import getuserinfo
from fastapi import File, UploadFile
import os
from fastapi.responses import JSONResponse

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/settings", response_class=HTMLResponse,)
async def home(response:Response,request: Request ,client=Depends(get_supabase_client)):
    user_info = getuserinfo(client=client,response=response,request=request)
    data = {}
    if isinstance(user_info, RedirectResponse):
        return user_info
    data["email"] = user_info["user"].user.email
    user_id = user_info["user"].user.id
    user = client.table("userinfo").select("*").eq("id", user_id).execute()
    try:
        username = user.data[0]["username"]
    except:
        username = ""
    try:
        image_url = user.data[0]["image_url"]
    except:
        image_url = ""
    data["image_url"] = image_url
    data["username"] = username
    return templates.TemplateResponse("settings.html", {"request": request,"data":data})


@router.post("/uploadfile/profile")
async def upload_file(response:Response,request: Request, file: UploadFile = File(...), client=Depends(get_supabase_client)):
    user_info = getuserinfo(client=client,response=response,request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    user_id = user_info["user"].user.id
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"profile/{user_id}{file_extension}"
    user = client.table("userinfo").update({"image_url": file_location}).eq("id", user_id).execute()
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"image_url": file_location}


@router.post("/delete/profile")
async def delete_file(response: Response, request: Request, client=Depends(get_supabase_client)):
    # 유저 정보 가져오기
    user_info = getuserinfo(client=client, response=response, request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    
    user_id = user_info["user"].user.id
    
    # 데이터베이스에서 현재 이미지 URL을 가져오기
    user_data = client.table("userinfo").select("image_url").eq("id", user_id).single().execute()
    if user_data and user_data.data:
        file_location = user_data.data["image_url"]
        
        # 서버에서 파일 삭제
        if os.path.exists(file_location):
            os.remove(file_location)
        else:
            return HTTPException(status_code=404, detail="File not found")

        # 데이터베이스에서 이미지 URL 제거 또는 기본 이미지로 설정
        client.table("userinfo").update({"image_url": None}).eq("id", user_id).execute()
        
        return {"image_url": file_location}
    else:
        return HTTPException(status_code=404, detail="User not found or no image to delete")
