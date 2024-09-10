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
from src.database.info_save import *

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

            #취약점 정보의 게시일과 현재 보고서의 생성시간 추가
            info_result['nvd']['수정시간'] = info_result['nvd']['수정시간'].split('T')[0]
            current_date = date.today()

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
                "metrics_summary": metrics_summary,
                "current_date": current_date
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


#메인페이지의 cve정보검색 div 밑에서 아코디언으로 get_cve_details(문자열로 검색한 결과) 보여주기(동건)

@router.post("/saveinfo")
async def create_vulnerability(vulnerability: VulnerabilityCreate):
    vulnerability_data = vulnerability.model_dump()
    response = supabase.table("info").insert(vulnerability_data).execute()
    
    # 오류 처리를 위한 수정된 코드
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"]["message"])
    
    return {"message": "취약점 정보 수집 성공!"}
