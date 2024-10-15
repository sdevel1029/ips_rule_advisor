# src/getinfo/getinfo_routes.py
import json
from fastapi import APIRouter, Request
from src.getinfo.getinfo_service import get_info, InfoServiceError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.openai.openai_service import (
    translate_to_korean,
    classify_attack,
    summarize_vector,
    translate_bulk_to_korean
)
from starlette.responses import RedirectResponse
from src.getinfo.strsearch import get_cve_details
from src.getinfo.newssearch import news_search
from src.database.info_save import *
from datetime import date
from src.auth.auth_service import profile 

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

with open('src/openai/attack_types.json', 'r')as file:
    attack_types = json.load(file)

@router.get("/getinfo", response_class=HTMLResponse)
async def get_info_page(request: Request, cve_code: str = None, filter_type: str = "CVE"):
    if not cve_code:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "CVE 코드를 입력해주세요"},
        )

    try:
        # CVE 코드 검색시
        if filter_type == "CVE" and (cve_code.startswith("CVE-") or cve_code.startswith("cve-")):
            info_result = await get_info(cve_code)
            info_result['nvd']['수정시간'] = info_result['nvd']['수정시간'].split('T')[0]
            current_date = date.today()

            if "설명" in info_result.get("nvd", {}):
                info_result["nvd"]["설명"] = await translate_to_korean(info_result["nvd"]["설명"])
            metrics_summary = None
            if "메트릭" in info_result.get("nvd", {}):
                metrics_summary = await summarize_vector(info_result["nvd"]["메트릭"])
       
            attack_type = await classify_attack(info_result["nvd"]["설명"])
            attack_description = attack_types.get(attack_type, "정보없음")

            snort_community_rules = info_result.get("snort_community_rule", {}).get("rules", [])
            emerging_rules = info_result.get("emerging_rule", {}).get("rules", [])

            return templates.TemplateResponse("info.html",{
                "request": request,
                "info": info_result,
                "type": attack_type,
                "type_description": attack_description,
                "metrics_summary": metrics_summary,
                "current_date": current_date,
                "snort_community_rule": snort_community_rules,
                "emerging_rule": emerging_rules
            })

         # 키워드로 검색시
        elif filter_type == "Keyword":
            search_results = get_cve_details(cve_code)
            if not search_results:
                return JSONResponse(content={"error": "No results found"}, status_code=404)

            translated_results = await translate_bulk_to_korean(search_results)
            return templates.TemplateResponse("getinfo.html", {
                "request": request,
                "search_results": translated_results
            })

        # 뉴스 기사, 칼럼 으로 검색시
        elif filter_type == "News":
            search_results = await news_search(keyword=cve_code)
            if not search_results:
                return JSONResponse(content={"error": "No results found"}, status_code=404)

            return templates.TemplateResponse("getinfo.html", {
                "request": request,
                "news_search_results": search_results
            })

         # 필터 타입이 올바르지 않을 경우
        else:
            return templates.TemplateResponse(
                "error.html", {"request": request, "error": "Invalid filter type."}
            )
           

    except InfoServiceError as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@router.get("/redirect-to-ruletest")
async def redirect_to_ruletest():
    return RedirectResponse(url="/ruletest")


@router.post("/saveinfo")
async def create_vulnerability(request: Request, vulnerability: VulnerabilityCreate):
    user_info = profile(supabase, request)
    print(user_info)
    if not user_info:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user_info['user'].user.id # 사용자 ID 가져오기

    vulnerability_data = vulnerability.model_dump()
    vulnerability_data['user_id'] = user_id
    response = supabase.table("info").insert(vulnerability_data).execute()
    
    # 오류 처리를 위한 수정된 코드
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"]["message"])
    
    return {"message": "취약점 정보 수집 성공!"}
