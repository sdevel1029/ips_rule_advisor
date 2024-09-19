from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.mypage.mypage_service import *
from src.database.supabase_client import get_supabase_client

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/mypage", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("my_info.html", {"request": request})


@router.get("/gptkey", response_class=HTMLResponse)
async def gpt_key(request: Request):
    return templates.TemplateResponse("chage_gptkey.html", {"request": request})

@router.get("/pastresult", response_class=HTMLResponse)
async def past(request: Request,client=Depends(get_supabase_client)):
    final = past_final(client=client,request=request)
    return templates.TemplateResponse("past_result.html", {"data": final,"request": request})

@router.get("/ruleresult", response_class=HTMLResponse)
async def past(request: Request,client=Depends(get_supabase_client)):
    test = past_test(client=client,request=request)
    return templates.TemplateResponse("my_ruletest.html", {"data" : test,"request": request})

@router.get("/ruleshow", response_class=HTMLResponse)
async def past(request: Request,testid,client=Depends(get_supabase_client)):
    test_result = client.table("test_result").select("*").eq("id", testid).execute()
    return templates.TemplateResponse("my_ruletest_show.html", {"test_result": test_result,"request": request})


@router.post("/gptkey/change")
async def gpt_key(request: Request,client=Depends(get_supabase_client)):
    data = await request.json()
    key =data.get("key")
    chage_gpt(client=client,request=request,key=key)
    return "success"

@router.post("/card/change")
async def gpt_card(request: Request,client=Depends(get_supabase_client)):
    data = await request.json()
    key =data.get("card")
    chage_card(client=client,request=request,key=key)
    return "success"
