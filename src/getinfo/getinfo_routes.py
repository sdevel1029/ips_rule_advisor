# src/getinfo/getinfo_routes.py
from fastapi import APIRouter, Request
from src.getinfo.getinfo_service import get_info, InfoServiceError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.openai.openai_service import (
    translate_to_korean,
    classify_attack,
    summarize_vector,
)
from starlette.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/getinfo", response_class=HTMLResponse)
async def get_info_page(request: Request, cve_code: str = None):
    # cve_code = request.query_params.get("cve_code") FastAPI가 자동 매핑해줌
    if not cve_code:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "cve_code parameter is required"},
        )

    try:
        info_result = await get_info(cve_code)

        if "설명" in info_result.get("nvd", {}):
            info_result["nvd"]["설명"] = await translate_to_korean(
                info_result["nvd"]["설명"]
            )

        if "메트릭" in info_result.get("nvd", {}):
            metrics_summary = await summarize_vector(info_result["nvd"]["메트릭"])
        else:
            metrics_summary = None

        attack_type = await classify_attack(info_result["nvd"]["설명"])

        return templates.TemplateResponse(
            "info.html",
            {
                "request": request,
                "info": info_result,
                "type": attack_type,
                "metrics_summary": metrics_summary,
            },
        )
    except InfoServiceError as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@router.get("/redirect-to-ruletest")
async def redirect_to_ruletest():
    return RedirectResponse(url="/ruletest")
