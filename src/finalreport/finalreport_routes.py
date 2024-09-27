# src/getinfo/finalreport_routes.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.finalreport.finalreport_service import *
from src.database.comment_data import *


router = APIRouter()

templates = Jinja2Templates(directory="src/templates/")


@router.get("/finalreport", response_class=HTMLResponse)
async def final_report_page(request: Request):
    return templates.TemplateResponse("finalreport.html", {"request": request})

@router.get("/finalshow", response_class=HTMLResponse)
async def final_report_show(request: Request, response: Response, infoid, testid, client=Depends(get_supabase_client)):
    report_content = await get_final_report(request, response, infoid, testid, client)
    return templates.TemplateResponse("final_show.html", {"request": request, "report_content": report_content})


