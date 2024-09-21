# src/getinfo/finalreport_routes.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.finalreport.finalreport_service import *
from src.database.comment_data import *

router = APIRouter()

templates = Jinja2Templates(directory="src/templates/")


@router.get("/finalreport", response_class=HTMLResponse)
async def final_report_page(request: Request, cve_code: str):
    report_data = get_final_report(request, cve_code)

    comments = report_data["comments"] if report_data["comments"] else []
    
    return templates.TemplateResponse("finalreport.html", {
        "request": request, 
        "info": report_data["info"][0], 
        "test": report_data["test"][0],
        "comments": comments 
    })

@router.post("/comments", response_model=Comment)
async def create_comment(request: Request, comment: Comment):
  
    comment = await add_comment(request, comment)
    print("test" , comment)
    
    return comment

    
