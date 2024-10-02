from supabase import Client
from fastapi import HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel


class SignInData(BaseModel):
    email: str
    password: str


class Register(BaseModel):
    email: str
    password: str
    confirm_password: str


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
            response.set_cookie(key="user", value=res.session.access_token,path="/")
            response.set_cookie(key="userrefresh", value=res.session.refresh_token,path="/")

            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def sign_out(client: Client, response: Response):
    try:
        response.delete_cookie(key="user",path="/")
        response.delete_cookie(key="userrefresh",path="/")
        client.auth.sign_out()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def sign_in_google(client: Client, response: Response):
    try:
        res = client.auth.sign_in_with_oauth({"provider": "google"})
        return RedirectResponse(url=res.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def callback(client: Client, request: Request, response: Response):
    try:
        code = request.query_params.get("access_token")
        rcode = request.query_params.get("refresh_token")
        response = RedirectResponse(url="/")
        response.set_cookie(key="user", value=code,path="/")
        response.set_cookie(key="userrefresh", value=rcode,path="/")
        res = client.auth.set_session(code, rcode)
        return response  # 어디로 보낼지는 체크필요
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


def getuserinfo(client: Client, request: Request, response: Response):
    try:
        try:
            # 쿠키에서 세션 토큰 가져오기
            session_token_from_cookie = request.cookies.get("user")
            refresh_token_from_cookie = request.cookies.get("userrefresh")
            if not session_token_from_cookie:
                return {"status":False}

            # 세션 토큰을 사용하여 사용자 정보 가져오기
            user_info = client.auth.get_user(session_token_from_cookie)
            if user_info:
                return {"status":True, "user": user_info}
        except Exception as e:
            res = client.auth.refresh_session(refresh_token=refresh_token_from_cookie)
            response.delete_cookie(key="user",path="/")
            response.delete_cookie(key="userrefresh",path="/")
            response.set_cookie(key="user", value=res.session.access_token,path="/")
            response.set_cookie(key="userrefresh", value=res.session.refresh_token,path="/")
            user_info = client.auth.get_user(res.session.access_token)
            if user_info:
                return {"status":True, "user": user_info}
    except Exception as e:
        response = RedirectResponse(url="/login")
        sign_out(client=client,response=response)
        return response


def profile(client: Client, request: Request):
    try:
        # 쿠키에서 세션 토큰 가져오기
        session_token_from_cookie = request.cookies.get("user")
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
