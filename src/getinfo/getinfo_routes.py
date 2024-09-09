# src/getinfo/getinfo_routes.py
from fastapi import APIRouter, Request
from src.getinfo.getinfo_service import get_info, InfoServiceError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.openai.openai_service import (
    translate_to_korean,
    classify_attack,
    summarize_vector,
)
from starlette.responses import RedirectResponse
from src.getinfo.strsearch import get_cve_details

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/getinfo", response_class=HTMLResponse)
async def get_info_page(request: Request, cve_code: str = None):
    if not cve_code:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "cve_code parameter is required"},
        )

    try:
        if cve_code.startswith("CVE-")or cve_code.startswith("cve-"):
            info_result = await get_info(cve_code)

            if "설명" in info_result.get("nvd", {}):
                info_result["nvd"]["설명"] = await translate_to_korean(info_result["nvd"]["설명"])
            metrics_summary = None
            if "메트릭" in info_result.get("nvd", {}):
                metrics_summary = await summarize_vector(info_result["nvd"]["메트릭"])
       

            attack_type = await classify_attack(info_result["nvd"]["설명"])

            return templates.TemplateResponse("info.html",{
                "request": request,
                "info": info_result,
                "type": attack_type,
                "metrics_summary": metrics_summary
                })
        
        # CVE가 아닌 다른 코드를 입력한 경우
        # ex)log4j, dirty cow 등등...
        search_results = get_cve_details(cve_code)
        if not search_results:
            return JSONResponse(content={"error": "No results found"}, status_code=404)
        
        '''
        search_result = "<h1>Search Results</h1>"
        for cve_code, description in results :
            search_result += f"<p><strong>{cve_code}</strong> : {description}>/p>"
        '''
        return templates.TemplateResponse("getinfo.html", {
            "request" : request,
            "search_results" : search_results
        })
        #return HTMLResponse(content=results_html)
    

    except InfoServiceError as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@router.get("/redirect-to-ruletest")
async def redirect_to_ruletest():
    return RedirectResponse(url="/ruletest")

