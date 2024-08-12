from fastapi import Depends, FastAPI, HTTPException, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from supabase import create_client, Client
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import openai,os, uvicorn
from dotenv import load_dotenv

# Supabase URL과 키 설정
url: str = "https://hjneilihqnqaekpwkpkx.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqbmVpbGlocW5xYWVrcHdrcGt4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjA2OTQ0OTIsImV4cCI6MjAzNjI3MDQ5Mn0.yv3BRlAP53X8VrIwNs1CYWeEKVCLBKfIn797dEbsM2M"
supa: Client = create_client(url, key)

# FastAPI 애플리케이션 생성
app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}

@app.get("/sign_up")
def sign_up():
    try:
        res = supa.auth.sign_up({"email":"testsupa@gmail.com", "password": "testsupabasenow"})
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sign_out")
def sign_out(response: Response):
    try:
        response.delete_cookie(key="user")
        supa.auth.sign_out()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sign_in")
def sign_in(response: Response):
    try:
        res = supa.auth.sign_in_with_password({"email":"testsupa@gmail.com", "password": "testsupabasenow"})
        if res.user:
            response.set_cookie(key="user", value=res.session.access_token)
            return {"access_token": res.session.access_token}
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/sign_in_google")
def sign_in(response: Response):
    try:
        res= supa.auth.sign_in_with_oauth({"provider": 'google'})
        print(res)
        return RedirectResponse(url=res.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/callback")
def callback(request: Request, response: Response):
    try:
        # Google OAuth 인증 완료 후 Supabase에서 전달한 인증 코드를 처리합니다.
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing code parameter")

        # 인증 코드를 사용하여 세션 토큰을 교환합니다.
        user = supa.auth.api.exchange_code_for_session(code)
        if user:
            response.set_cookie(key="user", value=user.access_token)
            return {"access_token": user.access_token}
        else:
            raise HTTPException(status_code=400, detail="Invalid code or failed to exchange code for session")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/profile")
def profile(request: Request, session_token: Optional[str] = Cookie(None)):
    print(request.cookies.get("user"))
    print(session_token)
    try:
        # 쿠키에서 세션 토큰 가져오기
        session_token_from_cookie = request.cookies.get("user")
        if not session_token_from_cookie:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # 세션 토큰을 사용하여 사용자 정보 가져오기
        user_info = supa.auth.get_user(session_token_from_cookie)
        if user_info:
            return {"user": user_info}
        else:
            raise HTTPException(status_code=401, detail="Invalid session token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("키 적어주세요")

# 요청 모델 정의
class GPTRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

#GPT 모델에 요청을 보내고 응답을 반환
@app.post("/generate/")
async def generate_text(request: GPTRequest):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # 모델 이름은 사용 가능한 모델로 변경 가능
            prompt=request.prompt,
            max_tokens=request.max_tokens
        )
        return {"response": response.choices[0].text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# FastAPI 서버 실행
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
