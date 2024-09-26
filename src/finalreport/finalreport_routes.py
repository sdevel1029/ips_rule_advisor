# src/getinfo/finalreport_routes.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.finalreport.finalreport_service import *
from src.database.comment_data import *

router = APIRouter()

templates = Jinja2Templates(directory="src/templates/")


@router.get("/finalreport", response_class=HTMLResponse)
async def final_report_page(request: Request):
    return templates.TemplateResponse("finalreport.html", {"request": request})

@router.post("/comments", response_model=Comment)
async def create_comment(request: Request, comment: Comment):
  
    comment = await add_comment(request, comment)
    print("test" , comment)
    
    return comment

    
