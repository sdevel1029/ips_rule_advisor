# src/getinfo/finalreport_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/finalreport", response_class=HTMLResponse)
async def final_report_page(request: Request):
    return templates.TemplateResponse("finalreport.html", {"request": request})