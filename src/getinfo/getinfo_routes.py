#src/getinfo/getinfo_routes.py
from fastapi import APIRouter, Request
from src.getinfo.getinfo_service import get_info
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.openai.openai_service import translate_to_korean, classify_attack, summarize_vector

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/getinfo", response_class=HTMLResponse)
async def get_info_page(request: Request, cve_code: str):
    cve_code = request.query_params.get("cve_code")
    info_result = await get_info(cve_code)

    if '설명' in info_result.get('nvd', {}):
        info_result['nvd']['설명'] = await translate_to_korean(info_result['nvd']['설명'])
    
    if '메트릭' in info_result.get('nvd',{}):
        metrics_summary = await summarize_vector(info_result['nvd']['메트릭'])

    attack_type = await classify_attack(info_result['nvd']['설명'])


    return templates.TemplateResponse("info.html", {
        "request": request, 
        "info": info_result,
        "type": attack_type,
        "metrics_summary": metrics_summary
        })