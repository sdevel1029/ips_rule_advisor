from fastapi import APIRouter, Request, Depends, Response
from src.database.supabase_client import get_supabase_client
from src.sidebar.sidebar_service import get_past_cve_list, get_past_test_list

router = APIRouter()

@router.get("/past_info")
async def get_past_info(request: Request, response: Response, client=Depends(get_supabase_client)):
    # 사용자 정보 기반으로 CVE 및 테스트 리스트 가져오기
    past_info_list = await get_past_cve_list(client, request, response)
    past_test_list = await get_past_test_list(client, request, response)
    
    # 결과 반환
    return {"past_info_list": past_info_list, "past_test_list": past_test_list}
