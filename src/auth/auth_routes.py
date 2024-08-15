# src/auth/auth_routes.py
# 다른 인증 관련 라우팅 함수들도 이 파일에 추가
from fastapi import APIRouter, Depends, Response, Request, HTTPException, Cookie
from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import sign_up, sign_in, sign_out, sign_in_google, callback, profile

router = APIRouter()

@router.get("/sign_up")
def sign_up_route(client=Depends(get_supabase_client)):
    return sign_up(client, "testsupa@gmail.com", "testsupabasenow")

@router.get("/sign_in")
def sign_in_route(response: Response, client=Depends(get_supabase_client)):
    return sign_in(client, "testsupa@gmail.com", "testsupabasenow", response)

@router.get("/sign_out")
def sign_out_route(response: Response):
    return sign_out(response)

@router.get("/sign_in_google")
def sign_in_google_route(response: Response):
    return sign_in_google(response)

@router.get("/callback")
def callback_route(request: Request, response: Response):
    return callback(request, response)

# @router.get("/profile")
# def profile_route(request: Request, session_token: Optional[str] = Cookie(None)):
#     return profile(request, session_token)


