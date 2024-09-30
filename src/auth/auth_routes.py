# src/auth/auth_routes.py
# 다른 인증 관련 라우팅 함수들도 이 파일에 추가
from fastapi import APIRouter, Depends, Response, Request, HTTPException
from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import *
from fastapi.templating import Jinja2Templates
from json import JSONDecodeError

from supabase import create_client


router = APIRouter()
templates = Jinja2Templates(directory="src/templates/")


@router.post("/sign_up")
async def sign_up_route(request: Request, client=Depends(get_supabase_client)):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    email = data.get("email", "")
    password = data.get("password", "")

    result = sign_up(client=client, email=email, password=password)
    return result


@router.post("/sign_in")
async def sign_in_route(
    response: Response, request: Request, client=Depends(get_supabase_client)
):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    email = data.get("email", "")
    password = data.get("password", "")

    # sign_in 함수 호출
    result = sign_in(client=client, email=email, password=password, response=response)

    if not result:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return result


@router.get("/sign_out")
def sign_out_route(
    response: Response, request: Request, client=Depends(get_supabase_client)
):
    return sign_out(client=client, response=response)


@router.get("/sign_in_google")
def sign_in_google_route(response: Response, client=Depends(get_supabase_client)):
    return sign_in_google(response=response, client=client)


@router.get("/callback")
def callback_route(
    request: Request, response: Response, client=Depends(get_supabase_client)
):
    return callback(client=client, request=request, response=response)


@router.get("/profile")
def profile_route(request: Request, client=Depends(get_supabase_client)):
    return profile(request=request, client=client)

@router.post("/changeprofile")
async def change_profile(request: Request, response: Response,client=Depends(get_supabase_client)):
    try:
        data = await request.json()
        nickname = data.get("username", "")

        curpass = data.get("curpass", "")
        newpass = data.get("newpass", "")
        if newpass =="":
            user_info = getuserinfo(client=client,response=response,request=request)
            if isinstance(user_info, RedirectResponse):
                return user_info
            user_id = user_info["user"].user.id
            user = client.table("userinfo").update({"username": nickname}).eq("id", user_id).execute()
        else:
            user_info = getuserinfo(client=client,response=response,request=request)
            if isinstance(user_info, RedirectResponse):
                return user_info
            email = user_info["user"].user.identities[0].identity_data["email"]
            user_id = user_info["user"].user.id
            sign_out(client=client,response=response)
            sign_in(client=client,email=email,password=curpass,response=response)   
            client.auth.update_user({"id": email, "password": newpass })
            user = client.table("userinfo").update({"username": nickname}).eq("id", user_id).execute()
        return {"status":"good"}
    except Exception as e:
        # Log the exception and raise it properly so the client receives it
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
