# src/getinfo/finalreport_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.finalreport.finalreport_service import get_final_report

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/finalreport", response_class=HTMLResponse)
async def final_report_page(request: Request, cve_code: str):
    report_data = get_final_report(request, cve_code)
    return templates.TemplateResponse("finalreport.html", {
        "request": request, 
        "info": report_data["info"][0], 
        "test": report_data["test"][0]
    })