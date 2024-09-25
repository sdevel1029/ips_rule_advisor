from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.supabase_client import get_supabase_client
from src.root.root_service import get_past_cve_list

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

# 메인페이지 요청 라우터
@router.get("/", response_class=HTMLResponse)
async def get_info_page(request: Request, client=Depends(get_supabase_client)):
    user_cookie = request.cookies.get("user")  # 쿠키에서 사용자 정보를 가져옴

    # 로그인 여부에 따른 처리
    if user_cookie:
        # 로그인한 경우 CVE 리스트를 가져옴
        past_cve_list = get_past_cve_list(client=client, request=request)
    else:
        # 로그인하지 않은 경우 빈 리스트 처리
        past_cve_list = []

    # 디버깅용 출력
    print(f"User: {user_cookie}, CVE List: {past_cve_list}")

    # 템플릿에 'past_cve' 정보 전달
    return templates.TemplateResponse(
        "getinfo.html", 
        {"request": request, "past_cve_list": past_cve_list}
    )