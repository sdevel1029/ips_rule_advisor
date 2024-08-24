# src/auth/auth_routes.py
# 다른 인증 관련 라우팅 함수들도 이 파일에 추가
from fastapi import APIRouter, Depends, Response, Request, HTTPException
from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import sign_up, sign_in, sign_out, sign_in_google, callback, profile ,Login,read_root
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.post("/sign_up")
def sign_up_route(login:Login,client=Depends(get_supabase_client)):
    return sign_up(client=client, email=login.email, password=login.password)

@router.post("/sign_in")
def sign_in_route(login:Login, response: Response, client=Depends(get_supabase_client)):
    return sign_in(client, email=login.email, password=login.password, response=response)

@router.get("/sign_out")
def sign_out_route(response: Response):
    return sign_out(response)

@router.get("/sign_in_google")
def sign_in_google_route(response: Response,client=Depends(get_supabase_client)):
    return sign_in_google(response=response,client=client)


@router.get("/callback")
def callback_route(request: Request,response: Response,client=Depends(get_supabase_client)):
    return callback(client=client,request=request,response=response)

@router.get("/get_google")
def read_root_router():
    return read_root()

@router.get("/profile")
def profile_route(request: Request,client=Depends(get_supabase_client)):
    return profile(request=request,client=client)



