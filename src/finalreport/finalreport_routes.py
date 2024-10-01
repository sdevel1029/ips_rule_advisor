# src/getinfo/finalreport_routes.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.finalreport.finalreport_service import *
from src.database.comment_data import *


router = APIRouter()

templates = Jinja2Templates(directory="src/templates/")


@router.get("/finalreport", response_class=HTMLResponse)
async def final_report_page(request: Request):
    return templates.TemplateResponse("finalreport.html", {"request": request})

@router.get("/finalcreate", response_class=HTMLResponse)
async def final_report_create(request: Request, response: Response, infoid, testid, client=Depends(get_supabase_client)):
    report_id, report_content = await get_final_create(request, response, infoid, testid, client)
    result = await get_final_info(request, response, infoid, testid, report_id, client)
    return templates.TemplateResponse("final_show.html", {"request": request, "report_content": report_content, "data":result, "report_id": report_id})

@router.get("/finalshow", response_class=HTMLResponse)
async def final_report_create(request: Request, response: Response, report_id, client=Depends(get_supabase_client)):
    final_ids = await get_final_info_ids(request, response, report_id, client)

    if final_ids is None:
        return HTMLResponse(content="Final report not found", status_code=404)

    infoid = final_ids["infoid"]
    testid = final_ids["testid"]
    
    result = await get_final_info(request, response, infoid, testid, report_id, client)
    report_content = result['final']['content']
    return templates.TemplateResponse("final_show.html", {"request": request, "report_content": report_content, "data":result, "report_id": report_id})

@router.post("/comments", response_model=Comment)
async def create_comment(request: Request, comment: Comment, client=Depends(get_supabase_client)):
    comment = await add_comment(request, comment, client)
    print("test" , comment) 
    return comment
