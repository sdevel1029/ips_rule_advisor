from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.mypage.mypage_service import *
from src.database.supabase_client import get_supabase_client

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/settings", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})