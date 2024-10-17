from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.supabase_client import get_supabase_client
from fastapi import APIRouter, Depends
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

@router.get("/ruletest", response_class=HTMLResponse)
async def ruletest(request: Request):
    return templates.TemplateResponse("ruletest.html", {"request": request})

@router.get("/ruletest/result", response_class=HTMLResponse)
async def ruletest(request: Request,testid:str, client=Depends(get_supabase_client)):
    restest = client.table("test_result").select("*").eq("id", int(testid)).execute()
    
    return templates.TemplateResponse("past_test.html", {"request": request, "test_result": restest.data[0]})
