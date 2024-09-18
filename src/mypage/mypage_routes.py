from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.mypage.mypage_service import *
from src.database.supabase_client import get_supabase_client

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})


@router.get("/gptkey")
async def gpt_key(request: Request,client=Depends(get_supabase_client)):
    data = await request.json()
    key =data.get("key")
    chage_gpt(client=client,request=request,key=key)
    return templates.TemplateResponse("chage_gptkey.html", {"request": request})

@router.get("/pastresult", response_class=HTMLResponse)
async def past(request: Request,client=Depends(get_supabase_client)):
    final = past_final(client=client,request=request)
    test = past_test(client=client,request=request)
    return templates.TemplateResponse("past_result.html", {"final": final,"test" : test})
