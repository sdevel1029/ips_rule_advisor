from supabase import Client
from fastapi import HTTPException, Response, Request, Cookie
from fastapi.responses import RedirectResponse
from typing import Optional

def sign_up(client: Client, email: str, password: str):
    try:
        client.auth.sign_up({"email": email, "password": password})
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def sign_in(client: Client, email: str, password: str, response: Response):
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            response.set_cookie(key="user", value=res.session.access_token)
            return {"access_token": res.session.access_token}
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def sign_out(client: Client, response: Response):
    try:
        response.delete_cookie(key="user")
        client.auth.sign_out()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def sign_in_google(client: Client, response: Response):
    try:
        res = client.auth.sign_in_with_oauth({"provider": 'google'})
        return RedirectResponse(url=res.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def callback(client: Client, request: Request, response: Response):
    try:
        # Google OAuth 인증 완료 후 Supabase에서 전달한 인증 코드를 처리합니다.
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing code parameter")

        # 인증 코드를 사용하여 세션 토큰을 교환합니다.
        user = client.auth.api.exchange_code_for_session(code)
        if user:
            response.set_cookie(key="user", value=user.access_token)
            return {"access_token": user.access_token}
        else:
            raise HTTPException(status_code=400, detail="Invalid code or failed to exchange code for session")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def profile(client: Client, request: Request, session_token: Optional[str] = Cookie(None)):
    try:
        # 쿠키에서 세션 토큰 가져오기
        session_token_from_cookie = session_token or request.cookies.get("user")
        if not session_token_from_cookie:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # 세션 토큰을 사용하여 사용자 정보 가져오기
        user_info = client.auth.get_user(session_token_from_cookie)
        if user_info:
            return {"user": user_info}
        else:
            raise HTTPException(status_code=401, detail="Invalid session token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
